import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isInitialized: false,
      setTokens: (accessToken, refreshToken) => {
        console.log('AuthStore: Setting tokens', { 
          hasAccess: !!accessToken, 
          hasRefresh: !!refreshToken 
        });
        set({ 
          token: accessToken, 
          refreshToken: refreshToken, 
          isAuthenticated: !!accessToken,
          isInitialized: true
        });
      },
      logout: () => {
        console.log('AuthStore: Logging out');
        set({ 
          token: null, 
          refreshToken: null, 
          isAuthenticated: false,
          isInitialized: true
        });
      },
      initialize: () => {
        console.log('AuthStore: Initializing');
        set({ isInitialized: true });
      }
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      onRehydrateStorage: () => (state) => {
        console.log('AuthStore: Rehydrating from storage', state);
        if (state) {
          state.isInitialized = true;
          // Check if we have a token and mark as authenticated
          if (state.token) {
            state.isAuthenticated = true;
          }
        }
      },
    }
  )
);

// Initialize the store
useAuthStore.getState().initialize();