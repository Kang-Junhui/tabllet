<script lang="ts">
	import { goto } from '$app/navigation';
	import { register, ApiError } from '$lib/api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { toasts } from '$lib/stores/toast.svelte';
	import { Button, Icon } from '$lib/components';

	let username = $state('');
	let password = $state('');
	let confirm = $state('');
	let showPassword = $state(false);
	let submitting = $state(false);
	let error = $state<string | null>(null);

	let mismatch = $derived(confirm.length > 0 && password !== confirm);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		if (submitting) return;
		error = null;
		if (password !== confirm) {
			error = '비밀번호가 일치하지 않습니다.';
			return;
		}
		submitting = true;
		try {
			const session = await register({ username: username.trim(), password });
			authStore.setSession(session, authStore.remember);
			toasts.success(`가입 완료! ${session.user.username}님 환영합니다.`);
			await goto('/');
		} catch (err) {
			error = err instanceof ApiError ? err.message : '회원가입에 실패했습니다.';
		} finally {
			submitting = false;
		}
	}
</script>

<div class="flex min-h-dvh flex-col px-6 pt-[max(2rem,env(safe-area-inset-top))] pb-8">
	<button
		type="button"
		onclick={() => goto('/welcome')}
		aria-label="뒤로 가기"
		class="-ml-2 flex size-9 items-center justify-center rounded-full text-gray-500 hover:bg-gray-100"
	>
		<Icon name="chevron-left" size={24} />
	</button>

	<div class="mt-3 mb-7">
		<h1 class="text-2xl font-bold text-gray-900">회원가입</h1>
		<p class="mt-1 text-sm text-gray-500">처방전을 안전하게 보관할 계정을 만드세요.</p>
	</div>

	<form class="space-y-4" onsubmit={submit}>
		<label class="block">
			<span class="text-sm font-medium text-gray-600">아이디</span>
			<div class="relative mt-1.5">
				<span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-gray-400">
					<Icon name="user" size={18} />
				</span>
				<input
					type="text"
					bind:value={username}
					autocomplete="username"
					required
					class="w-full rounded-xl border-gray-200 bg-white pl-10 text-sm focus:border-brand-400 focus:ring-brand-400"
				/>
			</div>
		</label>

		<label class="block">
			<span class="text-sm font-medium text-gray-600">비밀번호</span>
			<div class="relative mt-1.5">
				<span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-gray-400">
					<Icon name="lock" size={18} />
				</span>
				{#if showPassword}
					<input
						type="text"
						bind:value={password}
						autocomplete="new-password"
						required
						minlength="8"
						class="w-full rounded-xl border-gray-200 bg-white px-10 text-sm focus:border-brand-400 focus:ring-brand-400"
					/>
				{:else}
					<input
						type="password"
						bind:value={password}
						autocomplete="new-password"
						required
						minlength="8"
						class="w-full rounded-xl border-gray-200 bg-white px-10 text-sm focus:border-brand-400 focus:ring-brand-400"
					/>
				{/if}
				<button
					type="button"
					onclick={() => (showPassword = !showPassword)}
					aria-label={showPassword ? '비밀번호 숨기기' : '비밀번호 표시'}
					class="absolute inset-y-0 right-2 flex items-center px-1 text-gray-400 hover:text-gray-600"
				>
					<Icon name={showPassword ? 'eye-off' : 'eye'} size={18} />
				</button>
			</div>
			<span class="mt-1 block text-xs text-gray-400">8자 이상 입력하세요.</span>
		</label>

		<label class="block">
			<span class="text-sm font-medium text-gray-600">비밀번호 확인</span>
			<div class="relative mt-1.5">
				<span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-gray-400">
					<Icon name="lock" size={18} />
				</span>
				<input
					type="password"
					bind:value={confirm}
					autocomplete="new-password"
					required
					class="w-full rounded-xl bg-white px-10 text-sm focus:ring-brand-400 {mismatch
						? 'border-caution-300 focus:border-caution-400'
						: 'border-gray-200 focus:border-brand-400'}"
				/>
			</div>
			{#if mismatch}
				<span class="mt-1 block text-xs text-caution-600">비밀번호가 일치하지 않습니다.</span>
			{/if}
		</label>

		<label class="flex items-center gap-2 text-sm text-gray-600">
			<input
				type="checkbox"
				bind:checked={authStore.remember}
				class="size-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
			/>
			자동 로그인
		</label>

		{#if error}
			<p class="flex items-start gap-1.5 text-sm text-caution-600">
				<Icon name="alert" size={16} class="mt-0.5 shrink-0" />
				{error}
			</p>
		{/if}

		<Button full size="lg" type="submit" loading={submitting}>가입하고 시작하기</Button>
	</form>

	<p class="mt-6 text-center text-sm text-gray-500">
		이미 계정이 있으신가요?
		<a href="/login" class="font-semibold text-brand-600 hover:underline">로그인</a>
	</p>
</div>
