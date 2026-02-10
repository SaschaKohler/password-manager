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

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (event.ctrlKey || event.metaKey) {
        dispatch('select', password);
      }
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
  class="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-medium hover:border-primary-300 transition-all duration-200 cursor-pointer {selected ? 'border-primary-500 bg-primary-50 shadow-medium' : ''} {password.is_favorite ? 'border-l-4 border-l-warning-500' : ''}"
  on:click={handleSelect}
  on:keydown={handleKeydown}
  role="button"
  tabindex="0"
>
  <div class="flex justify-between items-start mb-3">
    <div class="flex items-center gap-2 flex-1">
      <h3 class="text-lg font-semibold text-gray-900 m-0 leading-tight">{password.title}</h3>
      {#if password.is_favorite}
        <div class="text-base text-warning-500" title="Favorite">⭐</div>
      {/if}
    </div>
    <div class="flex gap-1 opacity-0 transition-opacity duration-200 hover:opacity-100">
      <button 
        class="bg-none border-none p-1-5 rounded cursor-pointer text-sm transition-colors duration-200 flex items-center justify-center hover:bg-warning-100 hover:text-warning-600" 
        on:click|stopPropagation={handleToggleFavorite}
        title={password.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
      >
        {password.is_favorite ? '⭐' : '☆'}
      </button>
      <button 
        class="bg-none border-none p-1-5 rounded cursor-pointer text-sm transition-colors duration-200 flex items-center justify-center hover:bg-blue-100 hover:text-blue-600" 
        on:click|stopPropagation={handleEdit}
        title="Edit password"
      >
        ✏️
      </button>
      <button 
        class="bg-none border-none p-1-5 rounded cursor-pointer text-sm transition-colors duration-200 flex items-center justify-center hover:bg-danger-100 hover:text-danger-600" 
        on:click|stopPropagation={handleDelete}
        title="Delete password"
      >
        🗑️
      </button>
    </div>
  </div>

  <div class="flex flex-col gap-2">
    <div class="flex items-start gap-2">
      <span class="text-xs font-medium text-gray-500 min-w-15 flex-shrink-0">Username:</span>
      <span class="text-sm text-gray-700 flex-1 break-all">{password.username_hint}</span>
    </div>

    {#if password.url_hint}
      <div class="flex items-start gap-2">
        <span class="text-xs font-medium text-gray-500 min-w-15 flex-shrink-0">URL:</span>
        <span class="text-sm text-gray-700 flex-1 break-all">{password.url_hint}</span>
      </div>
    {/if}

    {#if password.category}
      <div class="flex items-start gap-2">
        <span class="text-xs font-medium text-gray-500 min-w-15 flex-shrink-0">Category:</span>
        <span class="bg-gray-100 px-2 py-0-5 rounded text-xs font-medium text-gray-600">{password.category}</span>
      </div>
    {/if}

    {#if password.tags.length > 0}
      <div class="flex items-start gap-2">
        <span class="text-xs font-medium text-gray-500 min-w-15 flex-shrink-0">Tags:</span>
        <div class="flex flex-wrap gap-1">
          {#each password.tags as tag}
            <span class="bg-gray-200 text-gray-700 px-2 py-0-5 rounded text-xs font-medium">{tag}</span>
          {/each}
        </div>
      </div>
    {/if}

    {#if password.has_notes}
      <div class="flex items-start gap-2">
        <span class="text-xs font-medium text-gray-500 min-w-15 flex-shrink-0">Notes:</span>
        <span class="text-sm text-gray-700 flex-1">📝 Has notes</span>
      </div>
    {/if}
  </div>

  <div class="mt-3 pt-3 border-t border-gray-100">
    <div class="flex justify-between items-center text-xs text-gray-400">
      <span class="whitespace-nowrap">
        Created {formatDistanceToNow(new Date(password.created_at), { addSuffix: true })}
      </span>
      <span class="whitespace-nowrap">
        {getLastAccessedText()}
      </span>
    </div>
  </div>
</div>

<style>
  /* Responsive design */
  @media (max-width: 640px) {
    div {
      padding: 0.75rem !important;
    }
    
    h3 {
      font-size: 1rem !important;
    }
    
    .flex.gap-1 {
      opacity: 1 !important;
    }
    
    .flex {
      flex-direction: column !important;
      gap: 0.125rem !important;
    }
    
    .min-w-15 {
      min-width: auto !important;
    }
    
    .items-center {
      align-items: flex-start !important;
      gap: 0.125rem !important;
    }
  }
</style>
