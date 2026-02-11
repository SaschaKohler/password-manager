<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { api } from '$lib/services/api';
  import type { PasswordEntry } from '$lib/types/password';
  import { formatDistanceToNow } from 'date-fns';

  export let password: PasswordEntry | null = null;
  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let loading = true;
  let error: string | null = null;
  let history: {
    id: number;
    password_id: number;
    action: string;
    timestamp: string;
    details: Record<string, any>;
    user_id: number;
    username: string;
    ip_address: string;
  }[] = [];

  $: if (isOpen && password) {
    loadHistory();
  }

  async function loadHistory() {
    loading = true;
    error = null;
    history = [];

    try {
      history = await api.getPasswordHistory(password!.id);
    } catch (err: any) {
      error = err.message || 'Failed to load password history';
    } finally {
      loading = false;
    }
  }

  function handleClose() {
    isOpen = false;
    dispatch('close');
  }

  function getActionIcon(action: string): string {
    const icons: Record<string, string> = {
      'viewed': '👁️',
      'created': '✨',
      'updated': '✏️',
      'deleted': '🗑️',
      'copied': '📋',
      'exported': '📤',
      'shared': '🔗',
      'moved': '📁',
      'favorited': '⭐',
      'unfavorited': '☆',
    };
    return icons[action.toLowerCase()] || '📝';
  }

  function getActionColor(action: string): string {
    const colors: Record<string, string> = {
      'viewed': 'bg-blue-100 text-blue-800',
      'created': 'bg-success-100 text-success-800',
      'updated': 'bg-warning-100 text-warning-800',
      'deleted': 'bg-danger-100 text-danger-800',
      'copied': 'bg-primary-100 text-primary-800',
      'exported': 'bg-gray-100 text-gray-800',
      'shared': 'bg-purple-100 text-purple-800',
      'moved': 'bg-orange-100 text-orange-800',
      'favorited': 'bg-warning-100 text-warning-800',
      'unfavorited': 'bg-gray-100 text-gray-800',
    };
    return colors[action.toLowerCase()] || 'bg-gray-100 text-gray-800';
  }

  function formatAction(action: string): string {
    return action.charAt(0).toUpperCase() + action.slice(1);
  }
</script>

<svelte:window on:keydown={(e) => e.key === 'Escape' && handleClose()} />

{#if isOpen && password}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <span class="text-xl">📜</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Activity History</h2>
              <p class="text-sm text-gray-500">{password.title}</p>
            </div>
          </div>
          <button
            type="button"
            on:click={handleClose}
            class="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6">
        {#if loading}
          <div class="flex flex-col items-center justify-center py-12 gap-4">
            <div class="w-8 h-8 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
            <p class="text-gray-600">Loading history...</p>
          </div>
        {:else if error}
          <div class="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p class="text-danger-800">{error}</p>
            <button class="btn btn-secondary mt-4" on:click={loadHistory}>
              🔄 Retry
            </button>
          </div>
        {:else if history.length === 0}
          <div class="flex flex-col items-center justify-center py-12 gap-4 text-center">
            <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
              <span class="text-3xl">📭</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900">No Activity Yet</h3>
            <p class="text-gray-600">
              This password hasn't been accessed or modified yet.
            </p>
          </div>
        {:else}
          <div class="relative">
            <!-- Timeline line -->
            <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

            <div class="space-y-4">
              {#each history as event, index}
                <div class="relative flex gap-4 pl-10">
                  <!-- Timeline dot -->
                  <div class="absolute left-2 w-5 h-5 rounded-full bg-white border-2 border-gray-300 flex items-center justify-center text-xs z-10">
                    {getActionIcon(event.action)}
                  </div>

                  <!-- Content -->
                  <div class="flex-1 bg-gray-50 rounded-lg p-4">
                    <div class="flex items-start justify-between">
                      <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-xs font-medium {getActionColor(event.action)}">
                          {formatAction(event.action)}
                        </span>
                        <span class="text-sm text-gray-500">
                          {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                        </span>
                      </div>
                    </div>

                    <div class="mt-2 text-sm text-gray-600">
                      {#if event.details?.changes}
                        <div class="space-y-1">
                          {#each Object.entries(event.details.changes) as [field, change]}
                            <div class="flex items-center gap-2">
                              <span class="text-gray-400">{field}:</span>
                              <span class="line-through text-danger-600">{change.old}</span>
                              <span class="text-success-600">{change.new}</span>
                            </div>
                          {/each}
                        </div>
                      {:else if event.action === 'copied'}
                        <p>Password was copied to clipboard</p>
                      {:else if event.action === 'viewed'}
                        <p>Password details were viewed</p>
                      {/if}
                    </div>

                    <div class="mt-3 flex items-center gap-4 text-xs text-gray-400">
                      <span class="flex items-center gap-1">
                        <span>👤</span>
                        {event.username}
                      </span>
                      {#if event.ip_address}
                        <span class="flex items-center gap-1">
                          <span>🌐</span>
                          {event.ip_address}
                        </span>
                      {/if}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-200 flex justify-between items-center">
        <p class="text-sm text-gray-500">
          {history.length} {history.length === 1 ? 'event' : 'events'}
        </p>
        <button
          type="button"
          on:click={handleClose}
          class="btn btn-secondary"
        >
          Close
        </button>
      </div>
    </div>
  </div>
{/if}
