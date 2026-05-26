import { backendClient } from '../http/client';
import { API_ROUTES } from '../apiRoutes';
import { type UserProfile } from '../auth/authService';

export const listUsers = async (): Promise<UserProfile[]> => {
  const response = await backendClient.get<UserProfile[]>(API_ROUTES.admin.users);
  return response.data;
};

export const updateUser = async (
  userId: number,
  payload: Partial<Pick<UserProfile, 'username' | 'email' | 'is_active'>> & {
    password?: string;
  },
): Promise<UserProfile> => {
  const response = await backendClient.put<UserProfile>(`${API_ROUTES.admin.users}/${userId}`, payload);
  return response.data;
};

export const deleteUser = async (userId: number): Promise<void> => {
  await backendClient.delete(`${API_ROUTES.admin.users}/${userId}`);
};
