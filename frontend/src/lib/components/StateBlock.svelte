<script lang="ts">
	import type { Snippet } from 'svelte';
	import Icon, { type IconName } from './Icon.svelte';
	import Spinner from './Spinner.svelte';

	interface Props {
		/** loading 이면 스피너, 아니면 icon 을 보여준다. */
		variant?: 'loading' | 'empty' | 'error';
		icon?: IconName;
		title: string;
		description?: string;
		/** 버튼 등 부가 액션 슬롯. */
		action?: Snippet;
	}

	let { variant = 'empty', icon = 'info', title, description, action }: Props = $props();

	let tone = $derived(
		{
			loading: 'bg-brand-50 text-brand-500',
			empty: 'bg-gray-100 text-gray-400',
			error: 'bg-caution-50 text-caution-500'
		}[variant]
	);
</script>

<div class="flex flex-col items-center justify-center gap-4 px-6 py-14 text-center">
	<span class="flex size-16 items-center justify-center rounded-2xl {tone}">
		{#if variant === 'loading'}
			<Spinner size={30} />
		{:else}
			<Icon name={variant === 'error' ? 'alert-triangle' : icon} size={30} />
		{/if}
	</span>
	<div>
		<p class="text-lg font-bold text-gray-800">{title}</p>
		{#if description}
			<p class="mx-auto mt-1.5 max-w-xs text-sm whitespace-pre-line text-gray-500">{description}</p>
		{/if}
	</div>
	{#if action}
		{@render action()}
	{/if}
</div>
