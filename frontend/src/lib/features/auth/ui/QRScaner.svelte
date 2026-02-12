<script lang="ts">
    import { onMount, onDestroy, tick } from 'svelte';
    import { BrowserMultiFormatReader } from '@zxing/library';
    import { Button } from '$lib/shared';
    import { t } from '$lib/shared/locale';

    interface Props {
        onScan: (token: string) => void;
        onClose: () => void;
    }

    let { onScan, onClose }: Props = $props();

    let video = $state<HTMLVideoElement | undefined>(undefined);
    let error = $state<string | null>(null);
    let isSecureContextError = $state(false);
    let scanning = $state(true);
    let codeReader: BrowserMultiFormatReader | null = null;
    let stream: MediaStream | null = null;

    onMount(async () => {
        await tick();
        const videoEl = video;
        if (!videoEl) {
            error = t('auth.cameraError');
            return;
        }

        if (!navigator.mediaDevices?.getUserMedia) {
            error = t('auth.cameraError');
            return;
        }
        const insecureContext = typeof window !== 'undefined' && !window.isSecureContext;
        if (insecureContext) {
            isSecureContextError = true;
            error = t('auth.cameraSecureContext');
            return;
        }

        codeReader = new BrowserMultiFormatReader();

        try {
            // Запрашиваем камеру: сначала с задней (для телефона), при ошибке — любая
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
                });
            } catch {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
            }

            await codeReader.decodeFromStream(stream, videoEl, (result, err) => {
                if (err) return;
                if (result && scanning) {
                    scanning = false;
                    onScan(result.getText());
                }
            });
        } catch (err) {
            console.error('Camera access error:', err);
            const isSecurityError =
                err instanceof DOMException &&
                (err.name === 'SecurityError' || err.name === 'NotAllowedError');
            const msg = err instanceof Error ? err.message : String(err);
            const isSecureContextRequired =
                msg.includes('secure') || msg.includes('Secure') || msg.includes('insecure');
            if (
                (typeof window !== 'undefined' && !window.isSecureContext) ||
                (isSecurityError && isSecureContextRequired)
            ) {
                isSecureContextError = true;
                error = t('auth.cameraSecureContext');
            } else if (msg.includes('Permission') || msg.includes('NotAllowed') || msg.includes('denied')) {
                error = t('auth.cameraError');
            } else if (msg.includes('NotFound') || msg.includes('no camera')) {
                error = t('auth.cameraError');
            } else {
                error = t('auth.cameraError');
            }
        }
    });

    onDestroy(() => {
        if (stream) {
            stream.getTracks().forEach((t) => t.stop());
            stream = null;
        }
        if (codeReader) {
            codeReader.reset();
            codeReader = null;
        }
    });
</script>

<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
<div
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4"
        role="dialog"
        aria-modal="true"
        tabindex="-1"
        onclick={onClose}
>
    <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions a11y_no_noninteractive_element_interactions -->
    <div
            class="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl"
            role="document"
            onclick={(e) => e.stopPropagation()}
    >
        <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-semibold text-slate-800">
                {t('auth.scanQRTitle')}
            </h2>
            <button
                    type="button"
                    onclick={onClose}
                    class="rounded-lg p-1 hover:bg-slate-100"
                    aria-label={t('common.close')}
            >
                <svg class="h-6 w-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>

        {#if error}
            <div class="mb-4 rounded-lg bg-red-50 p-4 text-center text-red-600">
                {error}
                <p class="mt-2 text-sm text-slate-600">
                    {isSecureContextError ? t('auth.cameraSecureContextHelp') : t('auth.cameraHelp')}
                </p>
            </div>
        {:else}
            <div class="relative mb-4 overflow-hidden rounded-lg bg-black">
                <!-- Видео поток -->
                <video
                        bind:this={video}
                        class="h-auto w-full"
                        autoplay
                ></video>

                <!-- Оверлей с рамкой для сканирования -->
                <div class="absolute inset-0 flex items-center justify-center">
                    <div class="h-48 w-48 rounded-lg border-2 border-white/50">
                        <div class="absolute left-1/2 top-1/2 h-0.5 w-48 -translate-x-1/2 -translate-y-1/2 bg-white/50"></div>
                        <div class="absolute left-1/2 top-1/2 h-48 w-0.5 -translate-x-1/2 -translate-y-1/2 bg-white/50"></div>
                    </div>
                </div>

                {#if !scanning}
                    <div class="absolute inset-0 flex items-center justify-center bg-black/75">
                        <div class="text-center text-white">
                            <svg class="mx-auto mb-2 h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                            <p>{t('auth.scanSuccess')}</p>
                        </div>
                    </div>
                {/if}
            </div>

            <p class="mb-4 text-center text-sm text-slate-600">
                {t('auth.scanInstruction')}
            </p>
        {/if}

        <div class="flex justify-end">
            <Button class="border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-gray-500 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600" onclick={onClose}>
                {t('common.close')}
            </Button>
        </div>
    </div>
</div>

<style>
    video {
        transform: scaleX(-1);
    }
</style>