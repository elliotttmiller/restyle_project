import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isInitialized: false,
      setTokens: (accessToken, refreshToken) => set({ 
        token: accessToken, 
        refreshToken: refreshToken, 
        isAuthenticated: !!accessToken 
      }),
      logout: () => set({ 
        token: null, 
        refreshToken: null, 
        isAuthenticated: false 
      }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      onRehydrateStorage: (state) => {
        state.isInitialized = true;
      },
    }
  )
);

// This ensures the store tries to rehydrate as soon as the app loads.
useAuthStore.getState();