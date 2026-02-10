import { writable, derived } from 'svelte/store';
import type { PasswordEntry, CreatePasswordData, UpdatePasswordData } from '$lib/types/password';
import { api } from '$lib/services/api';

interface PasswordState {
  passwords: PasswordEntry[];
  loading: boolean;
  error: string | null;
  searchQuery: string;
  selectedCategory: string | null;
  selectedTags: string[];
  showFavoritesOnly: boolean;
  currentPage: number;
  totalPages: number;
  totalCount: number;
}

function createPasswordStore() {
  const { subscribe, set, update } = writable<PasswordState>({
    passwords: [],
    loading: false,
    error: null,
    searchQuery: '',
    selectedCategory: null,
    selectedTags: [],
    showFavoritesOnly: false,
    currentPage: 1,
    totalPages: 1,
    totalCount: 0,
  });

  // Derived store for filtered passwords
  const filteredPasswords = derived(
    { subscribe },
    ($state) => $state.passwords
  );

  // Derived store for categories
  const categories = derived(
    { subscribe },
    ($state) => {
      const cats = new Set($state.passwords.map(p => p.category).filter(Boolean));
      return Array.from(cats).sort();
    }
  );

  // Derived store for all tags
  const allTags = derived(
    { subscribe },
    ($state) => {
      const tags = new Set($state.passwords.flatMap(p => p.tags));
      return Array.from(tags).sort();
    }
  );

  return {
    subscribe,
    filteredPasswords,
    categories,
    allTags,

    // Load passwords
    async loadPasswords(params: {
      search?: string;
      category?: string;
      tags?: string[];
      is_favorite?: boolean;
      page?: number;
      page_size?: number;
    } = {}) {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const response = await api.getPasswords(params);
        
        update(state => ({
          ...state,
          passwords: response.results,
          totalCount: response.count,
          totalPages: Math.ceil(response.count / (params.page_size || 20)),
          currentPage: params.page || 1,
          loading: false,
          error: null,
        }));
        
        return response;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to load passwords';
        update(state => ({
          ...state,
          loading: false,
          error: errorMessage,
        }));
        
        throw error;
      }
    },

    // Create password
    async createPassword(data: CreatePasswordData) {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const newPassword = await api.createPassword(data);
        
        update(state => ({
          ...state,
          passwords: [newPassword, ...state.passwords],
          totalCount: state.totalCount + 1,
          loading: false,
          error: null,
        }));
        
        return newPassword;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to create password';
        update(state => ({
          ...state,
          loading: false,
          error: errorMessage,
        }));
        
        throw error;
      }
    },

    // Update password
    async updatePassword(id: number, data: UpdatePasswordData) {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const updatedPassword = await api.updatePassword(id, data);
        
        update(state => ({
          ...state,
          passwords: state.passwords.map(p => 
            p.id === id ? updatedPassword : p
          ),
          loading: false,
          error: null,
        }));
        
        return updatedPassword;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to update password';
        update(state => ({
          ...state,
          loading: false,
          error: errorMessage,
        }));
        
        throw error;
      }
    },

    // Delete password
    async deletePassword(id: number) {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        await api.deletePassword(id);
        
        update(state => ({
          ...state,
          passwords: state.passwords.filter(p => p.id !== id),
          totalCount: state.totalCount - 1,
          loading: false,
          error: null,
        }));
        
        return true;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to delete password';
        update(state => ({
          ...state,
          loading: false,
          error: errorMessage,
        }));
        
        throw error;
      }
    },

    // Bulk operations
    async bulkDelete(passwordIds: number[]) {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.bulkDelete(passwordIds);
        
        update(state => ({
          ...state,
          passwords: state.passwords.filter(p => !passwordIds.includes(p.id)),
          totalCount: state.totalCount - result.deleted,
          loading: false,
          error: null,
        }));
        
        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to delete passwords';
        update(state => ({
          ...state,
          loading: false,
          error: errorMessage,
        }));
        
        throw error;
      }
    },

    async bulkMove(passwordIds: number[], category: string) {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.bulkMove(passwordIds, category);
        
        update(state => ({
          ...state,
          passwords: state.passwords.map(p => 
            passwordIds.includes(p.id) ? { ...p, category } : p
          ),
          loading: false,
          error: null,
        }));
        
        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to move passwords';
        update(state => ({
          ...state,
          loading: false,
          error: errorMessage,
        }));
        
        throw error;
      }
    },

    async bulkAddTags(passwordIds: number[], tags: string[]) {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.bulkAddTags(passwordIds, tags);
        
        update(state => ({
          ...state,
          passwords: state.passwords.map(p => 
            passwordIds.includes(p.id) 
              ? { ...p, tags: [...new Set([...p.tags, ...tags])] }
              : p
          ),
          loading: false,
          error: null,
        }));
        
        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to add tags';
        update(state => ({
          ...state,
          loading: false,
          error: errorMessage,
        }));
        
        throw error;
      }
    },

    // Search and filter
    setSearchQuery(query: string) {
      update(state => ({ ...state, searchQuery: query }));
    },

    setSelectedCategory(category: string | null) {
      update(state => ({ ...state, selectedCategory: category }));
    },

    setSelectedTags(tags: string[]) {
      update(state => ({ ...state, selectedTags: tags }));
    },

    toggleFavoritesOnly() {
      update(state => ({ ...state, showFavoritesOnly: !state.showFavoritesOnly }));
    },

    // Pagination
    setCurrentPage(page: number) {
      update(state => ({ ...state, currentPage: page }));
    },

    // Clear error
    clearError() {
      update(state => ({ ...state, error: null }));
    },

    // Reset state
    reset() {
      set({
        passwords: [],
        loading: false,
        error: null,
        searchQuery: '',
        selectedCategory: null,
        selectedTags: [],
        showFavoritesOnly: false,
        currentPage: 1,
        totalPages: 1,
        totalCount: 0,
      });
    },
  };
}

export const passwords = createPasswordStore();
