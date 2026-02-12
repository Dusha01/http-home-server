<script lang="ts">
	import { fetchExplorerRoots, fetchExplorerList } from '$lib/features/workspace';
	import { getStoredToken } from '$lib/features/auth';
	import { isMainServer } from '$lib/shared/config';
	import type { ExplorerRootItem, ExplorerDirItem, ExplorerListResponse } from '$lib/entities/file';

	interface Props {
		/** Модальное окно открыто */
		open?: boolean;
		/** Начальное значение пути (например из localStorage или с сервера) */
		initialPath?: string;
		/** При закрытии (крестик, клик по фону, Escape) */
		onClose?: () => void;
		/** При нажатии «Сохранить» — передаётся выбранный/введённый путь (может быть async) */
		onSave?: (path: string) => void | Promise<void>;
	}

	let {
		open = false,
		initialPath = '',
		onClose = () => {},
		onSave = () => {}
	}: Props = $props();

	const token = $derived(getStoredToken());
	const initialPathValue = $derived(initialPath || '');

	let pathInput = $state('');
	let showPicker = $state(false);
	/** Режим: корни (диски/домашняя папка) или список папок по пути */
	let pickerView = $state<'roots' | 'list'>('roots');
	let pickerPath = $state('');
	let pickerRoots = $state<ExplorerRootItem[] | null>(null);
	let pickerContent = $state<ExplorerListResponse | null>(null);
	let pickerLoading = $state(false);
	let pickerError = $state('');

	$effect(() => {
		if (open) pathInput = initialPathValue;
	});

	async function loadPickerRoots() {
		pickerView = 'roots';
		pickerPath = '';
		pickerContent = null;
		pickerLoading = true;
		pickerError = '';
		try {
			pickerRoots = await fetchExplorerRoots(token);
			if (!pickerRoots?.length) pickerError = 'Нет доступных корневых папок';
		} catch (e) {
			pickerError = e instanceof Error ? e.message : 'Ошибка загрузки';
			pickerRoots = null;
		} finally {
			pickerLoading = false;
		}
	}

	async function loadPickerList(path: string) {
		pickerView = 'list';
		pickerPath = path;
		pickerLoading = true;
		pickerError = '';
		try {
			pickerContent = await fetchExplorerList(path, token);
		} catch (e) {
			pickerError = e instanceof Error ? e.message : 'Ошибка загрузки';
			pickerContent = null;
		} finally {
			pickerLoading = false;
		}
	}

	function openPicker() {
		showPicker = true;
		loadPickerRoots();
	}

	function closePicker() {
		showPicker = false;
		pickerView = 'roots';
		pickerPath = '';
		pickerRoots = null;
		pickerContent = null;
		pickerError = '';
	}

	function pickerSelectRoot(root: ExplorerRootItem) {
		loadPickerList(root.path);
	}

	function pickerNavigate(dir: ExplorerDirItem) {
		loadPickerList(dir.path);
	}

	function pickerGoBack() {
		if (pickerView === 'list' && pickerContent?.parent_path != null) {
			loadPickerList(pickerContent.parent_path);
		} else if (pickerView === 'list') {
			loadPickerRoots();
		} else {
			closePicker();
		}
	}

	function selectCurrentFolder() {
		const path = pickerView === 'list' && pickerPath ? pickerPath : pickerPath || pathInput.trim();
		if (path) pathInput = path;
		closePicker();
	}

	async function handleSave() {
		const path = pathInput.trim();
		await onSave(path || '/');
		onClose();
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) onClose();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			if (showPicker) closePicker();
			else onClose();
		}
	}
</script>

