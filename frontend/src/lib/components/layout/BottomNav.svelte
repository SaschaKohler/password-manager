<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let activeTab: 'home' | 'vault' | 'add' | 'more' | 'user' = 'home';

  const dispatch = createEventDispatcher<{
    selectTab: string;
    showAddPassword: void;
    showMore: void;
    showProfile: void;
  }>();

  function handleTabClick(tab: string) {
    if (tab === 'add') {
      dispatch('showAddPassword');
    } else if (tab === 'more') {
      dispatch('showMore');
    } else if (tab === 'user') {
      dispatch('showProfile');
    } else {
      dispatch('selectTab', tab);
    }
  }
</script>

<nav class="bottom-nav">
  <button
    type="button"
    class="nav-tab"
    class:nav-tab-active={activeTab === 'home'}
    on:click={() => handleTabClick('home')}
    aria-label="Home"
    aria-current={activeTab === 'home' ? 'page' : undefined}
  >
    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l2-2M3 6l2-2m0 0l2-2M3 18l2-2m0 0l2-2M5 21h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
    <span class="nav-label">Home</span>
  </button>

  <button
    type="button"
    class="nav-tab"
    class:nav-tab-active={activeTab === 'vault'}
    on:click={() => handleTabClick('vault')}
    aria-label="Vault"
    aria-current={activeTab === 'vault' ? 'page' : undefined}
  >
    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 1.79 4 4 4h12c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h12c2.21 0 4 1.79 4 4M4 7v10c0 2.21 1.79 4 4 4h12c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h12c2.21 0 4 1.79 4 4" />
    </svg>
    <span class="nav-label">Vault</span>
  </button>

  <button
    type="button"
    class="nav-tab nav-tab-fab"
    on:click={() => handleTabClick('add')}
    aria-label="Add Password"
  >
    <svg class="nav-icon nav-icon-fab" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
    </svg>
  </button>

  <button
    type="button"
    class="nav-tab"
    class:nav-tab-active={activeTab === 'more'}
    on:click={() => handleTabClick('more')}
    aria-label="More"
    aria-current={activeTab === 'more' ? 'page' : undefined}
  >
    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
    </svg>
    <span class="nav-label">More</span>
  </button>

  <button
    type="button"
    class="nav-tab"
    class:nav-tab-active={activeTab === 'user'}
    on:click={() => handleTabClick('user')}
    aria-label="User"
    aria-current={activeTab === 'user' ? 'page' : undefined}
  >
    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
    <span class="nav-label">User</span>
  </button>
</nav>

<style>
  .bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: space-around;
    background-color: var(--bg-primary);
    border-top: 1px solid var(--border-default);
    height: 3.5rem;
    z-index: var(--z-fixed);
    padding-bottom: env(safe-area-inset-bottom);
  }

  .nav-tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-1);
    flex: 1;
    padding: var(--space-2) var(--space-1);
    background: transparent;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-base) var(--transition-timing-default);
    min-width: 0;
  }

  .nav-tab:hover {
    background-color: var(--bg-secondary);
  }

  .nav-tab-active {
    color: var(--primary-600);
  }

  .dark .nav-tab-active {
    color: var(--primary-400);
  }

  .nav-tab-fab {
    flex: 0 0 auto;
    width: 3.5rem;
    height: 3.5rem;
    margin: 0 var(--space-2);
    background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
    border-radius: var(--radius-full);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    transform: translateY(-0.5rem);
  }

  .nav-tab-fab:hover {
    transform: translateY(-0.75rem);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.5);
  }

  .nav-icon {
    width: 1.25rem;
    height: 1.25rem;
    color: var(--text-tertiary);
    transition: color var(--transition-base) var(--transition-timing-default);
  }

  .nav-tab-active .nav-icon {
    color: var(--primary-600);
  }

  .dark .nav-tab-active .nav-icon {
    color: var(--primary-400);
  }

  .nav-icon-fab {
    width: 1.5rem;
    height: 1.5rem;
    color: white;
  }

  .nav-label {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    color: var(--text-tertiary);
    transition: color var(--transition-base) var(--transition-timing-default);
  }

  .nav-tab-active .nav-label {
    color: var(--primary-600);
  }

  .dark .nav-tab-active .nav-label {
    color: var(--primary-400);
  }

  /* Desktop - Hide bottom nav */
  @media (min-width: 768px) {
    .bottom-nav {
      display: none;
    }
  }
</style>
