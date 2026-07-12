import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

// 개발 서버(원격 포함) 시 백엔드 주소. 기본은 같은 호스트의 Django(:8000).
// 브라우저는 dev 포트로만 통신하고, 아래 프록시가 서버 안에서 /api·/healthz 를
// 백엔드로 전달하므로 내부망 다른 기기에서 접속해도 8000 노출이 필요 없다.
const BACKEND = process.env.VITE_DEV_BACKEND || 'http://localhost:8000';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		// 0.0.0.0 바인딩 — 내부망의 다른 기기에서 http://<서버IP>:5174 로 접속 가능.
		host: true,
		// 접속 URL 을 고정하기 위해 포트를 명시. 점유 중이면 에러로 알려준다
		// (다른 포트로 변경하려면 이 값만 수정).
		port: 5174,
		strictPort: true,
		// 내부망에서 IP·호스트네임으로 들어오는 요청을 허용 (Vite host 검사 우회).
		allowedHosts: true,
		proxy: {
			'/api': { target: BACKEND, changeOrigin: true },
			'/healthz': { target: BACKEND, changeOrigin: true }
		}
	}
});
