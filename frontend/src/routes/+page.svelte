<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fetchServerInfo } from '$lib/features/auth';
	import { getStoredToken } from '$lib/features/auth';

	let status = $state<'loading' | 'error'>('loading');
	let error = $state('');

	onMount(async () => {
		try {
			const info = await fetchServerInfo();
			const token = getStoredToken();
			if (info.auth_required && !token) {
				goto('/login', { replaceState: true });
				return;
			}
			goto('/workspace', { replaceState: true });
		} catch (e) {
			status = 'error';
			error = e instanceof Error ? e.message : 'Не удалось подключиться к серверу';
		}
	});
</script>

{#if status === 'loading'}
	<div class="flex min-h-screen items-center justify-center">
		<p class="text-slate-600">Загрузка…</p>
	</div>
{:else}
	<div class="flex min-h-screen flex-col items-center justify-center gap-4 p-4">
		<p class="text-red-600">{error}</p>
		<a href="/" class="text-sky-600 underline">Обновить</a>
	</div>
{/if}
