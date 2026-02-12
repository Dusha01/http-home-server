import { get } from 'svelte/store';
import { localeStore } from './store';
import { translations } from './translations';

export { localeStore, type Locale } from './store';
export { translations } from './translations';

/**
 * Функция перевода: подписывается на localeStore, возвращает строку по ключу.
 * Подстановки: t('workspace.downloadFile', { name: 'file.txt' }) → "Скачать file.txt"
 */
export function t(key: string, params?: Record<string, string>): string {
	const locale = get(localeStore);
	const dict = translations[locale];
	let s = dict?.[key] ?? translations.ru[key] ?? key;
	if (params) {
		for (const [k, v] of Object.entries(params)) {
			s = s.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
		}
	}
	return s;
}
