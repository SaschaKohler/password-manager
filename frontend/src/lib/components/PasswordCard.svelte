<script lang="ts">
  import type { PasswordEntry } from '$lib/types/password';
  import { createEventDispatcher } from 'svelte';
  import { formatDistanceToNow } from 'date-fns';

  export let password: PasswordEntry;
  export let selected = false;

  const dispatch = createEventDispatcher<{
    edit: PasswordEntry;
    delete: PasswordEntry;
    toggleFavorite: PasswordEntry;
    select: PasswordEntry;
    view: PasswordEntry;
    history: PasswordEntry;
    share: PasswordEntry;
  }>();

  function handleEdit() {
    dispatch('edit', password);
  }

  function handleDelete() {
    dispatch('delete', password);
  }

  function handleToggleFavorite() {
    dispatch('toggleFavorite', password);
  }

  function handleSelect(event: MouseEvent) {
    if (event.ctrlKey || event.metaKey) {
      dispatch('select', password);
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (event.ctrlKey || event.metaKey) {
        dispatch('select', password);
      }
    }
  }

  function handleView() {
    dispatch('view', password);
  }

  function handleViewHistory() {
    dispatch('history', password);
  }

  function handleShare() {
    dispatch('share', password);
  }

  function getLastAccessedText(): string {
    if (!password.last_accessed) return 'Never accessed';
    return `Last accessed ${formatDistanceToNow(new Date(password.last_accessed), { addSuffix: true })}`;
  }

  function getStrengthColor(strength: number): string {
    if (strength >= 4) return 'text-success-600';
    if (strength >= 3) return 'text-warning-600';
    if (strength >= 2) return 'text-warning-600';
    return 'text-danger-600';
  }

  function getStrengthText(strength: number): string {
    if (strength >= 4) return 'Strong';
    if (strength >= 3) return 'Good';
    if (strength >= 2) return 'Fair';
    return 'Weak';
  }
</script>

<div 
  class="password-card {selected ? 'password-card-selected' : ''} {password.is_favorite ? 'password-card-favorite' : ''}"
  on:click={handleSelect}
  on:keydown={handleKeydown}
  role="button"
  tabindex="0"
