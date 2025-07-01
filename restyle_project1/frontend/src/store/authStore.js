// frontend/src/store/authStore.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
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
      name: 'auth-storage', // name of the item in the storage (must be unique)
    }
  )
);

export default useAuthStore;