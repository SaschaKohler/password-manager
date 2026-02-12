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
  pageSize: number;
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
    pageSize: 20,
  });

  // Derived store for filtered passwords
  const filteredPasswords = derived(
    { subscribe },
    ($state) => {
      let filtered = $state.passwords;

      // Search filter
      if ($state.searchQuery) {
        const query = $state.searchQuery.toLowerCase();
        filtered = filtered.filter(password => 
          password.title.toLowerCase().includes(query) ||
          password.username_hint.toLowerCase().includes(query) ||
          password.url_hint.toLowerCase().includes(query) ||
          password.category.toLowerCase().includes(query) ||
          password.tags.some(tag => tag.toLowerCase().includes(query))
        );
      }

      // Category filter
      if ($state.selectedCategory) {
        filtered = filtered.filter(password => 
          password.category === $state.selectedCategory
        );
      }

      // Tags filter
      if ($state.selectedTags.length > 0) {
        filtered = filtered.filter(password => 
          $state.selectedTags.some(tag => password.tags.includes(tag))
        );
      }

      // Favorites filter
      if ($state.showFavoritesOnly) {
        filtered = filtered.filter(password => password.is_favorite);
      }

      return filtered;
    }
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
      let currentState: PasswordState | undefined;
      const unsubscribe = subscribe(state => { currentState = state; });
      unsubscribe();
      
      const pageSize = params.page_size ?? currentState?.pageSize ?? 20;
      const page = params.page ?? currentState?.currentPage ?? 1;
      
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const response = await api.getPasswords({
          ...params,
          page,
          page_size: pageSize,
        });
        
        update(state => ({
          ...state,
          passwords: response.results,
          totalCount: response.count,
          totalPages: Math.ceil(response.count / pageSize),
          currentPage: page,
          pageSize,
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

    setSelectedCategory(category: string) {
      update(state => ({ ...state, selectedCategory: category }));
    },

    setSelectedTags(tags: string[]) {
      update(state => ({ ...state, selectedTags: tags }));
    },

    setShowFavoritesOnly(show: boolean) {
      update(state => ({ ...state, showFavoritesOnly: show }));
    },

    toggleFavoritesOnly() {
      update(state => ({ ...state, showFavoritesOnly: !state.showFavoritesOnly }));
    },

    // Apply all filters
    applyFilters() {
      update(state => {
        const params: any = {};
        
        if (state.searchQuery) params.search = state.searchQuery;
        if (state.selectedCategory) params.category = state.selectedCategory;
        if (state.selectedTags.length > 0) params.tags = state.selectedTags;
        if (state.showFavoritesOnly) params.is_favorite = true;
        
        return state;
      });
    },

    // Clear all filters
    clearFilters() {
      update(state => ({
        ...state,
        searchQuery: '',
        selectedCategory: '',
        selectedTags: [],
        showFavoritesOnly: false,
      }));
    },

    // Pagination
    setCurrentPage(page: number) {
      update(state => ({ ...state, currentPage: page }));
    },

    setPageSize(size: number) {
      update(state => ({ ...state, pageSize: size, currentPage: 1 }));
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
        pageSize: 20,
      });
    },
  };
}

export const passwords = createPasswordStore();
export const { filteredPasswords, categories, allTags } = passwords;
