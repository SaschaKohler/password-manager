<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { PasswordEntry } from '$lib/types/password';
  import { api } from '$lib/services/api';
  import { formatDistanceToNow } from 'date-fns';

  export let password: PasswordEntry | null = null;
  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let showPassword = false;
  let copySuccess = false;
  let copyTimeout: ReturnType<typeof setTimeout>;
  let decryptedPassword: string | null = null;
  let loading = false;
  let error: string | null = null;

  // Fetch decrypted password when modal opens
  $: if (isOpen && password) {
    fetchDecryptedPassword();
  }

  async function fetchDecryptedPassword() {
    loading = true;
    error = null;
    decryptedPassword = null;

    try {
      decryptedPassword = await api.getDecryptedPassword(password!.id);
    } catch (err: any) {
      error = err.message || 'Failed to decrypt password';
    } finally {
      loading = false;
    }
  }

  async function handleCopyPassword() {
    if (!decryptedPassword) return;

    try {
      await navigator.clipboard.writeText(decryptedPassword);
      copySuccess = true;
      
      // Track this access
      await api.trackPasswordAccess(password!.id);

      clearTimeout(copyTimeout);
      copyTimeout = setTimeout(() => {
        copySuccess = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy password:', err);
    }
  }

  async function handleCopyUsername() {
    if (!password?.username_hint) return;

    try {
      await navigator.clipboard.writeText(password.username_hint);
      await api.trackPasswordAccess(password!.id);
    } catch (err) {
      console.error('Failed to copy username:', err);
    }
  }

  async function handleCopyURL() {
    if (!password?.url_hint) return;

    try {
      await navigator.clipboard.writeText(password.url_hint);
      await api.trackPasswordAccess(password!.id);
    } catch (err) {
      console.error('Failed to copy URL:', err);
    }
  }

  function handleClose() {
    isOpen = false;
    showPassword = false;
    decryptedPassword = null;
    error = null;
    dispatch('close');
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      handleClose();
    }
  }

  function getStrengthColor(strength: number): string {
    if (strength >= 80) return 'text-success-600';
    if (strength >= 60) return 'text-warning-600';
    return 'text-danger-600';
  }

  function getStrengthText(strength: number): string {
    if (strength >= 80) return 'Strong';
    if (strength >= 60) return 'Medium';
    return 'Weak';
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen && password}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <span class="text-xl">🔐</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">{password.title}</h2>
              {#if password.category}
                <span class="text-sm text-gray-500">{password.category}</span>
              {/if}
            </div>
          </div>
          <button
            type="button"
            on:click={handleClose}
            class="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6 space-y-6">
        {#if error}
          <div class="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p class="text-danger-800 text-sm">{error}</p>
          </div>
        {:else if loading}
          <div class="flex flex-col items-center justify-center py-8 gap-4">
            <div class="w-8 h-8 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
            <p class="text-gray-600">Decrypting password...</p>
          </div>
        {:else}
          <!-- Username -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">Username / Email</label>
            <div class="flex items-center gap-2">
              <input
                type="text"
                readonly
                value={password.username_hint}
                class="form-input flex-1 bg-gray-50"
              />
              <button
                type="button"
                on:click={handleCopyUsername}
                class="btn btn-secondary"
                title="Copy username"
              >
                📋
              </button>
            </div>
          </div>

          <!-- Password -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">Password</label>
            <div class="flex items-center gap-2">
              <input
                type={showPassword ? 'text' : 'password'}
                readonly
                value={decryptedPassword || ''}
                class="form-input flex-1 bg-gray-50 font-mono"
              />
              <button
                type="button"
                on:click={() => showPassword = !showPassword}
                class="btn btn-secondary"
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
              <button
                type="button"
                on:click={handleCopyPassword}
                class="btn {copySuccess ? 'btn-success' : 'btn-primary'}"
                title="Copy password"
              >
                {copySuccess ? '✅' : '📋'}
              </button>
            </div>
            {#if copySuccess}
              <p class="text-sm text-success-600">Copied to clipboard!</p>
            {/if}
          </div>

          <!-- URL -->
          {#if password.url_hint}
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700">URL</label>
              <div class="flex items-center gap-2">
                <input
                  type="url"
                  readonly
                  value={password.url_hint}
                  class="form-input flex-1 bg-gray-50"
                />
                <button
                  type="button"
                  on:click={handleCopyURL}
                  class="btn btn-secondary"
                  title="Copy URL"
                >
                  📋
                </button>
              </div>
            </div>
          {/if}

          <!-- Notes -->
          {#if password.has_notes}
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700">Notes</label>
              <div class="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
                <p>Notes are stored securely. Click to view in edit mode.</p>
              </div>
            </div>
          {/if}

          <!-- Tags -->
          {#if password.tags.length > 0}
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700">Tags</label>
              <div class="flex flex-wrap gap-2">
                {#each password.tags as tag}
                  <span class="inline-flex items-center px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full">
                    {tag}
                  </span>
                {/each}
              </div>
            </div>
          {/if}

          <!-- Password Strength -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Password Strength</span>
              <span class="text-sm font-medium {getStrengthColor(85)}">Strong</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-success-500 h-2 rounded-full" style="width: 85%"></div>
            </div>
          </div>

          <!-- Timestamps -->
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-500">Created</span>
              <p class="font-medium text-gray-900">
                {new Date(password.created_at).toLocaleDateString()}
              </p>
            </div>
            <div>
              <span class="text-gray-500">Last Modified</span>
              <p class="font-medium text-gray-900">
                {new Date(password.updated_at).toLocaleDateString()}
              </p>
            </div>
            <div>
              <span class="text-gray-500">Last Accessed</span>
              <p class="font-medium text-gray-900">
                {password.last_accessed 
                  ? formatDistanceToNow(new Date(password.last_accessed), { addSuffix: true })
                  : 'Never'
                }
              </p>
            </div>
            {#if password.is_favorite}
              <div>
                <span class="text-gray-500">Status</span>
                <p class="font-medium text-warning-600">⭐ Favorite</p>
              </div>
            {/if}
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-200 flex justify-between items-center">
        <div class="text-xs text-gray-500">
          🔒 End-to-end encrypted
        </div>
        <div class="flex gap-3">
          <button
            type="button"
            on:click={handleClose}
            class="btn btn-secondary"
          >
            Close
          </button>
          <button
            type="button"
            on:click={() => dispatch('edit', password)}
            class="btn btn-primary"
          >
            ✏️ Edit
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .btn-success {
    background-color: #22c55e;
    color: white;
  }

  .btn-success:hover {
    background-color: #16a34a;
  }

  .font-mono {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
  }
</style>
