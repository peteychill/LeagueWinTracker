import axios from 'axios';
import { User } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Configure axios to include credentials
axios.defaults.withCredentials = true;

export const authService = {
  async login(username: string, password: string): Promise<User> {
    const response = await axios.post(`${API_BASE_URL}/auth/login/`, {
      username,
      password,
    });
    return response.data.user;
  },

  async register(username: string, email: string, password: string, passwordConfirm: string): Promise<User> {
    const response = await axios.post(`${API_BASE_URL}/auth/register/`, {
      username,
      email,
      password,
      password_confirm: passwordConfirm,
    });
    return response.data.user;
  },

  async logout(): Promise<void> {
    await axios.post(`${API_BASE_URL}/auth/logout/`);
  },

  async getCurrentUser(): Promise<User> {
    const response = await axios.get(`${API_BASE_URL}/profile/`);
    return response.data.user;
  },
}; 