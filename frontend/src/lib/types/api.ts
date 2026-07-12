/**
 * 모든 백엔드 응답이 공유하는 통일 봉투 (CLAUDE.md "응답 규격 통일").
 *
 *   { "success": true,  "data": <payload>, "error": null }
 *   { "success": false, "data": null,      "error": <detail> }
 */
export interface ApiEnvelope<T> {
	success: boolean;
	data: T | null;
	error: ApiErrorBody | null;
}

/** DRF 예외 핸들러가 봉투의 `error` 로 넣는 본문. 형태가 일정하지 않아 느슨하게 둔다. */
export type ApiErrorBody =
	| string
	| { detail?: string; [key: string]: unknown }
	| Record<string, string[]>;
