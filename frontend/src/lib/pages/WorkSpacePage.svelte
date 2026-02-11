<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    import {fetchServerInfo, getStoredToken} from "$lib";
    import {WorkspaceLayout} from "$lib";
    import {Header} from "$lib";

    let showWorkspace = $state(false);
    let loading = $state(true);

    onMount(async () => {
        try {
            const info = await fetchServerInfo();
            const token = getStoredToken();
            if (info.auth_required && !token) {
                goto('/login', { replaceState: true });
                return;
            }
            showWorkspace = true;
        } catch {
            showWorkspace = true;
        } finally {
            loading = false;
        }
    });
</script>

<div class="flex h-screen flex-col">
    {#if loading}
        <div class="flex flex-1 items-center justify-center">
            <p class="text-slate-600">Загрузка…</p>
        </div>
    {:else if showWorkspace}
        <Header/>
        <WorkspaceLayout />
    {/if}
</div>