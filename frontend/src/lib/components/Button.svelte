<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';
	import Spinner from './Spinner.svelte';

	type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
	type Size = 'sm' | 'md' | 'lg';

	interface Props extends HTMLButtonAttributes {
		variant?: Variant;
		size?: Size;
		loading?: boolean;
		full?: boolean;
		/** 지정 시 <a> 로 렌더링한다 (라우팅 링크). */
		href?: string;
		children: Snippet;
	}

	let {
		variant = 'primary',
		size = 'md',
		loading = false,
		full = false,
		href,
		disabled,
		type = 'button',
		class: className = '',
		children,
		...rest
	}: Props = $props();

	const base =
		'inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-colors duration-150 focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:opacity-50 select-none';

	const variants: Record<Variant, string> = {
		primary: 'bg-brand-600 text-white hover:bg-brand-700 active:bg-brand-800 shadow-sm',
		secondary: 'bg-brand-50 text-brand-700 hover:bg-brand-100 border border-brand-100',
		ghost: 'bg-transparent text-gray-600 hover:bg-gray-100',
		danger: 'bg-caution-600 text-white hover:bg-caution-700 active:bg-caution-700 shadow-sm'
	};

	const sizes: Record<Size, string> = {
		sm: 'h-9 px-3 text-sm',
		md: 'h-11 px-4 text-[0.95rem]',
		lg: 'h-13 px-5 text-base'
	};

	let classes = $derived(
		`${base} ${variants[variant]} ${sizes[size]} ${full ? 'w-full' : ''} ${className}`
	);
	let isDisabled = $derived(disabled || loading);
</script>

{#if href}
	<a {href} class={classes} aria-disabled={isDisabled} {...(rest as Record<string, unknown>)}>
		{#if loading}<Spinner size={18} />{/if}
		{@render children()}
	</a>
{:else}
	<button {type} class={classes} disabled={isDisabled} {...rest}>
		{#if loading}<Spinner size={18} />{/if}
		{@render children()}
	</button>
{/if}
