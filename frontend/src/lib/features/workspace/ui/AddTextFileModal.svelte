<script lang="ts">
	import { t } from '$lib/shared/locale';
	import TextPreviewEdit from './TextPreviewEdit.svelte';
	import { uploadFile } from '../api/api';

	function normalizePath(p: string): string {
		return p.replace(/\\/g, '/').replace(/\/+/g, '/').replace(/\/$/, '') || '/';
	}

	interface Props {
		open: boolean;
		currentPath: string;
		token: string | null;
		onClose: () => void;
		onCreated: () => void;
	}

	let {
		open,
		currentPath,
		token,
		onClose,
		onCreated
	}: Props = $props();

	let content = $state('');
	let filename = $state('new.txt');
	let saveError = $state('');
	let editRequested = $state(1);

	$effect(() => {
		if (open) {
			content = '';
			filename = 'new.txt';
			saveError = '';
			editRequested = 1;
		}
	});

	async function handleSave(newContent: string) {
		const name = filename.trim() || 'new.txt';
		const safeName = name.replace(/[/\\]/g, '');

		if (!safeName) {
			saveError = t('workspace.enterFilename');
			return;
		}

		saveError = '';

		try {
			const dirPath = normalizePath(currentPath);
			const blob = new Blob([newContent], { type: 'text/plain;charset=UTF-8' });
			const file = new File([blob], safeName, { type: 'text/plain;charset=UTF-8' });

			await uploadFile(dirPath, file, false, token);

			onCreated();
			onClose();
		} catch (e) {
			saveError = e instanceof Error ? e.message : t('workspace.uploadError');
		}
	}

	function handleCancel() {
		editRequested = 0;
		onClose();
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			onClose();
		}
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onClose();
		}
	}
</script>

{#if open}
	<!-- svelte-ignore a11y_no_static_element_interactions a11y_click_events_have_key_events -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
		role="dialog"
		aria-modal="true"
		aria-labelledby="add-text-title"
		tabindex="-1"
		onclick={handleBackdropClick}
		onkeydown={handleKeyDown}
	>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<div class="flex max-h-[90vh] w-full max-w-4xl flex-col rounded-xl bg-white dark:bg-gray-800 shadow-xl" onclick={(e) => e.stopPropagation()}>
			<div class="flex items-center justify-between gap-3 border-b border-slate-200 dark:border-gray-600 px-4 py-3 flex-wrap">
				<h2 id="add-text-title" class="text-lg font-medium text-slate-800 dark:text-gray-200 flex items-center gap-2 shrink-0">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					{t('workspace.newTextFile')}
				</h2>
				<div class="flex items-center gap-2 flex-wrap">
					<label class="flex items-center gap-2 text-sm text-slate-600 dark:text-gray-400">
						<span class="shrink-0">{t('workspace.saveAs')}:</span>
						<input
							type="text"
							bind:value={filename}
							placeholder="filename.txt"
							class="rounded border border-slate-300 dark:border-gray-500 bg-white dark:bg-gray-700 px-2 py-1 font-mono text-sm text-slate-800 dark:text-gray-200 w-40 min-w-0"
						/>
					</label>
				</div>
			</div>

			{#if saveError}
				<div class="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-sm">
					{saveError}
				</div>
			{/if}

			<div class="min-h-0 flex-1 overflow-auto flex flex-col">
				<div class="flex-1 min-h-[300px]">
					<TextPreviewEdit
						content={content}
						filename={filename}
						editable={true}
						editRequested={editRequested}
						onSave={handleSave}
						onCancel={handleCancel}
					/>
				</div>
			</div>
		</div>
	</div>
{/if}
