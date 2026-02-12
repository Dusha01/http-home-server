<script lang="ts">
	import { Button, Input } from '$lib/shared/ui';
	import { setStoredToken, validateToken } from '$lib/features/auth';
	import { t } from '$lib/shared/locale';

	let token = $state('');
	let loading = $state(false);
	let error = $state('');

	async function onSubmit(e: Event) {
		e.preventDefault();
		error = '';
		const tokenVal = token.trim();
		if (!tokenVal) {
			error = t('auth.enterToken');
			return;
		}
		loading = true;
		try {
			const res = await validateToken(tokenVal);
			if (res.valid) {
				setStoredToken(tokenVal);
				window.location.href = '/workspace';
			} else {
				error = res.message ?? t('auth.invalidToken');
			}
		} catch (err) {
			error = err instanceof Error ? err.message : t('auth.checkError');
		} finally {
			loading = false;
		}
	}
</script>

<div class="mx-auto max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow-md">
	<h1 class="mb-4 text-xl font-semibold text-slate-800">{t('auth.loginTitle')}</h1>
	<form onsubmit={onSubmit} class="flex flex-col gap-4">
		<Input
			bind:value={token}
			type="password"
			placeholder={t('auth.tokenPlaceholder')}
			autocomplete="one-time-code"
			disabled={loading}
		/>
		{#if error}
			<p class="text-sm text-red-600">{error}</p>
		{/if}
		<Button type="submit" disabled={loading}>
			{loading ? t('auth.checking') : t('auth.signIn')}
		</Button>
	</form>
</div>
