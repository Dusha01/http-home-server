<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Home Server — облачная папка</title>
</svelte:head>
<div class="min-h-screen bg-slate-100 text-slate-900 dark:bg-gray-900 dark:text-gray-100 transition-colors duration-200">
	{@render children()}
</div>
