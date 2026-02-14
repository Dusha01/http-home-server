<script lang="ts">
	import { onMount } from 'svelte';
	import { API_BASE, getStoredFolderPath, setStoredFolderPath, FOLDER_PATH_CHANGED_EVENT } from '$lib/shared/config';
	import { t } from '$lib/shared/locale';
	import FileList from './FileList.svelte';
	import FilePreview from './FilePreview.svelte';

	import { fetchDirectoryContent, fetchServerRootPath, uploadFile, createDirectory, deletePath } from '../api/api';
	import { getStoredToken } from '$lib';
	import type { DirectoryContent } from '$lib/entities/file';

	/** Элемент для загрузки: файл и относительный путь папки (пустая строка = текущая папка) */
	type UploadItem = { file: File; relativeDir: string };

	/** Нормализованный корень: не подниматься выше этой папки */
	function normalizePath(p: string): string {
		return p.replace(/\\/g, '/').replace(/\/+/g, '/').replace(/\/$/, '') || '/';
	}

	/** Собрать файлы из DataTransfer (в т.ч. из папки при drag-and-drop через webkitGetAsEntry). */
	async function getFilesFromDataTransfer(dt: DataTransfer): Promise<UploadItem[]> {
		const items: UploadItem[] = [];
		const entries: Array<{ entry: FileSystemEntry; path: string }> = [];

		for (let i = 0; i < dt.items.length; i++) {
			const item = dt.items[i];
			const entry = 'webkitGetAsEntry' in item ? (item as DataTransferItem & { webkitGetAsEntry(): FileSystemEntry | null }).webkitGetAsEntry() : null;
			if (entry) {
				entries.push({ entry, path: '' });
			} else {
				const file = item.getAsFile();
				if (file) items.push({ file, relativeDir: '' });
			}
		}

		while (entries.length > 0) {
			const { entry, path } = entries.shift()!;
			if (entry.isFile) {
				const file = await new Promise<File>((resolve, reject) => {
					(entry as FileSystemFileEntry).file(resolve, reject);
				});
				items.push({ file, relativeDir: path });
			} else if (entry.isDirectory) {
				const dirEntry = entry as FileSystemDirectoryEntry;
				const name = entry.name || '';
				const nextPath = path ? `${path}/${name}` : name;
				const subEntries = await new Promise<FileSystemEntry[]>((resolve, reject) => {
					const r = dirEntry.createReader();
					r.readEntries(resolve, reject);
				});
				subEntries.forEach((e) => entries.push({ entry: e, path: nextPath }));
			}
		}
		return items;
	}

	/** Создать цепочку папок на сервере (parentPath + части relativeDir). */
	async function ensureDirectories(parentPath: string, relativeDir: string): Promise<void> {
		if (!relativeDir) return;
		const parts = relativeDir.split('/').filter(Boolean);
		let current = normalizePath(parentPath);
		for (const part of parts) {
			try {
				await createDirectory(current, part, token);
			} catch {
				// папка уже может существовать
			}
			current = current === '/' ? `/${part}` : `${current}/${part}`;
		}
	}

	/** Корень с сервера — один для всех в сети; пока не загружен — из localStorage (только основной сервер) */
	let serverRootPath = $state<string | null>(null);
	const rootPath = $derived.by(() => {
		const p = serverRootPath ?? getStoredFolderPath() ?? '/';
		const n = normalizePath(p);
		return n && n !== '/' ? n : null;
	});

	/** Текущий путь: при загрузке с сервера подставляем serverRootPath, иначе из настроек или / */
	const initialPath = getStoredFolderPath() || '/';
	let currentPath = $state(normalizePath(initialPath) === '.' ? '/' : normalizePath(initialPath) || '/');
	let content = $state<DirectoryContent | null>(null);
	let loading = $state(true);
	let error = $state('');
	/** Краткое сообщение при автоматическом переходе в корень (папка не найдена). */
	let pathFallbackMessage = $state('');

	// Состояние предпросмотра
	let previewOpen = $state(false);
	let previewPath = $state('');
	let previewName = $state('');

	let downloadError = $state('');
	let deleteError = $state('');

	let uploadCount = $state(0);
	let uploadError = $state('');
	let uploadSuccess = $state(false);
	let addMenuOpen = $state(false);
	let dragOver = $state(false);
	let fileInput = $state<HTMLInputElement | undefined>(undefined);
	let folderInput = $state<HTMLInputElement | undefined>(undefined);

	const token = $derived(getStoredToken());

	async function load(path: string) {
		loading = true;
		error = '';
		pathFallbackMessage = '';
		try {
			content = await fetchDirectoryContent(path, token);
		} catch (e) {
			const msg = e instanceof Error ? e.message : t('settings.loadError');
			const isPathNotFound =
					path !== '/' &&
					(msg.includes('Path not found') || msg.includes('path not found') || msg.includes('404'));
			if (isPathNotFound) {
				setStoredFolderPath('/');
				currentPath = '/';
				pathFallbackMessage = t('workspace.pathNotFoundFallback');
				window.dispatchEvent(new CustomEvent(FOLDER_PATH_CHANGED_EVENT, { detail: '/' }));
			} else {
				error = msg;
			}
			content = null;
		} finally {
			loading = false;
		}
	}

	function openDir(path: string) {
		const target = normalizePath(path);
		if (rootPath != null && rootPath !== '') {
			const root = normalizePath(rootPath);
			if (target !== root && !target.startsWith(root + '/')) {
				return;
			}
		}
		currentPath = path;
	}

	function openPreview(path: string, name: string) {
		previewOpen = true;
		previewPath = path;
		previewName = name;
	}

	function closePreview() {
		previewOpen = false;
		previewPath = '';
		previewName = '';
	}

	async function deleteFile(path: string, isDirectory: boolean) {
		deleteError = '';
		try {
			await deletePath(path, isDirectory, token);
			load(currentPath);
		} catch (e) {
			deleteError = e instanceof Error ? e.message : t('workspace.deleteError');
			setTimeout(() => (deleteError = ''), 4000);
		}
	}

	async function downloadFile(path: string) {
		const q = `path=${encodeURIComponent(path)}`;
		const endpoint = token ? `/share/download?${q}` : `/share/public/download?${q}`;
		const url = `${API_BASE}${endpoint}`;
		if (token) {
			try {
				const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
				if (!res.ok) throw new Error(res.statusText || 'Download failed');
				const blob = await res.blob();
				let name = path.split(/[/\\]/).pop() || 'download';
				const disp = res.headers.get('content-disposition');
				const m = disp?.match(/filename="?([^";\n]+)"?/);
				if (m?.[1]) name = m[1];
				const a = document.createElement('a');
				a.href = URL.createObjectURL(blob);
				a.download = name;
				a.click();
				URL.revokeObjectURL(a.href);
			} catch (e) {
				downloadError = e instanceof Error ? e.message : t('workspace.downloadError');
				setTimeout(() => (downloadError = ''), 4000);
			}
		} else {
			window.open(url, '_blank');
		}
	}

	async function doUpload(items: UploadItem[]): Promise<void> {
		if (items.length === 0) return;
		uploadError = '';
		uploadSuccess = false;
		uploadCount = items.length;
		const basePath = normalizePath(currentPath);
		const createdDirs = new Set<string>();

		for (const { file, relativeDir } of items) {
			try {
				if (relativeDir && !createdDirs.has(relativeDir)) {
					await ensureDirectories(basePath, relativeDir);
					createdDirs.add(relativeDir);
				}
				const dirPath = relativeDir ? (basePath === '/' ? `/${relativeDir}` : `${basePath}/${relativeDir}`) : basePath;
				await uploadFile(dirPath, file, false, token);
			} catch (e) {
				uploadError = e instanceof Error ? e.message : t('workspace.uploadError');
			}
			uploadCount -= 1;
		}

		if (!uploadError) {
			uploadSuccess = true;
			load(currentPath);
			setTimeout(() => (uploadSuccess = false), 3000);
		}
	}

	function handleDrop(e: DragEvent): void {
		e.preventDefault();
		dragOver = false;
		if (!e.dataTransfer?.items?.length) return;
		getFilesFromDataTransfer(e.dataTransfer).then((items) => {
			if (items.length) doUpload(items);
		}).catch(() => {
			uploadError = t('workspace.uploadError');
		});
	}

	function handleDragOver(e: DragEvent): void {
		e.preventDefault();
		if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
		dragOver = true;
	}

	function handleDragLeave(): void {
		dragOver = false;
	}

	function onFileInputChange(): void {
		const el = fileInput ?? undefined;
		if (!el?.files?.length) return;
		const items: UploadItem[] = [];
		for (let i = 0; i < el.files.length; i++) {
			const file = el.files[i];
			if (file) items.push({ file, relativeDir: '' });
		}
		el.value = '';
		doUpload(items);
	}

	function onFolderInputChange(): void {
		const el = folderInput ?? undefined;
		if (!el?.files?.length) return;
		const items: UploadItem[] = [];
		for (let i = 0; i < el.files.length; i++) {
			const file = el.files[i];
			if (!file) continue;
			const rel = (file as File & { webkitRelativePath?: string }).webkitRelativePath || '';
			const relativeDir = rel.includes('/') ? rel.replace(/\/[^/]+$/, '') : '';
			items.push({ file, relativeDir });
		}
		el.value = '';
		doUpload(items);
	}

	function openAddMenu(ev?: Event): void {
		addMenuOpen = !addMenuOpen;
		if (addMenuOpen) {
			const close = () => {
				addMenuOpen = false;
				document.removeEventListener('click', close);
			};
			ev?.stopPropagation();
			setTimeout(() => document.addEventListener('click', close), 0);
		}
	}

	function chooseFiles(): void {
		addMenuOpen = false;
		(fileInput ?? undefined)?.click();
	}

	function chooseFolder(): void {
		addMenuOpen = false;
		(folderInput ?? undefined)?.click();
	}

	$effect(() => {
		load(currentPath);
	});

	onMount(() => {
		fetchServerRootPath(token)
				.then((p) => {
					serverRootPath = p;
					if (p && p !== '/') currentPath = p;
				})
				.catch(() => {});

		const handler = (e: CustomEvent<string>) => {
			const path = e.detail?.trim() || '/';
			currentPath = path;
			serverRootPath = path;
		};
		window.addEventListener(FOLDER_PATH_CHANGED_EVENT, handler as EventListener);
		return () => window.removeEventListener(FOLDER_PATH_CHANGED_EVENT, handler as EventListener);
	});
