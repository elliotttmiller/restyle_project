import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  setToken: (token) => set({ token, isAuthenticated: !!token }),
  setTokens: (accessToken, refreshToken) => set({ 
    token: accessToken, 
    refreshToken: refreshToken, 
    isAuthenticated: !!accessToken 
  }),
  logout: () => set({ token: null, refreshToken: null, isAuthenticated: false }),
})); 