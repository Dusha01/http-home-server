// frontend/src/lib/features/workspace/ui/FilePreview.svelte (обновленная версия)
<script lang="ts">
    import { API_BASE } from '$lib/shared/config';
    import { t } from '$lib/shared/locale';
    import { getPreviewMode, type PreviewMode } from '$lib/entities/file/preview';
    import TextPreviewEdit from "$lib/features/workspace/ui/TextPreviewEdit.svelte";

    interface Props {
        open: boolean;
        path: string;
        name: string;
        token: string | null;
        canEdit?: boolean; // Новый пропс для разрешения редактирования
        onClose: () => void;
        onFileUpdate?: () => void; // Колбэк после успешного редактирования
    }

    let {
        open,
        path,
        name,
        token,
        canEdit = false,
        onClose,
        onFileUpdate
    }: Props = $props();

    let content = $state('');
    let loading = $state(false);
    let error = $state('');
    let mode = $state<PreviewMode>('text');
    let mediaUrl = $state('');
    let audioRef = $state<HTMLAudioElement | null>(null);
    let videoRef = $state<HTMLVideoElement | null>(null);
    let fileSize = $state<number | null>(null);
    let loadId = 0;
    let editRequested = $state(0);

    $effect(() => {
        if (open) {
            loadPreview();
        } else {
            cleanup();
        }
    });

    function cleanup() {
        if (mediaUrl && !mediaUrl.startsWith('http')) {
            URL.revokeObjectURL(mediaUrl);
        }
        mediaUrl = '';
        content = '';
        error = '';
        fileSize = null;
        editRequested = 0;

        if (audioRef) {
            audioRef.pause();
            audioRef = null;
        }
        if (videoRef) {
            videoRef.pause();
            videoRef = null;
        }
    }

    async function loadPreview() {
        const currentLoadId = ++loadId;
        content = '';
        error = '';
        loading = true;

        try {
            const extension = name.split('.').pop() ?? null;
            const previewMode = getPreviewMode(name, extension);
            mode = previewMode;

            switch (previewMode) {
                case 'image':
                case 'video':
                case 'audio':
                    await loadMedia(currentLoadId);
                    break;
                case 'pdf':
                    await loadPdf();
                    break;
                case 'archive':
                    await loadArchive();
                    break;
                case 'config':
                case 'text':
                    await loadText(currentLoadId);
                    break;
                default:
                    error = t('preview.unsupportedFormat');
            }
        } catch (e) {
            if (currentLoadId === loadId) {
                error = e instanceof Error ? e.message : t('settings.loadError');
            }
        } finally {
            if (currentLoadId === loadId) {
                loading = false;
            }
        }
    }

    async function loadMedia(expectedLoadId: number) {
        const q = `path=${encodeURIComponent(path)}&as_attachment=false`;
        const endpoint = token ? `/share/download?${q}` : `/share/public/download?${q}`;
        const url = `${API_BASE}${endpoint}`;

        const response = await fetch(url, {
            headers: token ? { Authorization: `Bearer ${token}` } : {}
        });

        if (!response.ok) {
            throw new Error(response.statusText || 'Failed to load');
        }

        if (expectedLoadId !== loadId) return;

        // Получаем размер файла из заголовков
        const contentLength = response.headers.get('content-length');
        if (contentLength) {
            fileSize = parseInt(contentLength, 10);
        }

        const blob = await response.blob();
        if (expectedLoadId !== loadId) return;
        if (mediaUrl && mediaUrl.startsWith('blob:')) {
            URL.revokeObjectURL(mediaUrl);
        }
        mediaUrl = URL.createObjectURL(blob);
    }

    async function loadText(expectedLoadId: number) {
        const q = `path=${encodeURIComponent(path)}`;
        const endpoint = token ? `/share/preview?${q}` : `/share/public/preview?${q}`;
        const url = `${API_BASE}${endpoint}`;

        const response = await fetch(url, {
            headers: token ? { Authorization: `Bearer ${token}` } : {}
        });

        if (!response.ok) {
            throw new Error(response.statusText || 'Failed to load preview');
        }

        const text = await response.text();
        if (expectedLoadId === loadId) {
            content = text;
        }
    }

    async function loadPdf() {
        const q = `path=${encodeURIComponent(path)}&as_attachment=false`;
        const endpoint = token ? `/share/download?${q}` : `/share/public/download?${q}`;
        const url = `${API_BASE}${endpoint}`;

        mediaUrl = url;
    }

    async function loadArchive() {
        const q = `path=${encodeURIComponent(path)}`;
        const endpoint = token ? `/share/list?${q}` : `/share/public/list?${q}`;
        const url = `${API_BASE}${endpoint}`;

        const response = await fetch(url, {
            headers: token ? { Authorization: `Bearer ${token}` } : {}
        });

        if (!response.ok) {
            throw new Error(response.statusText || 'Failed to load archive contents');
        }

        const data = await response.json();

        if (data.files && Array.isArray(data.files)) {
            content = data.files.map((f: any) =>
                `${f.name} (${formatFileSize(f.size)})`
            ).join('\n');
        }
    }

    async function handleSaveContent(newContent: string) {
        const q = `path=${encodeURIComponent(path)}`;
        const endpoint = token ? `/share/update?${q}` : `/share/public/update?${q}`;
        const url = `${API_BASE}${endpoint}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
                'Content-Type': 'text/plain;charset=UTF-8'
            },
            body: newContent
        });

        if (!response.ok) {
            throw new Error(response.statusText || 'Failed to save');
        }

        // Обновляем контент после успешного сохранения
        content = newContent;

        if (onFileUpdate) {
            onFileUpdate();
        }
    }

    function formatFileSize(bytes: number): string {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
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

    function handleDownload() {
        const q = `path=${encodeURIComponent(path)}&as_attachment=true`;
        const endpoint = token ? `/share/download?${q}` : `/share/public/download?${q}`;
        const url = `${API_BASE}${endpoint}`;

        window.open(url, '_blank');
    }

    function handleTextPreviewError(event: CustomEvent) {
        console.error('Text preview error:', event.detail.error);
        error = t('preview.saveError');
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
                <h2 id="preview-title" class="truncate text-lg font-medium text-slate-800 dark:text-gray-200 flex items-center gap-2">
                    <!-- Иконка в зависимости от типа -->
                    {#if mode === 'pdf'}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                    {:else if mode === 'archive'}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                        </svg>
                    {:else if mode === 'audio'}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                        </svg>
                    {:else if mode === 'text' || mode === 'config'}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    {/if}
                    <span class="truncate">{name}</span>
                    {#if fileSize}
                        <span class="text-sm font-normal text-gray-500 dark:text-gray-400">
                            ({formatFileSize(fileSize)})
                        </span>
                    {/if}
                </h2>
                <div class="flex items-center gap-2">
                    <button
                            type="button"
                            class="shrink-0 rounded p-2 text-slate-500 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-gray-700"
                            aria-label={t('common.download')}
                            onclick={handleDownload}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M12 4v12m0 0l-3-3m3 3l3-3" />
                        </svg>
                    </button>
                    {#if canEdit && (mode === 'text' || mode === 'config')}
                        <button
                                type="button"
                                class="shrink-0 rounded p-2 text-slate-500 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-gray-700"
                                aria-label={t('common.edit')}
                                onclick={() => editRequested++}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                        </button>
                    {/if}
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
            </div>

            <div class="min-h-0 flex-1 overflow-auto">
                {#if loading}
                    <div class="flex flex-col items-center justify-center h-full gap-3 p-8">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                        <p class="text-slate-500 dark:text-gray-400">{t('common.loading')}</p>
                    </div>
                {:else if error}
                    <div class="flex flex-col items-center justify-center h-full gap-3 p-8">
                        <p class="text-red-600 dark:text-red-400 mb-2">{error}</p>
                        <button
                                onclick={loadPreview}
                                class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                        >
                            {t('common.retry')}
                        </button>
                    </div>
                {:else if mode === 'image' && mediaUrl}
                    <div class="flex items-center justify-center p-4">
                        <img src={mediaUrl} alt={name} class="max-w-full max-h-[calc(90vh-8rem)] object-contain rounded" />
                    </div>

                {:else if mode === 'video' && mediaUrl}
                    <div class="flex items-center justify-center p-4">
                        <video
                                bind:this={videoRef}
                                src={mediaUrl}
                                controls
                                class="max-w-full max-h-[calc(90vh-8rem)] rounded"
                                onloadedmetadata={() => videoRef?.play()}
                        >
                            <track kind="captions" />
                        </video>
                    </div>

                {:else if mode === 'audio' && mediaUrl}
                    <div class="flex items-center justify-center p-4">
                        <div class="w-full max-w-md p-6 bg-gray-100 dark:bg-gray-700 rounded-lg">
                            <audio
                                    bind:this={audioRef}
                                    src={mediaUrl}
                                    controls
                                    class="w-full"
                                    onloadedmetadata={() => audioRef?.play()}
                            ></audio>
                        </div>
                    </div>

                {:else if mode === 'pdf'}
                    <iframe
                            src={`${mediaUrl}#toolbar=0&navpanes=0`}
                            class="w-full h-[calc(90vh-8rem)] border-0 rounded"
                            title={name}
                    ></iframe>

                {:else if mode === 'archive'}
                    <div class="p-4">
                        <h3 class="text-lg font-medium mb-3 text-slate-800 dark:text-gray-200">
                            {t('preview.archiveContents')}
                        </h3>
                        <pre class="w-full whitespace-pre-wrap break-words font-mono text-sm text-slate-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-900 p-4 rounded"><code>{content}</code></pre>
                    </div>

                {:else if mode === 'config' || mode === 'text'}
                    <div class="h-full">
                        <TextPreviewEdit
                                content={content}
                                filename={name}
                                language={mode === 'config' ? 'config' : undefined}
                                editable={false}
                                editRequested={editRequested}
                                onSave={handleSaveContent}
                                onCancel={() => editRequested = 0}
                                on:error={handleTextPreviewError}
                                on:save={() => {
                                    if (onFileUpdate) onFileUpdate();
                                }}
                        />
                    </div>

                {:else}
                    <div class="flex flex-col items-center justify-center h-full gap-3 p-8">
                        <p class="text-slate-500 dark:text-gray-400 mb-4">{t('preview.unsupportedFormat')}</p>
                        <button
                                onclick={handleDownload}
                                class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                        >
                            {t('common.download')}
                        </button>
                    </div>
                {/if}
            </div>
        </div>
    </div>
{/if}