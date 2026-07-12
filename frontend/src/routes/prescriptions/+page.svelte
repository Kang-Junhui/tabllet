<script lang="ts">
	import { goto } from '$app/navigation';
	import { listPrescriptions, deletePrescription, updatePrescription, ApiError } from '$lib/api';
	import type { Prescription } from '$lib/types';
	import { AppHeader, Button, Card, Icon, StateBlock } from '$lib/components';
	import { toasts } from '$lib/stores/toast.svelte';

	let prescriptions = $state<Prescription[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let manageMode = $state(false);
	let deletingId = $state<number | null>(null);
	let editingId = $state<number | null>(null);
	let editTitle = $state('');
	let savingTitle = $state(false);

	// 꾹 누르기(long-press) 감지용
	let pressTimer: ReturnType<typeof setTimeout> | null = null;
	let longPressed = false;

	async function load() {
		loading = true;
		error = null;
		try {
			prescriptions = await listPrescriptions();
		} catch (err) {
			error = err instanceof ApiError ? err.message : '처방전을 불러오지 못했습니다.';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		load();
	});

	function startPress() {
		longPressed = false;
		pressTimer = setTimeout(() => {
			manageMode = true;
			longPressed = true; // 뒤따르는 click 의 네비게이션 억제
			pressTimer = null;
		}, 450);
	}
	function cancelPress() {
		if (pressTimer) {
			clearTimeout(pressTimer);
			pressTimer = null;
		}
	}

	function openCard(id: number) {
		if (manageMode || longPressed) {
			longPressed = false;
			return; // 관리 모드/롱프레스 직후엔 이동하지 않음
		}
		goto(`/prescriptions/${id}`);
	}

	function startEdit(p: Prescription) {
		editingId = p.id;
		editTitle = p.title;
	}
	function cancelEdit() {
		editingId = null;
		editTitle = '';
	}
	async function saveTitle(p: Prescription) {
		if (savingTitle) return;
		const next = editTitle.trim();
		if (next === p.title) {
			cancelEdit();
			return;
		}
		savingTitle = true;
		try {
			const updated = await updatePrescription(p.id, { title: next });
			prescriptions = prescriptions.map((x) => (x.id === p.id ? { ...x, title: updated.title } : x));
			toasts.success('처방전 이름을 수정했습니다.');
			cancelEdit();
		} catch (err) {
			toasts.error(err instanceof ApiError ? err.message : '이름 수정에 실패했습니다.');
		} finally {
			savingTitle = false;
		}
	}

	async function remove(p: Prescription) {
		if (deletingId !== null) return;
		const label = p.title || `처방전 #${p.id}`;
		if (!confirm(`'${label}'을(를) 삭제할까요? 되돌릴 수 없습니다.`)) return;
		deletingId = p.id;
		try {
			await deletePrescription(p.id);
			prescriptions = prescriptions.filter((x) => x.id !== p.id);
			toasts.success('처방전을 삭제했습니다.');
			if (prescriptions.length === 0) manageMode = false;
		} catch (err) {
			toasts.error(err instanceof ApiError ? err.message : '삭제에 실패했습니다.');
		} finally {
			deletingId = null;
		}
	}

	function formatDate(value: string): string {
		const d = new Date(value);
		return Number.isNaN(d.getTime())
			? value
			: `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
	}
</script>

<AppHeader title="내 처방전" subtitle={manageMode ? '삭제할 처방전을 선택하세요' : '등록한 처방전 내역'}>
	{#snippet action()}
		{#if prescriptions.length > 0}
			<button
				type="button"
				onclick={() => {
					manageMode = !manageMode;
					if (!manageMode) cancelEdit();
				}}
				class="rounded-lg px-2.5 py-1.5 text-sm font-semibold {manageMode
					? 'text-brand-600'
					: 'text-gray-500 hover:bg-gray-100'}"
			>
				{manageMode ? '완료' : '관리'}
			</button>
		{/if}
	{/snippet}
</AppHeader>

<div class="px-4 py-5">
	{#if loading}
		<StateBlock variant="loading" title="불러오는 중" />
	{:else if error}
		<StateBlock variant="error" title="불러오기 실패" description={error}>
			{#snippet action()}
				<Button variant="secondary" onclick={load}>다시 시도</Button>
			{/snippet}
		</StateBlock>
	{:else if prescriptions.length === 0}
		<StateBlock
			icon="clipboard"
			title="아직 처방전이 없어요"
			description={'처방전을 스캔하면 이곳에 모입니다.'}
		>
			{#snippet action()}
				<Button href="/">
					<Icon name="scan" size={18} /> 처방전 스캔하기
				</Button>
			{/snippet}
		</StateBlock>
	{:else}
		{#if manageMode}
			<p class="mb-3 flex items-center gap-1.5 px-1 text-xs text-gray-400">
				<Icon name="info" size={14} /> 카드를 꾹 누르면 관리 모드로 전환됩니다.
			</p>
		{/if}
		<ul class="space-y-2.5">
			{#each prescriptions as p (p.id)}
				<li>
					<Card padded={false}>
						{#if editingId === p.id}
							<!-- 이름 인라인 수정 -->
							<div class="flex items-center gap-2 p-3">
								<span
									class="flex size-11 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600"
								>
									<Icon name="clipboard" size={22} />
								</span>
								<!-- svelte-ignore a11y_autofocus -->
								<input
									type="text"
									bind:value={editTitle}
									placeholder={`처방전 #${p.id}`}
									maxlength="200"
									autofocus
									class="min-w-0 flex-1 rounded-lg border-gray-200 bg-white text-sm focus:border-brand-400 focus:ring-brand-400"
									onkeydown={(e) => {
										if (e.key === 'Enter') saveTitle(p);
										else if (e.key === 'Escape') cancelEdit();
									}}
								/>
								<button
									type="button"
									class="flex size-9 shrink-0 items-center justify-center rounded-full text-brand-600 hover:bg-brand-50 disabled:opacity-40"
									aria-label="저장"
									disabled={savingTitle}
									onclick={() => saveTitle(p)}
								>
									<Icon name="check" size={20} />
								</button>
								<button
									type="button"
									class="flex size-9 shrink-0 items-center justify-center rounded-full text-gray-400 hover:bg-gray-100"
									aria-label="취소"
									onclick={cancelEdit}
								>
									<Icon name="x" size={20} />
								</button>
							</div>
						{:else}
							<div
								class="flex items-center gap-3 p-4"
								role="button"
								tabindex="0"
								onpointerdown={startPress}
								onpointerup={cancelPress}
								onpointerleave={cancelPress}
								onpointermove={cancelPress}
								oncontextmenu={(e) => e.preventDefault()}
								onclick={() => openCard(p.id)}
								onkeydown={(e) => {
									if (e.key === 'Enter') openCard(p.id);
								}}
							>
								<span
									class="flex size-11 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600"
								>
									<Icon name="clipboard" size={22} />
								</span>
								<div class="min-w-0 flex-1">
									<p class="truncate font-semibold text-gray-900">
										{p.title || `처방전 #${p.id}`}
									</p>
									<p class="mt-0.5 flex items-center gap-1.5 text-xs text-gray-400">
										<Icon name="calendar" size={13} />
										{formatDate(p.created_at)}
										<span class="text-gray-300">·</span>
										약품 {p.items.length}개
									</p>
								</div>
								{#if manageMode}
									<button
										type="button"
										class="flex size-9 shrink-0 items-center justify-center rounded-full text-gray-500 hover:bg-gray-100"
										aria-label="이름 수정"
										onclick={(e) => {
											e.stopPropagation();
											startEdit(p);
										}}
									>
										<Icon name="edit" size={19} />
									</button>
									<button
										type="button"
										class="flex size-9 shrink-0 items-center justify-center rounded-full text-caution-600 hover:bg-caution-50 disabled:opacity-40"
										aria-label="삭제"
										disabled={deletingId === p.id}
										onclick={(e) => {
											e.stopPropagation();
											remove(p);
										}}
									>
										<Icon name="trash" size={20} />
									</button>
								{:else}
									<Icon name="chevron-right" size={20} class="shrink-0 text-gray-300" />
								{/if}
							</div>
						{/if}
					</Card>
				</li>
			{/each}
		</ul>
	{/if}
</div>
