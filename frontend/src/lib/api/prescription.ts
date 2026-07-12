import { api } from './client';
import type {
	Prescription,
	PrescriptionCreate,
	RecommendationResult,
	ScanResult
} from '$lib/types';

/** GET /api/prescriptions/ — 내 처방전 목록. */
export function listPrescriptions(signal?: AbortSignal): Promise<Prescription[]> {
	return api.get<Prescription[]>('/api/prescriptions/', signal);
}

/** GET /api/prescriptions/{id}/ — 처방전 상세. */
export function getPrescription(id: number, signal?: AbortSignal): Promise<Prescription> {
	return api.get<Prescription>(`/api/prescriptions/${id}/`, signal);
}

/** DELETE /api/prescriptions/{id}/ — 처방전 삭제 (본인 것만). */
export function deletePrescription(id: number, signal?: AbortSignal): Promise<void> {
	return api.delete<void>(`/api/prescriptions/${id}/`, signal);
}

/** PATCH /api/prescriptions/{id}/ — 처방전 이름 등 부분 수정. */
export function updatePrescription(
	id: number,
	payload: { title?: string },
	signal?: AbortSignal
): Promise<Prescription> {
	return api.patch<Prescription>(`/api/prescriptions/${id}/`, payload, signal);
}

/** POST /api/prescriptions/ — 처방전 등록. */
export function createPrescription(
	payload: PrescriptionCreate,
	signal?: AbortSignal
): Promise<Prescription> {
	return api.post<Prescription>('/api/prescriptions/', payload, signal);
}

/** GET /api/prescriptions/{id}/recommendations/ — 영양소 추천(needed / caution). */
export function getRecommendations(
	id: number,
	signal?: AbortSignal
): Promise<RecommendationResult> {
	return api.get<RecommendationResult>(`/api/prescriptions/${id}/recommendations/`, signal);
}

/**
 * POST /api/prescriptions/scan/ — 처방전 이미지 업로드 → OCR→HIRA→LLM 적재.
 * 인식·등록된 약품 상태를 돌려준다(처방전 자체를 만들지는 않는다).
 */
export function scanPrescriptionImage(image: File, signal?: AbortSignal): Promise<ScanResult> {
	const form = new FormData();
	form.append('image', image);
	return api.postForm<ScanResult>('/api/prescriptions/scan/', form, signal);
}

/**
 * POST /api/prescriptions/resolve/ — 약품명 목록을 (이미지 없이) HIRA→LLM 로 재조회.
 * OCR 오인식을 수정하거나 누락된 약품을 추가한 뒤 카탈로그 상태를 다시 확인할 때 쓴다.
 */
export function resolveDrugNames(names: string[], signal?: AbortSignal): Promise<ScanResult> {
	return api.post<ScanResult>('/api/prescriptions/resolve/', { names }, signal);
}
