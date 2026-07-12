<script lang="ts">
	import { page } from '$app/state';
	import { getPrescription, getRecommendations, ApiError } from '$lib/api';
	import type { Prescription, RecommendationResult } from '$lib/types';
	import {
		AppHeader,
		Button,
		Card,
		ConflictCard,
		Icon,
		NutrientCard,
		StateBlock
	} from '$lib/components';

	let id = $derived(Number(page.params.id));

	let prescription = $state<Prescription | null>(null);
	let recommendations = $state<RecommendationResult | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function load(prescriptionId: number) {
		loading = true;
		error = null;
		try {
			// 상세와 추천을 병렬로 가져온다.
			const [detail, recs] = await Promise.all([
				getPrescription(prescriptionId),
				getRecommendations(prescriptionId)
			]);
			prescription = detail;
			recommendations = recs;
		} catch (err) {
			error = err instanceof ApiError ? err.message : '처방전을 불러오지 못했습니다.';
		} finally {
			loading = false;
		}
	}

	// id 가 바뀔 때마다 다시 로드.
	$effect(() => {
		if (Number.isFinite(id)) load(id);
	});

	let medsOpen = $state(false);

	let hasRecommendations = $derived(
		(recommendations?.needed.length ?? 0) +
			(recommendations?.caution.length ?? 0) +
			(recommendations?.conflicts.length ?? 0) >
			0
	);
</script>

<AppHeader title={prescription?.title || '처방전 상세'} back />

<div class="space-y-6 px-4 py-5">
	{#if loading}
		<StateBlock variant="loading" title="불러오는 중" />
	{:else if error}
		<StateBlock variant="error" title="불러오기 실패" description={error}>
			{#snippet action()}
				<Button variant="secondary" onclick={() => load(id)}>다시 시도</Button>
			{/snippet}
		</StateBlock>
	{:else if prescription}
		<!-- 처방 약품 (접기/펼치기) -->
		<section class="space-y-2.5">
			<button
				type="button"
				onclick={() => (medsOpen = !medsOpen)}
				aria-expanded={medsOpen}
				class="flex w-full items-center gap-1.5 text-sm font-bold text-gray-500"
			>
				<Icon name="pill" size={16} /> 처방 약품 {prescription.items.length}개
				<Icon
					name="chevron-right"
					size={16}
					class="ml-auto text-gray-400 transition-transform {medsOpen ? 'rotate-90' : ''}"
				/>
			</button>
			{#if medsOpen}
				<ul class="space-y-2">
					{#each prescription.items as item (item.id)}
						<li>
							<Card padded={false}>
								<div class="flex items-center gap-3 p-3.5">
									<span class="size-2 shrink-0 rounded-full bg-brand-400"></span>
									<span class="flex-1 font-medium text-gray-800">{item.medicine_name}</span>
									{#if item.dosage_instruction}
										<span class="text-xs text-gray-400">{item.dosage_instruction}</span>
									{/if}
								</div>
							</Card>
						</li>
					{/each}
				</ul>
			{/if}
		</section>

		<!-- 영양소 추천 -->
		{#if hasRecommendations}
			{#if recommendations && recommendations.conflicts.length}
				<section class="space-y-2.5">
					<div class="flex items-center gap-2">
						<span class="flex size-7 items-center justify-center rounded-lg bg-caution-100 text-caution-700">
							<Icon name="alert" size={18} strokeWidth={2} />
						</span>
						<h2 class="text-base font-bold text-gray-900">상담이 필요한 영양소</h2>
					</div>
					<p class="text-xs text-gray-500">
						필요와 주의가 동시에 감지되어 약 사이 상호작용이 우려됩니다.
					</p>
					<div class="space-y-2.5">
						{#each recommendations.conflicts as conflict (conflict.nutrient_id)}
							<ConflictCard {conflict} />
						{/each}
					</div>
				</section>
			{/if}

			{#if recommendations && recommendations.needed.length}
				<section class="space-y-2.5">
					<div class="flex items-center gap-2">
						<span class="flex size-7 items-center justify-center rounded-lg bg-positive-50 text-positive-600">
							<Icon name="plus" size={18} strokeWidth={2.2} />
						</span>
						<h2 class="text-base font-bold text-gray-900">보충이 필요한 영양소</h2>
					</div>
					<div class="space-y-2.5">
						{#each recommendations.needed as rec (rec.nutrient_id)}
							<NutrientCard recommendation={rec} kind="positive" />
						{/each}
					</div>
				</section>
			{/if}

			{#if recommendations && recommendations.caution.length}
				<section class="space-y-2.5">
					<div class="flex items-center gap-2">
						<span class="flex size-7 items-center justify-center rounded-lg bg-caution-50 text-caution-600">
							<Icon name="alert-triangle" size={17} strokeWidth={2} />
						</span>
						<h2 class="text-base font-bold text-gray-900">주의가 필요한 영양소</h2>
					</div>
					<div class="space-y-2.5">
						{#each recommendations.caution as rec (rec.nutrient_id)}
							<NutrientCard recommendation={rec} kind="caution" />
						{/each}
					</div>
				</section>
			{/if}

			<p class="px-1 text-xs leading-relaxed text-gray-400">
				본 안내는 약물–영양소 상호작용 데이터에 기반한 일반 정보이며, 의학적 조언을 대체하지
				않습니다. 영양제 복용 전 의사·약사와 상담하세요.
			</p>
		{:else}
			<StateBlock
				icon="leaf"
				title="추천할 영양소 정보가 없어요"
				description={'이 처방전의 약품에서 영양소 상호작용 정보를\n찾지 못했습니다.'}
			/>
		{/if}
	{/if}
</div>
