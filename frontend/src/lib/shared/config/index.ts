/**
 * Базовый URL API (бэкенд Home-server).
 * По умолчанию /api — прокси Vite на localhost:8080.
 * Иначе задайте VITE_API_URL в .env (например http://localhost:8080).
 */
export const API_BASE =
	typeof import.meta.env !== 'undefined' && import.meta.env.VITE_API_URL
		? (import.meta.env.VITE_API_URL as string).replace(/\/$/, '')
		: '/api';

/** Ключ localStorage для пути папки из настроек (папка транслятора). */
export const FOLDER_PATH_STORAGE_KEY = 'home-server-folder-path';

/** Событие при смене сохранённой папки в настройках (чтобы workspace обновил отображение). */
export const FOLDER_PATH_CHANGED_EVENT = 'home-server-folder-path-changed';

/** Записать путь папки в localStorage (только с основного сервера). */
export function setStoredFolderPath(path: string): void {
	if (typeof document === 'undefined' || !isMainServer()) return;
	const normalized = (path || '/').replace(/\\/g, '/').replace(/\/+/g, '/').trim().replace(/\/$/, '') || '/';
	localStorage.setItem(FOLDER_PATH_STORAGE_KEY, normalized === '.' ? '/' : normalized);
}

/** Открыто с основного сервера (localhost) — только там можно менять путь к папке. На клиентах опция недоступна. */
export function isMainServer(): boolean {
	if (typeof document === 'undefined') return false;
	const h = window.location.hostname;
	return h === 'localhost' || h === '127.0.0.1';
}

export function getStoredFolderPath(): string {
	if (typeof document === 'undefined') return '/';
	if (!isMainServer()) return '/';
	const raw = localStorage.getItem(FOLDER_PATH_STORAGE_KEY) || '/';
	const normalized = raw.replace(/\\/g, '/').replace(/\/+/g, '/').trim().replace(/\/$/, '') || '/';
	return normalized === '.' ? '/' : normalized || '/';
}
