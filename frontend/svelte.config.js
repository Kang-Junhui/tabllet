import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/**
 * SPA (단일 페이지 앱) 모드 설정.
 *
 * 이 앱은 최종적으로 Electron 데스크톱 앱으로 패키징되므로 서버가 없다.
 * 따라서 adapter-static + SPA fallback 으로 정적 빌드한다. 모든 데이터는
 * 클라이언트에서 Django API 를 직접 호출해 가져온다(SSR 금지, src/routes/+layout.ts 참고).
 *
 * @type {import('@sveltejs/kit').Config}
 */
const config = {
	preprocess: vitePreprocess(),
	compilerOptions: {
		runes: true
	},
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			// 동적 라우트(/prescriptions/[id])는 빌드 시 알 수 없으므로 SPA fallback 으로 처리한다.
			fallback: 'index.html',
			precompress: false,
			strict: false
		}),
		// file:// (Electron) 환경에서도 자산 경로가 깨지지 않도록 상대 경로 사용.
		paths: {
			relative: true
		}
	}
};

export default config;
