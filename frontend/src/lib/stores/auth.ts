import { writable, derived } from 'svelte/store';
import type { AuthState, AuthUser } from '$lib/types/password';
import { api } from '$lib/services/api';

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    loading: false,
    error: null,
  });

  // Derived store for authentication status
  const isAuthenticated = derived(
    { subscribe },
    ($state) => $state.isAuthenticated && $state.token !== null
  );

  // Derived store for user info
  const user = derived(
    { subscribe },
    ($state) => $state.user
  );

  return {
    subscribe,
    isAuthenticated,
    user,

    // Login action
    async login(email: string, password: string) {
      console.log('Auth store: Starting login process for', email);
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        console.log('Auth store: Calling API login');
        const response = await api.login(email, password);
        console.log('Auth store: API response received:', response);
        const { token, user } = response;
        
        // Store token in API service
        api.setToken(token);
        
        // Store token in localStorage (only on client side)
        if (typeof window !== 'undefined') {
          console.log('Auth store: Storing token in localStorage');
          localStorage.setItem('auth_token', token);
          console.log('Auth store: Token stored successfully');
        } else {
          console.log('Auth store: Window is undefined, not storing token');
        }
        
        // Update store
        const newState = {
          isAuthenticated: true,
          user,
          token,
          loading: false,
          error: null,
        };
        
        console.log('Auth store: Updating state to:', newState);
        set(newState);
        
        console.log('Auth store: Login process completed successfully');
        return { success: true, user };
      } catch (error) {
        console.error('Auth store: Login error:', error);
        const errorMessage = error instanceof Error ? error.message : 'Login failed';
        update(state => ({
          ...state,
          loading: false,
          error: errorMessage,
        }));
        
        return { success: false, error: errorMessage };
      }
    },

    // Register action
    async register(userData: {
      email: string;
      username: string;
      password: string;
      master_password: string;
    }) {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const response = await api.register(userData);
        const { token, user } = response;
        
        // Store token in API service
        api.setToken(token);
        
        // Store token in localStorage (only on client side)
        if (typeof window !== 'undefined') {
          localStorage.setItem('auth_token', token);
        }
        
        // Update store
        set({
          isAuthenticated: true,
          user,
          token,
          loading: false,
          error: null,
        });
        
        return { success: true, user };
      } catch (error) {
        let errorMessage = 'Registration failed';
        let fieldErrors: Record<string, string> | undefined;
        
        if (error instanceof Error) {
          errorMessage = error.message;
          
          // Check if this is an ApiError with field-specific errors
          if ('fieldErrors' in error && error.fieldErrors) {
            fieldErrors = {};
            // Convert string arrays to single strings for UI display
            for (const [field, messages] of Object.entries(error.fieldErrors as Record<string, string[]>)) {
              fieldErrors[field] = messages[0]; // Take first message for each field
            }
          }
        }
        
        update(state => ({
          ...state,
          loading: false,
          error: errorMessage,
        }));
        
        return { 
          success: false, 
          error: errorMessage,
          fieldErrors 
        };
      }
    },

    // Logout action
    async logout() {
      update(state => ({ ...state, loading: true }));
      
      try {
        await api.logout();
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        // Clear token from API service
        api.setToken('');
        
        // Remove token from localStorage (only on client side)
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        
        // Reset store
        set({
          isAuthenticated: false,
          user: null,
          token: null,
          loading: false,
          error: null,
        });
      }
    },

    // Check authentication status on app load
    async checkAuth() {
      // Only check on client side
      if (typeof window === 'undefined') {
        console.log('Auth store: Window is undefined, skipping checkAuth');
        return false;
      }
      
      console.log('Auth store: Checking authentication status');
      const token = localStorage.getItem('auth_token');
      console.log('Auth store: Token from localStorage:', token ? 'found' : 'not found');
      
      if (!token) {
        return false;
      }
      
      update(state => ({ ...state, loading: true }));
      
      try {
        // Set token in API service
        api.setToken(token);
        
        // Verify token with server
        const user = await api.getCurrentUser();
        
        set({
          isAuthenticated: true,
          user,
          token,
          loading: false,
          error: null,
        });
        
        return true;
      } catch (error) {
        // Token is invalid, clear it (only on client side)
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        api.setToken('');
        
        set({
          isAuthenticated: false,
          user: null,
          token: null,
          loading: false,
          error: null,
        });
        
        return false;
      }
    },

    // Clear error
    clearError() {
      update(state => ({ ...state, error: null }));
    },

    // Update user data
    updateUser(userData: Partial<AuthUser>) {
      update(state => ({
        ...state,
        user: state.user ? { ...state.user, ...userData } : null,
      }));
    },
  };
}

export const auth = createAuthStore();
