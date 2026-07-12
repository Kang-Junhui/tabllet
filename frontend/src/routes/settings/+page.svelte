<script lang="ts">
	import { goto } from '$app/navigation';
	import { logout as logoutApi } from '$lib/api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { toasts } from '$lib/stores/toast.svelte';
	import { AppHeader, Button, Card, Icon } from '$lib/components';

	let loggingOut = $state(false);

	async function handleLogout() {
		if (loggingOut) return;
		loggingOut = true;
		try {
			// 서버 토큰 무효화는 best-effort. 실패해도 로컬 세션은 정리한다.
			await logoutApi().catch(() => {});
			authStore.clear();
			toasts.info('로그아웃되었습니다.');
			await goto('/welcome');
		} finally {
			loggingOut = false;
		}
	}
</script>

<AppHeader title="설정" />

<div class="space-y-6 px-4 py-5">
	<!-- 계정 -->
	<section class="space-y-2.5">
		<h2 class="text-sm font-bold text-gray-500">계정</h2>
		<Card>
			<div class="flex items-center gap-3">
				<span class="flex size-12 items-center justify-center rounded-full bg-brand-50 text-brand-600">
					<Icon name="user" size={26} />
				</span>
				<div class="min-w-0">
					<p class="truncate font-semibold text-gray-900">{authStore.user?.username ?? '사용자'}</p>
					<p class="text-xs text-gray-400">로그인됨</p>
				</div>
			</div>
		</Card>
	</section>

	<!-- 환경설정 -->
	<section class="space-y-2.5">
		<h2 class="text-sm font-bold text-gray-500">환경설정</h2>
		<Card>
			<label class="flex items-center justify-between gap-3">
				<span class="min-w-0">
					<span class="block font-medium text-gray-800">자동 로그인</span>
					<span class="block text-xs text-gray-400">앱을 다시 열어도 로그인 상태를 유지합니다.</span>
				</span>
				<input
					type="checkbox"
					checked={authStore.remember}
					onchange={(e) => authStore.applyRemember(e.currentTarget.checked)}
					class="size-5 rounded-md border-gray-300 text-brand-600 focus:ring-brand-500"
				/>
			</label>
		</Card>
	</section>

	<!-- 정보 -->
	<section class="space-y-2.5">
		<h2 class="text-sm font-bold text-gray-500">정보</h2>
		<Card>
			<div class="flex items-center justify-between">
				<span class="text-gray-700">Tabllet</span>
				<span class="text-sm text-gray-400">v0.0.1</span>
			</div>
		</Card>
		<p class="px-1 text-xs leading-relaxed text-gray-400">
			본 서비스의 영양소 안내는 일반 정보이며 의학적 조언을 대체하지 않습니다.
		</p>
	</section>

	<Button full variant="secondary" loading={loggingOut} onclick={handleLogout}>
		<Icon name="log-out" size={18} /> 로그아웃
	</Button>
</div>
