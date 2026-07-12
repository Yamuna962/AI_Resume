import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/axios';
import { getApiErrorMessage } from '@/lib/api-error';
import { useAuthStore } from '@/stores/auth.store';
import type { User } from '@/types';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest extends LoginRequest {
  full_name?: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export function useAuth() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setToken, setUser, logout: storeLogout } = useAuthStore();
  const router = useRouter();

  const login = async (data: LoginRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.post<LoginResponse>('/auth/login', data);
      setToken(response.data.access_token);
      setUser(response.data.user);

      router.push('/dashboard');
    } catch (error: unknown) {
      setError(getApiErrorMessage(error, 'An error occurred during login'));
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      await api.post('/auth/register', data);

      await login({ email: data.email, password: data.password });
    } catch (error: unknown) {
      setError(getApiErrorMessage(error, 'An error occurred during registration'));
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    storeLogout();
    router.push('/login');
  };

  return { login, register, logout, isLoading, error };
}
