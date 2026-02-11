<script lang="ts">
  import { onMount } from 'svelte';
  import { onDestroy } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { passwords, filteredPasswords } from '$lib/stores/passwords';
  import { goto } from '$app/navigation';
  import PasswordCard from '$lib/components/PasswordCard.svelte';
  import PasswordForm from '$lib/components/PasswordForm.svelte';
  import ImportExport from '$lib/components/ImportExport.svelte';
  import ProfileSettings from '$lib/components/ProfileSettings.svelte';
  import PasswordViewModal from '$lib/components/PasswordViewModal.svelte';
  import SecurityDashboard from '$lib/components/SecurityDashboard.svelte';
  import PasswordHistory from '$lib/components/PasswordHistory.svelte';
  import FoldersManager from '$lib/components/FoldersManager.svelte';
  import AuditLogs from '$lib/components/AuditLogs.svelte';
  import SharePassword from '$lib/components/SharePassword.svelte';
  import type { PasswordEntry } from '$lib/types/password';

  let selectedPasswords: Set<number> = new Set();
  let showCreateModal = false;
  let showEditModal = false;
  let showImportExportModal = false;
  let showProfileModal = false;
  let showViewModal = false;
  let showSecurityModal = false;
  let showHistoryModal = false;
  let showFoldersModal = false;
  let showAuditLogsModal = false;
  let showShareModal = false;
  let showBulkActions = false;
  let editingPassword: PasswordEntry | null = null;
  let viewingPassword: PasswordEntry | null = null;
  let historyPassword: PasswordEntry | null = null;
  let sharingPassword: PasswordEntry | null = null;
  let mobileMenuOpen = false;

  // Theme support
  let theme: 'light' | 'dark' = 'light';

  onMount(async () => {
    // Wait for client-side hydration
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // Load theme
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    theme = savedTheme || (prefersDark ? 'dark' : 'light');
    applyTheme(theme);

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        theme = e.matches ? 'dark' : 'light';
        applyTheme(theme);
      }
    });
    
    // Check authentication status
    await auth.checkAuth();
    
    // Load passwords if authenticated
    if ($auth.isAuthenticated) {
      await passwords.loadPasswords();
    } else {
      goto('/login');
    }
  });

  function applyTheme(t: 'light' | 'dark') {
    if (t === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  function toggleTheme() {
    theme = theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    applyTheme(theme);
  }

  onDestroy(() => {
    passwords.reset();
  });

  // Watch for authentication changes
  $: if (!$auth.isAuthenticated && !$auth.loading) {
    goto('/login');
  }

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
    if (selectedPasswords.size === $filteredPasswords.length) {
      selectedPasswords.clear();
    } else {
      selectedPasswords = new Set($filteredPasswords.map(p => p.id));
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

  function handleViewPassword(password: PasswordEntry) {
    viewingPassword = password;
    showViewModal = true;
  }

  function handleViewHistory(password: PasswordEntry) {
    historyPassword = password;
    showHistoryModal = true;
  }

  function handleShare(password: PasswordEntry) {
    sharingPassword = password;
    showShareModal = true;
  }

  function handleLogout() {
    auth.logout();
  }

  function handleImportComplete(result: any) {
    passwords.loadPasswords();
  }

  function handleProfileUpdated() {
    // Profile updated successfully
  }

  function handlePasswordChanged() {
    // Password changed successfully
  }
</script>

<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</svelte:head>

<main class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
  {#if $auth.loading}
    <div class="flex flex-col items-center justify-center min-h-screen gap-4">
      <div class="w-8 h-8 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
      <p class="text-gray-600 dark:text-gray-400">Loading...</p>
    </div>
  {:else if !$auth.isAuthenticated}
    <div class="flex flex-col items-center justify-center min-h-screen gap-6 text-center">
      <h1 class="text-5xl font-bold text-gray-900 dark:text-white">🔐 Password Manager</h1>
      <p class="text-lg text-gray-600 dark:text-gray-400">Please log in to access your passwords.</p>
      <div class="flex gap-4">
        <a href="/login" class="btn btn-primary">Login</a>
        <a href="/register" class="btn btn-secondary">Register</a>
      </div>
    </div>
  {:else}
    <div class="min-h-screen flex flex-col">
      <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 sticky top-0 z-100 transition-colors duration-200">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
          <h1 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-white">🔐 Password Manager</h1>
          
          <!-- Desktop Navigation -->
          <div class="hidden md:flex gap-3 items-center">
            <!-- Theme Toggle -->
            <button
              type="button"
              class="btn btn-secondary"
              on:click={toggleTheme}
              aria-label="Toggle theme"
            >
              {#if theme === 'dark'}
                ☀️
              {:else}
                🌙
              {/if}
            </button>

            <button class="btn btn-secondary" on:click={() => showSecurityModal = true}>
              🛡️ Security
            </button>
            <button class="btn btn-secondary" on:click={() => showAuditLogsModal = true}>
              📋 Logs
            </button>
            <button class="btn btn-secondary" on:click={() => showFoldersModal = true}>
              📁 Folders
            </button>
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
          <div class="md:hidden border-t border-gray-200 dark:border-gray-700 mt-4 pt-4">
            <div class="flex flex-col gap-3">
              <button class="btn btn-secondary w-full" on:click={() => { showSecurityModal = true; mobileMenuOpen = false; }}>
                🛡️ Security
              </button>
              <button class="btn btn-secondary w-full" on:click={() => { showAuditLogsModal = true; mobileMenuOpen = false; }}>
                📋 Audit Logs
              </button>
              <button class="btn btn-secondary w-full" on:click={() => { showFoldersModal = true; mobileMenuOpen = false; }}>
                📁 Folders
              </button>
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

        <aside class="hidden md:block w-72 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-6 h-screen sticky top-16 overflow-y-auto transition-colors duration-200">
          <div class="mb-6">
            <input
              type="text"
              placeholder="Search passwords..."
              class="form-input dark:bg-gray-700 dark:text-white dark:border-gray-600"
              bind:value={$passwords.searchQuery}
            />
          </div>

          <div class="mb-6">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-4">Filters</h3>
            
            <div class="mb-4">
              <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  bind:checked={$passwords.showFavoritesOnly}
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600"
                />
                Favorites only
              </label>
            </div>

            {#if $passwords.categories && $passwords.categories.length > 0}
              <div class="mb-4">
                <h4 class="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">Categories</h4>
                {#each $passwords.categories as category}
                  <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer mb-1">
                    <input
                      type="radio"
                      name="category"
                      value={category}
                      bind:group={$passwords.selectedCategory}
                      class="text-primary-600 focus:ring-primary-500 dark:border-gray-600"
                    />
                    {category}
                  </label>
                {/each}
                <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                  <input
                    type="radio"
                    name="category"
                    value=""
                    bind:group={$passwords.selectedCategory}
                    class="text-primary-600 focus:ring-primary-500 dark:border-gray-600"
                  />
                  All
                </label>
              </div>
            {/if}
          </div>

          {#if showBulkActions}
            <div class="bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800 rounded-lg p-4 mt-6">
              <h3 class="text-sm font-semibold text-warning-800 dark:text-warning-200 mb-2">Bulk Actions</h3>
              <p class="text-xs text-warning-700 dark:text-warning-300 mb-3">{selectedPasswords.size} selected</p>
              <button class="btn btn-danger text-sm" on:click={handleBulkDelete}>
                🗑️ Delete Selected
              </button>
            </div>
          {/if}
        </aside>

        <!-- Mobile Filters Panel -->
        {#if mobileMenuOpen}
          <div class="md:hidden fixed inset-0 bg-black bg-opacity-50 z-30 flex" on:click={() => mobileMenuOpen = false}>
            <div class="w-80 bg-white dark:bg-gray-800 h-full overflow-y-auto" on:click|stopPropagation>
              <div class="p-6">
                <div class="flex items-center justify-between mb-6">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Filters</h3>
                  <button 
                    on:click={() => mobileMenuOpen = false}
                    class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
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
                    class="form-input dark:bg-gray-700 dark:text-white dark:border-gray-600"
                    bind:value={$passwords.searchQuery}
                  />
                </div>

                <div class="mb-6">
                  <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                    <input
                      type="checkbox"
                      bind:checked={$passwords.showFavoritesOnly}
                      class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600"
                    />
                    Favorites only
                  </label>
                </div>

                {#if $passwords.categories && $passwords.categories.length > 0}
                  <div class="mb-6">
                    <h4 class="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">Categories</h4>
                    {#each $passwords.categories as category}
                      <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer mb-1">
                        <input
                          type="radio"
                          name="mobile-category"
                          value={category}
                          bind:group={$passwords.selectedCategory}
                          class="text-primary-600 focus:ring-primary-500 dark:border-gray-600"
                        />
                        {category}
                      </label>
                    {/each}
                    <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                      <input
                        type="radio"
                        name="mobile-category"
                        value=""
                        bind:group={$passwords.selectedCategory}
                        class="text-primary-600 focus:ring-primary-500 dark:border-gray-600"
                      />
                      All
                    </label>
                  </div>
                {/if}

                {#if showBulkActions}
                  <div class="bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800 rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-warning-800 dark:text-warning-200 mb-2">Bulk Actions</h3>
                    <p class="text-xs text-warning-700 dark:text-warning-300 mb-3">{selectedPasswords.size} selected</p>
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
                <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedPasswords.size === $filteredPasswords.length}
                    on:change={handleSelectAll}
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600"
                  />
                  {selectedPasswords.size} of {$filteredPasswords.length} selected
                </label>
              {:else}
                <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={false}
                    on:change={handleSelectAll}
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600"
                  />
                  {$passwords.totalCount} passwords
                </label>
              {/if}
            </div>
          </div>

          {#if $passwords.loading}
            <div class="flex flex-col items-center justify-center min-h-96 gap-4">
              <div class="w-8 h-8 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
              <p class="text-gray-600 dark:text-gray-400">Loading passwords...</p>
            </div>
          {:else if $passwords.error}
            <div class="flex flex-col items-center justify-center min-h-96 gap-4 text-center">
              <p class="text-danger-600 dark:text-danger-400 text-lg">❌ {$passwords.error}</p>
              <button class="btn btn-secondary" on:click={() => passwords.loadPasswords()}>
                🔄 Retry
              </button>
            </div>
          {:else if $filteredPasswords.length === 0}
            <div class="flex flex-col items-center justify-center min-h-96 gap-4 text-center">
              <h2 class="text-2xl font-semibold text-gray-600 dark:text-gray-400">No passwords found</h2>
              <p class="text-gray-500 dark:text-gray-500">Get started by adding your first password.</p>
              <button class="btn btn-primary" on:click={() => showCreateModal = true}>
                ➕ Add Password
              </button>
            </div>
          {:else}
            <div class="space-y-2 md:space-y-3">
              {#each $filteredPasswords as password (password.id)}
                <PasswordCard
                  {password}
                  selected={selectedPasswords.has(password.id)}
                  on:edit={handleEditPassword}
                  on:delete={handleDeletePassword}
                  on:toggleFavorite={handleToggleFavorite}
                  on:select={handleSelectPassword}
                  on:view={() => handleViewPassword(password)}
                  on:history={() => handleViewHistory(password)}
                  on:share={() => handleShare(password)}
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

<!-- Password View Modal -->
<PasswordViewModal
  password={viewingPassword}
  isOpen={showViewModal}
  on:close={() => { showViewModal = false; viewingPassword = null; }}
  on:edit={(e) => { handleEditPassword(e.detail); showViewModal = false; viewingPassword = null; }}
/>

<!-- Password History Modal -->
<PasswordHistory
  password={historyPassword}
  isOpen={showHistoryModal}
  on:close={() => { showHistoryModal = false; historyPassword = null; }}
/>

<!-- Security Dashboard Modal -->
<SecurityDashboard
  isOpen={showSecurityModal}
  on:close={() => showSecurityModal = false}
/>

<!-- Audit Logs Modal -->
<AuditLogs
  isOpen={showAuditLogsModal}
  on:close={() => showAuditLogsModal = false}
/>

<!-- Folders Manager Modal -->
<FoldersManager
  isOpen={showFoldersModal}
  {passwords}
  on:close={() => { showFoldersModal = false; }}
  on:select={(e) => { passwords.setSelectedCategory(e.detail); showFoldersModal = false; }}
/>

<!-- Share Password Modal -->
<SharePassword
  password={sharingPassword}
  isOpen={showShareModal}
  on:close={() => { showShareModal = false; sharingPassword = null; }}
  on:shared={() => { /* Refresh shared data */ }}
  on:revoked={() => { /* Refresh shared data */ }}
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

<style>
  :global(.dark) {
    color-scheme: dark;
  }

  :global(.dark body) {
    background-color: #111827;
    color: #f9fafb;
  }
</style>
