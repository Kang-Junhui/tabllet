<script lang="ts">
	interface Props {
		size?: number;
		class?: string;
	}
	let { size = 24, class: className = '' }: Props = $props();
</script>

<svg
	class="animate-spin {className}"
	width={size}
	height={size}
	viewBox="0 0 24 24"
	fill="none"
	aria-label="로딩 중"
	role="status"
>
	<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2.5" class="opacity-20" />
	<path
		d="M21 12a9 9 0 0 0-9-9"
		stroke="currentColor"
		stroke-width="2.5"
		stroke-linecap="round"
	/>
</svg>
