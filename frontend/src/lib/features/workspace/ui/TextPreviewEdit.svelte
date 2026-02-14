<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';
    import { t } from '$lib/shared/locale';

    let hljs: any = null;
    let hljsLoaded = $state(false);

    interface Props {
        content: string;
        filename: string;
        language?: string;
        editable?: boolean;
        editRequested?: number;
        onSave?: (content: string) => Promise<void>;
        onCancel?: () => void;
    }

    let {
        content: initialContent,
        filename,
        language = 'plaintext',
        editable = false,
        editRequested = 0,
        onSave,
        onCancel
    }: Props = $props();

    let content = $state('');
    let editedContent = $state('');
    let isEditing = $state(false);
    let isSaving = $state(false);
    let lineCount = $state(0);
    let highlightedHtml = $state('');
    let editorRef = $state<HTMLPreElement | null>(null);
    let textareaRef = $state<HTMLTextAreaElement | null>(null);

    const dispatch = createEventDispatcher();

    // Загрузка highlight.js при монтировании
    onMount(async () => {
        try {
            const module = await import('highlight.js');
            hljs = module.default;

            // Загружаем тему
            await import('highlight.js/styles/github-dark.min.css');

            hljsLoaded = true;
            highlightContent();
        } catch (e) {
            console.error('Failed to load highlight.js:', e);
        }
    });

    $effect(() => {
        if (!isEditing && initialContent !== content) {
            content = initialContent;
            editedContent = initialContent;
        }
        updateLineCount(isEditing ? editedContent : content);
        highlightContent();
    });

    $effect(() => {
        if (editRequested > 0 && !isEditing) {
            isEditing = true;
            editedContent = content;
        }
    });

    $effect(() => {
        if (isEditing && textareaRef) {
            textareaRef.focus();
            adjustTextareaHeight();
        }
    });

    function updateLineCount(text: string) {
        lineCount = (text.match(/\n/g) || '').length + 1;
    }

    function highlightContent() {
        if (!hljsLoaded || !hljs || !content) {
            highlightedHtml = escapeHtml(content);
            return;
        }

        try {
            const detected = hljs.highlightAuto(content, getLanguageHints());
            highlightedHtml = String(detected.value);
        } catch (e) {
            console.error('Highlight error:', e);
            highlightedHtml = escapeHtml(content);
        }
    }

    function getLanguageHints(): string[] {
        const ext = filename.split('.').pop()?.toLowerCase() ?? '';
        const lowerName = filename.toLowerCase();
        const extToLang: Record<string, string> = {
            'js': 'javascript',
            'jsx': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',
            'py': 'python',
            'rb': 'ruby',
            'php': 'php',
            'java': 'java',
            'go': 'go',
            'rs': 'rust',
            'c': 'c',
            'cpp': 'cpp',
            'cs': 'csharp',
            'html': 'html',
            'css': 'css',
            'scss': 'scss',
            'json': 'json',
            'xml': 'xml',
            'yaml': 'yaml',
            'yml': 'yaml',
            'md': 'markdown',
            'sql': 'sql',
            'sh': 'bash',
            'bash': 'bash',
            'dockerfile': 'dockerfile',
            'readme': 'markdown'
        };
        if (ext && extToLang[ext]) return [extToLang[ext]];
        if (lowerName === 'dockerfile' || lowerName === 'readme') return [extToLang[lowerName] ?? 'plaintext'];
        return [];
    }

    function escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function adjustTextareaHeight() {
        if (textareaRef) {
            textareaRef.style.height = 'auto';
            textareaRef.style.height = textareaRef.scrollHeight + 'px';
        }
    }

    function handleEdit() {
        isEditing = true;
        editedContent = content;
    }

    async function handleSave() {
        if (!onSave) return;

        isSaving = true;
        try {
            await onSave(editedContent);
            content = editedContent;
            isEditing = false;
            updateLineCount(editedContent);
            highlightContent();
            dispatch('save', { content: editedContent });
        } catch (error) {
            dispatch('error', { error });
        } finally {
            isSaving = false;
        }
    }

    function handleCancel() {
        isEditing = false;
        editedContent = content;
        onCancel?.();
    }

    function handleTextareaInput(e: Event) {
        const target = e.target as HTMLTextAreaElement;
        editedContent = target.value;
        adjustTextareaHeight();
    }

    function handleKeyDown(e: KeyboardEvent) {
        if (e.key === 'Escape' && isEditing) {
            handleCancel();
        }

        if ((e.ctrlKey || e.metaKey) && e.key === 's' && isEditing) {
            e.preventDefault();
            handleSave();
        }
    }

    // Генерация номеров строк
    $effect(() => {
        updateLineCount(isEditing ? editedContent : content);
    });
