<script lang="ts">
	import { t } from '$lib/shared/locale';

	interface Props {
		status?: number;
		error?: unknown;
	}

	let { status, error }: Props = $props();

	const message = $derived(
		error instanceof Error ? error.message : typeof error === 'string' ? error : t('error.generic')
	);
</script>

<div class="flex min-h-screen flex-col items-center justify-center gap-4 p-4">
	<h1 class="text-xl font-semibold text-slate-800 dark:text-gray-200">
		{t('error.title')} {status != null ? status : ''}
	</h1>
	<p class="max-w-md text-center text-slate-600 dark:text-gray-400">
		{message}
	</p>
	<a
		href="/"
		class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700"
	>
		{t('common.refresh')}
	</a>
</div>
