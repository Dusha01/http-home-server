<script lang="ts">
    import {onMount} from "svelte";
    import {goto} from "$app/navigation";

    import { fetchServerInfo, getStoredToken, LoginForm } from "$lib";
    import { t } from '$lib/shared/locale';

    let showForm = $state(false);
    let loading = $state(true);

    onMount(async () => {
        try {
            const info = await fetchServerInfo();
            const token = getStoredToken();
            if (!info.auth_required || token) {
                goto('/workspace', { replaceState: true });
                return;
            }
            showForm = true;
        } catch {
            showForm = true;
        } finally {
            loading = false;
        }
    });
</script>

<div class="flex min-h-screen items-center justify-center p-4">
    {#if loading}
        <p class="text-slate-600">{t('common.loading')}</p>
    {:else if showForm}
        <LoginForm />
    {/if}
</div>