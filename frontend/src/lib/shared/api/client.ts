import { API_BASE } from '$lib/shared/config';

export type RequestOptions = {
	method?: string;
	body?: string | FormData;
	headers?: Record<string, string>;
	token?: string | null;
};

async function request<T>(
	path: string,
	options: RequestOptions = {}
): Promise<T> {
	const { method = 'GET', body, headers = {}, token } = options;
	const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
	const h: Record<string, string> = { ...headers };
	if (token) h['Authorization'] = `Bearer ${token}`;
	if (body && typeof body === 'string' && !h['Content-Type'])
		h['Content-Type'] = 'application/json';

	const res = await fetch(url, { method, body, headers: h });
	if (!res.ok) {
		const text = await res.text();
		throw new Error(text || `HTTP ${res.status}`);
	}
	if (res.status === 204) return undefined as T;
	return res.json() as Promise<T>;
}

async function requestText(path: string, token?: string | null): Promise<string> {
	const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
	const h: Record<string, string> = {};
	if (token) h['Authorization'] = `Bearer ${token}`;
	const res = await fetch(url, { method: 'GET', headers: h });
	if (!res.ok) {
		const text = await res.text();
		throw new Error(text || `HTTP ${res.status}`);
	}
	return res.text();
}

export const api = {
	get: <T>(path: string, token?: string | null) =>
		request<T>(path, { method: 'GET', token }),

	getText: (path: string, token?: string | null) => requestText(path, token),

	post: <T>(path: string, body?: object, token?: string | null) =>
		request<T>(path, {
			method: 'POST',
			body: body ? JSON.stringify(body) : undefined,
			token
		}),

	/** POST with FormData (e.g. file upload). Do not set Content-Type so browser sets multipart boundary. */
	postForm: <T>(path: string, formData: FormData, token?: string | null) =>
		request<T>(path, {
			method: 'POST',
			body: formData,
			token
		}),

	delete: <T>(path: string, body?: object, token?: string | null) =>
		request<T>(path, {
			method: 'DELETE',
			body: body ? JSON.stringify(body) : undefined,
			token
		})
};
