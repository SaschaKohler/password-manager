<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { auth } from '$lib/stores/auth';

  export let theme: 'light' | 'dark' = 'light';

  const dispatch = createEventDispatcher<{
    toggleTheme: void;
    showSecurity: void;
    showProfile: void;
    logout: void;
  }>();

  let showUserMenu = false;

  function handleToggleTheme() {
    dispatch('toggleTheme');
  }

  function handleShowSecurity() {
    dispatch('showSecurity');
  }

  function handleShowProfile() {
    dispatch('showProfile');
  }

  function handleLogout() {
    dispatch('logout');
    showUserMenu = false;
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      showUserMenu = false;
    }
  }

  // Close user menu when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.user-menu-container')) {
      showUserMenu = false;
    }
  }
</script>

<svelte:window on:click={handleClickOutside} on:keydown={handleKeydown} />

<header class="header">
  <div class="header-container">
    <!-- Logo & Brand -->
    <div class="header-brand">
      <div class="logo">
        <span class="logo-icon">🔐</span>
      </div>
      <div class="brand-text">
        <h1 class="brand-name">Vaultspace</h1>
        <p class="brand-tagline">Secure password workspace</p>
      </div>
    </div>

    <!-- Search Bar (Desktop) -->
    <div class="header-search hidden md:flex">
      <div class="search-input-wrapper">
        <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          placeholder="Search passwords..."
          class="search-input"
          aria-label="Search passwords"
        />
      </div>
    </div>

    <!-- Header Actions -->
    <div class="header-actions">
      <!-- Theme Toggle -->
      <button
        type="button"
        class="btn-icon"
        on:click={handleToggleTheme}
        aria-label="Toggle theme"
        title="Toggle theme"
      >
        {#if theme === 'dark'}
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        {:else}
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        {/if}
      </button>

      <!-- Security Button -->
      <button
        type="button"
        class="btn-icon"
        on:click={handleShowSecurity}
        aria-label="Security"
        title="Security"
      >
        <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </button>

      <!-- User Menu -->
      <div class="user-menu-container">
        <button
          type="button"
          class="user-menu-button"
          on:click={() => showUserMenu = !showUserMenu}
          aria-label="User menu"
          aria-expanded={showUserMenu}
        >
          <div class="user-avatar">
            <span class="user-avatar-text">{$auth.user?.username?.charAt(0).toUpperCase() || 'U'}</span>
          </div>
          <svg class="chevron-icon" class:rotate-180={showUserMenu} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {#if showUserMenu}
          <div class="user-menu-dropdown">
            <div class="user-menu-header">
              <div class="user-avatar user-avatar-lg">
                <span class="user-avatar-text">{$auth.user?.username?.charAt(0).toUpperCase() || 'U'}</span>
              </div>
              <div class="user-info">
                <p class="user-name">{$auth.user?.username || 'User'}</p>
                <p class="user-email">{$auth.user?.email || ''}</p>
              </div>
            </div>
            <div class="user-menu-divider"></div>
            <button
              type="button"
              class="user-menu-item"
              on:click={handleShowProfile}
            >
              <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Profile
            </button>
            <button
              type="button"
              class="user-menu-item"
              on:click={handleShowSecurity}
            >
              <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Security
            </button>
            <div class="user-menu-divider"></div>
            <button
              type="button"
              class="user-menu-item user-menu-item-danger"
              on:click={handleLogout}
            >
              <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>
        {/if}
      </div>
    </div>
  </div>
</header>

<style>
  .header {
    position: sticky;
    top: 0;
    z-index: var(--z-sticky);
    background-color: var(--bg-primary);
    border-bottom: 1px solid var(--border-default);
    height: 4rem;
    transition: background-color var(--transition-base) var(--transition-timing-default),
                border-color var(--transition-base) var(--transition-timing-default);
  }

  .header-container {
    max-width: 80rem;
    margin: 0 auto;
    padding: 0 var(--space-4);
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
  }

  /* Logo & Brand */
  .header-brand {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    flex-shrink: 0;
  }

  .logo {
    width: 2.5rem;
    height: 2.5rem;
    background: linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-sm);
  }

  .dark .logo {
    background: linear-gradient(135deg, var(--primary-900) 0%, var(--primary-800) 100%);
  }

  .logo-icon {
    font-size: 1.25rem;
  }

  .brand-text {
    display: flex;
    flex-direction: column;
  }

  .brand-name {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
    line-height: var(--line-height-tight);
    margin: 0;
  }

  .brand-tagline {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    line-height: var(--line-height-tight);
    margin: 0;
  }

  /* Search Bar */
  .header-search {
    flex: 1;
    max-width: 28rem;
  }

  .search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-icon {
    position: absolute;
    left: var(--space-3);
    width: 1rem;
    height: 1rem;
    color: var(--text-tertiary);
  }

  .search-input {
    width: 100%;
    padding: var(--space-2) var(--space-3) var(--space-2) var(--space-10);
    font-size: var(--font-size-sm);
    color: var(--text-primary);
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    transition: all var(--transition-base) var(--transition-timing-default);
  }

  .search-input::placeholder {
    color: var(--text-tertiary);
  }

  .search-input:focus {
    outline: none;
    border-color: var(--border-focus);
    box-shadow: 0 0 0 3px var(--ring-color);
  }

  /* Header Actions */
  .header-actions {
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }

  .icon {
    width: 1.25rem;
    height: 1.25rem;
  }

  /* User Menu */
  .user-menu-container {
    position: relative;
  }

  .user-menu-button {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-1);
    background: transparent;
    border: none;
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: background-color var(--transition-base) var(--transition-timing-default);
  }

  .user-menu-button:hover {
    background-color: var(--bg-secondary);
  }

  .user-avatar {
    width: 2rem;
    height: 2rem;
    background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-sm);
  }

  .user-avatar-lg {
    width: 3rem;
    height: 3rem;
    font-size: var(--font-size-lg);
  }

  .user-avatar-text {
    color: white;
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

  .user-menu-dropdown {
    position: absolute;
    top: calc(100% + var(--space-2));
    right: 0;
    min-width: 16rem;
    background-color: var(--bg-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-xl);
    z-index: var(--z-dropdown);
    padding: var(--space-2);
    animation: dropdownIn var(--transition-base) var(--transition-timing-default);
  }

  @keyframes dropdownIn {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .user-menu-header {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3);
  }

  .user-info {
    flex: 1;
    overflow: hidden;
  }

  .user-name {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .user-email {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .user-menu-divider {
    height: 1px;
    background-color: var(--border-default);
    margin: var(--space-2) 0;
  }

  .user-menu-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    width: 100%;
    padding: var(--space-2) var(--space-3);
    font-size: var(--font-size-sm);
    color: var(--text-primary);
    background: transparent;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: background-color var(--transition-base) var(--transition-timing-default);
    text-align: left;
  }

  .user-menu-item:hover {
    background-color: var(--bg-secondary);
  }

  .user-menu-item-danger {
    color: var(--danger-600);
  }

  .user-menu-item-danger:hover {
    background-color: var(--danger-50);
  }

  .dark .user-menu-item-danger:hover {
    background-color: rgba(239, 68, 68, 0.1);
  }

  .menu-item-icon {
    width: 1rem;
    height: 1rem;
    flex-shrink: 0;
  }

  /* Mobile Adjustments */
  @media (max-width: 768px) {
    .header-container {
      padding: 0 var(--space-3);
    }

    .brand-tagline {
      display: none;
    }

    .header-search {
      display: none;
    }
  }
</style>
