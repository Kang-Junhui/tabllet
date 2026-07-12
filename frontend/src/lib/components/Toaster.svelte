<script lang="ts">
	import { fly } from 'svelte/transition';
	import { toasts } from '$lib/stores/toast.svelte';
	import Icon, { type IconName } from './Icon.svelte';

	const style: Record<string, { icon: IconName; class: string }> = {
		info: { icon: 'info', class: 'border-gray-200 text-gray-700' },
		success: { icon: 'check-circle', class: 'border-brand-200 text-brand-700' },
		error: { icon: 'alert-triangle', class: 'border-caution-200 text-caution-700' }
	};
</script>

<div
	class="pointer-events-none fixed inset-x-0 top-0 z-50 mx-auto flex max-w-md flex-col gap-2 px-4 pt-[max(0.75rem,env(safe-area-inset-top))]"
>
	{#each toasts.items as toast (toast.id)}
		<div
			role="alert"
			transition:fly={{ y: -16, duration: 200 }}
			class="pointer-events-auto flex items-start gap-2.5 rounded-xl border bg-white px-3.5 py-3 shadow-lg {style[
				toast.kind
			].class}"
		>
			<Icon name={style[toast.kind].icon} size={18} strokeWidth={2} class="mt-0.5 shrink-0" />
			<p class="flex-1 text-sm font-medium whitespace-pre-line">{toast.message}</p>
			<button
				type="button"
				class="shrink-0 text-gray-300 hover:text-gray-500"
				aria-label="닫기"
				onclick={() => toasts.dismiss(toast.id)}
			>
				<Icon name="x" size={16} strokeWidth={2} />
			</button>
		</div>
	{/each}
</div>
