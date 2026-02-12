<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { api } from '$lib/services/api';
  import type { PasswordEntry, CreatePasswordData, UpdatePasswordData } from '$lib/types/password';

  export let password: PasswordEntry | null = null;
  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let formData: CreatePasswordData = {
    title: '',
    username: '',
    password: '',
    url: '',
    notes: '',
    category: '',
    tags: [],
    is_favorite: false
  };

  let loading = false;
  let error: string | null = null;
  let tagInput = '';
  let showPassword = false;
  let generatedPassword = '';
  let passwordStrength = 0;

  let categories: string[] = [];

  onMount(async () => {
    try {
      categories = await api.getCategories();
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  });

  $: isEdit = password !== null;
  $: formTitle = isEdit ? 'Edit Password' : 'Create Password';

  if (password) {
    formData = {
      title: password.title,
      username: '', // Not available in PasswordEntry
      password: '', // Never pre-fill password
      url: password.url_hint,
      notes: '',
      category: password.category,
      tags: password.tags,
      is_favorite: password.is_favorite
    };
  }

  async function generatePassword() {
    try {
      const result = await api.generatePassword({
        length: 16,
        include_uppercase: true,
        include_lowercase: true,
        include_numbers: true,
        include_symbols: true,
        exclude_ambiguous: false
      });
      
      generatedPassword = result.password;
      passwordStrength = result.strength;
      formData.password = generatedPassword;
    } catch (err) {
      error = 'Failed to generate password';
    }
  }

  async function checkPasswordStrength() {
    if (!formData.password) return;
    
    try {
      const result = await api.validatePassword(formData.password);
      passwordStrength = result.strength;
    } catch (err) {
      console.error('Failed to validate password:', err);
    }
  }

  function addTag() {
    if (tagInput.trim() && !formData.tags?.includes(tagInput.trim())) {
      formData.tags = [...(formData.tags || []), tagInput.trim()];
      tagInput = '';
    }
  }

  function removeTag(tagToRemove: string) {
    formData.tags = formData.tags?.filter(tag => tag !== tagToRemove) || [];
  }

  async function handleSubmit() {
    loading = true;
    error = null;

    try {
      if (isEdit && password) {
        const updateData: UpdatePasswordData = {
          title: formData.title,
          username: formData.username,
          url: formData.url,
          notes: formData.notes,
          category: formData.category,
          tags: formData.tags,
          is_favorite: formData.is_favorite
        };
        
        if (formData.password) {
          updateData.password = formData.password;
        }

        await api.updatePassword(password.id, updateData);
      } else {
        await api.createPassword(formData);
      }

      dispatch('success');
      handleClose();
    } catch (err: any) {
      error = err.message || 'Failed to save password';
    } finally {
      loading = false;
    }
  }

  function handleClose() {
    isOpen = false;
    error = null;
    tagInput = '';
    generatedPassword = '';
    passwordStrength = 0;
    
    if (!isEdit) {
      formData = {
        title: '',
        username: '',
        password: '',
        url: '',
        notes: '',
        category: '',
        tags: [],
        is_favorite: false
      };
    }
  }

  function getStrengthColor(strength: number) {
    if (strength >= 80) return 'text-success-600';
    if (strength >= 60) return 'text-warning-600';
    return 'text-danger-600';
  }

  function getStrengthText(strength: number) {
    if (strength >= 80) return 'Strong';
    if (strength >= 60) return 'Medium';
    return 'Weak';
  }
</script>

{#if isOpen}
  <div class="modal-backdrop">
    <div class="modal modal-lg">
    <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">{formTitle}</h2>
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

      <form on:submit|preventDefault={handleSubmit} class="p-6 space-y-6">
        {#if error}
          <div class="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p class="text-danger-800 text-sm">{error}</p>
          </div>
        {/if}

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-2">
            <label for="title" class="block text-sm font-medium text-gray-700">
              Title <span class="text-danger-500">*</span>
            </label>
            <input
              id="title"
              type="text"
              required
              class="form-input"
              bind:value={formData.title}
              placeholder="e.g., Gmail Account"
            />
          </div>

          <div class="space-y-2">
            <label for="username" class="block text-sm font-medium text-gray-700">
              Username/Email <span class="text-danger-500">*</span>
            </label>
            <input
              id="username"
              type="text"
              required
              class="form-input"
              bind:value={formData.username}
              placeholder="username@example.com"
            />
          </div>

          <div class="space-y-2">
            <label for="password" class="block text-sm font-medium text-gray-700">
              Password <span class="text-danger-500">*</span>
            </label>
            <div class="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                required={!isEdit}
                class="form-input pr-20"
                bind:value={formData.password}
                placeholder={isEdit ? 'Leave empty to keep current password' : 'Enter password'}
                on:input={checkPasswordStrength}
              />
              <div class="absolute inset-y-0 right-0 flex items-center pr-3 gap-2">
                {#if formData.password && passwordStrength > 0}
                  <span class="text-xs font-medium {getStrengthColor(passwordStrength)}">
                    {getStrengthText(passwordStrength)}
                  </span>
                {/if}
                <button
                  type="button"
                  on:click={() => showPassword = !showPassword}
                  class="text-gray-400 hover:text-gray-600"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {#if showPassword}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  {:else}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  {/if}
                </button>
              </div>
            </div>
            <button
              type="button"
              on:click={generatePassword}
              class="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              🔐 Generate Password
            </button>
          </div>

          <div class="space-y-2">
            <label for="url" class="block text-sm font-medium text-gray-700">
              URL
            </label>
            <input
              id="url"
              type="url"
              class="form-input"
              bind:value={formData.url}
              placeholder="https://example.com"
            />
          </div>

          <div class="space-y-2">
            <label for="category" class="block text-sm font-medium text-gray-700">
              Category
            </label>
            <select
              id="category"
              class="form-input"
              bind:value={formData.category}
            >
              <option value="">Select category</option>
              {#each categories as category}
                <option value={category}>{category}</option>
              {/each}
              <option value="Custom">+ Add Custom Category</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input
                type="checkbox"
                bind:checked={formData.is_favorite}
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              Mark as favorite
            </label>
          </div>
        </div>

        <div class="space-y-2">
          <label for="notes" class="block text-sm font-medium text-gray-700">
            Notes
          </label>
          <textarea
            id="notes"
            rows={3}
            class="form-input"
            bind:value={formData.notes}
            placeholder="Additional notes..."
          />
        </div>

        <div class="space-y-2">
          <label for="tags" class="block text-sm font-medium text-gray-700">
            Tags
          </label>
          <div class="flex gap-2">
            <input
              id="tags"
              type="text"
              class="form-input"
              bind:value={tagInput}
              placeholder="Add tag..."
              on:keypress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addTag();
                }
              }}
            />
            <button
              type="button"
              on:click={addTag}
              class="btn btn-secondary"
            >
              Add
            </button>
          </div>
          {#if formData.tags && formData.tags.length > 0}
            <div class="flex flex-wrap gap-2 mt-2">
              {#each formData.tags as tag}
                <span class="inline-flex items-center gap-1 px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full">
                  {tag}
                  <button
                    type="button"
                    on:click={() => removeTag(tag)}
                    class="text-primary-600 hover:text-primary-800"
                    aria-label={`Remove ${tag} tag`}
                  >
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </span>
              {/each}
            </div>
          {/if}
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            on:click={handleClose}
            class="btn btn-secondary"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            disabled={loading}
          >
            {#if loading}
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
            {/if}
            {isEdit ? 'Update Password' : 'Create Password'}
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
{/if}
