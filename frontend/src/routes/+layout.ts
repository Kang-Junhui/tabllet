// Electron 데스크톱 앱 제약: 서버 사이드 렌더링(SSR)을 전역적으로 금지한다.
// 정적으로 prerender 된 셸을 클라이언트에서 하이드레이션해 SPA 로 동작한다.
// (CLAUDE.md 프론트엔드 코딩 컨벤션)
export const ssr = false;
export const prerender = true;
