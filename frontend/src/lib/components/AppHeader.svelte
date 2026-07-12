<script lang="ts">
	import type { Snippet } from 'svelte';
	import Icon from './Icon.svelte';
	import AppLogo from './AppLogo.svelte';

	interface Props {
		title: string;
		subtitle?: string;
		/** 뒤로가기 버튼 표시 여부. */
		back?: boolean;
		onback?: () => void;
		/** 우측 액션 슬롯. */
		action?: Snippet;
	}

	let { title, subtitle, back = false, onback, action }: Props = $props();

	function goBack() {
		if (onback) onback();
		else history.back();
	}
</script>

<header
	class="sticky top-0 z-30 border-b border-gray-100 bg-white/90 backdrop-blur-md pt-[env(safe-area-inset-top)]"
>
	<div class="mx-auto flex h-14 max-w-md items-center gap-2 px-4">
		{#if back}
			<button
				type="button"
				onclick={goBack}
				aria-label="뒤로 가기"
				class="-ml-2 flex size-9 items-center justify-center rounded-full text-gray-500 hover:bg-gray-100"
			>
				<Icon name="arrow-left" size={22} />
			</button>
		{:else}
			<!-- 좌상단 앱 아이콘 -->
			<AppLogo size={30} class="-ml-0.5 shrink-0 rounded-lg" />
		{/if}
		<div class="min-w-0 flex-1">
			<h1 class="truncate text-base font-bold text-gray-900">{title}</h1>
			{#if subtitle}<p class="truncate text-xs text-gray-400">{subtitle}</p>{/if}
		</div>
		{#if action}
			<div class="shrink-0">{@render action()}</div>
		{/if}
	</div>
</header>
