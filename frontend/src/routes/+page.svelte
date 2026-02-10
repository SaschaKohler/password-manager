<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { passwords } from '$lib/stores/passwords';
  import PasswordCard from '$lib/components/PasswordCard.svelte';
  import type { PasswordEntry } from '$lib/types/password';

  let selectedPasswords: Set<number> = new Set();
  let showCreateModal = false;
  let showBulkActions = false;

  onMount(async () => {
    // Check authentication status
    await auth.checkAuth();
    
    // Load passwords if authenticated
    if ($auth.isAuthenticated) {
      await passwords.loadPasswords();
    }
  });

  $: showBulkActions = selectedPasswords.size > 0;

  async function handleCreatePassword(passwordData: any) {
    try {
      await passwords.createPassword(passwordData);
      showCreateModal = false;
    } catch (error) {
      console.error('Failed to create password:', error);
    }
  }

  async function handleEditPassword(password: PasswordEntry) {
    // TODO: Open edit modal
    console.log('Edit password:', password);
  }

  async function handleDeletePassword(password: PasswordEntry) {
    if (confirm(`Are you sure you want to delete "${password.title}"?`)) {
      try {
        await passwords.deletePassword(password.id);
      } catch (error) {
        console.error('Failed to delete password:', error);
      }
    }
  }

  async function handleToggleFavorite(password: PasswordEntry) {
    try {
      await passwords.updatePassword(password.id, {
        is_favorite: !password.is_favorite
      });
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  }

  function handleSelectPassword(password: PasswordEntry) {
    if (selectedPasswords.has(password.id)) {
      selectedPasswords.delete(password.id);
    } else {
      selectedPasswords.add(password.id);
    }
    selectedPasswords = new Set(selectedPasswords); // Trigger reactivity
  }

  function handleSelectAll() {
    if (selectedPasswords.size === $passwords.filteredPasswords.length) {
      selectedPasswords.clear();
    } else {
      selectedPasswords = new Set($passwords.filteredPasswords.map(p => p.id));
    }
    selectedPasswords = new Set(selectedPasswords); // Trigger reactivity
  }

  async function handleBulkDelete() {
    if (confirm(`Are you sure you want to delete ${selectedPasswords.size} passwords?`)) {
      try {
        await passwords.bulkDelete(Array.from(selectedPasswords));
        selectedPasswords.clear();
      } catch (error) {
        console.error('Failed to delete passwords:', error);
      }
    }
  }

  function handleLogout() {
    auth.logout();
  }
</script>

<main class="min-h-screen bg-gray-50">
  {#if $auth.loading}
    <div class="flex flex-col items-center justify-center min-h-screen gap-4">
      <div class="w-8 h-8 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
      <p class="text-gray-600">Loading...</p>
    </div>
  {:else if !$auth.isAuthenticated}
    <div class="flex flex-col items-center justify-center min-h-screen gap-6 text-center">
      <h1 class="text-5xl font-bold text-gray-900">Password Manager</h1>
      <p class="text-lg text-gray-600">Please log in to access your passwords.</p>
      <div class="flex gap-4">
        <a href="/login" class="btn btn-primary">Login</a>
        <a href="/register" class="btn btn-secondary">Register</a>
      </div>
    </div>
  {:else}
    <div class="min-h-screen flex flex-col">
      <header class="bg-white border-b border-gray-200 p-4 sticky top-0 z-100">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">🔐 Password Manager</h1>
          <div class="flex gap-3">
            <button class="btn btn-primary" on:click={() => showCreateModal = true}>
              ➕ Add Password
            </button>
            <button class="btn btn-secondary" on:click={handleLogout}>
              🚪 Logout
            </button>
          </div>
        </div>
      </header>

      <div class="flex-1 flex max-w-7xl mx-auto w-full">
        <aside class="w-72 bg-white border-r border-gray-200 p-6 h-screen sticky top-16 overflow-y-auto">
          <div class="mb-6">
            <input
              type="text"
              placeholder="Search passwords..."
              class="form-input"
              bind:value={$passwords.searchQuery}
            />
          </div>

          <div class="mb-6">
            <h3 class="text-base font-semibold text-gray-900 mb-4">Filters</h3>
            
            <div class="mb-4">
              <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  bind:checked={$passwords.showFavoritesOnly}
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                Favorites only
              </label>
            </div>

            {#if $passwords.categories.length > 0}
              <div class="mb-4">
                <h4 class="text-sm font-semibold text-gray-800 mb-2">Categories</h4>
                {#each $passwords.categories as category}
                  <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer mb-1">
                    <input
                      type="radio"
                      name="category"
                      value={category}
                      bind:group={$passwords.selectedCategory}
                      class="text-primary-600 focus:ring-primary-500"
                    />
                    {category}
                  </label>
                {/each}
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="radio"
                    name="category"
                    value=""
                    bind:group={$passwords.selectedCategory}
                    class="text-primary-600 focus:ring-primary-500"
                  />
                  All
                </label>
              </div>
            {/if}
          </div>

          {#if showBulkActions}
            <div class="bg-warning-50 border border-warning-200 rounded-lg p-4 mt-6">
              <h3 class="text-sm font-semibold text-warning-800 mb-2">Bulk Actions</h3>
              <p class="text-xs text-warning-700 mb-3">{selectedPasswords.size} selected</p>
              <button class="btn btn-danger text-sm" on:click={handleBulkDelete}>
                🗑️ Delete Selected
              </button>
            </div>
          {/if}
        </aside>

        <main class="flex-1 p-6 overflow-y-auto">
          <div class="mb-6">
            <div class="flex items-center gap-2">
              {#if selectedPasswords.size > 0}
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedPasswords.size === $passwords.filteredPasswords.length}
                    on:change={handleSelectAll}
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  {selectedPasswords.size} of {$passwords.filteredPasswords.length} selected
                </label>
              {:else}
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={false}
                    on:change={handleSelectAll}
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  {$passwords.totalCount} passwords
                </label>
              {/if}
            </div>
          </div>

          {#if $passwords.loading}
            <div class="flex flex-col items-center justify-center min-h-96 gap-4">
              <div class="w-8 h-8 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
              <p class="text-gray-600">Loading passwords...</p>
            </div>
          {:else if $passwords.error}
            <div class="flex flex-col items-center justify-center min-h-96 gap-4 text-center">
              <p class="text-danger-600 text-lg">❌ {$passwords.error}</p>
              <button class="btn btn-secondary" on:click={() => passwords.loadPasswords()}>
                🔄 Retry
              </button>
            </div>
          {:else if $passwords.filteredPasswords.length === 0}
            <div class="flex flex-col items-center justify-center min-h-96 gap-4 text-center">
              <h2 class="text-2xl font-semibold text-gray-600">No passwords found</h2>
              <p class="text-gray-500">Get started by adding your first password.</p>
              <button class="btn btn-primary" on:click={() => showCreateModal = true}>
                ➕ Add Password
              </button>
            </div>
          {:else}
            <div class="space-y-3">
              {#each $passwords.filteredPasswords as password (password.id)}
                <PasswordCard
                  {password}
                  selected={selectedPasswords.has(password.id)}
                  on:edit={handleEditPassword}
                  on:delete={handleDeletePassword}
                  on:toggleFavorite={handleToggleFavorite}
                  on:select={handleSelectPassword}
                />
              {/each}
            </div>
          {/if}
        </main>
      </div>
    </div>
  {/if}
</main>

