import { backendClient } from '@services/http/client';
import { API_ROUTES } from '@services/apiRoutes';

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
  role: 'admin' | 'trainer';
  force_password_change: boolean;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'trainer';
  permissions: string[];
  force_password_change: boolean;
  starter_pokemon_selected: boolean;
  is_active: boolean;
}

export const login = async (payload: LoginPayload): Promise<TokenResponse> => {
  const body = new URLSearchParams({
    username: payload.username,
    password: payload.password,
  });

  const response = await backendClient.post<TokenResponse>(API_ROUTES.user.login, body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  return response.data;
};

export const register = async (payload: RegisterPayload): Promise<void> => {
  await backendClient.post(API_ROUTES.user.register, payload);
};

export const getCurrentUserProfile = async (): Promise<UserProfile> => {
  const response = await backendClient.get<UserProfile>(API_ROUTES.user.profile);
  return response.data;
};

export const changePassword = async (
  currentPassword: string,
  newPassword: string,
): Promise<void> => {
  await backendClient.post(API_ROUTES.user.changePassword, {
    current_password: currentPassword,
    new_password: newPassword,
  });
};
