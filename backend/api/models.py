"""Domain models for the prescription -> nutrient recommendation service.

Schema (normalized per CLAUDE.md):

    User ─< Prescription ─< PrescriptionItem >─ Medicine ─< MedicineIngredient >─ Ingredient
                                                                                      │
                                                                  IngredientNutrient (N:M)
                                                                                      │
                                                                                  Nutrient

Privacy note: prescription data is sensitive health information. We deliberately
do NOT denormalize patient-identifying fields onto Prescription — the only link
to a person is the FK to the auth user, so identity and prescription content stay
separable. See CLAUDE.md "데이터베이스 및 보안".
"""
from django.conf import settings
from django.db import models


class Nutrient(models.Model):
    """A nutrient that may be needed or cautioned against (e.g. Vitamin B12)."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """An active pharmaceutical ingredient (성분), e.g. Metformin."""

    name = models.CharField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    nutrients = models.ManyToManyField(
        Nutrient,
        through="IngredientNutrient",
        related_name="ingredients",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class IngredientNutrient(models.Model):
    """N:M join table describing how an ingredient interacts with a nutrient.

    `effect` is the core of the recommendation algorithm: POSITIVE means the drug
    depletes/raises demand for the nutrient (the patient likely *needs* more),
    CAUTION means intake should be limited or it interferes with the drug.
    """

    class Effect(models.TextChoices):
        POSITIVE = "positive", "필요 (보충 권장)"
        CAUTION = "caution", "주의 (제한 권장)"

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="nutrient_links"
    )
    nutrient = models.ForeignKey(
        Nutrient, on_delete=models.CASCADE, related_name="ingredient_links"
    )
    effect = models.CharField(max_length=10, choices=Effect.choices)
    # 0..1 strength of the interaction, used to rank recommendations.
    weight = models.FloatField(default=1.0)
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "nutrient", "effect"],
                name="uniq_ingredient_nutrient_effect",
            )
        ]

    def __str__(self):
        return f"{self.ingredient} -> {self.nutrient} ({self.effect})"


class Medicine(models.Model):
    """A prescribed drug product (약품), composed of one or more ingredients."""

    name = models.CharField(max_length=200, unique=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through="MedicineIngredient",
        related_name="medicines",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MedicineIngredient(models.Model):
    """Join table: which ingredients (and how much) make up a medicine."""

    medicine = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, related_name="ingredient_links"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name="medicine_links"
    )
    dosage = models.CharField(max_length=80, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["medicine", "ingredient"],
                name="uniq_medicine_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.medicine} / {self.ingredient}"


class DrugCaution(models.Model):
    """Raw HIRA 사용상의주의사항 plus its LLM-refined structured form.

    Created by the ingest pipeline when a drug name from OCR is missing from the
    catalog. Keeps the provenance (raw text) alongside the refined JSON so the
    refinement can be audited or re-run later.
    """

    medicine = models.OneToOneField(
        "Medicine", on_delete=models.CASCADE, related_name="caution"
    )
    source = models.CharField(max_length=40, default="hira")
    # Cleaned NB_DOC_DATA text blocks as fetched from HIRA.
    raw_precautions = models.JSONField(default=list)
    # Structured payload returned by the LLM refinement server.
    refined = models.JSONField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Caution for {self.medicine}"


class Prescription(models.Model):
    """A prescription (처방전) belonging to a user, listing prescribed medicines."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )
    title = models.CharField(max_length=200, blank=True)
    issued_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    medicines = models.ManyToManyField(
        Medicine,
        through="PrescriptionItem",
        related_name="prescriptions",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Prescription #{self.pk}"


class PrescriptionItem(models.Model):
    """A single line on a prescription: one medicine and its dosage instructions."""

    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name="items"
    )
    medicine = models.ForeignKey(
        Medicine, on_delete=models.PROTECT, related_name="prescription_items"
    )
    dosage_instruction = models.CharField(max_length=200, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["prescription", "medicine"],
                name="uniq_prescription_medicine",
            )
        ]

    def __str__(self):
        return f"{self.prescription} / {self.medicine}"
