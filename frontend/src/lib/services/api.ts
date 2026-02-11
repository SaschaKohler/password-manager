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

  // Get decrypted password
  async getDecryptedPassword(id: number): Promise<string> {
    return this.request(`/passwords/${id}/decrypt/`);
  }

  // Track password access
  async trackPasswordAccess(id: number): Promise<void> {
    await this.request(`/passwords/${id}/access/`, { method: 'POST' });
  }

  // Password History
  async getPasswordHistory(id: number): Promise<{
    id: number;
    password_id: number;
    action: string;
    timestamp: string;
    details: Record<string, any>;
  }[]> {
    return this.request(`/passwords/${id}/history/`);
  }

  // Security Audit
  async getSecurityAudit(): Promise<{
    total_passwords: number;
    weak_passwords: number;
    duplicate_passwords: number;
    old_passwords: number;
    shared_passwords: number;
    breached_passwords: number;
    last_audit: string;
  }> {
    return this.request('/passwords/audit/');
  }

  // Get folders
  async getFolders(): Promise<{
    id: number;
    name: string;
    icon: string;
    color: string;
    password_count: number;
    created_at: string;
    updated_at: string;
  }[]> {
    return this.request('/folders/');
  }

  // Create folder
  async createFolder(data: {
    name: string;
    icon?: string;
    color?: string;
    parent_id?: number;
  }): Promise<{
    id: number;
    name: string;
    icon: string;
    color: string;
  }> {
    return this.request('/folders/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Move password to folder
  async moveToFolder(passwordId: number, folderId: number): Promise<void> {
    await this.request(`/passwords/${passwordId}/move/`, {
      method: 'POST',
      body: JSON.stringify({ folder_id: folderId }),
    });
  }

  // Get audit logs
  async getAuditLogs(params: {
    page?: number;
    page_size?: number;
    action?: string;
    password_id?: number;
  } = {}): Promise<{
    count: number;
    results: {
      id: number;
      user_id: number;
      username: string;
      action: string;
      password_id: number;
      password_title: string;
      details: Record<string, any>;
      ip_address: string;
      user_agent: string;
      timestamp: string;
    }[];
  }> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });

    const query = searchParams.toString();
    return this.request(`/audit/${query ? `?${query}` : ''}`);
  }

  // Enable 2FA
  async enable2FA(): Promise<{
    secret: string;
    qr_code: string;
    backup_codes: string[];
  }> {
    return this.request('/auth/2fa/enable/', { method: 'POST' });
  }

  // Verify 2FA setup
  async verify2FASetup(token: string): Promise<void> {
    await this.request('/auth/2fa/verify/', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  }

  // Disable 2FA
  async disable2FA(token: string): Promise<void> {
    await this.request('/auth/2fa/disable/', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  }

  // Check if 2FA is enabled
  async get2FAStatus(): Promise<{
    enabled: boolean;
    method: string | null;
  }> {
    return this.request('/auth/2fa/status/');
  }

  // Share password
  async sharePassword(data: {
    password_id: number;
    user_id: number;
    permission: 'view' | 'edit';
    expires_at?: string;
  }): Promise<{
    id: number;
    shared_with: number;
    permission: string;
    expires_at: string | null;
  }> {
    return this.request('/sharing/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Get shared passwords
  async getSharedPasswords(): Promise<{
    shared_with_me: {
      id: number;
      password_id: number;
      password_title: string;
      shared_by: number;
      shared_by_username: string;
      permission: string;
      shared_at: string;
    }[];
    shared_by_me: {
      id: number;
      password_id: number;
      password_title: string;
      shared_with: number;
      shared_with_username: string;
      permission: string;
      shared_at: string;
    }[];
  }> {
    return this.request('/sharing/');
  }

  // Revoke sharing
  async revokeSharing(shareId: number): Promise<void> {
    await this.request(`/sharing/${shareId}/`, { method: 'DELETE' });
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
