import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  token: null,
  isAuthenticated: false,
  setToken: (token) => set({ token, isAuthenticated: !!token }),
  logout: () => set({ token: null, isAuthenticated: false }),
})); 