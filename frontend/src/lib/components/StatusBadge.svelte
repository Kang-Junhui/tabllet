<script lang="ts" module>
	import type { ScanStatus } from '$lib/types';
	import type { IconName } from './Icon.svelte';

	const META: Record<ScanStatus, { label: string; icon: IconName; class: string }> = {
		existing: {
			label: '등록됨',
			icon: 'check-circle',
			class: 'bg-brand-50 text-brand-700 border-brand-100'
		},
		imported: {
			label: '새로 추가',
			icon: 'sparkles',
			class: 'bg-positive-50 text-positive-700 border-positive-100'
		},
		not_found: {
			label: '정보 없음',
			icon: 'alert',
			class: 'bg-gray-100 text-gray-500 border-gray-200'
		},
		error: {
			label: '처리 실패',
			icon: 'alert-triangle',
			class: 'bg-caution-50 text-caution-700 border-caution-100'
		}
	};
</script>

<script lang="ts">
	import Icon from './Icon.svelte';

	interface Props {
		status: ScanStatus;
	}
	let { status }: Props = $props();
	let meta = $derived(META[status]);
</script>

<span
	class="inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold {meta.class}"
>
	<Icon name={meta.icon} size={14} strokeWidth={2} />
	{meta.label}
</span>
