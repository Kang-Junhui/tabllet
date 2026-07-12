<script lang="ts">
	import { goto } from '$app/navigation';
	import {
		scanPrescriptionImage,
		resolveDrugNames,
		createPrescription,
		ApiError
	} from '$lib/api';
	import { scanStore } from '$lib/stores/scan.svelte';
	import { toasts } from '$lib/stores/toast.svelte';
	import type { PrescriptionItemInput } from '$lib/types';
	import {
		AppHeader,
		Button,
		Card,
		Icon,
		StateBlock,
		StatusBadge,
		UploadDropzone
	} from '$lib/components';

	let previewUrl = $state<string | null>(null);
	let title = $state('');
	let creating = $state(false);

	// 결과를 반영하고, 적재 오류(error) 약품은 목록에서 제거하며 어떤 약품이 문제인지 안내한다.
	function applyResult(result: Awaited<ReturnType<typeof scanPrescriptionImage>>) {
		scanStore.setFromResult(result);
		const removed = scanStore.dropErrors();
		const ok = result.medicines.filter((m) => m.medicine_id !== null).length;
		if (removed.length) {
			toasts.error(`처리 중 오류가 난 약품을 목록에서 제거했습니다: ${removed.join(', ')}`);
		} else if (ok === 0) {
			toasts.info('등록된 약품이 없습니다. 약품명을 수정하거나 추가해 보세요.');
		} else {
			toasts.success(`${result.recognized.length}개 중 ${ok}개 약품을 확인했습니다.`);
		}
	}

	async function handleSelect(file: File) {
		if (previewUrl) URL.revokeObjectURL(previewUrl);
		previewUrl = URL.createObjectURL(file);
		title = '';
		scanStore.start();
		try {
			applyResult(await scanPrescriptionImage(file));
		} catch (err) {
			const message = err instanceof ApiError ? err.message : '스캔 중 오류가 발생했습니다.';
			scanStore.fail(message);
			toasts.error(message);
		}
	}

	// 수정/추가한 약품명 목록을 다시 조회(HIRA→LLM)해 상태를 갱신한다.
	async function recheck() {
		const names = scanStore.names;
		if (names.length === 0) {
			toasts.info('확인할 약품명을 입력해 주세요.');
			return;
		}
		scanStore.startResolving();
		try {
			applyResult(await resolveDrugNames(names));
		} catch (err) {
			// 재조회 실패 시엔 처음 화면으로 돌아가지 않고 편집 목록을 유지한 채 알림만 띄운다.
			const message = err instanceof ApiError ? err.message : '약품 확인 중 오류가 발생했습니다.';
			scanStore.phase = 'done';
			toasts.error(message);
		}
	}

	function resetAll() {
		if (previewUrl) URL.revokeObjectURL(previewUrl);
		previewUrl = null;
		title = '';
		scanStore.reset();
	}

	async function createFromSelection() {
		const ids = scanStore.selectedIds;
		if (ids.length === 0) {
			toasts.info('처방전에 담을 약품을 한 개 이상 선택해 주세요.');
			return;
		}
		const items: PrescriptionItemInput[] = ids.map((medicine) => ({ medicine }));
		creating = true;
		try {
			const created = await createPrescription({ title: title.trim() || undefined, items });
			toasts.success('처방전을 등록했습니다.');
			const id = created.id;
			resetAll();
			await goto(`/prescriptions/${id}`);
		} catch (err) {
			const message = err instanceof ApiError ? err.message : '처방전 등록에 실패했습니다.';
			toasts.error(message);
		} finally {
			creating = false;
		}
	}
</script>

<AppHeader title="Tabllet" subtitle="처방전 맞춤 영양소 안내" />

