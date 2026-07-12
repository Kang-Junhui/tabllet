/**
 * 전역 토스트 알림 상태 (Svelte 5 runes).
 *
 * API 에러/성공 피드백을 화면 어디서든 일관되게 띄우기 위한 작은 store.
 */
export type ToastKind = 'info' | 'success' | 'error';

export interface Toast {
	id: number;
	kind: ToastKind;
	message: string;
}

class ToastStore {
	items = $state<Toast[]>([]);
	#seq = 0;

	#push(kind: ToastKind, message: string, timeout: number) {
		const id = ++this.#seq;
		this.items = [...this.items, { id, kind, message }];
		if (timeout > 0) {
			setTimeout(() => this.dismiss(id), timeout);
		}
		return id;
	}

	info(message: string, timeout = 3500) {
		return this.#push('info', message, timeout);
	}

	success(message: string, timeout = 3500) {
		return this.#push('success', message, timeout);
	}

	error(message: string, timeout = 6000) {
		return this.#push('error', message, timeout);
	}

	dismiss(id: number) {
		this.items = this.items.filter((t) => t.id !== id);
	}
}

export const toasts = new ToastStore();
