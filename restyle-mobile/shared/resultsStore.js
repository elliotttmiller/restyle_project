// restyle-mobile/shared/resultsStore.js
import { create } from 'zustand';
import { analyzeImageApi } from './api';

const useResultsStore = create((set) => ({
  results: null,
  isLoading: false,
  error: null,
  startAnalysis: async (imageAsset) => {
    set({ isLoading: true, results: null, error: null });
    try {
      const responseData = await analyzeImageApi(imageAsset);
      set({ results: responseData, isLoading: false });
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || "An unknown server error occurred.";
      set({ error: errorMessage, isLoading: false });
    }
  },
  clearResults: () => set({ results: null, isLoading: false, error: null }),
}));

export default useResultsStore;