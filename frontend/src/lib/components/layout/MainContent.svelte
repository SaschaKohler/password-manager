<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { passwords, filteredPasswords } from '$lib/stores/passwords';
  import PasswordCard from '$lib/components/PasswordCard.svelte';
  import type { PasswordEntry } from '$lib/types/password';

  export let selectedPasswords: Set<number> = new Set();
  export let showBulkActions = false;

  const dispatch = createEventDispatcher<{
    edit: PasswordEntry;
    delete: PasswordEntry;
    toggleFavorite: PasswordEntry;
    select: PasswordEntry;
    view: PasswordEntry;
    history: PasswordEntry;
    share: PasswordEntry;
    selectAll: void;
    bulkDelete: void;
    showCreateModal: void;
  }>();

  function handleSelectAll() {
    dispatch('selectAll');
  }

  function handleBulkDelete() {
    dispatch('bulkDelete');
  }

  function handleShowCreateModal() {
    dispatch('showCreateModal');
  }
</script>

<main class="main-content">
  <!-- Stats Cards -->
  <section class="stats-section">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon-primary">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 1.79 4 4 4h12c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h12c2.21 0 4 1.79 4 4M4 7v10c0 2.21 1.79 4 4 4h12c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h12c2.21 0 4 1.79 4 4" />
          </svg>
        </div>
        <div class="stat-content">
          <p class="stat-label">Total</p>
          <p class="stat-value">{$passwords.totalCount}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-warning">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 2.008 0a2.5 2.5 0 01-2.448 2.527 6.757 6.757 0 01-1.189 2.03 12.942 12.942 0 01-6.915 3.839c-.375-.766-.642-1.64-.642-2.606 0-3.236 2.615-5.85 5.85-5.85 1.348 0 2.505.445 3.51 1.204z" />
          </svg>
        </div>
        <div class="stat-content">
          <p class="stat-label">Favorites</p>
          <p class="stat-value">{$filteredPasswords.filter(p => p.is_favorite).length}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-info">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l2 2c.39.391.586.902.586 1.414v5c0 .512-.195 1.024-.586 1.414l-2 2c-.39.391-.586.902-.586 1.414v3a2 2 0 01-2 2H7a2 2 0 01-2-2v-3c0-.512.195-1.024.586-1.414l2-2c.39-.391.586-.902.586-1.414z" />
          </svg>
        </div>
        <div class="stat-content">
          <p class="stat-label">Categories</p>
          <p class="stat-value">{$passwords.categories?.length ?? 0}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-success">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a2 2 0 002-2h-2a2 2 0 00-2 2H9a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2V9a2 2 0 00-2-2h-2a2 2 0 00-2 2v-6a2 2 0 002-2h2a2 2 0 002 2v6z" />
          </svg>
        </div>
        <div class="stat-content">
          <p class="stat-label">Selected</p>
          <p class="stat-value">{selectedPasswords.size}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Quick Actions -->
  <section class="quick-actions">
    <div class="quick-actions-header">
      <h2 class="section-title">Quick Actions</h2>
      <button
        type="button"
        class="btn btn-primary"
        on:click={handleShowCreateModal}
      >
        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Password
      </button>
    </div>
  </section>

  <!-- Password List Header -->
  <section class="list-header">
    <div class="list-header-left">
      <label class="checkbox-wrapper">
        <input
          type="checkbox"
          checked={selectedPasswords.size > 0 && selectedPasswords.size === $filteredPasswords.length}
          on:change={handleSelectAll}
          class="checkbox"
        />
        <span class="checkbox-label">
          {#if selectedPasswords.size > 0}
            {selectedPasswords.size} of {$filteredPasswords.length} selected
          {:else}
            {$passwords.totalCount} passwords
          {/if}
        </span>
      </label>
    </div>
    <div class="list-header-right">
      <button
        type="button"
        class="btn btn-secondary btn-sm"
        on:click={handleShowCreateModal}
      >
        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1v16a1 1 0 01-1 1H3a1 1 0 01-1-1V4a1 1 0 011-1h18a1 1 0 011 1v16a1 1 0 01-1 1H3a1 1 0 01-1-1V4z" />
        </svg>
        View Options
      </button>
    </div>
  </section>

  <!-- Bulk Actions -->
  {#if showBulkActions}
    <section class="bulk-actions">
      <div class="bulk-actions-content">
        <div class="bulk-actions-info">
          <svg class="bulk-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 3.161-2.719a6.002 6.002 0 01-2.455-2.455 4.001 4.001 0 01-3.831-2.165 6.515-6.515 1.163-2.324 1.064-2.57 1.541-3.977 1.083-2.591 1.541-4.829 1.083-3.42 1.541-5.196 1.083-5.637 1.541-5.468 2.317-4.951 1.562-4.237 1.541-3.451 1.541-5.468-2.317-4.951-1.562-4.237-1.541-3.451m0 3.161c1.72 0 3.112-1.667 3.161-2.719a6.002 6.002 0 01-2.455-2.455 4.001 4.001 0 01-3.831-2.165 6.515-6.515 1.163-2.324 1.064-2.57 1.541-3.977 1.083-2.591 1.541-4.829 1.083-3.42 1.541-5.196 1.083-5.637 1.541-5.468 2.317-4.951 1.562-4.237 1.541-3.451 1.541-5.468-2.317-4.951-1.562-4.237-1.541-3.451" />
          </svg>
          <div class="bulk-actions-text">
            <p class="bulk-actions-title">{selectedPasswords.size} selected</p>
            <p class="bulk-actions-subtitle">Choose an action</p>
          </div>
        </div>
        <button
          type="button"
          class="btn btn-danger"
          on:click={handleBulkDelete}
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6M4 7v6a1 1 0 001 1h14a1 1 0 001-1V7a1 1 0 00-1-1H4a1 1 0 00-1 1v6a1 1 0 001 1h14a1 1 0 001-1V7a1 1 0 00-1-1H4z" />
          </svg>
          Delete Selected
        </button>
      </div>
    </section>
  {/if}

  <!-- Password List -->
  <section class="password-list">
    {#if $passwords.loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p class="loading-text">Loading passwords...</p>
      </div>
    {:else if $passwords.error}
      <div class="error-state">
        <svg class="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 3.161-2.719a6.002 6.002 0 01-2.455-2.455 4.001 4.001 0 01-3.831-2.165 6.515-6.515 1.163-2.324 1.064-2.57 1.541-3.977 1.083-2.591 1.541-4.829 1.083-3.42 1.541-5.196 1.083-5.637 1.541-5.468 2.317-4.951 1.562-4.237 1.541-3.451 1.541-5.468-2.317-4.951-1.562-4.237-1.541-3.451m0 3.161c1.72 0 3.112-1.667 3.161-2.719a6.002 6.002 0 01-2.455-2.455 4.001 4.001 0 01-3.831-2.165 6.515-6.515 1.163-2.324 1.064-2.57 1.541-3.977 1.083-2.591 1.541-4.829 1.083-3.42 1.541-5.196 1.083-5.637 1.541-5.468 2.317-4.951 1.562-4.237 1.541-3.451 1.541-5.468-2.317-4.951-1.562-4.237-1.541-3.451" />
        </svg>
        <p class="error-text">{$passwords.error}</p>
        <button
          type="button"
          class="btn btn-secondary"
          on:click={() => passwords.loadPasswords()}
        >
          Retry
        </button>
      </div>
    {:else if $filteredPasswords.length === 0}
      <div class="empty-state">
        <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 1.79 4 4 4h12c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h12c2.21 0 4 1.79 4 4M4 7v10c0 2.21 1.79 4 4 4h12c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h12c2.21 0 4 1.79 4 4" />
        </svg>
        <h3 class="empty-title">No passwords found</h3>
        <p class="empty-text">Get started by adding your first password.</p>
        <button
          type="button"
          class="btn btn-primary"
          on:click={handleShowCreateModal}
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Password
        </button>
      </div>
    {:else}
      <div class="password-grid">
        {#each $filteredPasswords as password (password.id)}
          <PasswordCard
            {password}
            selected={selectedPasswords.has(password.id)}
            on:edit={(e) => dispatch('edit', e.detail)}
            on:delete={(e) => dispatch('delete', e.detail)}
            on:toggleFavorite={(e) => dispatch('toggleFavorite', e.detail)}
            on:select={(e) => dispatch('select', e.detail)}
            on:view={(e) => dispatch('view', e.detail)}
            on:history={(e) => dispatch('history', e.detail)}
            on:share={(e) => dispatch('share', e.detail)}
          />
        {/each}
      </div>
    {/if}
  </section>
</main>

<style>
  .main-content {
    flex: 1;
    padding: var(--space-4) var(--space-6);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
  }

  /* Stats Section */
  .stats-section {
    margin-bottom: var(--space-6);
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  @media (min-width: 640px) {
    .stats-grid {
      grid-template-columns: repeat(4, 1fr);
    }
  }

  .stat-card {
    background-color: var(--bg-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-xl);
    padding: var(--space-4);
    display: flex;
    align-items: center;
    gap: var(--space-3);
    transition: all var(--transition-base) var(--transition-timing-default);
  }

  .stat-card:hover {
    border-color: var(--primary-300);
    box-shadow: var(--shadow-md);
  }

  .dark .stat-card:hover {
    border-color: var(--primary-600);
  }

  .stat-icon {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .stat-icon-primary {
    background-color: var(--primary-100);
    color: var(--primary-700);
  }

  .dark .stat-icon-primary {
    background-color: var(--primary-900);
    color: var(--primary-300);
  }

  .stat-icon-warning {
    background-color: var(--warning-100);
    color: var(--warning-700);
  }

  .dark .stat-icon-warning {
    background-color: var(--warning-900);
    color: var(--warning-300);
  }

  .stat-icon-info {
    background-color: var(--info-100);
    color: var(--info-700);
  }

  .dark .stat-icon-info {
    background-color: var(--info-900);
    color: var(--info-300);
  }

  .stat-icon-success {
    background-color: var(--success-100);
    color: var(--success-700);
  }

  .dark .stat-icon-success {
    background-color: var(--success-900);
    color: var(--success-300);
  }

  .stat-icon svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .stat-content {
    flex: 1;
  }

  .stat-label {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    margin: 0;
  }

  .stat-value {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  /* Quick Actions */
  .quick-actions {
    margin-bottom: var(--space-6);
  }

  .quick-actions-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
  }

  .section-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  /* List Header */
  .list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    background-color: var(--bg-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-xl);
    margin-bottom: var(--space-4);
  }

  .list-header-left {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .checkbox-wrapper {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    cursor: pointer;
  }

  .checkbox-label {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  .list-header-right {
    display: flex;
    gap: var(--space-2);
  }

  /* Bulk Actions */
  .bulk-actions {
    margin-bottom: var(--space-4);
  }

  .bulk-actions-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    background-color: var(--warning-50);
    border: 1px solid var(--warning-200);
    border-radius: var(--radius-lg);
  }

  .dark .bulk-actions-content {
    background-color: rgba(245, 158, 11, 0.1);
    border-color: var(--warning-800);
  }

  .bulk-actions-info {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .bulk-icon {
    width: 1.5rem;
    height: 1.5rem;
    color: var(--warning-600);
  }

  .bulk-actions-text {
    flex: 1;
  }

  .bulk-actions-title {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--warning-800);
    margin: 0;
  }

  .dark .bulk-actions-title {
    color: var(--warning-200);
  }

  .bulk-actions-subtitle {
    font-size: var(--font-size-xs);
    color: var(--warning-700);
    margin: 0;
  }

  .dark .bulk-actions-subtitle {
    color: var(--warning-300);
  }

  /* Password List */
  .password-list {
    flex: 1;
  }

  .password-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }

  @media (min-width: 640px) {
    .password-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (min-width: 1024px) {
    .password-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  /* Loading State */
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-12);
    gap: var(--space-4);
  }

  .loading-text {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  /* Error State */
  .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-12);
    gap: var(--space-4);
  }

  .error-icon {
    width: 3rem;
    height: 3rem;
    color: var(--danger-500);
  }

  .error-text {
    font-size: var(--font-size-base);
    color: var(--danger-600);
    text-align: center;
  }

  /* Empty State */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-12);
    gap: var(--space-4);
    text-align: center;
  }

  .empty-icon {
    width: 4rem;
    height: 4rem;
    color: var(--text-tertiary);
  }

  .empty-title {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  .empty-text {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    margin: 0;
  }

  /* Mobile Adjustments */
  @media (max-width: 640px) {
    .main-content {
      padding: var(--space-3) var(--space-4);
    }

    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: var(--space-3);
    }

    .stat-card {
      padding: var(--space-3);
    }

    .stat-icon {
      width: 2rem;
      height: 2rem;
    }

    .stat-value {
      font-size: var(--font-size-base);
    }
  }
</style>
