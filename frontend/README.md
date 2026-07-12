# Tabllet — Frontend

처방전 기반 맞춤 영양소 안내 서비스의 클라이언트.

- **SvelteKit (SPA 모드 · `@sveltejs/adapter-static`) + TypeScript**
- **Tailwind CSS v4** (brand=teal, positive=blue, caution=orange 디자인 토큰)
- 데스크톱 앱(Electron) 패키징 대상이므로 **SSR 금지** (`src/routes/+layout.ts`에서
  `ssr=false`, `prerender=true`). 모든 데이터는 클라이언트에서 Django API 를 호출해 가져온다.

## 디렉토리 구조

```
src/
├── routes/                       파일 기반 라우팅
│   ├── +layout.svelte            앱 셸 (모바일 폭 컨테이너 · 하단 네비 · 토스트)
│   ├── +layout.ts                ssr=false / prerender=true (전역)
│   ├── +page.svelte              홈: 처방전 스캔 → 약품 선택 → 처방전 생성
│   ├── prescriptions/
│   │   ├── +page.svelte          내 처방전 목록
│   │   └── [id]/+page.svelte     처방전 상세 + 영양소 추천 (needed / caution)
│   └── reference/+page.svelte    약품·영양소 참고 목록
└── lib/
    ├── api/        Django API 호출 중앙화 (client + 도메인별 모듈)
    ├── components/ 재사용 UI (PascalCase, 단색 아이콘)
    ├── stores/     상태 관리 (스캔 플로우 · 토스트, Svelte 5 runes)
    └── types/      DTO 타입 정의
```

## 환경 변수

| 변수 | 설명 | 기본값 |
| --- | --- | --- |
| `PUBLIC_API_BASE_URL` | Django 백엔드 주소 (trailing slash 제외) | `http://localhost:8000` |

`.env` 에 `PUBLIC_API_BASE_URL=...` 로 지정하거나 빌드 시 환경에 주입한다.

## 개발 / 빌드

```sh
pnpm install
pnpm dev          # 개발 서버 (Vite, http://localhost:5173)
pnpm check        # svelte-check 타입 검사
pnpm build        # 정적 SPA 빌드 → build/
pnpm preview      # 빌드 결과 미리보기
```

> Electron 패키징은 추후 별도 단계에서 추가한다 (`adapter-static` 출력 `build/` 를
> 데스크톱 셸에서 로드하는 방식).
