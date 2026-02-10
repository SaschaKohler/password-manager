export interface PasswordEntry {
  id: number;
  title: string;
  username_hint: string;
  url_hint: string;
  category: string;
  tags: string[];
  is_favorite: boolean;
  has_notes: boolean;
  created_at: string;
  updated_at: string;
  last_accessed: string | null;
}

export interface CreatePasswordData {
  title: string;
  username: string;
  password: string;
  url?: string;
  notes?: string;
  category?: string;
  tags?: string[];
  is_favorite?: boolean;
}

export interface UpdatePasswordData {
  title?: string;
  username?: string;
  password?: string;
  url?: string;
  notes?: string;
  category?: string;
  tags?: string[];
  is_favorite?: boolean;
}

export interface PasswordOptions {
  length: number;
  include_uppercase: boolean;
  include_lowercase: boolean;
  include_numbers: boolean;
  include_symbols: boolean;
  exclude_ambiguous: boolean;
}

export interface AuthUser {
  id: number;
  email: string;
  username: string;
  encryption_key: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}