>
  <div class="card-header">
    <div class="card-title">
      <h3 class="title-text">{password.title}</h3>
      {#if password.is_favorite}
        <span class="favorite-icon" title="Favorite">⭐</span>
      {/if}
    </div>
    <div class="card-actions">
      <button 
        class="action-btn"
        on:click|stopPropagation={handleView}
        title="View password"
        aria-label="View password"
      >
        <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </button>
      <button 
        class="action-btn"
        on:click|stopPropagation={handleViewHistory}
        title="View history"
        aria-label="View history"
      >
        <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a2 2 0 11-4 0 2 2 0 014 0m-2 2a2 2 0 012-2h4a2 2 0 012 2v6a2 2 0 01-2 2H7a2 2 0 01-2-2v-6a2 2 0 012-2h4a2 2 0 012 2z" />
        </svg>
      </button>
      <button 
        class="action-btn action-btn-favorite"
        on:click|stopPropagation={handleToggleFavorite}
        title={password.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
        aria-label={password.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
      >
        {password.is_favorite ? '⭐' : '☆'}
      </button>
      <button 
        class="action-btn"
        on:click|stopPropagation={handleShare}
        title="Share password"
        aria-label="Share password"
      >
        <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656-1.172l-4-4a4 4 0 00-5.656 1.172V4a2 2 0 012-2h4a2 2 0 012 2v6a2 2 0 01-2 2H7a2 2 0 01-2-2v-6a2 2 0 012-2h4a2 2 0 012 2z" />
        </svg>
      </button>
      <button 
        class="action-btn"
        on:click|stopPropagation={handleEdit}
        title="Edit password"
        aria-label="Edit password"
      >
        <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V6a2 2 0 00-2-2h-2a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      </button>
      <button 
        class="action-btn action-btn-danger"
        on:click|stopPropagation={handleDelete}
        title="Delete password"
        aria-label="Delete password"
      >
        <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6M4 7v6a1 1 0 001 1h14a1 1 0 001-1V7a1 1 0 00-1-1H4a1 1 0 00-1 1v6a1 1 0 001 1h14a1 1 0 001-1V7a1 1 0 00-1-1H4z" />
        </svg>
      </button>
    </div>
  </div>

  <div class="card-body">
    <div class="info-row">
      <span class="info-label">Username</span>
      <span class="info-value">{password.username_hint}</span>
    </div>

    {#if password.url_hint}
      <div class="info-row">
        <span class="info-label">URL</span>
        <span class="info-value info-value-url">{password.url_hint}</span>
      </div>
    {/if}

    {#if password.category}
      <div class="info-row">
        <span class="info-label">Category</span>
        <span class="badge badge-primary">{password.category}</span>
      </div>
    {/if}

    {#if password.tags.length > 0}
      <div class="info-row">
        <span class="info-label">Tags</span>
        <div class="tags-container">
          {#each password.tags as tag}
            <span class="badge badge-gray">{tag}</span>
          {/each}
        </div>
      </div>
    {/if}

    {#if password.has_notes}
      <div class="info-row">
        <span class="info-label">Notes</span>
        <span class="info-value info-value-notes">📝 Has notes</span>
      </div>
    {/if}
  </div>

  <div class="card-footer">
    <span class="footer-text">
      Created {formatDistanceToNow(new Date(password.created_at), { addSuffix: true })}
    </span>
    <span class="footer-text">
      {getLastAccessedText()}
    </span>
  </div>
</div>

<style>
  .password-card {
    background-color: var(--bg-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-xl);
    padding: var(--space-4);
    transition: all var(--transition-base) var(--transition-timing-default);
    cursor: pointer;
  }

  .password-card:hover {
    border-color: var(--primary-300);
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
  }

  .dark .password-card:hover {
    border-color: var(--primary-600);
  }

  .password-card-selected {
    border-color: var(--primary-500);
    background-color: var(--primary-50);
    box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.15), 0 12px 32px -20px rgba(37, 99, 235, 0.5);
  }

  .dark .password-card-selected {
    border-color: var(--primary-400);
    background-color: var(--primary-900);
    box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.15), 0 12px 32px -20px rgba(96, 165, 250, 0.5);
  }

  .password-card-favorite {
    border-left: 4px solid var(--warning-500);
  }

  /* Card Header */
  .card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: var(--space-3);
  }

  .card-title {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    flex: 1;
  }

  .title-text {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  .favorite-icon {
    font-size: var(--font-size-base);
    flex-shrink: 0;
  }

  .card-actions {
    display: flex;
    gap: var(--space-1);
    opacity: 0;
    transition: opacity var(--transition-base) var(--transition-timing-default);
  }

  .password-card:hover .card-actions {
    opacity: 1;
  }

  .action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background: transparent;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-base) var(--transition-timing-default);
    color: var(--text-tertiary);
  }

  .action-btn:hover {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
  }

  .action-btn-favorite {
    color: var(--warning-500);
  }

  .action-btn-favorite:hover {
    background-color: var(--warning-50);
  }

  .dark .action-btn-favorite:hover {
    background-color: rgba(245, 158, 11, 0.1);
  }

  .action-btn-danger:hover {
    background-color: var(--danger-50);
    color: var(--danger-600);
  }

  .dark .action-btn-danger:hover {
    background-color: rgba(239, 68, 68, 0.1);
    color: var(--danger-400);
  }

  .action-icon {
    width: 1.125rem;
    height: 1.125rem;
  }

  /* Card Body */
  .card-body {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .info-row {
    display: flex;
    align-items: flex-start;
    gap: var(--space-2);
  }

  .info-label {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    color: var(--text-tertiary);
    min-width: 4rem;
    flex-shrink: 0;
  }

  .info-value {
    font-size: var(--font-size-sm);
    color: var(--text-primary);
    flex: 1;
    word-break: break-word;
  }

  .info-value-url {
    color: var(--primary-600);
  }

  .dark .info-value-url {
    color: var(--primary-400);
  }

  .info-value-notes {
    color: var(--text-tertiary);
  }

  .tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1);
  }

  /* Card Footer */
  .card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: var(--space-3);
    border-top: 1px solid var(--border-subtle);
    margin-top: var(--space-3);
  }

  .footer-text {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
  }

  /* Mobile Adjustments */
  @media (max-width: 640px) {
    .password-card {
      padding: var(--space-3);
    }

    .card-header {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--space-2);
    }

    .card-actions {
      opacity: 1;
      width: 100%;
      justify-content: flex-start;
    }

    .action-btn {
      width: auto;
      padding: var(--space-2);
    }

    .info-label {
      min-width: auto;
    }
  }
</style>
