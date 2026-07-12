<script lang="ts">
	import type { NutrientConflict } from '$lib/types';
	import Icon from './Icon.svelte';

	interface Props {
		conflict: NutrientConflict;
	}
	let { conflict }: Props = $props();
</script>

<article class="rounded-2xl border-2 border-caution-200 bg-caution-50/60 p-4">
	<div class="flex items-start gap-3">
		<span
			class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-caution-100 text-caution-600"
		>
			<Icon name="alert-triangle" size={20} />
		</span>
		<div class="min-w-0 flex-1">
			<div class="flex flex-wrap items-center gap-2">
				<h3 class="text-base font-bold text-gray-900">{conflict.nutrient_name}</h3>
				<span
					class="rounded-full bg-caution-100 px-2 py-0.5 text-xs font-semibold text-caution-700"
				>
					필요 · 주의 동시
				</span>
			</div>

			<p class="mt-2 text-sm leading-relaxed text-gray-700">{conflict.message}</p>

			<dl class="mt-3 space-y-1.5">
				<div class="flex items-start gap-2 text-xs">
					<dt
						class="shrink-0 rounded-md bg-positive-50 px-1.5 py-0.5 font-semibold text-positive-700"
					>
						필요
					</dt>
					<dd class="text-gray-600">{conflict.positive_medicines.join(', ')}</dd>
				</div>
				<div class="flex items-start gap-2 text-xs">
					<dt
						class="shrink-0 rounded-md bg-caution-100 px-1.5 py-0.5 font-semibold text-caution-700"
					>
						주의
					</dt>
					<dd class="text-gray-600">{conflict.caution_medicines.join(', ')}</dd>
				</div>
			</dl>
		</div>
	</div>
</article>
