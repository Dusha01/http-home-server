<script lang="ts">
    import { onMount } from 'svelte';
    import { Button, Input } from '$lib/shared/ui';
    import { setStoredToken, validateToken } from '$lib/features/auth';
    import { t } from '$lib/shared/locale';
    import QRScaner from '$lib/features/auth/ui/QRScaner.svelte';

    let token = $state('');
    let loading = $state(false);
    let error = $state('');
    let showQRScanner = $state(false);

    onMount(() => {
        const params = new URLSearchParams(typeof window !== 'undefined' ? window.location.search : '');
        const tokenFromUrl = params.get('token');
        if (tokenFromUrl?.trim()) {
            token = tokenFromUrl.trim();
            onSubmit(new Event('submit'));
        }
    });

    /** Извлечь токен из отсканированного URL (сервер генерирует QR с auth_url: .../auth/login?token=XXX) или вернуть как есть. */
    function parseTokenFromScanned(scanned: string): string {
        const s = scanned.trim();
        try {
            const url = new URL(s);
            const tokenParam = url.searchParams.get('token');
            if (tokenParam) return tokenParam;
        } catch {
            // не URL — возможно, отсканирован сам токен
        }
        return s;
    }

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

    function handleQRScan(scannedValue: string) {
        token = parseTokenFromScanned(scannedValue);
        showQRScanner = false;
        if (token) {
            setTimeout(() => onSubmit(new Event('submit')), 100);
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

        <div class="flex flex-col gap-2">
            <Button type="submit" disabled={loading}>
                {loading ? t('auth.checking') : t('auth.signIn')}
            </Button>
            <button
                type="button"
                class="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-50 dark:border-gray-500 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
                onclick={() => showQRScanner = true}
                disabled={loading}
            >
                <svg class="h-5 w-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                </svg>
                {t('auth.scanQR')}
            </button>
        </div>
    </form>
</div>

{#if showQRScanner}
    <QRScaner
        onScan={handleQRScan}
        onClose={() => showQRScanner = false}
    />
{/if}