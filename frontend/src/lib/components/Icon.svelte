<script lang="ts" module>
	// 단색(monochrome) 아이콘 세트. 이모지를 쓰지 않고 currentColor 로 그린다
	// (CLAUDE.md 디자인 가이드라인). 경로는 stroke 기반 1.75 두께 라인 아이콘.
	export type IconName =
		| 'home'
		| 'scan'
		| 'camera'
		| 'image'
		| 'pill'
		| 'clipboard'
		| 'leaf'
		| 'plus'
		| 'check'
		| 'check-circle'
		| 'alert'
		| 'alert-triangle'
		| 'x'
		| 'upload'
		| 'info'
		| 'chevron-right'
		| 'arrow-left'
		| 'arrow-right'
		| 'trash'
		| 'calendar'
		| 'search'
		| 'sparkles'
		| 'shield'
		| 'user'
		| 'lock'
		| 'settings'
		| 'log-out'
		| 'chevron-left'
		| 'eye'
		| 'eye-off'
		| 'edit';

	const PATHS: Record<IconName, string> = {
		home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9.5 21v-6h5v6"/>',
		scan: '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>',
		camera:
			'<path d="M4 8.5A1.5 1.5 0 0 1 5.5 7H8l1.2-2h5.6L16 7h2.5A1.5 1.5 0 0 1 20 8.5V18a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18z"/><circle cx="12" cy="12.5" r="3.2"/>',
		image:
			'<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9.5" r="1.5"/><path d="m4 17.5 4.5-4.5 3.5 3.5 3-3 5 5"/>',
		pill: '<rect x="3.2" y="8" width="17.6" height="8" rx="4" transform="rotate(-45 12 12)"/><path d="M9 9l6 6"/>',
		clipboard:
			'<path d="M8 4H6a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2"/><rect x="8" y="2.5" width="8" height="4" rx="1.5"/><path d="M8.5 12h7"/><path d="M8.5 16h4.5"/>',
		leaf: '<path d="M5 19c0-8 6-13 14-13 0 8-5 14-13 14"/><path d="M5 19c2-4 5-6 9-7.5"/>',
		plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
		check: '<path d="m5 12.5 4.5 4.5L19 7"/>',
		'check-circle': '<circle cx="12" cy="12" r="9"/><path d="m8.5 12.5 2.5 2.5 4.5-5"/>',
		alert: '<circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><path d="M12 16h.01"/>',
		'alert-triangle':
			'<path d="M10.3 4.3 2.8 17.5A2 2 0 0 0 4.5 20.5h15a2 2 0 0 0 1.7-3L13.7 4.3a2 2 0 0 0-3.4 0Z"/><path d="M12 9.5v4"/><path d="M12 17h.01"/>',
		x: '<path d="M6 6l12 12"/><path d="M18 6 6 18"/>',
		upload: '<path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M5 20h14"/>',
		info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>',
		'chevron-right': '<path d="m9 5 7 7-7 7"/>',
		'arrow-left': '<path d="M19 12H5"/><path d="m11 6-6 6 6 6"/>',
		'arrow-right': '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
		trash:
			'<path d="M4 7h16"/><path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/><path d="M6 7l1 13a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-13"/>',
		calendar:
			'<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 9h16"/><path d="M8 3v4"/><path d="M16 3v4"/>',
		search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
		sparkles:
			'<path d="M12 4l1.6 4.4L18 10l-4.4 1.6L12 16l-1.6-4.4L6 10l4.4-1.6z"/><path d="M18 15l.8 2.2L21 18l-2.2.8L18 21l-.8-2.2L15 18l2.2-.8z"/>',
		shield: '<path d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6z"/><path d="m9 12 2 2 4-4"/>',
		user: '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-3.5 3.6-6 8-6s8 2.5 8 6"/>',
		lock: '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
		settings:
			'<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
		'log-out': '<path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3"/><path d="M10 17l-5-5 5-5"/><path d="M5 12h12"/>',
		'chevron-left': '<path d="m15 5-7 7 7 7"/>',
		eye: '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z"/><circle cx="12" cy="12" r="3"/>',
		'eye-off':
			'<path d="M10.6 6.7A9 9 0 0 1 12 6.5c6 0 9.5 6.5 9.5 6.5a16 16 0 0 1-3 3.6"/><path d="M6.5 7.6A16 16 0 0 0 2.5 13s3.5 6.5 9.5 6.5a9 9 0 0 0 4-1"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/><path d="m3 3 18 18"/>',
		edit: '<path d="M4 20h4L18.5 9.5a2.12 2.12 0 0 0-3-3L5 16z"/><path d="m13.5 6.5 3 3"/>'
	};
</script>

<script lang="ts">
	interface Props {
		name: IconName;
		size?: number;
		class?: string;
		strokeWidth?: number;
	}

	let { name, size = 22, class: className = '', strokeWidth = 1.75 }: Props = $props();
</script>

<svg
	xmlns="http://www.w3.org/2000/svg"
	width={size}
	height={size}
	viewBox="0 0 24 24"
	fill="none"
	stroke="currentColor"
	stroke-width={strokeWidth}
	stroke-linecap="round"
	stroke-linejoin="round"
	class={className}
	aria-hidden="true"
>
	<!-- eslint-disable-next-line svelte/no-at-html-tags -->
	{@html PATHS[name]}
</svg>
