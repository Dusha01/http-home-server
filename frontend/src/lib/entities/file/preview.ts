/**
 * Расширения и имена файлов, для которых доступно текстовое превью.
 * Должно совпадать с бэкендом (FileUtils.PREVIEW_EXTENSIONS / is_text_previewable).
 */
const TEXT_PREVIEW_EXTENSIONS = new Set([
	'txt', 'md', 'py', 'js', 'html', 'css', 'json', 'xml', 'yml', 'yaml',
	'ini', 'cfg', 'conf', 'log', 'csv', 'tsv', 'sql', 'sh', 'bat', 'ps1',
	'rst', 'tex', 'latex', 'c', 'cpp', 'h', 'java', 'php', 'rb', 'go', 'rs',
	'swift', 'kt', 'scala', 'toml', 'env', 'example', 'config', 'gitignore', 'dockerignore'
]);

const TEXT_PREVIEW_NAMES = new Set([
	'.env', '.env.example', '.env.local', '.env.sample',
	'.config', '.gitignore', '.dockerignore', '.editorconfig'
]);

/** Расширения для превью изображений (совпадает с бэкендом FileUtils.IMAGE_EXTENSIONS). */
const IMAGE_EXTENSIONS = new Set([
	'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico'
]);

/** Расширения для превью видео. */
const VIDEO_EXTENSIONS = new Set([
	'mp4', 'webm', 'ogg', 'ogv', 'mov', 'avi', 'mkv', 'm4v'
]);

export function isTextPreviewable(name: string, extension?: string | null): boolean {
	const ext = (extension ?? '').toLowerCase().replace(/^\./, '');
	const lowerName = name.toLowerCase();
	if (ext && TEXT_PREVIEW_EXTENSIONS.has(ext)) return true;
	if (TEXT_PREVIEW_NAMES.has(lowerName)) return true;
	if (lowerName.startsWith('.env') || lowerName.endsWith('.example')) return true;
	return false;
}

export function isImagePreviewable(name: string, extension?: string | null): boolean {
	const ext = (extension ?? name.split('.').pop() ?? '').toLowerCase().replace(/^\./, '');
	return IMAGE_EXTENSIONS.has(ext);
}

export function isVideoPreviewable(name: string, extension?: string | null): boolean {
	const ext = (extension ?? name.split('.').pop() ?? '').toLowerCase().replace(/^\./, '');
	return VIDEO_EXTENSIONS.has(ext);
}

export type FileIconType =
	| 'folder'
	| 'image'
	| 'video'
	| 'audio'
	| 'archive'
	| 'pdf'
	| 'config'
	| 'text'
	| 'default';

const ARCHIVE_EXTENSIONS = new Set([
	'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'zst'
]);
const AUDIO_EXTENSIONS = new Set([
	'mp3', 'wav', 'ogg', 'oga', 'flac', 'm4a', 'aac', 'wma'
]);
const CONFIG_EXTENSIONS = new Set([
	'json', 'yml', 'yaml', 'xml', 'ini', 'cfg', 'conf', 'toml', 'env'
]);

export function getFileIconType(name: string, extension?: string | null): FileIconType {
	const ext = (extension ?? name.split('.').pop() ?? '').toLowerCase().replace(/^\./, '');
	const lowerName = name.toLowerCase();
	if (ext && IMAGE_EXTENSIONS.has(ext)) return 'image';
	if (ext && VIDEO_EXTENSIONS.has(ext)) return 'video';
	if (ext && AUDIO_EXTENSIONS.has(ext)) return 'audio';
	if (ext && ARCHIVE_EXTENSIONS.has(ext)) return 'archive';
	if (ext === 'pdf') return 'pdf';
	if (ext && CONFIG_EXTENSIONS.has(ext)) return 'config';
	if (TEXT_PREVIEW_EXTENSIONS.has(ext) || TEXT_PREVIEW_NAMES.has(lowerName) ||
		lowerName.startsWith('.env') || lowerName.endsWith('.example')) return 'text';
	return 'default';
}
