<script lang="ts">
	// reference/tabllet_app_icon.png 를 참조한 앱 로고: teal 라운드 사각형 위에
	// 캡슐(알약)이 작은 테이블에 놓인 모양 (table + tablet = Tabllet).
	interface Props {
		size?: number;
		class?: string;
	}
	let { size = 28, class: className = '' }: Props = $props();
</script>

<svg
	width={size}
	height={size}
	viewBox="0 0 48 48"
	fill="none"
	class={className}
	role="img"
	aria-label="Tabllet"
>
	<rect width="48" height="48" rx="11" fill="#0e7490" />
	<!-- 캡슐(알약) -->
	<rect x="12" y="11" width="24" height="9" rx="4.5" fill="#ffffff" />
	<line x1="24" y1="12.4" x2="24" y2="18.6" stroke="#0e7490" stroke-width="1.4" stroke-linecap="round" />
	<circle cx="29.4" cy="14" r="1.15" fill="#0e7490" />
	<!-- 테이블 상판 -->
	<rect x="9" y="22.8" width="30" height="3.6" rx="1.8" fill="#ffffff" />
	<!-- 바깥쪽 다리 2개 + 가로대 -->
	<g stroke="#ffffff" stroke-linecap="round" fill="none">
		<path d="M14 27 L11 39" stroke-width="3" />
		<path d="M34 27 L37 39" stroke-width="3" />
		<path d="M13 33.5 H35" stroke-width="2.6" />
	</g>
</svg>
