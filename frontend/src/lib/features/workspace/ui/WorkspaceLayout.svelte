<script lang="ts">
	import { onMount } from 'svelte';
	import { API_BASE, getStoredFolderPath, FOLDER_PATH_CHANGED_EVENT } from '$lib/shared/config';
	import FileList from './FileList.svelte';

	import { fetchDirectoryContent, fetchPreview, fetchServerRootPath } from '../api/api';
	import { getStoredToken, clearStoredToken } from '$lib';
	import type { DirectoryContent } from '$lib/entities/file';

	/** Нормализованный корень: не подниматься выше этой папки */
	function normalizePath(p: string): string {
		return p.replace(/\\/g, '/').replace(/\/+/g, '/').replace(/\/$/, '') || '/';
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

	let previewOpen = $state(false);
	let previewName = $state('');
	let previewPath = $state('');
	let previewContent = $state('');
	let previewLoading = $state(false);
	let previewError = $state('');
	let downloadError = $state('');

	const token = $derived(getStoredToken());

	async function load(path: string) {
		loading = true;
		error = '';
		try {
			content = await fetchDirectoryContent(path, token);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Ошибка загрузки';
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
		previewName = name;
		previewPath = path;
		previewContent = '';
		previewError = '';
		previewLoading = true;
		fetchPreview(path, token)
			.then((text) => {
				previewContent = text;
				previewError = '';
			})
			.catch((e) => {
				previewError = e instanceof Error ? e.message : 'Ошибка загрузки';
			})
			.finally(() => {
				previewLoading = false;
			});
	}

	function closePreview() {
		previewOpen = false;
		previewName = '';
		previewPath = '';
		previewContent = '';
		previewError = '';
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
				downloadError = e instanceof Error ? e.message : 'Ошибка скачивания';
				setTimeout(() => (downloadError = ''), 4000);
			}
		} else {
			window.open(url, '_blank');
		}
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
		<p class="text-slate-500 dark:text-gray-400">Загрузка…</p>
	{:else if error}
		<p class="text-red-600 dark:text-red-400">{error}</p>
	{:else if content}
		{#if downloadError}
			<p class="text-sm text-red-600 dark:text-red-400">{downloadError}</p>
		{/if}
		<div class="text-sm text-slate-500 dark:text-gray-400">
			Путь: <span class="font-mono text-slate-700 dark:text-gray-300">{content.current_path}</span>
		</div>
		<FileList
			directories={content.directories}
			files={content.files}
			currentPath={content.current_path}
			parentPath={content.parent_path}
			rootPath={rootPath}
			onOpenDir={openDir}
			onPreview={openPreview}
			onDownload={downloadFile}
		/>
	{/if}
</div>

{#if previewOpen}
	<!-- svelte-ignore a11y_no_static_element_interactions a11y_click_events_have_key_events -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
		role="dialog"
		aria-modal="true"
		aria-labelledby="preview-title"
		tabindex="-1"
		onclick={(e) => e.target === e.currentTarget && closePreview()}
		onkeydown={(e) => e.key === 'Escape' && closePreview()}
	>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<div class="flex max-h-[85vh] w-full max-w-3xl flex-col rounded-xl bg-white dark:bg-gray-800 shadow-xl" onclick={(e) => e.stopPropagation()}>
			<div class="flex items-center justify-between gap-3 border-b border-slate-200 dark:border-gray-600 px-4 py-3">
				<h2 id="preview-title" class="truncate text-lg font-medium text-slate-800 dark:text-gray-200">
					{previewName}
				</h2>
				<button
					type="button"
					class="shrink-0 rounded p-2 text-slate-500 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-gray-700"
					aria-label="Закрыть"
					onclick={closePreview}
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>
			<div class="min-h-0 flex-1 overflow-auto p-4">
				{#if previewLoading}
					<p class="text-slate-500 dark:text-gray-400">Загрузка…</p>
				{:else if previewError}
					<p class="text-red-600 dark:text-red-400">{previewError}</p>
				{:else}
					<pre class="whitespace-pre-wrap break-words font-mono text-sm text-slate-800 dark:text-gray-200"><code>{previewContent}</code></pre>
				{/if}
			</div>
		</div>
	</div>
{/if}
