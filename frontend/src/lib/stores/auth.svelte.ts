/**
 * 인증 상태 (Svelte 5 runes).
 *
 * 토큰을 저장소에 보관해 앱을 다시 열어도 로그인이 유지되게 한다(자동 로그인).
 * - 자동 로그인 ON  → localStorage (영구 보관, 앱 재시작 후에도 유지)
 * - 자동 로그인 OFF → sessionStorage (탭/창을 닫으면 사라짐)
 *
 * SSR/prerender 중에는 window 가 없으므로 저장소 접근은 모두 browser 가드로 감싼다.
 */
import { browser } from '$app/environment';
import type { AuthSession, User } from '$lib/types';

const STORAGE_KEY = 'tabllet.auth';

class AuthStore {
	token = $state<string | null>(null);
	user = $state<User | null>(null);
	/** 자동 로그인 선호 (로그인 화면 체크박스와 연동). */
	remember = $state(true);
	/** 저장소에서 초기 복원이 끝났는지 — 가드가 깜빡임 없이 동작하도록. */
	ready = $state(false);

	get isAuthenticated(): boolean {
		return this.token !== null;
	}

	/** 앱 시작 시 1회 호출 — 저장된 세션을 복원한다. */
	restore() {
		if (!browser) return;
		const raw = localStorage.getItem(STORAGE_KEY) ?? sessionStorage.getItem(STORAGE_KEY);
		if (raw) {
			try {
				const parsed = JSON.parse(raw) as AuthSession;
				if (parsed?.token && parsed?.user) {
					this.token = parsed.token;
					this.user = parsed.user;
					this.remember = localStorage.getItem(STORAGE_KEY) !== null;
				}
			} catch {
				this.#wipeStorage();
			}
		}
		this.ready = true;
	}

	/** 로그인/회원가입 성공 시 세션 저장. */
	setSession(session: AuthSession, remember: boolean) {
		this.token = session.token;
		this.user = session.user;
		this.remember = remember;
		if (!browser) return;
		this.#wipeStorage();
		const store = remember ? localStorage : sessionStorage;
		store.setItem(STORAGE_KEY, JSON.stringify(session));
	}

	/** 자동 로그인 토글: 현재 세션을 선택한 저장소로 옮긴다(설정 화면용). */
	applyRemember(value: boolean) {
		if (this.token && this.user) {
			this.setSession({ token: this.token, user: this.user }, value);
		} else {
			this.remember = value;
		}
	}

	/** 로그아웃/토큰 만료 시 세션 제거. */
	clear() {
		this.token = null;
		this.user = null;
		this.#wipeStorage();
	}

	#wipeStorage() {
		if (!browser) return;
		localStorage.removeItem(STORAGE_KEY);
		sessionStorage.removeItem(STORAGE_KEY);
	}
}

export const authStore = new AuthStore();
