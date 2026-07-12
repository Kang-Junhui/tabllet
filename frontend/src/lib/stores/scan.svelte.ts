/**
 * 처방전 스캔 → (이름 수정/추가) → 처방전 생성 플로우의 상태 (Svelte 5 runes).
 *
 * OCR 인식 결과를 편집 가능한 약품 목록으로 보관한다. 사용자는 오인식된 이름을 고치거나
 * 누락된 약품을 추가할 수 있고, '약품 정보 확인'으로 다시 조회(resolve)해 카탈로그 상태를
 * 갱신한 뒤 선택한 약품으로 처방전을 만든다.
 */
import type { ScanResult, ScanStatus } from '$lib/types';

export type ScanPhase = 'idle' | 'scanning' | 'resolving' | 'done' | 'error';

/** 'pending' = 사용자가 이름을 수정/추가했지만 아직 재조회하지 않은 상태. */
export type EntryStatus = ScanStatus | 'pending';

export interface DrugEntry {
	/** #each 키 안정용 로컬 id. */
	id: number;
	name: string;
	medicineId: number | null;
	status: EntryStatus;
	selected: boolean;
}

class ScanStore {
	phase = $state<ScanPhase>('idle');
	entries = $state<DrugEntry[]>([]);
	errorMessage = $state<string | null>(null);
	#seq = 0;

	/** 처방전에 담을 수 있는(카탈로그 등록된) 선택 약품 id 목록. */
	get selectedIds(): number[] {
		return this.entries
			.filter((e) => e.selected && e.medicineId !== null)
			.map((e) => e.medicineId as number);
	}

	get selectedCount(): number {
		return this.selectedIds.length;
	}

	/** 등록되어 처방전에 담을 수 있는 약품이 하나라도 있는가. */
	get hasResolvable(): boolean {
		return this.entries.some((e) => e.medicineId !== null);
	}

	/** 수정/추가했지만 아직 확인하지 않은 이름이 있는가. */
	get hasPending(): boolean {
		return this.entries.some((e) => e.status === 'pending' && e.name.trim() !== '');
	}

	get notFoundNames(): string[] {
		return this.entries.filter((e) => e.status === 'not_found').map((e) => e.name);
	}

	/** 재조회에 보낼 (공백 제외) 이름 목록. */
	get names(): string[] {
		return this.entries.map((e) => e.name).filter((n) => n.trim() !== '');
	}

	start() {
		this.phase = 'scanning';
		this.errorMessage = null;
	}

	startResolving() {
		this.phase = 'resolving';
		this.errorMessage = null;
	}

	/** 스캔/재조회 결과로 편집 목록을 구성한다(등록된 약품은 기본 선택). */
	setFromResult(result: ScanResult) {
		this.entries = result.medicines.map((m) => ({
			id: ++this.#seq,
			name: m.name,
			medicineId: m.medicine_id,
			status: m.status,
			selected: m.medicine_id !== null
		}));
		this.phase = 'done';
	}

	/** 적재 오류(status='error') 약품을 목록에서 제거하고 제거된 이름을 돌려준다. */
	dropErrors(): string[] {
		const removed = this.entries.filter((e) => e.status === 'error').map((e) => e.name);
		if (removed.length) {
			this.entries = this.entries.filter((e) => e.status !== 'error');
		}
		return removed;
	}

	editName(id: number, name: string) {
		this.entries = this.entries.map((e) =>
			e.id === id ? { ...e, name, status: 'pending', medicineId: null, selected: false } : e
		);
	}

	addEntry() {
		this.entries = [
			...this.entries,
			{ id: ++this.#seq, name: '', medicineId: null, status: 'pending', selected: false }
		];
	}

	removeEntry(id: number) {
		this.entries = this.entries.filter((e) => e.id !== id);
	}

	toggle(id: number) {
		this.entries = this.entries.map((e) =>
			e.id === id && e.medicineId !== null ? { ...e, selected: !e.selected } : e
		);
	}

	fail(message: string) {
		this.phase = 'error';
		this.errorMessage = message;
	}

	reset() {
		this.phase = 'idle';
		this.entries = [];
		this.errorMessage = null;
	}
}

export const scanStore = new ScanStore();
