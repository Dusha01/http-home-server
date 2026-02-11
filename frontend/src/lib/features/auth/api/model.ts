const TOKEN_KEY = 'home-server-token';

export function getStoredToken(): string | null {
	if (typeof window === 'undefined') return null;
	return sessionStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
	sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken(): void {
	sessionStorage.removeItem(TOKEN_KEY);
}
