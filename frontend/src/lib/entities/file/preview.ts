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

export function isTextPreviewable(name: string, extension?: string | null): boolean {
	const ext = (extension ?? '').toLowerCase().replace(/^\./, '');
	const lowerName = name.toLowerCase();
	if (ext && TEXT_PREVIEW_EXTENSIONS.has(ext)) return true;
	if (TEXT_PREVIEW_NAMES.has(lowerName)) return true;
	if (lowerName.startsWith('.env') || lowerName.endsWith('.example')) return true;
	return false;
}
