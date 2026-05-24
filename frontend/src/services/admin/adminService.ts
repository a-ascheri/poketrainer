import { backendClient } from '@services/http/client';
import { type UserProfile } from '@services/auth/authService';

export const listUsers = async (): Promise<UserProfile[]> => {
  const response = await backendClient.get<UserProfile[]>('/admin/users');
  return response.data;
};

export const updateUser = async (
  userId: number,
  payload: Partial<Pick<UserProfile, 'username' | 'email' | 'is_active'>> & {
    password?: string;
  },
): Promise<UserProfile> => {
  const response = await backendClient.put<UserProfile>(`/admin/users/${userId}`, payload);
  return response.data;
};

export const deleteUser = async (userId: number): Promise<void> => {
  await backendClient.delete(`/admin/users/${userId}`);
};
