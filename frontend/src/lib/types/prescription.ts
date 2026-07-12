/** 처방전 항목 한 줄 — PrescriptionItemSerializer. */
export interface PrescriptionItem {
	id: number;
	/** Medicine FK id */
	medicine: number;
	medicine_name: string;
	dosage_instruction: string;
}

/** 처방전 상세/목록 — PrescriptionSerializer. */
export interface Prescription {
	id: number;
	title: string;
	issued_on: string | null;
	created_at: string;
	items: PrescriptionItem[];
}

/** POST /api/prescriptions/ 등록 시 보내는 항목. */
export interface PrescriptionItemInput {
	medicine: number;
	dosage_instruction?: string;
}

/** POST /api/prescriptions/ 등록 페이로드. */
export interface PrescriptionCreate {
	title?: string;
	issued_on?: string | null;
	items: PrescriptionItemInput[];
}

/** 단일 영양소 추천 — NutrientRecommendationSerializer. */
export interface NutrientRecommendation {
	nutrient_id: number;
	nutrient_name: string;
	/** 처방전 내 모든 성분↔영양소 상호작용 가중치 합 (랭킹 점수). */
	score: number;
	/** 이 영양소와 관련된 처방 약품명 목록 (성분명이 아님). */
	medicines: string[];
}

/** positive·caution 양쪽에 걸친 영양소 충돌 — NutrientConflictSerializer. */
export interface NutrientConflict {
	nutrient_id: number;
	nutrient_name: string;
	/** 이 영양소를 필요로 하는 약품. */
	positive_medicines: string[];
	/** 이 영양소와 상호작용 우려가 있는 약품. */
	caution_medicines: string[];
	/** 상담 권고 안내 문구. */
	message: string;
}

/** GET /api/prescriptions/{id}/recommendations/ — RecommendationResultSerializer. */
export interface RecommendationResult {
	/** 보충이 필요한 영양소 (effect=positive). */
	needed: NutrientRecommendation[];
	/** 섭취 주의가 필요한 영양소 (effect=caution). */
	caution: NutrientRecommendation[];
	/** 필요·주의가 동시에 걸려 상담이 필요한 영양소. */
	conflicts: NutrientConflict[];
}
