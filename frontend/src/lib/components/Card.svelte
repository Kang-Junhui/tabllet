<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		/** 클릭 가능한 카드(목록 항목 등)면 href 또는 onclick 지정. */
		href?: string;
		onclick?: () => void;
		padded?: boolean;
		class?: string;
		children: Snippet;
	}

	let { href, onclick, padded = true, class: className = '', children }: Props = $props();

	const base =
		'block rounded-2xl bg-white border border-gray-100 shadow-[0_1px_2px_rgba(16,24,40,0.04),0_1px_3px_rgba(16,24,40,0.06)]';
	const interactive =
		'text-left w-full transition-colors hover:border-brand-200 hover:bg-brand-50/40 focus-visible:outline-2 focus-visible:outline-brand-500';

	let classes = $derived(
		`${base} ${href || onclick ? interactive : ''} ${padded ? 'p-4' : ''} ${className}`
	);
</script>

{#if href}
	<a {href} class={classes}>{@render children()}</a>
{:else if onclick}
	<button type="button" {onclick} class={classes}>{@render children()}</button>
{:else}
	<div class={classes}>{@render children()}</div>
{/if}