{#if open}
	<!-- svelte-ignore a11y_no_static_element_interactions a11y_click_events_have_key_events -->
	<div
		class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4"
		role="dialog"
		aria-modal="true"
		aria-labelledby="settings-modal-title"
		tabindex="-1"
		onclick={handleBackdropClick}
		onkeydown={handleKeydown}
	>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<div
			class="flex max-h-[90vh] w-full max-w-lg flex-col rounded-xl bg-white dark:bg-gray-800 shadow-xl"
			onclick={(e) => e.stopPropagation()}
		>
			<div class="flex items-center justify-between gap-3 border-b border-slate-200 dark:border-gray-600 px-4 py-3">
				<h2 id="settings-modal-title" class="text-lg font-semibold text-slate-800 dark:text-gray-200">
					Настройки
				</h2>
				<button
					type="button"
					class="shrink-0 rounded p-2 text-slate-500 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-gray-700"
					aria-label="Закрыть"
					onclick={onClose}
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>

			<div class="min-h-0 flex-1 overflow-auto p-4">
				{#if showPicker}
					<!-- Проводник: файловая система ПК -->
					<div class="flex flex-col gap-3">
						<p class="text-sm text-slate-600 dark:text-gray-400">
							Выберите любую папку на компьютере, где запущен сервер (диск → папка → …).
						</p>
						<div class="flex items-center gap-2 rounded-lg border border-slate-200 dark:border-gray-600 bg-slate-50 dark:bg-gray-700/50 px-3 py-2">
							<button
								type="button"
								class="shrink-0 rounded p-1.5 text-slate-500 hover:bg-slate-200 dark:hover:bg-gray-600"
								aria-label="Назад"
								onclick={pickerGoBack}
							>
								<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
								</svg>
							</button>
							<span class="text-sm font-mono text-slate-700 dark:text-gray-300 truncate min-w-0" title={pickerPath || 'Корни системы'}>
								{pickerView === 'roots' ? 'Корни системы' : pickerPath || '—'}
							</span>
						</div>
						<div class="min-h-[200px] rounded-lg border border-slate-200 dark:border-gray-600 bg-white dark:bg-gray-700/50 overflow-auto">
							{#if pickerLoading}
								<p class="p-4 text-slate-500 dark:text-gray-400">Загрузка…</p>
							{:else if pickerError}
								<p class="p-4 text-red-600 dark:text-red-400">{pickerError}</p>
							{:else if pickerView === 'roots' && pickerRoots}
								<ul class="divide-y divide-slate-100 dark:divide-gray-600">
									{#each pickerRoots as root}
										<li>
											<button
												type="button"
												class="flex w-full items-center gap-3 px-4 py-2.5 text-left hover:bg-slate-50 dark:hover:bg-gray-600/80"
												onclick={() => pickerSelectRoot(root)}
											>
												<span class="text-xl shrink-0" aria-hidden="true">💾</span>
												<span class="font-medium text-slate-800 dark:text-gray-200">{root.name}</span>
												<span class="text-xs font-mono text-slate-400 dark:text-gray-500 truncate">{root.path}</span>
											</button>
										</li>
									{/each}
								</ul>
							{:else if pickerView === 'list' && pickerContent}
								<ul class="divide-y divide-slate-100 dark:divide-gray-600">
									{#each pickerContent.directories as dir}
										<li>
											<button
												type="button"
												class="flex w-full items-center gap-3 px-4 py-2.5 text-left hover:bg-slate-50 dark:hover:bg-gray-600/80"
												onclick={() => pickerNavigate(dir)}
											>
												<span class="text-xl shrink-0" aria-hidden="true">📁</span>
												<span class="font-medium text-slate-800 dark:text-gray-200">{dir.name}</span>
											</button>
										</li>
									{/each}
								</ul>
								{#if pickerContent.directories.length === 0}
									<p class="p-4 text-slate-500 dark:text-gray-400">Нет вложенных папок</p>
								{/if}
							{/if}
						</div>
						<div class="flex gap-2">
							{#if pickerView === 'list' && pickerPath}
								<button
									type="button"
									class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-600"
									onclick={selectCurrentFolder}
								>
									Выбрать эту папку
								</button>
							{/if}
							<button
								type="button"
								class="rounded-lg border border-slate-300 dark:border-gray-600 px-4 py-2 text-sm font-medium text-slate-700 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-gray-700"
								onclick={closePicker}
							>
								Отмена
							</button>
						</div>
					</div>
				{:else if isMainServer()}
					<!-- Поле пути и кнопка обзора — только на основном сервере (localhost) -->
					<div class="flex flex-col gap-4">
						<label for="settings-folder-path" class="block text-sm font-medium text-slate-700 dark:text-gray-300">
							Папка транслятора
						</label>
						<p class="text-sm text-slate-500 dark:text-gray-400">
							Введите абсолютный путь к папке на ПК (например <code class="rounded bg-slate-100 dark:bg-gray-700 px-1">C:\Users\Имя\Папка</code> или <code class="rounded bg-slate-100 dark:bg-gray-700 px-1">/home/user/папка</code>) или выберите через проводник.
						</p>
						<div class="flex gap-2">
							<input
								id="settings-folder-path"
								type="text"
								class="min-w-0 flex-1 rounded-lg border border-slate-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-slate-800 dark:text-gray-200 placeholder-slate-400 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
								placeholder="C:\ или /home/..."
								bind:value={pathInput}
							/>
							<button
								type="button"
								class="shrink-0 rounded-lg border border-slate-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-sm font-medium text-slate-700 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-gray-600 flex items-center gap-2"
								onclick={openPicker}
							>
								<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
								</svg>
								Обзор
							</button>
						</div>
					</div>
				{:else}
					<!-- На клиентах (не localhost) опция смены пути недоступна -->
					<p class="text-sm text-slate-600 dark:text-gray-400">
						Путь к папке для просмотра файлов можно изменить только на основном сервере (при открытии с <code class="rounded bg-slate-100 dark:bg-gray-700 px-1">localhost</code>).
					</p>
				{/if}
			</div>

			{#if !showPicker}
				<div class="flex justify-end gap-2 border-t border-slate-200 dark:border-gray-600 px-4 py-3">
					{#if isMainServer()}
						<button
							type="button"
							class="rounded-lg border border-slate-300 dark:border-gray-600 px-4 py-2 text-sm font-medium text-slate-700 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-gray-700"
							onclick={onClose}
						>
							Отмена
						</button>
						<button
							type="button"
							class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-600"
							onclick={handleSave}
						>
							Сохранить
						</button>
					{:else}
						<button
							type="button"
							class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-600"
							onclick={onClose}
						>
							Закрыть
						</button>
					{/if}
				</div>
			{/if}
		</div>
	</div>
{/if}
