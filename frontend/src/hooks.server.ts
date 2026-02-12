import type { Handle } from '@sveltejs/kit';

const API_PROXY_PATH = '/api';
const BACKEND_URL =
	typeof process !== 'undefined' && process.env?.VITE_API_URL
		? (process.env.VITE_API_URL as string).replace(/\/$/, '')
		: 'http://localhost:8080';

const handle: Handle = async ({ event, resolve }) => {
	if (event.url.pathname.startsWith(API_PROXY_PATH)) {
		const path = event.url.pathname.slice(API_PROXY_PATH.length) || '/';
		const url = `${BACKEND_URL}${path}${event.url.search}`;
		const headers = new Headers(event.request.headers);
		headers.delete('connection');
		headers.set('host', new URL(BACKEND_URL).host);
		try {
			const res = await fetch(url, {
				method: event.request.method,
				headers,
				body: event.request.method !== 'GET' && event.request.method !== 'HEAD' ? event.request.body : undefined
			});
			const resHeaders = new Headers();
			res.headers.forEach((value, key) => {
				const lower = key.toLowerCase();
				if (lower !== 'connection' && lower !== 'transfer-encoding') resHeaders.set(key, value);
			});
			return new Response(res.body, {
				status: res.status,
				statusText: res.statusText,
				headers: resHeaders
			});
		} catch (e) {
			console.error('[api proxy]', e);
			return new Response(
				JSON.stringify({ detail: 'Backend unreachable. Is the server running on ' + BACKEND_URL + '?' }),
				{ status: 502, headers: { 'content-type': 'application/json' } }
			);
		}
	}
	return resolve(event);
};

export { handle };
