<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button, Icon, type IconName } from '$lib/components';

	interface Slide {
		icon: IconName;
		title: string;
		body: string;
		tone: string;
	}

	const slides: Slide[] = [
		{
			icon: 'scan',
			title: '처방전을 스캔하세요',
			body: '약 봉투나 처방전을 촬영하면\n약물명을 자동으로 인식합니다.',
			tone: 'from-brand-600 to-brand-500'
		},
		{
			icon: 'leaf',
			title: '필요한 영양소를 한눈에',
			body: '복용 약과 영양소의 상호작용을 분석해\n보충이 필요한 것과 주의할 것을 구분해 드려요.',
			tone: 'from-positive-600 to-positive-500'
		},
		{
			icon: 'shield',
			title: '내 처방전을 안전하게',
			body: '처방 이력을 계정에 모아 두고\n언제든 다시 확인할 수 있습니다.',
			tone: 'from-caution-500 to-caution-600'
		}
	];

	let index = $state(0);
	let isLast = $derived(index === slides.length - 1);

	function next() {
		if (isLast) goto('/register');
		else index += 1;
	}

	function go(i: number) {
		index = Math.max(0, Math.min(slides.length - 1, i));
	}

	// 좌우 스와이프로도 넘길 수 있도록 터치 시작점을 기록한다.
	let touchStartX = 0;
	function onTouchStart(e: TouchEvent) {
		touchStartX = e.changedTouches[0].clientX;
	}
	function onTouchEnd(e: TouchEvent) {
		const dx = e.changedTouches[0].clientX - touchStartX;
		if (Math.abs(dx) < 40) return;
		go(index + (dx < 0 ? 1 : -1));
	}
</script>

<div class="flex min-h-dvh flex-col px-6 pt-[max(2rem,env(safe-area-inset-top))] pb-[max(1.5rem,env(safe-area-inset-bottom))]">
	<!-- 건너뛰기 -->
	<div class="flex justify-end">
		<button
			type="button"
			class="text-sm font-medium text-gray-400 hover:text-gray-600"
			onclick={() => goto('/login')}
		>
			건너뛰기
		</button>
	</div>

	<!-- 슬라이드 트랙 (다음/스와이프 시 옆으로 넘어감) -->
	<div
		class="relative flex-1 overflow-hidden"
		role="group"
		aria-roledescription="carousel"
		aria-label="기능 소개 슬라이드"
		ontouchstart={onTouchStart}
		ontouchend={onTouchEnd}
	>
		<div
			class="absolute inset-0 flex transition-transform duration-300 ease-out"
			style="transform: translateX(-{index * 100}%)"
		>
			{#each slides as slide (slide.title)}
				<div
					class="flex h-full w-full shrink-0 flex-col items-center justify-center px-2 text-center"
				>
					<div
						class="flex size-28 items-center justify-center rounded-3xl bg-gradient-to-br text-white shadow-lg {slide.tone}"
					>
						<Icon name={slide.icon} size={52} strokeWidth={1.6} />
					</div>
					<h1 class="mt-8 text-2xl font-bold text-gray-900">{slide.title}</h1>
					<p class="mt-3 text-[0.95rem] leading-relaxed whitespace-pre-line text-gray-500">
						{slide.body}
					</p>
				</div>
			{/each}
		</div>
	</div>

	<!-- 인디케이터 -->
	<div class="mb-7 flex justify-center gap-2">
		{#each slides as _, i (i)}
			<button
				type="button"
				aria-label={`${i + 1}번째 소개`}
				onclick={() => go(i)}
				class="h-2 rounded-full transition-all {i === index
					? 'w-6 bg-brand-600'
					: 'w-2 bg-gray-200'}"
			></button>
		{/each}
	</div>

	<!-- 액션 -->
	<div class="space-y-3">
		<Button full size="lg" onclick={next}>
			{isLast ? '시작하기' : '다음'}
			{#if !isLast}<Icon name="arrow-right" size={18} />{/if}
		</Button>
		<p class="text-center text-sm text-gray-500">
			이미 계정이 있으신가요?
			<a href="/login" class="font-semibold text-brand-600 hover:underline">로그인</a>
		</p>
	</div>
</div>
