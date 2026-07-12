import { api } from './client';
import type { Medicine, Nutrient } from '$lib/types';

/** GET /api/medicines/ — 약품 카탈로그(성분 포함). */
export function listMedicines(signal?: AbortSignal): Promise<Medicine[]> {
	return api.get<Medicine[]>('/api/medicines/', signal);
}

/** GET /api/nutrients/ — 영양소 참조 목록. */
export function listNutrients(signal?: AbortSignal): Promise<Nutrient[]> {
	return api.get<Nutrient[]>('/api/nutrients/', signal);
}
