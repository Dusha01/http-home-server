import { api } from '$lib/shared/api/client';
import type { DirectoryContent } from '$lib/entities/file';

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
