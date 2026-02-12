<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { localeStore, t } from '$lib/shared/locale';

	let { children } = $props();

	$effect(() => {
		const unsub = localeStore.subscribe((locale) => {
			if (typeof document !== 'undefined') {
				document.documentElement.lang = locale === 'en' ? 'en' : 'ru';
			}
		});
		return unsub;
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>{t('layout.title')}</title>
</svelte:head>
<div class="min-h-screen bg-slate-100 text-slate-900 dark:bg-gray-900 dark:text-gray-100 transition-colors duration-200">
	{@render children()}
</div>
