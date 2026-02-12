<script lang="ts">
	import type { FileInfo } from '$lib/entities/file';
	import { isTextPreviewable } from '$lib/entities/file/preview';
	import { t } from '$lib/shared/locale';

	interface Props {
		directories: FileInfo[];
		files: FileInfo[];
		currentPath: string;
		/** Родительская папка из API — для кнопки «Назад» (корректно для абсолютных путей и Windows). */
		parentPath?: string | null;
		/** Корневая папка из настроек: при совпадении с currentPath кнопку «Назад» не показываем (не подниматься выше). */
		rootPath?: string | null;
		onOpenDir: (path: string) => void;
		/** Клик по строке файла: открыть превью (для текстовых) или ничего */
		onPreview?: (path: string, name: string) => void;
		/** Клик по иконке загрузки: скачать файл */
		onDownload?: (path: string) => void;
	}
	let { directories, files, currentPath, parentPath = null, rootPath = null, onOpenDir, onPreview, onDownload }: Props = $props();

	function formatSize(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}

	function goParent() {
		if (parentPath != null && parentPath !== '') {
			onOpenDir(parentPath);
			return;
		}
		const parts = currentPath.split('/').filter(Boolean);
		parts.pop();
		onOpenDir(parts.length ? '/' + parts.join('/') : '/');
	}

	const showBackButton = $derived.by(() => {
		const hasParent = parentPath != null && parentPath !== '';
		if (rootPath != null && rootPath !== '') {
			const atSelectedRoot = normalizePath(currentPath) === normalizePath(rootPath);
			return hasParent && !atSelectedRoot;
		}
		return hasParent || (currentPath !== '/' && currentPath !== '.');
	});

	function normalizePath(p: string): string {
		return p.replace(/\\/g, '/').replace(/\/+/g, '/').replace(/\/$/, '') || '/';
	}

	function canPreview(item: FileInfo) {
		return isTextPreviewable(item.name, item.extension ?? null);
	}
</script>

<div class="min-h-0 flex-1 overflow-auto rounded-lg border border-slate-200 dark:border-gray-600 bg-white dark:bg-gray-700/80 transition-colors duration-200">
	{#if showBackButton}
		<button
			type="button"
			class="flex w-full items-center gap-2 border-b border-slate-100 dark:border-gray-600 px-4 py-2 text-left text-slate-600 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-gray-600/80"
			onclick={goParent}
		>
			<span class="text-lg">↩</span>
			<span>{t('common.back')}</span>
		</button>
	{/if}
	<ul class="divide-y divide-slate-100 dark:divide-gray-600">
		{#each directories as item}
			<li>
				<button
					type="button"
					class="flex w-full items-center gap-3 px-4 py-2 text-left hover:bg-slate-50 dark:hover:bg-gray-600/80"
					onclick={() => onOpenDir(item.path)}
				>
					<span class="text-2xl" aria-hidden="true">📁</span>
					<span class="font-medium text-slate-800 dark:text-gray-200">{item.name}</span>
				</button>
			</li>
		{/each}
		{#each files as item}
			<li class="group flex items-center gap-3 px-4 py-2 hover:bg-slate-50 dark:hover:bg-gray-600/80 min-w-0">
				<button
					type="button"
					class="flex min-w-0 flex-1 items-center gap-3 text-left"
					onclick={() => canPreview(item) && onPreview?.(item.path, item.name)}
				>
					<span class="text-xl shrink-0" aria-hidden="true">📄</span>
					<span class="min-w-0 flex-1 truncate text-slate-700 dark:text-gray-300" title={item.name}>
						{item.name}
					</span>
					{#if item.size != null}
						<span class="shrink-0 text-sm text-slate-400 dark:text-gray-400">{formatSize(item.size)}</span>
					{/if}
				</button>
				<button
					type="button"
					class="file-download-btn shrink-0 min-w-[2.25rem] rounded p-1.5 text-slate-500 dark:text-gray-400 hover:bg-slate-200 dark:hover:bg-gray-500 hover:text-slate-700 dark:hover:text-gray-200"
					aria-label="Скачать {item.name}"
					onclick={(e) => {
						e.stopPropagation();
						onDownload?.(item.path);
					}}
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
						<polyline points="7 10 12 15 17 10" />
						<line x1="12" y1="15" x2="12" y2="3" />
					</svg>
				</button>
			</li>
		{/each}
	</ul>
	{#if directories.length === 0 && files.length === 0}
		<p class="p-4 text-slate-500 dark:text-gray-400">{t('workspace.emptyFolder')}</p>
	{/if}
</div>

<style>
	.file-download-btn {
		opacity: 0;
		pointer-events: none;
		transition: opacity 0.15s ease;
	}
	:global(.group:hover) .file-download-btn {
		opacity: 1;
		pointer-events: auto;
	}
	@media (max-width: 1024px) {
		.file-download-btn {
			opacity: 1;
			pointer-events: auto;
		}
	}
</style>
