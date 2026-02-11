<script lang="ts">
	import type { FileInfo } from '$lib/entities/file';

	interface Props {
		directories: FileInfo[];
		files: FileInfo[];
		currentPath: string;
		onOpenDir: (path: string) => void;
		onOpenFile?: (path: string) => void;
	}
	let { directories, files, currentPath, onOpenDir, onOpenFile }: Props = $props();

	function formatSize(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}

	function goParent() {
		const parts = currentPath.split('/').filter(Boolean);
		parts.pop();
		onOpenDir(parts.length ? '/' + parts.join('/') : '/');
	}
</script>

<div class="min-h-0 flex-1 overflow-auto rounded-lg border border-slate-200 bg-white">
	{#if currentPath !== '/'}
		<button
			type="button"
			class="flex w-full items-center gap-2 border-b border-slate-100 px-4 py-2 text-left text-slate-600 hover:bg-slate-50"
			onclick={goParent}
		>
			<span class="text-lg">↩</span>
			<span>Назад</span>
		</button>
	{/if}
	<ul class="divide-y divide-slate-100">
		{#each directories as item}
			<li>
				<button
					type="button"
					class="flex w-full items-center gap-3 px-4 py-2 text-left hover:bg-slate-50"
					onclick={() => onOpenDir(item.path)}
				>
					<span class="text-2xl" aria-hidden="true">📁</span>
					<span class="font-medium text-slate-800">{item.name}</span>
				</button>
			</li>
		{/each}
		{#each files as item}
			<li>
				<button
					type="button"
					class="flex w-full items-center gap-3 px-4 py-2 text-left hover:bg-slate-50"
					onclick={() => onOpenFile?.(item.path)}
				>
					<span class="text-xl" aria-hidden="true">📄</span>
					<span class="text-slate-700">{item.name}</span>
					{#if item.size != null}
						<span class="ml-auto text-sm text-slate-400">{formatSize(item.size)}</span>
					{/if}
				</button>
			</li>
		{/each}
	</ul>
	{#if directories.length === 0 && files.length === 0}
		<p class="p-4 text-slate-500">Папка пуста</p>
	{/if}
</div>
