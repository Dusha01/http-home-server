<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/shared/locale';

	onMount(() => {
		const search = typeof window !== 'undefined' ? window.location.search : '';
		goto('/login' + search, { replaceState: true });
	});
</script>

<p class="p-4 text-slate-600">{t('common.loading')}</p>
