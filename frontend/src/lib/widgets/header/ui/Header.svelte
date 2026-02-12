<script lang="ts">
	import { onMount } from 'svelte';
	import SettingsModal from './SettingsModal.svelte';
	import {
		getStoredFolderPath,
		FOLDER_PATH_STORAGE_KEY,
		FOLDER_PATH_CHANGED_EVENT
	} from '$lib/shared/config';
	import { setServerRootPath } from '$lib/features/workspace';
	import { getStoredToken } from '$lib/features/auth';

	export type Theme = 'light' | 'dark';

	const STORAGE_KEY = 'theme';

	function readTheme(): Theme {
		if (typeof document === 'undefined') return 'light';
		const saved = localStorage.getItem(STORAGE_KEY) as Theme | null;
		if (saved === 'dark' || saved === 'light') return saved;
		return 'light';
	}

	function applyTheme(theme: Theme) {
		const root = document.documentElement;
		root.classList.remove('light', 'dark');
		root.classList.add(theme);
		localStorage.setItem(STORAGE_KEY, theme);
	}

	let theme = $state<Theme>(readTheme());

	function toggleTheme() {
		theme = theme === 'light' ? 'dark' : 'light';
		applyTheme(theme);
	}

	onMount(() => {
		theme = readTheme();
		applyTheme(theme);
	});

	/** Слот для дополнительных кнопок в шапке (настройки, уведомления и т.д.) */
	let actions: import('svelte').Snippet | undefined = $props();

	let settingsOpen = $state(false);

	function openSettings() {
		settingsOpen = true;
	}

	function closeSettings() {
		settingsOpen = false;
	}

	async function saveFolderPath(path: string) {
		const p = (path || '/').trim() || '/';
		try {
			await setServerRootPath(p, getStoredToken());
		} catch {
			// без токена или при ошибке сети — сохраняем только локально
		}
		localStorage.setItem(FOLDER_PATH_STORAGE_KEY, p);
		window.dispatchEvent(
			new CustomEvent(FOLDER_PATH_CHANGED_EVENT, { detail: p })
		);
	}
</script>

<header
	class="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 shadow-md transition-colors duration-200"
>
	<div class="container mx-auto px-4">
		<div class="flex items-center justify-between h-16">
			<div class="flex items-center gap-4">
				<a
					href="/"
					class="text-xl font-bold text-gray-800 dark:text-white hover:text-sky-600 dark:hover:text-sky-400 transition-colors"
				>
					Home Server
				</a>
			</div>

			<div class="flex items-center gap-2">
				{#if typeof actions === 'function'}
					{@render actions()}
				{/if}

				<!-- Кнопка: настройки -->
				<button
					type="button"
					class="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900"
					aria-label="Настройки"
					onclick={openSettings}
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-5 w-5"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path
							d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
						/>
						<path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
					</svg>
				</button>

				<!-- Кнопка: смена темы -->
				<button
					type="button"
					class="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900"
					aria-label={theme === 'light' ? 'Включить тёмную тему' : 'Включить светлую тему'}
					onclick={toggleTheme}
				>
					{#if theme === 'light'}
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-5 w-5 text-gray-700"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
						</svg>
					{:else}
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-5 w-5 text-gray-300"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
						</svg>
					{/if}
				</button>
			</div>
		</div>
	</div>
</header>

<SettingsModal
	open={settingsOpen}
	initialPath={settingsOpen ? getStoredFolderPath() : ''}
	onClose={closeSettings}
	onSave={saveFolderPath}
/>

<div class="h-16" aria-hidden="true"></div>
