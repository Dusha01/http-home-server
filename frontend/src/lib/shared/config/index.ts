/**
 * Базовый URL API (бэкенд Home-server).
 * По умолчанию /api — прокси Vite на localhost:8080.
 * Иначе задайте VITE_API_URL в .env (например http://localhost:8080).
 */
export const API_BASE =
	typeof import.meta.env !== 'undefined' && import.meta.env.VITE_API_URL
		? (import.meta.env.VITE_API_URL as string).replace(/\/$/, '')
		: '/api';
