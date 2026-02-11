<script lang="ts">
	import { API_BASE } from '$lib/shared/config';
	import FileList from './FileList.svelte';

	import { fetchDirectoryContent } from '../api/api';
	import { getStoredToken, clearStoredToken } from '$lib';
	import type { DirectoryContent } from '$lib/entities/file';

	/** Текущий путь в облаке (например / или /foo/bar). */
	let currentPath = $state('/');
	let content = $state<DirectoryContent | null>(null);
	let loading = $state(true);
	let error = $state('');

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

	function openFile(path: string) {
		const q = `path=${encodeURIComponent(path)}`;
		const url = token ? `${API_BASE}/share/download?${q}` : `${API_BASE}/share/public/download?${q}`;
		window.open(url, '_blank');
	}

	$effect(() => {
		load(currentPath);
	});
</script>

<div class="flex h-full flex-col gap-4 p-4">
	{#if loading && !content}
		<p class="text-slate-500">Загрузка…</p>
	{:else if error}
		<p class="text-red-600">{error}</p>
	{:else if content}
		<div class="text-sm text-slate-500">
			Путь: <span class="font-mono">{content.current_path}</span>
		</div>
		<FileList
			directories={content.directories}
			files={content.files}
			currentPath={content.current_path}
			onOpenDir={openDir}
			onOpenFile={openFile}
		/>
	{/if}
</div>