<div class="space-y-6 px-4 py-5">
	{#if scanStore.phase === 'idle'}
		<section class="space-y-4">
			<div class="rounded-2xl bg-gradient-to-br from-brand-600 to-brand-500 p-5 text-white">
				<span class="flex size-11 items-center justify-center rounded-xl bg-white/15">
					<Icon name="sparkles" size={24} />
				</span>
				<h2 class="mt-3 text-lg font-bold">처방전을 스캔하면<br />필요한 영양소를 알려드려요</h2>
				<p class="mt-1.5 text-sm text-white/80">
					복용 중인 약과 영양소의 상호작용을 분석해 보충이 필요한 영양소와 주의할 영양소를 구분해
					안내합니다.
				</p>
			</div>

			<UploadDropzone onselect={handleSelect} />

			<ul class="space-y-2 text-sm text-gray-500">
				<li class="flex items-center gap-2">
					<Icon name="shield" size={16} class="text-brand-500" /> 처방 정보는 분석에만 사용됩니다.
				</li>
				<li class="flex items-center gap-2">
					<Icon name="pill" size={16} class="text-brand-500" /> 인식이 틀려도 약품명을 직접 수정·추가할
					수 있어요.
				</li>
			</ul>
		</section>
	{:else if scanStore.phase === 'scanning' || scanStore.phase === 'resolving'}
		<StateBlock
			variant="loading"
			title={scanStore.phase === 'scanning' ? '처방전을 분석하고 있어요' : '약품 정보를 확인하고 있어요'}
			description={'약물명을 인식하고 성분·영양소 정보를\n불러오는 중입니다. 잠시만 기다려 주세요.'}
		/>
		{#if previewUrl && scanStore.phase === 'scanning'}
			<img
				src={previewUrl}
				alt="업로드한 처방전 미리보기"
				class="mx-auto max-h-52 rounded-xl object-contain opacity-70"
			/>
		{/if}
	{:else if scanStore.phase === 'error'}
		<StateBlock variant="error" title="문제가 발생했어요" description={scanStore.errorMessage ?? ''}>
			{#snippet action()}
				<Button variant="secondary" onclick={resetAll}>
					<Icon name="arrow-left" size={18} /> 다시 시도
				</Button>
			{/snippet}
		</StateBlock>
	{:else if scanStore.phase === 'done'}
		<section class="space-y-4">
			<div class="flex items-center justify-between">
				<div>
					<h2 class="text-base font-bold text-gray-900">인식 결과</h2>
					<p class="text-sm text-gray-500">약품명을 확인하고 필요하면 수정·추가하세요</p>
				</div>
				<button
					type="button"
					class="flex items-center gap-1 text-sm font-medium text-gray-400 hover:text-gray-600"
					onclick={resetAll}
				>
					<Icon name="x" size={16} /> 초기화
				</button>
			</div>

			<!-- 편집 가능한 약품 목록 -->
			<ul class="space-y-2">
				{#each scanStore.entries as entry (entry.id)}
					<li>
						<Card padded={false}>
							<div class="flex items-center gap-2 p-2.5">
								<input
									type="checkbox"
									class="size-5 shrink-0 rounded-md border-gray-300 text-brand-600 focus:ring-brand-500 disabled:opacity-30"
									checked={entry.selected}
									disabled={entry.medicineId === null}
									onchange={() => scanStore.toggle(entry.id)}
									aria-label="처방전에 포함"
								/>
								<input
									type="text"
									value={entry.name}
									placeholder="약품명"
									oninput={(e) => scanStore.editName(entry.id, e.currentTarget.value)}
									class="min-w-0 flex-1 rounded-lg border-transparent bg-transparent px-1.5 py-1 text-sm font-medium text-gray-800 focus:border-brand-300 focus:bg-white focus:ring-0"
								/>
								{#if entry.status === 'pending'}
									<span
										class="shrink-0 rounded-full border border-gray-200 bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-500"
									>
										미확인
									</span>
								{:else}
									<StatusBadge status={entry.status} />
								{/if}
								<button
									type="button"
									class="shrink-0 rounded-full p-1 text-gray-300 hover:bg-gray-100 hover:text-gray-500"
									aria-label="삭제"
									onclick={() => scanStore.removeEntry(entry.id)}
								>
									<Icon name="x" size={16} />
								</button>
							</div>
						</Card>
					</li>
				{/each}
			</ul>

			<div class="flex gap-2">
				<Button variant="secondary" size="sm" onclick={() => scanStore.addEntry()}>
					<Icon name="plus" size={16} /> 약품 추가
				</Button>
				<Button variant="secondary" size="sm" onclick={recheck}>
					<Icon name="search" size={16} /> 약품 정보 확인
				</Button>
			</div>

			{#if scanStore.notFoundNames.length}
				<div class="rounded-xl border border-gray-200 bg-gray-50 p-3.5">
					<p class="flex items-center gap-1.5 text-sm font-semibold text-gray-500">
						<Icon name="alert" size={16} /> 정보를 찾지 못한 약품
					</p>
					<p class="mt-1 text-xs text-gray-400">
						{scanStore.notFoundNames.join(', ')} — 이름을 수정한 뒤 '약품 정보 확인'을 눌러 보세요.
					</p>
				</div>
			{/if}

			{#if scanStore.hasPending}
				<p class="flex items-center gap-1.5 px-1 text-xs text-caution-600">
					<Icon name="info" size={14} /> 수정·추가한 약품은 '약품 정보 확인'을 눌러야 처방전에 담을 수
					있어요.
				</p>
			{/if}

			<!-- 처방전 생성 -->
			{#if scanStore.hasResolvable}
				<div class="space-y-3 border-t border-gray-100 pt-4">
					<label class="block">
						<span class="text-sm font-medium text-gray-600">처방전 이름 (선택)</span>
						<input
							type="text"
							bind:value={title}
							placeholder="예: 6월 정기 처방"
							maxlength="200"
							class="mt-1.5 w-full rounded-xl border-gray-200 bg-white text-sm focus:border-brand-400 focus:ring-brand-400"
						/>
					</label>
					<Button
						full
						size="lg"
						loading={creating}
						disabled={scanStore.selectedCount === 0}
						onclick={createFromSelection}
					>
						<Icon name="check" size={20} /> 선택한 {scanStore.selectedCount}개로 처방전 만들기
					</Button>
				</div>
			{:else}
				<p class="px-1 text-center text-sm text-gray-400">
					처방전에 담을 수 있는 약품이 없습니다. 약품명을 수정·추가한 뒤 확인해 주세요.
				</p>
			{/if}
		</section>
	{/if}
</div>
