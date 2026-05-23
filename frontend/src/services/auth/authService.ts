import { backendClient } from '@services/http/client';

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const login = async (payload: LoginPayload): Promise<TokenResponse> => {
  const body = new URLSearchParams({
    username: payload.username,
    password: payload.password,
  });

  const response = await backendClient.post<TokenResponse>('/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  return response.data;
};

export const register = async (payload: RegisterPayload): Promise<void> => {
  await backendClient.post('/users/', payload);
};
