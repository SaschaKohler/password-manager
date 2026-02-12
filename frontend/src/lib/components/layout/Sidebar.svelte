<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { passwords } from '$lib/stores/passwords';

  export let isOpen = true;

  const dispatch = createEventDispatcher<{
    selectCategory: string;
    selectFolder: string;
    selectTag: string;
    showFolders: void;
    showImportExport: void;
    showAuditLogs: void;
  }>();

  let expandedSections: Set<string> = new Set(['folders', 'tags']);

  function toggleSection(section: string) {
    if (expandedSections.has(section)) {
      expandedSections.delete(section);
    } else {
      expandedSections.add(section);
    }
    expandedSections = new Set(expandedSections);
  }

  function handleSelectCategory(category: string) {
    dispatch('selectCategory', category);
  }

  function handleSelectFolder(folder: string) {
    dispatch('selectFolder', folder);
  }

  function handleSelectTag(tag: string) {
    dispatch('selectTag', tag);
  }

  function handleShowFolders() {
    dispatch('showFolders');
  }

  function handleShowImportExport() {
    dispatch('showImportExport');
  }

  function handleShowAuditLogs() {
    dispatch('showAuditLogs');
  }
</script>

<aside class="sidebar" class:sidebar-closed={!isOpen}>
  <div class="sidebar-content">
    <!-- Navigation -->
    <nav class="sidebar-nav">
      <!-- Dashboard -->
      <button
        type="button"
        class="nav-item nav-item-active"
        on:click={() => handleSelectCategory('')}
      >
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l2-2M3 6l2-2m0 0l2-2M3 18l2-2m0 0l2-2M5 21h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
        <span class="nav-text">Dashboard</span>
      </button>

      <!-- All Passwords -->
      <button
        type="button"
        class="nav-item"
        on:click={() => handleSelectCategory('all')}
      >
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 1.79 4 4 4h12c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h12c2.21 0 4 1.79 4 4M4 7v10c0 2.21 1.79 4 4 4h12c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h12c2.21 0 4 1.79 4 4" />
        </svg>
        <span class="nav-text">All Passwords</span>
      </button>

      <!-- Favorites -->
      <button
        type="button"
        class="nav-item"
        on:click={() => handleSelectCategory('favorites')}
      >
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 2.008 0a2.5 2.5 0 01-2.448 2.527 6.757 6.757 0 01-1.189 2.03 12.942 12.942 0 01-6.915 3.839c-.375-.766-.642-1.64-.642-2.606 0-3.236 2.615-5.85 5.85-5.85 1.348 0 2.505.445 3.51 1.204z" />
        </svg>
        <span class="nav-text">Favorites</span>
      </button>
    </nav>

    <!-- Divider -->
    <div class="sidebar-divider"></div>

    <!-- Folders Section -->
    <div class="sidebar-section">
      <button
        type="button"
        class="sidebar-section-header"
        on:click={() => toggleSection('folders')}
        aria-expanded={expandedSections.has('folders')}
      >
        <svg class="section-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span class="section-title">Folders</span>
        <svg class="chevron-icon" class:rotate-180={expandedSections.has('folders')} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {#if expandedSections.has('folders')}
        <div class="sidebar-section-content">
          {#if $passwords.folders && $passwords.folders.length > 0}
            {#each $passwords.folders as folder}
              <button
                type="button"
                class="nav-item nav-item-sub"
                on:click={() => handleSelectFolder(folder)}
              >
                <svg class="nav-icon nav-icon-sub" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v10a2 2 0 01-2 2H7a2 2 0 01-2-2z" />
                </svg>
                <span class="nav-text">{folder}</span>
              </button>
            {/each}
          {:else}
            <p class="empty-state">No folders yet</p>
          {/if}
          <button
            type="button"
            class="nav-item nav-item-action"
            on:click={handleShowFolders}
          >
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span class="nav-text">Manage Folders</span>
          </button>
        </div>
      {/if}
    </div>

    <!-- Tags Section -->
    <div class="sidebar-section">
      <button
        type="button"
        class="sidebar-section-header"
        on:click={() => toggleSection('tags')}
        aria-expanded={expandedSections.has('tags')}
      >
        <svg class="section-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l2 2c.39.391.586.902.586 1.414v5c0 .512-.195 1.024-.586 1.414l-2 2c-.39.391-.586.902-.586 1.414v3a2 2 0 01-2 2H7a2 2 0 01-2-2v-3c0-.512.195-1.024.586-1.414l2-2c.39-.391.586-.902.586-1.414z" />
        </svg>
        <span class="section-title">Tags</span>
        <svg class="chevron-icon" class:rotate-180={expandedSections.has('tags')} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {#if expandedSections.has('tags')}
        <div class="sidebar-section-content">
          {#if $passwords.tags && $passwords.tags.length > 0}
            {#each $passwords.tags as tag}
              <button
                type="button"
                class="nav-item nav-item-sub"
                on:click={() => handleSelectTag(tag)}
              >
                <svg class="nav-icon nav-icon-sub" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l2 2c.39.391.586.902.586 1.414v5c0 .512-.195 1.024-.586 1.414l-2 2c-.39.391-.586.902-.586 1.414v3a2 2 0 01-2 2H7a2 2 0 01-2-2v-3c0-.512.195-1.024.586-1.414l2-2c.39-.391.586-.902.586-1.414z" />
                </svg>
                <span class="nav-text">{tag}</span>
              </button>
            {/each}
          {:else}
            <p class="empty-state">No tags yet</p>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Divider -->
    <div class="sidebar-divider"></div>

    <!-- Settings Section -->
    <div class="sidebar-section">
      <button
        type="button"
        class="nav-item"
        on:click={handleShowImportExport}
      >
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m5-3v9" />
        </svg>
        <span class="nav-text">Import / Export</span>
      </button>

      <button
        type="button"
        class="nav-item"
        on:click={handleShowAuditLogs}
      >
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 5h.01" />
        </svg>
        <span class="nav-text">Audit Logs</span>
      </button>
    </div>
  </div>
</aside>

<style>
  .sidebar {
    position: sticky;
    top: 4rem;
    height: calc(100vh - 4rem);
    width: 17.5rem;
    background-color: var(--bg-primary);
    border-right: 1px solid var(--border-default);
    overflow-y: auto;
    transition: transform var(--transition-base) var(--transition-timing-default),
                width var(--transition-base) var(--transition-timing-default);
    z-index: var(--z-sticky);
  }

  .sidebar-closed {
    transform: translateX(-100%);
    width: 0;
  }

  .sidebar-content {
    padding: var(--space-4);
  }

  /* Navigation */
  .sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    margin-bottom: var(--space-4);
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    width: 100%;
    padding: var(--space-2) var(--space-3);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    background: transparent;
    border: none;
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all var(--transition-base) var(--transition-timing-default);
    text-align: left;
  }

  .nav-item:hover {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
  }

  .nav-item-active {
    background-color: var(--primary-50);
    color: var(--primary-700);
  }

  .dark .nav-item-active {
    background-color: var(--primary-900);
    color: var(--primary-300);
  }

  .nav-item-sub {
    padding-left: var(--space-8);
  }

  .nav-item-action {
    color: var(--primary-600);
  }

  .dark .nav-item-action {
    color: var(--primary-400);
  }

  .nav-icon {
    width: 1.25rem;
    height: 1.25rem;
    flex-shrink: 0;
    color: var(--text-tertiary);
  }

  .nav-icon-sub {
    width: 1rem;
    height: 1rem;
  }

  .nav-text {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* Sidebar Sections */
  .sidebar-section {
    margin-bottom: var(--space-2);
  }

  .sidebar-section-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    width: 100%;
    padding: var(--space-2) var(--space-3);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    background: transparent;
    border: none;
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: background-color var(--transition-base) var(--transition-timing-default);
    text-align: left;
  }

  .sidebar-section-header:hover {
    background-color: var(--bg-secondary);
  }

  .section-icon {
    width: 1.25rem;
    height: 1.25rem;
    flex-shrink: 0;
    color: var(--text-tertiary);
  }

  .section-title {
    flex: 1;
  }

  .chevron-icon {
    width: 1rem;
    height: 1rem;
    color: var(--text-tertiary);
    transition: transform var(--transition-base) var(--transition-timing-default);
  }

  .chevron-icon.rotate-180 {
    transform: rotate(180deg);
  }

  .sidebar-section-content {
    padding-left: var(--space-3);
    margin-top: var(--space-1);
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    animation: slideDown var(--transition-base) var(--transition-timing-default);
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .empty-state {
    padding: var(--space-2) var(--space-3);
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    font-style: italic;
  }

  .sidebar-divider {
    height: 1px;
    background-color: var(--border-default);
    margin: var(--space-4) 0;
  }

  /* Mobile Adjustments */
  @media (max-width: 1024px) {
    .sidebar {
      position: fixed;
      top: 4rem;
      left: 0;
      height: calc(100vh - 4rem);
      z-index: var(--z-fixed);
      transform: translateX(-100%);
    }

    .sidebar:not(.sidebar-closed) {
      transform: translateX(0);
    }
  }
</style>
