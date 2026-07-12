/** 인증된 사용자 — UserSerializer (GET /api/auth/me/). */
export interface User {
	id: number;
	username: string;
}

/** register/login 응답 — {token, user}. */
export interface AuthSession {
	token: string;
	user: User;
}

/** 로그인·회원가입 입력. */
export interface Credentials {
	username: string;
	password: string;
}
