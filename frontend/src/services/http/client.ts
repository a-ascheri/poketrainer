import axios from 'axios';
import { getToken } from '../auth/authStorage';

const backendBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.trim() || '';

export const backendClient = axios.create({
  baseURL: backendBaseUrl,
});

export const pokeApiClient = axios.create({
  baseURL: 'https://pokeapi.co/api/v2',
});

backendClient.interceptors.request.use((config) => {
  const token = getToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});