</script>

<div class="text-preview relative">
    {#if isEditing}
        <div class="editing-mode">
            <div class="sticky top-0 z-10 flex items-center justify-between gap-2 p-2 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                    {t('preview.editing')} {filename}
                </span>
                <div class="flex items-center gap-2">
                    <button
                            onclick={handleSave}
                            disabled={isSaving}
                            class="flex items-center gap-1 px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {#if isSaving}
                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>{t('common.saving')}</span>
                        {:else}
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                            <span>{t('common.save')}</span>
                        {/if}
                    </button>
                    <button
                            onclick={handleCancel}
                            class="flex items-center gap-1 px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600 transition"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        <span>{t('common.cancel')}</span>
                    </button>
                </div>
            </div>

            <div class="flex">
                <!-- Номера строк для редактора -->
                <div class="line-numbers py-4 pl-3 pr-2 text-right text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-800 select-none font-mono text-sm border-r border-gray-200 dark:border-gray-700">
                    {#each Array(lineCount) as _, i}
                        <div class="leading-6">{i + 1}</div>
                    {/each}
                </div>

                <!-- Текстовое поле для редактирования -->
                <textarea
                        bind:this={textareaRef}
                        value={editedContent}
                        oninput={handleTextareaInput}
                        onkeydown={handleKeyDown}
                        class="flex-1 p-4 font-mono text-sm bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 outline-none resize-none"
                        style="min-height: 200px; line-height: 1.5rem;"
                        spellcheck="false"
                ></textarea>
            </div>
        </div>
    {:else}
        <div class="view-mode flex">
            <!-- Номера строк для просмотра -->
            <div class="line-numbers py-4 pl-3 pr-2 text-right text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-800 select-none font-mono text-sm border-r border-gray-200 dark:border-gray-700">
                {#each Array(lineCount) as _, i}
                    <div class="leading-6">{i + 1}</div>
                {/each}
            </div>

            <!-- Подсвеченный код (без пробелов внутри pre — иначе первая строка пустая) -->
            <pre
                    class="flex-1 min-w-0 p-4 font-mono text-sm overflow-x-auto leading-6"
                    class:hljs={hljsLoaded}
            ><code>{@html highlightedHtml}</code></pre>
        </div>
    {/if}
</div>

<style>
    .text-preview {
        width: 100%;
        height: 100%;
        min-height: 200px;
    }

    .view-mode pre {
        margin: 0;
        white-space: pre-wrap;
        word-wrap: break-word;
        background: transparent;
        min-width: 0;
    }

    .view-mode code {
        font-family: inherit;
        background: transparent;
        display: block;
        width: 100%;
    }

    .line-numbers {
        min-width: 3rem;
        user-select: none;
    }

    textarea {
        font-family: 'Fira Code', 'Consolas', monospace;
        line-height: 1.5rem;
        tab-size: 4;
    }

    textarea:focus {
        outline: none;
    }

    /* Стили для скроллбаров */
    .overflow-x-auto::-webkit-scrollbar {
        height: 8px;
    }

    .overflow-x-auto::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    .overflow-x-auto::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }

    .overflow-x-auto::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

    /* Темная тема для скроллбаров */
    :global(.dark) .overflow-x-auto::-webkit-scrollbar-track {
        background: #374151;
    }

    :global(.dark) .overflow-x-auto::-webkit-scrollbar-thumb {
        background: #4b5563;
    }

    :global(.dark) .overflow-x-auto::-webkit-scrollbar-thumb:hover {
        background: #6b7280;
    }
</style>