<script lang="ts">
	import Icon from './Icon.svelte';
	import Button from './Button.svelte';

	interface Props {
		/** 사용자가 이미지를 고르면 호출. */
		onselect: (file: File) => void;
		disabled?: boolean;
	}

	let { onselect, disabled = false }: Props = $props();

	let dragging = $state(false);
	// 카메라(촬영)와 갤러리(파일 선택)를 분리하기 위해 입력을 두 개 둔다.
	let cameraInput: HTMLInputElement;
	let galleryInput: HTMLInputElement;

	function pick(files: FileList | null | undefined) {
		const file = files?.[0];
		if (!file) return; // 카메라/선택을 취소한 경우 (파일 없음)
		// 모바일 카메라로 촬영한 파일은 type 이 빈 문자열로 오는 경우가 많다.
		// 빈 타입은 허용하고, 명시적으로 이미지가 아닌 타입만 거른다.
		if (file.type && !file.type.startsWith('image/')) return;
		onselect(file);
	}

	function onDrop(event: DragEvent) {
		event.preventDefault();
		dragging = false;
		if (!disabled) pick(event.dataTransfer?.files);
	}
</script>

<div
	role="group"
	aria-label="처방전 이미지 추가"
	class="flex w-full flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed px-6 py-8 text-center transition-colors
		{dragging ? 'border-brand-400 bg-brand-50' : 'border-gray-200 bg-gray-50'}
		{disabled ? 'pointer-events-none opacity-60' : ''}"
	ondragover={(e) => {
		e.preventDefault();
		if (!disabled) dragging = true;
	}}
	ondragleave={() => (dragging = false)}
	ondrop={onDrop}
>
	<span class="flex size-14 items-center justify-center rounded-2xl bg-brand-100 text-brand-600">
		<Icon name="scan" size={26} />
	</span>
	<div>
		<p class="font-semibold text-gray-800">처방전 사진을 추가하세요</p>
		<p class="mt-1 text-sm text-gray-500">카메라로 촬영하거나 갤러리에서 선택하세요</p>
	</div>

	<div class="flex w-full max-w-xs gap-2">
		<Button {disabled} full onclick={() => cameraInput.click()}>
			<Icon name="camera" size={18} /> 카메라
		</Button>
		<Button {disabled} full variant="secondary" onclick={() => galleryInput.click()}>
			<Icon name="image" size={18} /> 갤러리
		</Button>
	</div>

	<!-- 카메라: 모바일에서 후면 카메라로 바로 촬영 (데스크톱은 파일 선택으로 동작) -->
	<input
		bind:this={cameraInput}
		type="file"
		accept="image/*"
		capture="environment"
		class="hidden"
		{disabled}
		onchange={(e) => pick(e.currentTarget.files)}
	/>
	<!-- 갤러리: 저장된 사진/파일 선택 -->
	<input
		bind:this={galleryInput}
		type="file"
		accept="image/*"
		class="hidden"
		{disabled}
		onchange={(e) => pick(e.currentTarget.files)}
	/>
</div>
