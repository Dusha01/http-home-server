/**
 * Локаль приложения: ru | en. Сохраняется в localStorage.
 */
import { writable } from 'svelte/store';

export type Locale = 'ru' | 'en';

const STORAGE_KEY = 'home-server-locale';

function readStored(): Locale {
	if (typeof localStorage === 'undefined') return 'ru';
	const v = localStorage.getItem(STORAGE_KEY);
	if (v === 'en' || v === 'ru') return v;
	return 'ru';
}

function createLocaleStore() {
	const { subscribe, set } = writable<Locale>(readStored());
	return {
		subscribe,
		setLocale(locale: Locale) {
			localStorage.setItem(STORAGE_KEY, locale);
			set(locale);
		},
		getLocale(): Locale {
			return readStored();
		}
	};
}

export const localeStore = createLocaleStore();
