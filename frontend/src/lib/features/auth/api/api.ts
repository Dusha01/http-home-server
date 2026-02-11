import { api } from '$lib/shared/api/client';

export interface ServerInfo {
	name: string;
	version: string;
	status: string;
	auth_required: boolean;
}

/** Проверка: нужна ли аутентификация и статус сервера. */
export async function fetchServerInfo(): Promise<ServerInfo> {
	return api.get<ServerInfo>('/');
}

export interface ValidateTokenResponse {
	valid: boolean;
	message?: string | null;
	token_data?: unknown;
}

/** Проверка токена (POST /auth/token/validate). */
export async function validateToken(token: string): Promise<ValidateTokenResponse> {
	return api.post<ValidateTokenResponse>('/auth/token/validate', { token });
}
