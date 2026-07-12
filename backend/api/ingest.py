"""Ingest pipeline: prescription image -> recognized & catalogued medicines.

    OCR(image) -> drug names
      for every name not already in the catalog (batched):
        HIRA(name)   -> raw 사용상의주의사항 records              ※ cache-first
        LLM(records) -> {name: {positive: [...], caution: [...]}}   ※ one batch call
        persist      -> Medicine + Ingredient + Nutrient(s) + IngredientNutrient
                        + DrugCaution

The refine server already classifies nutrients with the IngredientNutrient
effect vocabulary (`positive` = 보충 권장, `caution` = 제한 권장), so the buckets
map straight onto the effect. The refinement is batched: all unknown drugs go to
the LLM server in a single request.

Network calls happen synchronously within the request. For large batches this
should move to a task queue; documented here intentionally.
"""
import logging

from django.db import transaction

from .integrations import hira, llm, ocr

logger = logging.getLogger(__name__)
from .models import (
    DrugCaution,
    Ingredient,
    IngredientNutrient,
    Medicine,
    MedicineIngredient,
    Nutrient,
)

# Refine-server buckets, which already use the IngredientNutrient.Effect vocabulary.
_EFFECT_BY_BUCKET = {
    "positive": IngredientNutrient.Effect.POSITIVE,
    "caution": IngredientNutrient.Effect.CAUTION,
}


def _link_nutrients(ingredient: Ingredient, names: list, effect: str) -> None:
    """Attach each named nutrient to the ingredient with the given effect."""
    for raw in names or []:
        nutrient_name = (raw or "").strip()
        if not nutrient_name:
            continue
        nutrient, _ = Nutrient.objects.get_or_create(name=nutrient_name)
        IngredientNutrient.objects.get_or_create(
            ingredient=ingredient, nutrient=nutrient, effect=effect
        )


@transaction.atomic
def _persist_drug(name: str, summary: dict, refined: dict) -> Medicine:
    """Create the Medicine and derived rows from one drug's refined buckets."""
    # Store under the recognized (OCR) name so future scans match on lookup.
    medicine = Medicine.objects.create(name=name)

    # The refine server no longer returns an ingredient list; use HIRA's primary
    # ingredient, falling back to the drug name so the nutrient links stay valid.
    ingredient_name = (summary.get("ingredient") or "").strip() or name
    ingredient, _ = Ingredient.objects.get_or_create(name=ingredient_name)
    MedicineIngredient.objects.get_or_create(medicine=medicine, ingredient=ingredient)

    for bucket, effect in _EFFECT_BY_BUCKET.items():
        _link_nutrients(ingredient, refined.get(bucket), effect)

    DrugCaution.objects.create(
        medicine=medicine,
        raw_precautions=summary.get("사용상의주의사항", []),
        refined=refined,
    )
    return medicine


def import_drugs(names: list[str]) -> tuple[dict[str, Medicine | None], list[str]]:
    """Fetch -> batch-refine -> persist every unknown drug.

    Resilient per-drug: a failure persisting one drug must not abort the whole
    batch (otherwise a single bad drug 500s the entire scan/resolve request).
    Each drug's persist is its own atomic unit, so a failure rolls back only that
    drug. Returns ``(result, failed)`` where ``result`` is {name: Medicine|None}
    (None = no HIRA data) and ``failed`` lists names whose import raised.
    """
    records_by_name = {name: hira.fetch_records(name) for name in names}
    refinable = {name: recs for name, recs in records_by_name.items() if recs}

    refined_by_name = llm.refine_drugs(refinable) if refinable else {}

    result: dict[str, Medicine | None] = {}
    failed: list[str] = []
    for name in names:
        records = records_by_name.get(name)
        if not records:
            result[name] = None  # HIRA has no data -> not_found
            continue
        try:
            summary = hira.summarize(name, records) or {}
            refined = refined_by_name.get(name) or {"positive": [], "caution": []}
            result[name] = _persist_drug(name, summary, refined)
        except Exception:  # noqa: BLE001 — one bad drug shouldn't kill the batch
            logger.exception("Failed to import drug %r", name)
            result[name] = None
            failed.append(name)
    return result, failed


def resolve_drug_names(names: list[str]) -> dict:
    """Map drug names to catalog status (existing / imported / not_found).

    Dedupes and trims names, imports unknown ones via HIRA→LLM, and reports the
    per-drug status. Reused by both image scan and manual name correction so the
    user can fix OCR misreads or add drugs the OCR missed.
    """
    names = list(dict.fromkeys(n.strip() for n in names if n and n.strip()))

    existing = {m.name: m for m in Medicine.objects.filter(name__in=names)}
    unknown = [name for name in names if name not in existing]
    imported, failed = import_drugs(unknown) if unknown else ({}, [])
    failed_set = set(failed)

    medicines = []
    for name in names:
        if name in existing:
            medicines.append(
                {"name": name, "medicine_id": existing[name].id, "status": "existing"}
            )
        elif imported.get(name):
            medicines.append(
                {"name": name, "medicine_id": imported[name].id, "status": "imported"}
            )
        elif name in failed_set:
            # 적재 중 오류가 난 약품: 처방전에 담을 수 없으니 클라이언트가 제거하도록 표시.
            medicines.append({"name": name, "medicine_id": None, "status": "error"})
        else:
            medicines.append({"name": name, "medicine_id": None, "status": "not_found"})

    return {"recognized": names, "medicines": medicines}


def scan_prescription_image(image_bytes: bytes, filename: str, content_type: str) -> dict:
    """Run the full pipeline for an uploaded image and report per-drug status."""
    names = ocr.extract_drug_names(image_bytes, filename, content_type)
    return resolve_drug_names(names)
