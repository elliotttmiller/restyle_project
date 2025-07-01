// File: frontend/src/store/authStore.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist( // <-- This is the key part that saves to localStorage
    (set) => ({
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      login: (tokens) => set({ 
        accessToken: tokens.access, 
        refreshToken: tokens.refresh,
        isAuthenticated: true 
      }),
      logout: () => set({ 
        accessToken: null, 
        refreshToken: null,
        isAuthenticated: false
      }),
    }),
    {
      name: 'auth-storage', // This is the key in localStorage
    }
  )
);

export default useAuthStore;