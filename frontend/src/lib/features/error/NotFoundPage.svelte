<script lang="ts">
	import { t } from '$lib/shared/locale';

	interface Props {
		statusError?: string;
		titleError?: string;
	}

	let { statusError = '404', titleError }: Props = $props();

	const title = $derived(titleError ?? t('error.notFound'));
</script>

<div class="flex min-h-screen flex-col items-center justify-center gap-4 p-4">
	<p class="text-6xl font-light text-slate-400 dark:text-gray-500">{statusError}</p>
	<h1 class="text-xl font-semibold text-slate-800 dark:text-gray-200">
		{title}
	</h1>
	<p class="max-w-md text-center text-slate-600 dark:text-gray-400">
		{t('error.notFoundDescription')}
	</p>
	<a
		href="/"
		class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700"
	>
		{t('common.back')}
	</a>
</div>
