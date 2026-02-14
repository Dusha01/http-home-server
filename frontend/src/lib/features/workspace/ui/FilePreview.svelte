<script lang="ts">
    import { API_BASE } from '$lib/shared/config';
    import { t } from '$lib/shared/locale';
    import { isImagePreviewable, isVideoPreviewable } from '$lib/entities/file/preview';

    interface Props {
        open: boolean;
        path: string;
        name: string;
        token: string | null;
        onClose: () => void;
    }

    let { open, path, name, token, onClose }: Props = $props();

    let content = $state('');
    let loading = $state(false);
    let error = $state('');
    let mode = $state<'text' | 'image' | 'video'>('text');
    let mediaUrl = $state('');

    $effect(() => {
        if (open) {
            loadPreview();
        } else {
            cleanup();
        }
    });

    function cleanup() {
        if (mediaUrl) {
            URL.revokeObjectURL(mediaUrl);
            mediaUrl = '';
        }
        content = '';
        error = '';
        mode = 'text';
    }

    async function loadPreview() {
        cleanup();
        loading = true;
        error = '';

        try {
            const extension = name.split('.').pop() ?? null;

            if (isImagePreviewable(name, extension)) {
                mode = 'image';
                await loadMedia();
            } else if (isVideoPreviewable(name, extension)) {
                mode = 'video';
                await loadMedia();
            } else {
                mode = 'text';
                await loadText();
            }
        } catch (e) {
            error = e instanceof Error ? e.message : t('settings.loadError');
        } finally {
            loading = false;
        }
    }

    async function loadMedia() {
        const q = `path=${encodeURIComponent(path)}&as_attachment=false`;
        const endpoint = token ? `/share/download?${q}` : `/share/public/download?${q}`;
        const url = `${API_BASE}${endpoint}`;

        const response = await fetch(url, {
            headers: token ? { Authorization: `Bearer ${token}` } : {}
        });

        if (!response.ok) {
            throw new Error(response.statusText || 'Failed to load');
        }

        const blob = await response.blob();
        mediaUrl = URL.createObjectURL(blob);
    }

    async function loadText() {
        const q = `path=${encodeURIComponent(path)}`;
        const endpoint = token ? `/share/preview?${q}` : `/share/public/preview?${q}`;
        const url = `${API_BASE}${endpoint}`;

        const response = await fetch(url, {
            headers: token ? { Authorization: `Bearer ${token}` } : {}
        });

        if (!response.ok) {
            throw new Error(response.statusText || 'Failed to load preview');
        }

        content = await response.text();
    }

    function handleKeyDown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            onClose();
        }
    }

    function handleBackdropClick(e: MouseEvent) {
        if (e.target === e.currentTarget) {
            onClose();
        }
    }
</script>

{#if open}
    <!-- svelte-ignore a11y_no_static_element_interactions a11y_click_events_have_key_events -->
    <div
            class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="preview-title"
            tabindex="-1"
            onclick={handleBackdropClick}
            onkeydown={handleKeyDown}
    >
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <div class="flex max-h-[90vh] w-full max-w-4xl flex-col rounded-xl bg-white dark:bg-gray-800 shadow-xl" onclick={(e) => e.stopPropagation()}>
            <div class="flex items-center justify-between gap-3 border-b border-slate-200 dark:border-gray-600 px-4 py-3">
                <h2 id="preview-title" class="truncate text-lg font-medium text-slate-800 dark:text-gray-200">
                    {name}
                </h2>
                <button
                        type="button"
                        class="shrink-0 rounded p-2 text-slate-500 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-gray-700"
                        aria-label={t('common.close')}
                        onclick={onClose}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div class="min-h-0 flex-1 overflow-auto p-4 flex items-center justify-center">
                {#if loading}
                    <p class="text-slate-500 dark:text-gray-400">{t('common.loading')}</p>
                {:else if error}
                    <p class="text-red-600 dark:text-red-400">{error}</p>
                {:else if mode === 'image' && mediaUrl}
                    <img src={mediaUrl} alt={name} class="max-w-full max-h-[80vh] object-contain rounded" />
                {:else if mode === 'video' && mediaUrl}
                    <video src={mediaUrl} controls class="max-w-full max-h-[80vh] rounded">
                        <track kind="captions" />
                    </video>
                {:else}
                    <pre class="w-full whitespace-pre-wrap break-words font-mono text-sm text-slate-800 dark:text-gray-200"><code>{content}</code></pre>
                {/if}
            </div>
        </div>
    </div>
{/if}