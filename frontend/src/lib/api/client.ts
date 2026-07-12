/**
 * 백엔드 통신의 단일 진입점.
 *
 * Svelte 컴포넌트에서 URL 을 하드코딩해 fetch 하지 않고, 모든 호출을 이 모듈을 통해
 * 도메인별 API 모듈(prescription.ts 등)에서 추상화한다 (CLAUDE.md "API 호출 중앙화").
 *
 * 백엔드는 모든 응답을 { success, data, error } 봉투로 감싸므로, 여기서 봉투를 풀어
 * 성공 시 data 를, 실패 시 ApiError 를 던진다.
 */
import { env } from '$env/dynamic/public';
import { authStore } from '$lib/stores/auth.svelte';
import type { ApiEnvelope, ApiErrorBody } from '$lib/types';

/**
 * 백엔드 주소.
 * - 미설정(기본): 빈 문자열 → 같은 출처(same-origin)로 호출한다. 개발 서버에서는
 *   vite.config.ts 의 프록시가 /api·/healthz 를 백엔드로 전달하므로, 원격 접속
 *   환경에서도 dev 포트 하나만 포워딩하면 동작한다(8000 포워딩·CORS 불필요).
 * - PUBLIC_API_BASE_URL 지정 시: 해당 절대 주소로 직접 호출(배포·Electron 등).
 */
export const API_BASE_URL = (env.PUBLIC_API_BASE_URL || '').replace(/\/$/, '');

/** API 호출 실패를 표현하는 에러. UI 는 message 를 그대로 보여줄 수 있다. */
export class ApiError extends Error {
	readonly status: number;
	readonly body: ApiErrorBody | null;

	constructor(message: string, status: number, body: ApiErrorBody | null = null) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
		this.body = body;
	}
}

/** DRF 에러 본문(문자열 / {detail} / 필드별 배열)에서 사람이 읽을 메시지를 추출. */
function describeError(body: ApiErrorBody | null, status: number): string {
	if (!body) return `요청을 처리하지 못했습니다 (HTTP ${status})`;
	if (typeof body === 'string') return body;
	if (typeof body.detail === 'string') return body.detail;
	const parts: string[] = [];
	for (const [field, value] of Object.entries(body)) {
		const text = Array.isArray(value) ? value.join(', ') : String(value);
		parts.push(field === 'non_field_errors' ? text : `${field}: ${text}`);
	}
	return parts.length ? parts.join('\n') : `요청을 처리하지 못했습니다 (HTTP ${status})`;
}

interface RequestOptions {
	method?: string;
	/** JSON 본문. body 와 동시 사용 금지. */
	json?: unknown;
	/** 원시 본문 (FormData 등). json 과 동시 사용 금지. */
	body?: BodyInit;
	signal?: AbortSignal;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
	const { method = 'GET', json, body, signal } = options;
	const headers: Record<string, string> = { Accept: 'application/json' };

	// 토큰이 있으면 DRF TokenAuthentication 형식으로 첨부한다.
	if (authStore.token) {
		headers['Authorization'] = `Token ${authStore.token}`;
	}

	let payload: BodyInit | undefined = body;
	if (json !== undefined) {
		headers['Content-Type'] = 'application/json';
		payload = JSON.stringify(json);
	}

	let response: Response;
	try {
		response = await fetch(`${API_BASE_URL}${path}`, { method, headers, body: payload, signal });
	} catch (cause) {
		if (cause instanceof DOMException && cause.name === 'AbortError') throw cause;
		throw new ApiError('서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해 주세요.', 0);
	}

	// 204 No Content 등 본문이 없는 응답.
	if (response.status === 204) return undefined as T;

	let envelope: ApiEnvelope<T> | null = null;
	try {
		envelope = (await response.json()) as ApiEnvelope<T>;
	} catch {
		envelope = null;
	}

	if (!response.ok || (envelope && envelope.success === false)) {
		// 토큰 만료/무효: 보관된 세션을 비워 레이아웃 가드가 온보딩으로 보낸다.
		// (로그인 자체의 401(잘못된 자격증명)은 토큰이 없으므로 영향 없음.)
		if (response.status === 401 && authStore.token) {
			authStore.clear();
		}
		const errorBody = envelope ? envelope.error : null;
		throw new ApiError(describeError(errorBody, response.status), response.status, errorBody);
	}

	// 봉투가 정상이면 data 를, 봉투가 아니면(이론상) 원본을 반환.
	return envelope ? (envelope.data as T) : (undefined as T);
}

export const api = {
	get: <T>(path: string, signal?: AbortSignal) => request<T>(path, { signal }),
	post: <T>(path: string, json?: unknown, signal?: AbortSignal) =>
		request<T>(path, { method: 'POST', json, signal }),
	patch: <T>(path: string, json?: unknown, signal?: AbortSignal) =>
		request<T>(path, { method: 'PATCH', json, signal }),
	postForm: <T>(path: string, form: FormData, signal?: AbortSignal) =>
		request<T>(path, { method: 'POST', body: form, signal }),
	delete: <T>(path: string, signal?: AbortSignal) =>
		request<T>(path, { method: 'DELETE', signal })
};
