import type { PasswordEntry, CreatePasswordData, UpdatePasswordData, AuthUser } from '$lib/types/password';

const API_BASE_URL = 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(
    message: string, 
    public status: number,
    public fieldErrors?: Record<string, string[]>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class PasswordAPI {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      // Handle validation errors (400 status with field-specific errors)
      if (response.status === 400 && typeof errorData === 'object' && errorData !== null) {
        // Check if this is a validation error with field-specific messages
        const fieldErrors: Record<string, string[]> = {};
        let hasFieldErrors = false;
        
        for (const [field, messages] of Object.entries(errorData)) {
          if (Array.isArray(messages)) {
            fieldErrors[field] = messages;
            hasFieldErrors = true;
          }
        }
        
        if (hasFieldErrors) {
          throw new ApiError('Validation failed', response.status, fieldErrors);
        }
      }
      
      // Handle generic errors
      const message = errorData.error || errorData.message || `HTTP ${response.status}`;
      throw new ApiError(message, response.status);
    }

    return response.json();
  }

  // Authentication
  async login(email: string, password: string): Promise<{ token: string; user: AuthUser }> {
    return this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(userData: {
    email: string;
    username: string;
    password: string;
    master_password: string;
  }): Promise<{ token: string; user: AuthUser }> {
    const registerData = {
      ...userData,
      password_confirm: userData.password, // Add password confirmation
    };
    return this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(registerData),
    });
  }

  async logout(): Promise<void> {
    await this.request('/auth/logout/', { method: 'POST' });
    this.token = null;
  }

  async getCurrentUser(): Promise<AuthUser> {
    return this.request('/auth/me/');
  }

  // Password Management
  async getPasswords(params: {
    search?: string;
    category?: string;
    tags?: string[];
    is_favorite?: boolean;
    page?: number;
    page_size?: number;
  } = {}): Promise<{
    count: number;
    next: string | null;
    previous: string | null;
    results: PasswordEntry[];
  }> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, v));
        } else {
          searchParams.append(key, value.toString());
        }
      }
    });

    const query = searchParams.toString();
    return this.request(`/passwords/${query ? `?${query}` : ''}`);
  }

  async getPassword(id: number): Promise<PasswordEntry> {
    return this.request(`/passwords/${id}/`);
  }

  async createPassword(data: CreatePasswordData): Promise<PasswordEntry> {
    return this.request('/passwords/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePassword(id: number, data: UpdatePasswordData): Promise<PasswordEntry> {
    return this.request(`/passwords/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deletePassword(id: number): Promise<void> {
    await this.request(`/passwords/${id}/`, { method: 'DELETE' });
  }

  // Password Generation
  async generatePassword(options: {
    length: number;
    include_uppercase: boolean;
    include_lowercase: boolean;
    include_numbers: boolean;
    include_symbols: boolean;
    exclude_ambiguous: boolean;
  }): Promise<{ password: string; strength: number }> {
    return this.request('/passwords/generate/', {
      method: 'POST',
      body: JSON.stringify(options),
    });
  }

  async validatePassword(password: string): Promise<{
    is_valid: boolean;
    strength: number;
    suggestions: string[];
  }> {
    return this.request('/passwords/validate/', {
      method: 'POST',
      body: JSON.stringify({ password }),
    });
  }

  // Categories
  async getCategories(): Promise<string[]> {
    return this.request('/passwords/categories/');
  }

  // Bulk Operations
  async bulkDelete(passwordIds: number[]): Promise<{ deleted: number }> {
    return this.request('/passwords/bulk/', {
      method: 'POST',
      body: JSON.stringify({
        action: 'delete',
        password_ids: passwordIds,
      }),
    });
  }

  async bulkMove(passwordIds: number[], category: string): Promise<{ updated: number }> {
    return this.request('/passwords/bulk/', {
      method: 'POST',
      body: JSON.stringify({
        action: 'move',
        password_ids: passwordIds,
        category,
      }),
    });
  }

  async bulkAddTags(passwordIds: number[], tags: string[]): Promise<{ updated: number }> {
    return this.request('/passwords/bulk/', {
      method: 'POST',
      body: JSON.stringify({
        action: 'tag',
        password_ids: passwordIds,
        tags,
      }),
    });
  }

  // Security Audit
  async getSecurityAudit(): Promise<{
    total_passwords: number;
    weak_passwords: number;
    duplicate_passwords: number;
    old_passwords: number;
    shared_passwords: number;
    last_audit: string;
  }> {
    return this.request('/passwords/audit/');
  }

  // Import/Export
  async importPasswords(file: File, mergeStrategy: string = 'skip'): Promise<{
    imported: number;
    skipped: number;
    errors: string[];
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('merge_strategy', mergeStrategy);

    return this.request('/passwords/import/', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async exportPasswords(format: 'csv' | 'json' = 'csv'): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/passwords/export/?format=${format}`, {
      headers: this.token ? { Authorization: `Bearer ${this.token}` } : {},
    });

    if (!response.ok) {
      throw new ApiError('Export failed', response.status);
    }

    return response.blob();
  }
}

export const api = new PasswordAPI();
export default api;
