import type { PasswordOptions } from '$lib/types/password';

export class CryptoService {
  // Password generation
  static generatePassword(options: PasswordOptions): string {
    const {
      length,
      include_uppercase,
      include_lowercase,
      include_numbers,
      include_symbols,
      exclude_ambiguous
    } = options;

    let charset = '';
    
    if (include_lowercase) charset += 'abcdefghijklmnopqrstuvwxyz';
    if (include_uppercase) charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (include_numbers) charset += '0123456789';
    if (include_symbols) charset += '!@#$%^&*()_+-=[]{}|;:,.<>?';
    
    // Remove ambiguous characters if requested
    if (exclude_ambiguous) {
      const ambiguous = '0O1lI';
      charset = charset.split('').filter(char => !ambiguous.includes(char)).join('');
    }
    
    if (!charset) {
      throw new Error('At least one character type must be selected');
    }
    
    let password = '';
    const array = new Uint32Array(length);
    crypto.getRandomValues(array);
    
    for (let i = 0; i < length; i++) {
      password += charset[array[i] % charset.length];
    }
    
    return password;
  }

  // Password strength calculation
  static calculateStrength(password: string): number {
    let strength = 0;
    
    // Length bonus
    if (password.length >= 8) strength += 1;
    if (password.length >= 12) strength += 1;
    if (password.length >= 16) strength += 1;
    
    // Character variety bonus
    if (/[a-z]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
    
    // Complexity bonus
    if (password.length >= 20) strength += 1;
    if (/(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9])/.test(password)) strength += 1;
    
    return Math.min(strength, 5); // Max strength is 5
  }

  // Password validation
  static validatePassword(password: string): {
    is_valid: boolean;
    strength: number;
    suggestions: string[];
  } {
    const suggestions: string[] = [];
    let isValid = true;
    
    // Length checks
    if (password.length < 8) {
      suggestions.push('Password should be at least 8 characters long');
      isValid = false;
    }
    
    // Character variety checks
    if (!/[a-z]/.test(password)) {
      suggestions.push('Include lowercase letters');
      isValid = false;
    }
    
    if (!/[A-Z]/.test(password)) {
      suggestions.push('Include uppercase letters');
      isValid = false;
    }
    
    if (!/[0-9]/.test(password)) {
      suggestions.push('Include numbers');
      isValid = false;
    }
    
    if (!/[^a-zA-Z0-9]/.test(password)) {
      suggestions.push('Include special characters');
      isValid = false;
    }
    
    // Common patterns
    if (/(.)\1{2,}/.test(password)) {
      suggestions.push('Avoid repeating characters');
      isValid = false;
    }
    
    if (/123|abc|qwe/i.test(password)) {
      suggestions.push('Avoid common sequences');
      isValid = false;
    }
    
    const strength = this.calculateStrength(password);
    
    return {
      is_valid: isValid,
      strength,
      suggestions
    };
  }

  // Generate secure random bytes
  static generateRandomBytes(length: number): Uint8Array {
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    return array;
  }

  // Generate master key from password and salt
  static async deriveKey(password: string, salt: Uint8Array): Promise<CryptoKey> {
    const encoder = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(password),
      'PBKDF2',
      false,
      ['deriveBits', 'deriveKey']
    );
    
    return crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: salt.buffer,
        iterations: 100000,
        hash: 'SHA-256'
      },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      true,
      ['encrypt', 'decrypt']
    );
  }

  // Encrypt data
  static async encrypt(data: string, key: CryptoKey): Promise<{
    encrypted: Uint8Array;
    iv: Uint8Array;
  }> {
    const encoder = new TextEncoder();
    const iv = this.generateRandomBytes(12); // 96-bit IV for GCM
    
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv: iv.buffer },
      key,
      encoder.encode(data)
    );
    
    return {
      encrypted: new Uint8Array(encrypted),
      iv
    };
  }

  // Decrypt data
  static async decrypt(encrypted: Uint8Array, iv: Uint8Array, key: CryptoKey): Promise<string> {
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: iv.buffer },
      key,
      encrypted.buffer
    );
    
    const decoder = new TextDecoder();
    return decoder.decode(decrypted);
  }

  // Convert encrypted data to base64 for storage
  static arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  // Convert base64 to array buffer
  static base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }
}

export default CryptoService;
