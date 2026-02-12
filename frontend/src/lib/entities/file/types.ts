/** Тип элемента (совпадает с бэкендом FileType). */
export type FileType = 'file' | 'directory' | 'symlink' | 'other';

/** Информация о файле/папке (ответ API). */
export interface FileInfo {
	name: string;
	path: string;
	type: FileType;
	size?: number | null;
	modified?: string | null;
	created?: string | null;
	extension?: string | null;
	is_hidden: boolean;
	is_readable: boolean;
	is_writable: boolean;
}

/** Содержимое директории (GET /share/browse или /share/public/browse). */
export interface DirectoryContent {
	current_path: string;
	parent_path: string | null;
	directories: FileInfo[];
	files: FileInfo[];
	total_items: number;
}

/** Корневой пункт проводника (диск или корень системы). */
export interface ExplorerRootItem {
	path: string;
	name: string;
}

/** Элемент списка папок в проводнике. */
export interface ExplorerDirItem {
	path: string;
	name: string;
}

/** Ответ GET /share/explorer/list — список папок по абсолютному пути. */
export interface ExplorerListResponse {
	path: string;
	parent_path: string | null;
	directories: ExplorerDirItem[];
}
