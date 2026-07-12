import type { CapacitorConfig } from '@capacitor/cli';

/**
 * Capacitor 설정 — SvelteKit adapter-static 출력(build/)을 안드로이드 앱으로 패키징.
 *
 * - webDir: 정적 SPA 빌드 결과 디렉토리.
 * - androidScheme 'http': 앱이 http://localhost 로 서빙되어, http 백엔드(Tailscale
 *   http://100.118...:8000) 호출 시 mixed-content 차단을 피한다. (카메라는 file input
 *   기반이라 secure-context가 필요 없음.)
 * - cleartext: 평문(http) API 호출 허용.
 *
 * 백엔드 절대주소는 빌드 시 PUBLIC_API_BASE_URL 로 주입한다 (package.json android:* 스크립트).
 */
const config: CapacitorConfig = {
	appId: 'kr.tabllet.app',
	appName: 'Tabllet',
	webDir: 'build',
	server: {
		androidScheme: 'http',
		cleartext: true
	}
};

export default config;
