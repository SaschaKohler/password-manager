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

  function getLastAccessedText(): string {
    if (!password.last_accessed) return 'Never accessed';
    return `Last accessed ${formatDistanceToNow(new Date(password.last_accessed), { addSuffix: true })}`;
  }

  function getStrengthColor(strength: number): string {
    if (strength >= 4) return 'text-green-600';
    if (strength >= 3) return 'text-yellow-600';
    if (strength >= 2) return 'text-orange-600';
    return 'text-red-600';
  }

  function getStrengthText(strength: number): string {
    if (strength >= 4) return 'Strong';
    if (strength >= 3) return 'Good';
    if (strength >= 2) return 'Fair';
    return 'Weak';
  }
</script>

<div 
  class="password-card {selected ? 'selected' : ''}"
  class:favorite={password.is_favorite}
  on:click={handleSelect}
  role="button"
  tabindex="0"
>
  <div class="card-header">
    <div class="title-section">
      <h3 class="title">{password.title}</h3>
      {#if password.is_favorite}
        <div class="favorite-indicator" title="Favorite">⭐</div>
      {/if}
    </div>
    <div class="actions">
      <button 
        class="action-btn favorite-btn" 
        on:click|stopPropagation={handleToggleFavorite}
        title={password.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
      >
        {password.is_favorite ? '⭐' : '☆'}
      </button>
      <button 
        class="action-btn edit-btn" 
        on:click|stopPropagation={handleEdit}
        title="Edit password"
      >
        ✏️
      </button>
      <button 
        class="action-btn delete-btn" 
        on:click|stopPropagation={handleDelete}
        title="Delete password"
      >
        🗑️
      </button>
    </div>
  </div>

  <div class="card-content">
    <div class="field">
      <span class="field-label">Username:</span>
      <span class="field-value">{password.username_hint}</span>
    </div>

    {#if password.url_hint}
      <div class="field">
        <span class="field-label">URL:</span>
        <span class="field-value">{password.url_hint}</span>
      </div>
    {/if}

    {#if password.category}
      <div class="field">
        <span class="field-label">Category:</span>
        <span class="field-value category">{password.category}</span>
      </div>
    {/if}

    {#if password.tags.length > 0}
      <div class="field">
        <span class="field-label">Tags:</span>
        <div class="tags">
          {#each password.tags as tag}
            <span class="tag">{tag}</span>
          {/each}
        </div>
      </div>
    {/if}

    {#if password.has_notes}
      <div class="field">
        <span class="field-label">Notes:</span>
        <span class="field-value">📝 Has notes</span>
      </div>
    {/if}
  </div>

  <div class="card-footer">
    <div class="meta-info">
      <span class="created-date">
        Created {formatDistanceToNow(new Date(password.created_at), { addSuffix: true })}
      </span>
      <span class="last-accessed">
        {getLastAccessedText()}
      </span>
    </div>
  </div>
</div>

<style>
  .password-card {
    @apply bg-white border border-gray-200 rounded-xl p-4 hover:shadow-medium hover:border-primary-300 transition-all duration-200 cursor-pointer;
  }

  .password-card.selected {
    @apply border-primary-500 bg-primary-50 shadow-medium;
  }

  .password-card.favorite {
    @apply border-l-4 border-l-warning-500;
  }

  .card-header {
    @apply flex justify-between items-start mb-3;
  }

  .title-section {
    @apply flex items-center gap-2 flex-1;
  }

  .title {
    @apply text-lg font-semibold text-gray-900 m-0 leading-tight;
  }

  .favorite-indicator {
    @apply text-base text-warning-500;
  }

  .actions {
    @apply flex gap-1 opacity-0 transition-opacity duration-200;
  }

  .password-card:hover .actions {
    @apply opacity-100;
  }

  .action-btn {
    @apply bg-none border-none p-1.5 rounded cursor-pointer text-sm transition-colors duration-200 flex items-center justify-center;
  }

  .action-btn:hover {
    @apply bg-gray-100;
  }

  .favorite-btn:hover {
    @apply bg-warning-100 text-warning-600;
  }

  .edit-btn:hover {
    @apply bg-blue-100 text-blue-600;
  }

  .delete-btn:hover {
    @apply bg-danger-100 text-danger-600;
  }

  .card-content {
    @apply flex flex-col gap-2;
  }

  .field {
    @apply flex items-start gap-2;
  }

  .field-label {
    @apply text-xs font-medium text-gray-500 min-w-15 flex-shrink-0;
  }

  .field-value {
    @apply text-sm text-gray-700 flex-1 break-all;
  }

  .field-value.category {
    @apply bg-gray-100 px-2 py-0.5 rounded text-xs font-medium text-gray-600;
  }

  .tags {
    @apply flex flex-wrap gap-1;
  }

  .tag {
    @apply bg-gray-200 text-gray-700 px-2 py-0.5 rounded text-xs font-medium;
  }

  .card-footer {
    @apply mt-3 pt-3 border-t border-gray-100;
  }

  .meta-info {
    @apply flex justify-between items-center text-xs text-gray-400;
  }

  .created-date,
  .last-accessed {
    @apply whitespace-nowrap;
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .password-card {
      @apply p-3;
    }

    .title {
      @apply text-base;
    }

    .actions {
      @apply opacity-100;
    }

    .field {
      @apply flex-col gap-0.5;
    }

    .field-label {
      @apply min-w-auto;
    }

    .meta-info {
      @apply flex-col items-start gap-0.5;
    }
  }
</style>
