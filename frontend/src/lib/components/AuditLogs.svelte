<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { api } from '$lib/services/api';
  import { formatDistanceToNow } from 'date-fns';

  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let loading = true;
  let error: string | null = null;
  let logs: {
    id: number;
    user_id: number;
    username: string;
    action: string;
    password_id: number;
    password_title: string;
    details: Record<string, any>;
    ip_address: string;
    user_agent: string;
    timestamp: string;
  }[] = [];
  let page = 1;
  let pageSize = 20;
  let totalCount = 0;
  let actionFilter = '';
  let actionOptions = ['viewed', 'created', 'updated', 'deleted', 'copied', 'exported', 'shared', 'login', 'logout', '2fa_enabled', '2fa_disabled'];

  onMount(() => {
    if (isOpen) {
      loadLogs();
    }
  });

  $: if (isOpen) {
    loadLogs();
  }

  async function loadLogs() {
    loading = true;
    error = null;

    try {
      const result = await api.getAuditLogs({
        page,
        page_size: pageSize,
        action: actionFilter || undefined,
      });
      logs = result.results;
      totalCount = result.count;
    } catch (err: any) {
      error = err.message || 'Failed to load audit logs';
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
      'login': '🚪',
      'logout': '🚪',
      '2fa_enabled': '🔐',
      '2fa_disabled': '🔓',
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
      'login': 'bg-success-100 text-success-800',
      'logout': 'bg-gray-100 text-gray-800',
      '2fa_enabled': 'bg-success-100 text-success-800',
      '2fa_disabled': 'bg-warning-100 text-warning-800',
    };
    return colors[action.toLowerCase()] || 'bg-gray-100 text-gray-800';
  }

  function formatAction(action: string): string {
    return action.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  }

  function handlePageChange(newPage: number) {
    page = newPage;
    loadLogs();
  }
</script>

<svelte:window on:keydown={(e) => e.key === 'Escape' && handleClose()} />

{#if isOpen}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
              <span class="text-xl">📋</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Audit Logs</h2>
              <p class="text-sm text-gray-500">Track all account activity</p>
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

      <!-- Filters -->
      <div class="p-4 border-b border-gray-200 bg-gray-50">
        <div class="flex items-center gap-4">
          <div class="flex-1">
            <label for="action-filter" class="block text-sm font-medium text-gray-700 mb-1">
              Filter by Action
            </label>
            <select
              id="action-filter"
              class="form-input"
              bind:value={actionFilter}
              on:change={() => { page = 1; loadLogs(); }}
            >
              <option value="">All Actions</option>
              {#each actionOptions as action}
                <option value={action}>{formatAction(action)}</option>
              {/each}
            </select>
          </div>
          <div class="flex items-end">
            <button class="btn btn-secondary" on:click={() => { actionFilter = ''; page = 1; loadLogs(); }}>
              🔄 Clear Filter
            </button>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6">
        {#if loading}
          <div class="flex flex-col items-center justify-center py-12 gap-4">
            <div class="w-8 h-8 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
            <p class="text-gray-600">Loading audit logs...</p>
          </div>
        {:else if error}
          <div class="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p class="text-danger-800">{error}</p>
            <button class="btn btn-secondary mt-4" on:click={loadLogs}>
              🔄 Retry
            </button>
          </div>
        {:else if logs.length === 0}
          <div class="flex flex-col items-center justify-center py-12 gap-4 text-center">
            <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
              <span class="text-3xl">📭</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900">No Logs Found</h3>
            <p class="text-gray-600">
              {#if actionFilter}
                No {formatAction(actionFilter).toLowerCase()} events found.
              {:else}
                No audit logs available yet.
              {/if}
            </p>
          </div>
        {:else}
          <!-- Logs Table -->
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-200">
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">Action</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">Details</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">User</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">IP Address</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">Time</th>
                </tr>
              </thead>
              <tbody>
                {#each logs as log}
                  <tr class="border-b border-gray-100 hover:bg-gray-50">
                    <td class="py-3 px-4">
                      <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium {getActionColor(log.action)}">
                        <span class="mr-1">{getActionIcon(log.action)}</span>
                        {formatAction(log.action)}
                      </span>
                    </td>
                    <td class="py-3 px-4">
                      <span class="text-sm text-gray-900">
                        {log.password_title || 'N/A'}
                      </span>
                    </td>
                    <td class="py-3 px-4">
                      <span class="text-sm text-gray-600">{log.username}</span>
                    </td>
                    <td class="py-3 px-4">
                      <span class="text-sm text-gray-500 font-mono">{log.ip_address}</span>
                    </td>
                    <td class="py-3 px-4">
                      <span class="text-sm text-gray-500" title={new Date(log.timestamp).toLocaleString()}>
                        {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                      </span>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          {#if totalCount > pageSize}
            <div class="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
              <p class="text-sm text-gray-500">
                Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, totalCount)} of {totalCount} logs
              </p>
              <div class="flex gap-2">
                <button
                  class="btn btn-secondary"
                  disabled={page === 1}
                  on:click={() => handlePageChange(page - 1)}
                >
                  ← Previous
                </button>
                <button
                  class="btn btn-secondary"
                  disabled={page * pageSize >= totalCount}
                  on:click={() => handlePageChange(page + 1)}
                >
                  Next →
                </button>
              </div>
            </div>
          {/if}
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-200 flex justify-between items-center">
        <p class="text-sm text-gray-500">
          🔒 Logs are retained for 90 days
        </p>
        <button
          type="button"
          on:click={handleClose}
          class="btn btn-primary"
        >
          Close
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .font-mono {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
  }
</style>
