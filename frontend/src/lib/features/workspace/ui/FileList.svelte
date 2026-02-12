<script lang="ts">
	import type { FileInfo } from '$lib/entities/file';
	import { isTextPreviewable, isImagePreviewable, isVideoPreviewable, getFileIconType, type FileIconType } from '$lib/entities/file/preview';
	import { t } from '$lib/shared/locale';

	interface Props {
		directories: FileInfo[];
		files: FileInfo[];
		currentPath: string;
		parentPath?: string | null;
		rootPath?: string | null;
		onOpenDir: (path: string) => void;
		onPreview?: (path: string, name: string) => void;
		onDownload?: (path: string) => void;
		onDelete?: (path: string, isDirectory: boolean) => void;
	}
	let { directories, files, currentPath, parentPath = null, rootPath = null, onOpenDir, onPreview, onDownload, onDelete }: Props = $props();

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
		return isTextPreviewable(item.name, item.extension ?? null) ||
				isImagePreviewable(item.name, item.extension ?? null) ||
				isVideoPreviewable(item.name, item.extension ?? null);
	}

	function getIcon(type: FileIconType, fileName?: string): string {
		const extension = fileName?.split('.').pop()?.toLowerCase();

		const icons: Record<FileIconType | string, string> = {
			// Базовые типы
			folder: '📁',
			image: '🖼️',
			video: '🎬',
			audio: '🎵',
			archive: '📦',
			pdf: '📕',
			config: '⚙️',
			text: '📄',
			default: '📄',

			// Документы
			word: '📘',
			excel: '📗',
			powerpoint: '📙',

			// Код
			javascript: '🟨',
			typescript: '🔷',
			python: '🐍',
			java: '☕',
			cpp: '⚡',
			csharp: '🎯',
			go: '🐹',
			rust: '🦀',
			ruby: '💎',
			php: '🐘',
			swift: '🐦',
			kotlin: '🅺',
			html: '🌐',
			css: '🎨',
			scss: '🎨',
			sass: '🎨',
			json: '📋',
			yaml: '📋',
			xml: '📋',
			sql: '🗄️',

			// Разметка и текст
			markdown: '📝',
			md: '📝',
			rst: '📝',
			tex: '📜',

			// Shell и скрипты
			bash: '🐚',
			sh: '🐚',
			zsh: '🐚',
			fish: '🐠',
			ps1: '🪟',
			batch: '🪟',

			// Системные
			dockerfile: '🐳',
			git: '📌',
			env: '🔐',
			toml: '⚙️',
			ini: '⚙️',

			// Базы данных
			db: '🗄️',
			sqlite: '🗄️',
			csv: '📊',
			tsv: '📊',

			// Графика
			svg: '🎯',
			psd: '🎨',
			ai: '🎯',
			fig: '🎨',

			// Другие
			license: '📜',
			readme: '📖',
			makefile: '🔨',
			log: '📋',
			lock: '🔒',
			key: '🔑',
			cert: '🛡️',
			iso: '💿',
			exe: '⚙️',
			dmg: '💿',
			apk: '📱',
			deb: '🐧',
			rpm: '🐧',
		};

		// Проверяем конкретные расширения
		if (extension) {
			// JavaScript/TypeScript фреймворки
			if (['jsx', 'tsx', 'vue', 'svelte'].includes(extension)) {
				return '⚛️';
			}

			// Файлы README
			if (fileName?.toLowerCase().includes('readme')) {
				return icons.readme;
			}

			// Файлы лицензий
			if (fileName?.toLowerCase().includes('license') || fileName?.toLowerCase().includes('licence')) {
				return icons.license;
			}

			// Dockerfile
			if (fileName === 'Dockerfile' || fileName?.includes('dockerfile')) {
				return icons.dockerfile;
			}

			// Git файлы
			if (fileName?.startsWith('.git') || fileName === 'gitignore' || fileName === 'gitattributes') {
				return icons.git;
			}

			// Makefile
			if (fileName === 'Makefile' || fileName === 'makefile') {
				return icons.makefile;
			}

			// Файлы окружения
			if (fileName?.startsWith('.env')) {
				return icons.env;
			}

			// Проверяем по расширению
			if (icons[extension]) {
				return icons[extension];
			}
		}

		// Возвращаем иконку по базовому типу
		return icons[type] ?? icons.default;
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
			<li class="group flex items-center gap-3 px-4 py-2 hover:bg-slate-50 dark:hover:bg-gray-600/80 min-w-0">
				<button
						type="button"
						class="flex min-w-0 flex-1 items-center gap-3 text-left"
						onclick={() => onOpenDir(item.path)}
				>
					<span class="text-2xl shrink-0" aria-hidden="true">{getIcon('folder')}</span>
					<span class="font-medium text-slate-800 dark:text-gray-200 truncate" title={item.name}>{item.name}</span>
				</button>
				{#if onDelete}
					<button
							type="button"
							class="file-action-btn shrink-0 min-w-[2.25rem] rounded p-1.5 text-slate-500 dark:text-gray-400 hover:bg-red-100 dark:hover:bg-red-900/40 hover:text-red-600 dark:hover:text-red-400"
							aria-label={t('workspace.deleteFile') + ' ' + item.name}
							onclick={(e) => {
							e.stopPropagation();
							onDelete?.(item.path, true);
						}}
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<polyline points="3 6 5 6 21 6" />
							<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
							<line x1="10" y1="11" x2="10" y2="17" />
							<line x1="14" y1="11" x2="14" y2="17" />
						</svg>
					</button>
				{/if}
			</li>
		{/each}
		{#each files as item}
			<li class="group flex items-center gap-3 px-4 py-2 hover:bg-slate-50 dark:hover:bg-gray-600/80 min-w-0">
				<button
						type="button"
						class="flex min-w-0 flex-1 items-center gap-3 text-left"
						onclick={() => canPreview(item) && onPreview?.(item.path, item.name)}
				>
					<span class="text-xl shrink-0" aria-hidden="true">{getIcon(getFileIconType(item.name, item.extension ?? null), item.name)}</span>
					<span class="min-w-0 flex-1 truncate text-slate-700 dark:text-gray-300" title={item.name}>
						{item.name}
					</span>
					{#if item.size != null}
						<span class="shrink-0 text-sm text-slate-400 dark:text-gray-400">{formatSize(item.size)}</span>
					{/if}
				</button>
				<button
						type="button"
						class="file-action-btn shrink-0 min-w-[2.25rem] rounded p-1.5 text-slate-500 dark:text-gray-400 hover:bg-slate-200 dark:hover:bg-gray-500 hover:text-slate-700 dark:hover:text-gray-200"
						aria-label={t('workspace.downloadFile').replace('{name}', item.name)}
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
				{#if onDelete}
					<button
							type="button"
							class="file-action-btn shrink-0 min-w-[2.25rem] rounded p-1.5 text-slate-500 dark:text-gray-400 hover:bg-red-100 dark:hover:bg-red-900/40 hover:text-red-600 dark:hover:text-red-400"
							aria-label={t('workspace.deleteFile') + ' ' + item.name}
							onclick={(e) => {
							e.stopPropagation();
							onDelete?.(item.path, false);
						}}
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<polyline points="3 6 5 6 21 6" />
							<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
							<line x1="10" y1="11" x2="10" y2="17" />
							<line x1="14" y1="11" x2="14" y2="17" />
						</svg>
					</button>
				{/if}
			</li>
		{/each}
	</ul>
	{#if directories.length === 0 && files.length === 0}
		<p class="p-4 text-slate-500 dark:text-gray-400">{t('workspace.emptyFolder')}</p>
	{/if}
</div>

<style>
	.file-action-btn {
		opacity: 0;
		pointer-events: none;
		transition: opacity 0.15s ease;
	}
	:global(.group:hover) .file-action-btn {
		opacity: 1;
		pointer-events: auto;
	}
	@media (max-width: 1024px) {
		.file-action-btn {
			opacity: 1;
			pointer-events: auto;
		}
	}
</style>