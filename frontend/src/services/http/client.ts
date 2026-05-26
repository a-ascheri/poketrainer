import axios from 'axios';
import { getToken } from '../auth/authStorage';

export const backendClient = axios.create({
  baseURL: 'http://localhost:8000',
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
