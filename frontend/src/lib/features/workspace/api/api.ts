import { api } from '$lib/shared/api/client';
import type {
	DirectoryContent,
	ExplorerRootItem,
	ExplorerListResponse
} from '$lib/entities/file';

/**
 * Загрузка содержимого папки.
 * С токеном — /share/browse, без — /share/public/browse (если сервер без auth).
 */
export async function fetchDirectoryContent(
	path: string,
	token: string | null
): Promise<DirectoryContent> {
	const q = `path=${encodeURIComponent(path)}`;
	const endpoint = token ? `/share/browse?${q}` : `/share/public/browse?${q}`;
	return api.get<DirectoryContent>(endpoint, token);
}

/**
 * Превью текстового файла (txt, конфиги, .env и т.д.).
 */
export async function fetchPreview(path: string, token: string | null): Promise<string> {
	const q = `path=${encodeURIComponent(path)}`;
	const endpoint = token ? `/share/preview?${q}` : `/share/public/preview?${q}`;
	return api.getText(endpoint, token);
}

/**
 * Корневые пункты проводника (диски на Windows, корень/домашняя папка на Linux).
 * Требует авторизации.
 */
export async function fetchExplorerRoots(token: string | null): Promise<ExplorerRootItem[]> {
	return api.get<ExplorerRootItem[]>('/share/explorer/roots', token);
}

/**
 * Список подпапок по абсолютному пути на сервере (файловая система ПК).
 * Требует авторизации.
 */
export async function fetchExplorerList(
	path: string,
	token: string | null
): Promise<ExplorerListResponse> {
	const q = `path=${encodeURIComponent(path)}`;
	return api.get<ExplorerListResponse>(`/share/explorer/list?${q}`, token);
}

/** Ответ API с путём папки транслятора (общий корень для всех в сети). */
export interface TransmitterRootResponse {
	path: string;
}

/**
 * Получить путь папки транслятора с сервера — один и тот же для всех устройств в сети.
 */
export async function fetchServerRootPath(token: string | null): Promise<string> {
	const data = await api.get<TransmitterRootResponse>('/share/root-path', token);
	const p = (data?.path ?? '/').replace(/\\/g, '/').trim().replace(/\/$/, '') || '/';
	return p === '.' ? '/' : p;
}

/**
 * Установить на сервере путь папки транслятора (только с основного сервера с авторизацией).
 */
export async function setServerRootPath(path: string, token: string | null): Promise<string> {
	const normalized = (path ?? '/').trim().replace(/\\/g, '/').replace(/\/$/, '') || '/';
	await api.post<TransmitterRootResponse>('/share/root-path', { path: normalized || '/' }, token);
	return normalized === '.' ? '/' : normalized || '/';
}
