<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { passwords } from '$lib/stores/passwords';
  import PasswordCard from '$lib/components/PasswordCard.svelte';
  import PasswordForm from '$lib/components/PasswordForm.svelte';
  import ImportExport from '$lib/components/ImportExport.svelte';
  import ProfileSettings from '$lib/components/ProfileSettings.svelte';
  import type { PasswordEntry } from '$lib/types/password';

  let selectedPasswords: Set<number> = new Set();
  let showCreateModal = false;
  let showEditModal = false;
  let showImportExportModal = false;
  let showProfileModal = false;
  let showBulkActions = false;
  let editingPassword: PasswordEntry | null = null;
  let mobileMenuOpen = false;

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
    editingPassword = password;
    showEditModal = true;
  }

  async function handleUpdatePassword(passwordData: any) {
    try {
      if (editingPassword) {
        await passwords.updatePassword(editingPassword.id, passwordData);
        showEditModal = false;
        editingPassword = null;
      }
    } catch (error) {
      console.error('Failed to update password:', error);
    }
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

  function handleImportComplete(result: any) {
    // Reload passwords after import
    passwords.loadPasswords();
  }

  function handleProfileUpdated() {
    // Profile updated successfully
  }

  function handlePasswordChanged() {
    // Password changed successfully
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
          <h1 class="text-xl md:text-2xl font-bold text-gray-900">🔐 Password Manager</h1>
          
          <!-- Desktop Navigation -->
          <div class="hidden md:flex gap-3">
            <button class="btn btn-secondary" on:click={() => showImportExportModal = true}>
              📁 Import/Export
            </button>
            <button class="btn btn-secondary" on:click={() => showProfileModal = true}>
              👤 Profile
            </button>
            <button class="btn btn-primary" on:click={() => showCreateModal = true}>
              ➕ Add Password
            </button>
            <button class="btn btn-secondary" on:click={handleLogout}>
              🚪 Logout
            </button>
          </div>

          <!-- Mobile Menu Button -->
          <button 
            class="md:hidden btn btn-secondary" 
            on:click={() => mobileMenuOpen = !mobileMenuOpen}
            aria-label="Toggle menu"
          >
            {#if mobileMenuOpen}
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            {:else}
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            {/if}
          </button>
        </div>

        <!-- Mobile Menu -->
        {#if mobileMenuOpen}
          <div class="md:hidden border-t border-gray-200 mt-4 pt-4">
            <div class="flex flex-col gap-3">
              <button class="btn btn-secondary w-full" on:click={() => { showImportExportModal = true; mobileMenuOpen = false; }}>
                📁 Import/Export
              </button>
              <button class="btn btn-secondary w-full" on:click={() => { showProfileModal = true; mobileMenuOpen = false; }}>
                👤 Profile
              </button>
              <button class="btn btn-primary w-full" on:click={() => { showCreateModal = true; mobileMenuOpen = false; }}>
                ➕ Add Password
              </button>
              <button class="btn btn-secondary w-full" on:click={handleLogout}>
                🚪 Logout
              </button>
            </div>
          </div>
        {/if}
      </header>

      <div class="flex-1 flex max-w-7xl mx-auto w-full">
        <!-- Mobile Filter Toggle -->
        <button 
          class="md:hidden fixed bottom-4 right-4 z-40 bg-primary-600 text-white rounded-full p-3 shadow-lg"
          on:click={() => mobileMenuOpen = !mobileMenuOpen}
          aria-label="Toggle filters"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
        </button>

        <aside class="hidden md:block w-72 bg-white border-r border-gray-200 p-6 h-screen sticky top-16 overflow-y-auto">
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

        <!-- Mobile Filters Panel -->
        {#if mobileMenuOpen}
          <div class="md:hidden fixed inset-0 bg-black bg-opacity-50 z-30 flex" on:click={() => mobileMenuOpen = false}>
            <div class="w-80 bg-white h-full overflow-y-auto" on:click|stopPropagation>
              <div class="p-6">
                <div class="flex items-center justify-between mb-6">
                  <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
                  <button 
                    on:click={() => mobileMenuOpen = false}
                    class="text-gray-400 hover:text-gray-600"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div class="mb-6">
                  <input
                    type="text"
                    placeholder="Search passwords..."
                    class="form-input"
                    bind:value={$passwords.searchQuery}
                  />
                </div>

                <div class="mb-6">
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
                  <div class="mb-6">
                    <h4 class="text-sm font-semibold text-gray-800 mb-2">Categories</h4>
                    {#each $passwords.categories as category}
                      <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer mb-1">
                        <input
                          type="radio"
                          name="mobile-category"
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
                        name="mobile-category"
                        value=""
                        bind:group={$passwords.selectedCategory}
                        class="text-primary-600 focus:ring-primary-500"
                      />
                      All
                    </label>
                  </div>
                {/if}

                {#if showBulkActions}
                  <div class="bg-warning-50 border border-warning-200 rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-warning-800 mb-2">Bulk Actions</h3>
                    <p class="text-xs text-warning-700 mb-3">{selectedPasswords.size} selected</p>
                    <button class="btn btn-danger text-sm w-full" on:click={handleBulkDelete}>
                      🗑️ Delete Selected
                    </button>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        {/if}

        <main class="flex-1 p-4 md:p-6 overflow-y-auto">
          <div class="mb-4 md:mb-6">
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
            <div class="space-y-2 md:space-y-3">
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

<!-- Password Form Modal -->
<PasswordForm 
  isOpen={showCreateModal} 
  on:success={handleCreatePassword}
/>

<PasswordForm 
  isOpen={showEditModal} 
  password={editingPassword}
  on:success={handleUpdatePassword}
/>

<!-- Import/Export Modal -->
<ImportExport 
  isOpen={showImportExportModal}
  on:import-complete={handleImportComplete}
/>

<!-- Profile Settings Modal -->
<ProfileSettings 
  isOpen={showProfileModal}
  on:profile-updated={handleProfileUpdated}
  on:password-changed={handlePasswordChanged}
/>

