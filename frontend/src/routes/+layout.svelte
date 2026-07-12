<script lang="ts">
	import './layout.css';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { fetchMe } from '$lib/api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { BottomNav, Spinner, Toaster } from '$lib/components';

	let { children } = $props();

	// 미로그인 상태에서 접근 가능한 화면 (온보딩/로그인/회원가입).
	const PUBLIC = ['/welcome', '/login', '/register'];
	function isPublic(pathname: string): boolean {
		return PUBLIC.includes(pathname.replace(/\/$/, '') || '/');
	}

	onMount(() => {
		authStore.restore();
		// 저장된 토큰이 있으면 유효성을 백그라운드로 확인(만료 시 client 가 401→clear).
		if (authStore.token) {
			fetchMe()
				.then((user) => (authStore.user = user))
				.catch(() => {});
		}
	});

	// 인증 가드: 복원이 끝난 뒤 라우트와 로그인 상태를 맞춘다.
	$effect(() => {
		if (!authStore.ready) return;
		const path = page.url.pathname;
		if (!authStore.isAuthenticated && !isPublic(path)) {
			goto('/welcome');
		} else if (authStore.isAuthenticated && isPublic(path)) {
			goto('/');
		}
	});

	let onPublic = $derived(isPublic(page.url.pathname));
	let showNav = $derived(authStore.ready && authStore.isAuthenticated && !onPublic);
	// 보호 라우트인데 미로그인이면 가드가 /welcome 으로 보내는 중 — 그 사이 보호 페이지가
	// 마운트되어 401 요청을 쏘지 않도록 렌더링을 잠시 보류한다.
	let redirecting = $derived(authStore.ready && !authStore.isAuthenticated && !onPublic);
</script>

<Toaster />

{#if !authStore.ready || redirecting}
	<!-- 세션 복원 / 가드 리다이렉트 중 깜빡임 방지용 스플래시 -->
	<div class="flex min-h-dvh items-center justify-center bg-canvas">
		<Spinner size={32} class="text-brand-500" />
	</div>
{:else}
	<div class="mx-auto flex min-h-dvh max-w-md flex-col bg-canvas shadow-sm">
		<main class="flex-1">
			{@render children()}
		</main>
		{#if showNav}
			<BottomNav />
		{/if}
	</div>
{/if}
