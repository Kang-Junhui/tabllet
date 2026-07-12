/** 영양소 참조 항목 — GET /api/nutrients/ (NutrientSerializer). */
export interface Nutrient {
	id: number;
	name: string;
	description: string;
}

/** 약물 성분 — MedicineSerializer 안에 중첩되어 내려온다 (IngredientSerializer). */
export interface Ingredient {
	id: number;
	name: string;
	description: string;
}

/** 약품 카탈로그 항목 — GET /api/medicines/ (MedicineSerializer). */
export interface Medicine {
	id: number;
	name: string;
	manufacturer: string;
	ingredients: Ingredient[];
}