</script>

<div class="flex h-full flex-col gap-4 rounded-xl bg-slate-50/80 dark:bg-gray-800/90 p-4 transition-colors duration-200">
	{#if loading && !content}
		<p class="text-slate-500 dark:text-gray-400">{t('common.loading')}</p>
	{:else if error}
		<p class="text-red-600 dark:text-red-400">{error}</p>
	{:else if content}
		{#if pathFallbackMessage}
			<p class="text-sm text-amber-600 dark:text-amber-400">{pathFallbackMessage}</p>
		{/if}
		{#if downloadError}
			<p class="text-sm text-red-600 dark:text-red-400">{downloadError}</p>
		{/if}
		{#if uploadError}
			<p class="text-sm text-red-600 dark:text-red-400">{uploadError}</p>
		{/if}
		{#if deleteError}
			<p class="text-sm text-red-600 dark:text-red-400">{deleteError}</p>
		{/if}
		{#if uploadSuccess}
			<p class="text-sm text-green-600 dark:text-green-400">{t('workspace.uploadSuccess')}</p>
		{/if}
		<div class="flex items-center justify-between gap-2 flex-wrap">
			<div class="text-sm text-slate-500 dark:text-gray-400">
				{t('workspace.path')} <span class="font-mono text-slate-700 dark:text-gray-300">{content.current_path}</span>
			</div>
			<div class="relative">
				<button
						type="button"
						class="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 dark:border-gray-500 bg-white dark:bg-gray-700 px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-gray-200 hover:bg-slate-50 dark:hover:bg-gray-600"
						onclick={(e) => openAddMenu(e)}
						aria-haspopup="true"
						aria-expanded={addMenuOpen}
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
					</svg>
					{t('workspace.add')}
					<svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
					</svg>
				</button>
				{#if addMenuOpen}
					<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
					<div
							class="absolute right-0 top-full z-20 mt-1 min-w-[10rem] rounded-lg border border-slate-200 dark:border-gray-600 bg-white dark:bg-gray-700 shadow-lg py-1"
							role="menu"
							tabindex="-1"
							onclick={(e) => e.stopPropagation()}
					>
						<button type="button" class="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-slate-700 dark:text-gray-200 hover:bg-slate-100 dark:hover:bg-gray-600" role="menuitem" onclick={chooseFiles}>
							{t('workspace.addFiles')}
						</button>
						<button type="button" class="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-slate-700 dark:text-gray-200 hover:bg-slate-100 dark:hover:bg-gray-600" role="menuitem" onclick={chooseFolder}>
							{t('workspace.addFolder')}
						</button>
					</div>
				{/if}
				<input
						bind:this={fileInput}
						type="file"
						multiple
						class="hidden"
						accept="*/*"
						onchange={onFileInputChange}
				/>
				<input
						bind:this={folderInput}
						type="file"
						class="hidden"
						webkitdirectory
						onchange={onFolderInputChange}
				/>
			</div>
		</div>
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
				class="min-h-0 flex-1 flex flex-col rounded-lg border border-slate-200 dark:border-gray-600 transition-colors {dragOver ? 'border-blue-400 dark:border-blue-500 bg-blue-50/50 dark:bg-blue-900/20' : ''}"
				ondrop={handleDrop}
				ondragover={handleDragOver}
				ondragleave={handleDragLeave}
				role="region"
				aria-label={t('workspace.dropFiles')}
		>
			{#if dragOver}
				<div class="flex flex-1 items-center justify-center rounded-lg border-2 border-dashed border-blue-400 dark:border-blue-500 bg-blue-50/50 dark:bg-blue-900/20 p-6 text-center text-slate-600 dark:text-gray-300">
					{t('workspace.dropFiles')}
				</div>
			{:else}
				<FileList
						directories={content.directories}
						files={content.files}
						currentPath={content.current_path}
						parentPath={content.parent_path}
						rootPath={rootPath}
						onOpenDir={openDir}
						onPreview={openPreview}
						onDownload={downloadFile}
						onDelete={deleteFile}
				/>
			{/if}
		</div>
		{#if uploadCount > 0}
			<p class="text-sm text-slate-500 dark:text-gray-400">{t('workspace.uploading')} ({uploadCount})</p>
		{/if}
	{/if}
</div>

<FilePreview
		open={previewOpen}
		path={previewPath}
		name={previewName}
		token={token}
		onClose={closePreview}
/>