<script lang="ts">
	import { Button, Input } from '$lib/shared/ui';
	import { setStoredToken, validateToken } from '$lib/features/auth';

	let token = $state('');
	let loading = $state(false);
	let error = $state('');

	async function onSubmit(e: Event) {
		e.preventDefault();
		error = '';
		const t = token.trim();
		if (!t) {
			error = 'Введите токен';
			return;
		}
		loading = true;
		try {
			const res = await validateToken(t);
			if (res.valid) {
				setStoredToken(t);
				window.location.href = '/workspace';
			} else {
				error = res.message ?? 'Неверный токен';
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Ошибка проверки токена';
		} finally {
			loading = false;
		}
	}
</script>

<div class="mx-auto max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow-md">
	<h1 class="mb-4 text-xl font-semibold text-slate-800">Вход в облачную папку</h1>
	<form onsubmit={onSubmit} class="flex flex-col gap-4">
		<Input
			bind:value={token}
			type="password"
			placeholder="Токен доступа"
			autocomplete="one-time-code"
			disabled={loading}
		/>
		{#if error}
			<p class="text-sm text-red-600">{error}</p>
		{/if}
		<Button type="submit" disabled={loading}>
			{loading ? 'Проверка…' : 'Войти'}
		</Button>
	</form>
</div>
