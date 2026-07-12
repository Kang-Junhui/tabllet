/**
 * 이미지 스캔 적재 결과 — POST /api/prescriptions/scan/ (api/ingest.scan_prescription_image).
 */

/**
 * 인식된 약품의 카탈로그 상태.
 * - existing:  이미 DB 에 있던 약품
 * - imported:  이번 스캔에서 HIRA→LLM 적재로 새로 등록됨
 * - not_found: HIRA 에 데이터가 없어 등록하지 못함 (이름 수정 후 재확인 가능)
 * - error:     적재 중 오류 발생 (처방전에 담을 수 없어 클라이언트가 목록에서 제거)
 */
export type ScanStatus = 'existing' | 'imported' | 'not_found' | 'error';

export interface ScannedMedicine {
	name: string;
	/** 카탈로그에 등록된 경우의 Medicine id (not_found 면 null). */
	medicine_id: number | null;
	status: ScanStatus;
}

export interface ScanResult {
	/** OCR 이 인식한 약물명 목록 (용량·단위 제거된 기본명). */
	recognized: string[];
	medicines: ScannedMedicine[];
}
