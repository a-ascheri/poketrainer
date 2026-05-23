const TOKEN_KEY = 'token';
const LAST_USERNAME_KEY = 'last_username';

export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);

export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

export const getLastUsername = (): string =>
  localStorage.getItem(LAST_USERNAME_KEY) ?? '';

export const setLastUsername = (username: string): void => {
  localStorage.setItem(LAST_USERNAME_KEY, username);
};

export const clearLastUsername = (): void => {
  localStorage.removeItem(LAST_USERNAME_KEY);
};
