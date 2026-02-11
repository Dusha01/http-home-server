<script lang="ts">
	import { API_BASE } from '$lib/shared/config';
	import FileList from '$lib/widgets/file-list/FileList.svelte';
	import { fetchDirectoryContent, fetchPreview } from '$lib/features/workspace';
	import { getStoredToken, clearStoredToken } from '$lib/features/auth';
	import type { DirectoryContent } from '$lib/entities/file';

	let currentPath = $state('/');
	let content = $state<DirectoryContent | null>(null);
	let loading = $state(true);
	let error = $state('');

	let previewOpen = $state(false);
	let previewName = $state('');
	let previewPath = $state('');
	let previewContent = $state('');
	let previewLoading = $state(false);
	let previewError = $state('');

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

	function downloadFile(path: string) {
		const q = `path=${encodeURIComponent(path)}`;
		const url = token ? `${API_BASE}/share/download?${q}` : `${API_BASE}/share/public/download?${q}`;
		window.open(url, '_blank');
	}

	$effect(() => {
		load(currentPath);
	});
</script>

<div class="flex h-full flex-col gap-4 rounded-xl bg-slate-50/80 dark:bg-gray-800/90 p-4 transition-colors duration-200">
	<header class="flex items-center justify-between gap-4 border-b border-slate-200 dark:border-gray-600 pb-3">
		<h1 class="text-lg font-semibold text-slate-800 dark:text-gray-200">Облачная папка</h1>
		{#if token}
			<button
				type="button"
				class="text-sm text-slate-500 dark:text-gray-400 underline hover:text-slate-700 dark:hover:text-gray-300"
				onclick={() => {
					clearStoredToken();
					window.location.href = '/login';
				}}
			>
				Выйти
			</button>
		{/if}
	</header>

	{#if loading && !content}
		<p class="text-slate-500 dark:text-gray-400">Загрузка…</p>
	{:else if error}
		<p class="text-red-600 dark:text-red-400">{error}</p>
	{:else if content}
		<div class="text-sm text-slate-500 dark:text-gray-400">
			Путь: <span class="font-mono text-slate-700 dark:text-gray-300">{content.current_path}</span>
		</div>
		<FileList
			directories={content.directories}
			files={content.files}
			currentPath={content.current_path}
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
