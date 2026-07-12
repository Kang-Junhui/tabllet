from django.contrib import admin

from .models import (
    DrugCaution,
    Ingredient,
    IngredientNutrient,
    Medicine,
    MedicineIngredient,
    Nutrient,
    Prescription,
    PrescriptionItem,
)


class IngredientNutrientInline(admin.TabularInline):
    model = IngredientNutrient
    extra = 1


class MedicineIngredientInline(admin.TabularInline):
    model = MedicineIngredient
    extra = 1


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Nutrient)
class NutrientAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    inlines = [IngredientNutrientInline]


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    search_fields = ["name", "manufacturer"]
    inlines = [MedicineIngredientInline]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "issued_on", "created_at"]
    inlines = [PrescriptionItemInline]


@admin.register(DrugCaution)
class DrugCautionAdmin(admin.ModelAdmin):
    list_display = ["medicine", "source", "fetched_at"]
    readonly_fields = ["fetched_at"]
