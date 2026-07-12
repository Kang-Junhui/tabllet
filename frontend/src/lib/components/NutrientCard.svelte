<script lang="ts">
	import type { NutrientRecommendation } from '$lib/types';
	import Icon from './Icon.svelte';

	interface Props {
		recommendation: NutrientRecommendation;
		/** positive: 보충 권장(블루) / caution: 주의(주황·적색) */
		kind: 'positive' | 'caution';
	}

	let { recommendation, kind }: Props = $props();

	const themes = {
		positive: {
			ring: 'border-positive-100',
			accent: 'bg-positive-500',
			icon: 'leaf' as const,
			iconWrap: 'bg-positive-50 text-positive-600'
		},
		caution: {
			ring: 'border-caution-100',
			accent: 'bg-caution-500',
			icon: 'alert-triangle' as const,
			iconWrap: 'bg-caution-50 text-caution-600'
		}
	};
	let theme = $derived(themes[kind]);
</script>

<article
	class="relative overflow-hidden rounded-2xl border bg-white p-4 shadow-sm {theme.ring}"
>
	<span class="absolute inset-y-0 left-0 w-1.5 {theme.accent}" aria-hidden="true"></span>
	<div class="flex items-start gap-3 pl-1.5">
		<span class="flex size-10 shrink-0 items-center justify-center rounded-xl {theme.iconWrap}">
			<Icon name={theme.icon} size={20} />
		</span>
		<div class="min-w-0 flex-1">
			<h3 class="truncate text-base font-bold text-gray-900">{recommendation.nutrient_name}</h3>
			{#if recommendation.medicines.length}
				<p class="mt-0.5 text-xs text-gray-400">
					관련 약품 {recommendation.medicines.length}개
				</p>
				<ul class="mt-2 flex flex-wrap gap-1.5">
					{#each recommendation.medicines as medicine (medicine)}
						<li class="rounded-lg bg-gray-50 px-2 py-1 text-xs text-gray-600">{medicine}</li>
					{/each}
				</ul>
			{/if}
		</div>
	</div>
</article>
