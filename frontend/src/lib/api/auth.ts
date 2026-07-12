import { api } from './client';
import type { AuthSession, Credentials, User } from '$lib/types';

/** POST /api/auth/register/ — 회원가입 후 토큰·사용자 반환. */
export function register(credentials: Credentials, signal?: AbortSignal): Promise<AuthSession> {
	return api.post<AuthSession>('/api/auth/register/', credentials, signal);
}

/** POST /api/auth/login/ — 로그인 후 토큰·사용자 반환. */
export function login(credentials: Credentials, signal?: AbortSignal): Promise<AuthSession> {
	return api.post<AuthSession>('/api/auth/login/', credentials, signal);
}

/** POST /api/auth/logout/ — 서버 측 토큰 무효화. */
export function logout(signal?: AbortSignal): Promise<{ detail: string }> {
	return api.post<{ detail: string }>('/api/auth/logout/', undefined, signal);
}

/** GET /api/auth/me/ — 저장된 토큰의 유효성 확인 + 최신 사용자 정보. */
export function fetchMe(signal?: AbortSignal): Promise<User> {
	return api.get<User>('/api/auth/me/', signal);
}
