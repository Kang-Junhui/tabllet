<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import type { Pathname } from '$app/types';
	import Icon, { type IconName } from './Icon.svelte';

	interface NavItem {
		href: string;
		label: string;
		icon: IconName;
		/** 정확히 일치할 때만 활성으로 볼 경로(루트). */
		exact?: boolean;
	}

	const items: NavItem[] = [
		{ href: '/', label: '스캔', icon: 'scan', exact: true },
		{ href: '/prescriptions', label: '처방전', icon: 'clipboard' },
		{ href: '/settings', label: '설정', icon: 'settings' }
	];

	function isActive(item: NavItem): boolean {
		const path = page.url.pathname.replace(/\/$/, '') || '/';
		if (item.exact) return path === item.href;
		return path === item.href || path.startsWith(item.href + '/');
	}
</script>

<nav
	class="sticky bottom-0 z-30 border-t border-gray-100 bg-white/90 backdrop-blur-md pb-[env(safe-area-inset-bottom)]"
>
	<ul class="mx-auto flex max-w-md items-stretch">
		{#each items as item (item.href)}
			{@const active = isActive(item)}
			<li class="flex-1">
				<a
					href={resolve(item.href as Pathname)}
					aria-current={active ? 'page' : undefined}
					class="flex flex-col items-center gap-1 py-2.5 text-xs font-medium transition-colors
						{active ? 'text-brand-600' : 'text-gray-400 hover:text-gray-600'}"
				>
					<Icon name={item.icon} size={23} strokeWidth={active ? 2.1 : 1.75} />
					{item.label}
				</a>
			</li>
		{/each}
	</ul>
</nav>
