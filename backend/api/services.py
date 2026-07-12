"""Business logic for nutrient recommendations.

Kept out of the views (Fat Models / Skinny Views, per CLAUDE.md): views call
``recommend_for_prescription`` and serialize the result, nothing more.
"""
from collections import defaultdict
from dataclasses import dataclass, field

from .models import IngredientNutrient, Prescription


@dataclass
class NutrientRecommendation:
    nutrient_id: int
    nutrient_name: str
    # Aggregated interaction weight across all ingredients in the prescription.
    score: float = 0.0
    # 약품명 목록 — 이 추천을 유발한 처방 약품들(성분명이 아니라 사용자가 아는 약품명).
    medicines: list[str] = field(default_factory=list)


@dataclass
class NutrientConflict:
    """A nutrient flagged as BOTH needed (positive) and cautioned (caution).

    One drug raises demand for the nutrient while another may interact with it,
    so the user must consult a professional before supplementing.
    """

    nutrient_id: int
    nutrient_name: str
    # 영양소를 필요로 하는 약품(positive) / 상호작용 우려가 있는 약품(caution).
    positive_medicines: list[str]
    caution_medicines: list[str]
    message: str


@dataclass
class RecommendationResult:
    needed: list[NutrientRecommendation]
    caution: list[NutrientRecommendation]
    conflicts: list[NutrientConflict]


def _josa(word: str, with_batchim: str, without_batchim: str) -> str:
    """Pick the right Korean particle based on the last char's 받침(batchim)."""
    if not word:
        return without_batchim
    code = ord(word[-1])
    if 0xAC00 <= code <= 0xD7A3:  # Hangul syllable block
        return with_batchim if (code - 0xAC00) % 28 else without_batchim
    return without_batchim  # numbers/latin → default form


def _conflict_message(nutrient: str, positives: list[str], cautions: list[str]) -> str:
    a = ", ".join(positives)
    b = ", ".join(cautions)
    return (
        f"현재 처방받은 {a}{_josa(a, '은', '는')} {nutrient}{_josa(nutrient, '을', '를')} "
        f"필요로 하지만, 함께 처방된 {b}{_josa(b, '과', '와')}는 상호작용이 발생할 수 "
        "있습니다. 섭취 전 반드시 주치의나 약사와 상담하세요."
    )


def recommend_for_prescription(prescription: Prescription) -> RecommendationResult:
    """Aggregate every ingredient↔nutrient interaction in a prescription.

    Walks Prescription -> medicines -> ingredients -> nutrient interactions,
    summing weights per (effect, nutrient). Each recommendation reports the
    *medicine names* that drove it (not ingredient names) so the user can see
    which drug relates to which nutrient. Nutrients flagged as both positive and
    caution are pulled out into ``conflicts`` with a consult-your-doctor message.
    """
    # 이 처방전의 약품과 (성분 → 약품명) 매핑을 만든다. 영양소 추천을 약품명으로
    # 표현하기 위해 어떤 약품이 어떤 성분을 갖는지 알아야 한다.
    ingredient_to_medicines: dict[int, list[str]] = defaultdict(list)
    ingredient_ids: set[int] = set()
    for medicine in prescription.medicines.prefetch_related("ingredients"):
        for ingredient in medicine.ingredients.all():
            ingredient_ids.add(ingredient.id)
            if medicine.name not in ingredient_to_medicines[ingredient.id]:
                ingredient_to_medicines[ingredient.id].append(medicine.name)

    links = IngredientNutrient.objects.filter(
        ingredient_id__in=ingredient_ids
    ).select_related("nutrient")

    # (effect, nutrient_id) -> NutrientRecommendation
    buckets: dict[tuple[str, int], NutrientRecommendation] = {}

    for link in links:
        key = (link.effect, link.nutrient_id)
        rec = buckets.get(key)
        if rec is None:
            rec = NutrientRecommendation(
                nutrient_id=link.nutrient_id,
                nutrient_name=link.nutrient.name,
            )
            buckets[key] = rec
        rec.score += link.weight
        for medicine_name in ingredient_to_medicines.get(link.ingredient_id, ()):
            if medicine_name not in rec.medicines:
                rec.medicines.append(medicine_name)

    positive = IngredientNutrient.Effect.POSITIVE
    caution = IngredientNutrient.Effect.CAUTION

    # 같은 영양소가 positive·caution 양쪽에 있으면 충돌로 분리한다.
    positive_nids = {nid for (eff, nid) in buckets if eff == positive}
    caution_nids = {nid for (eff, nid) in buckets if eff == caution}
    conflict_nids = positive_nids & caution_nids

    def collect(effect: str) -> list[NutrientRecommendation]:
        recs = [
            r
            for (eff, nid), r in buckets.items()
            if eff == effect and nid not in conflict_nids
        ]
        return sorted(recs, key=lambda r: (-r.score, r.nutrient_name))

    conflicts: list[NutrientConflict] = []
    for nid in conflict_nids:
        pos = buckets[(positive, nid)]
        cau = buckets[(caution, nid)]
        conflicts.append(
            NutrientConflict(
                nutrient_id=nid,
                nutrient_name=pos.nutrient_name,
                positive_medicines=pos.medicines,
                caution_medicines=cau.medicines,
                message=_conflict_message(
                    pos.nutrient_name, pos.medicines, cau.medicines
                ),
            )
        )
    conflicts.sort(key=lambda c: c.nutrient_name)

    return RecommendationResult(
        needed=collect(positive),
        caution=collect(caution),
        conflicts=conflicts,
    )
