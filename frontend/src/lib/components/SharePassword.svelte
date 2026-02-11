<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { api } from '$lib/services/api';
  import { formatDistanceToNow } from 'date-fns';
  import type { PasswordEntry } from '$lib/types/password';

  export let isOpen = false;
  export let password: PasswordEntry | null = null;

  const dispatch = createEventDispatcher();

  let loading = true;
  let error: string | null = null;
  let success: string | null = null;
  let shareEmail = '';
  let sharePermission: 'view' | 'edit' = 'view';
  let expiryDays = 7;
  let sharedData: {
    shared_with_me: {
      id: number;
      password_id: number;
      password_title: string;
      shared_by: number;
      shared_by_username: string;
      permission: string;
      shared_at: string;
      expires_at: string | null;
    }[];
    shared_by_me: {
      id: number;
      password_id: number;
      password_title: string;
      shared_with: number;
      shared_with_username: string;
      permission: string;
      shared_at: string;
      expires_at: string | null;
    }[];
  } | null = null;

  $: if (isOpen) {
    loadSharedData();
  }

  async function loadSharedData() {
    loading = true;
    error = null;

    try {
      sharedData = await api.getSharedPasswords();
    } catch (err: any) {
      error = err.message || 'Failed to load sharing data';
    } finally {
      loading = false;
    }
  }

  async function handleShare() {
    if (!shareEmail.trim()) {
      error = 'Please enter an email address';
      return;
    }

    if (!password) return;

    loading = true;
    error = null;
    success = null;

    try {
      const expiryDate = new Date();
      expiryDate.setDate(expiryDate.getDate() + expiryDays);

      await api.sharePassword({
        password_id: password.id,
        user_id: 0, // Backend will resolve by email
        permission: sharePermission,
        expires_at: expiryDate.toISOString(),
      });

      success = `Password shared with ${shareEmail}`;
      shareEmail = '';
      await loadSharedData();
      dispatch('shared');
    } catch (err: any) {
      error = err.message || 'Failed to share password';
    } finally {
      loading = false;
    }
  }

  async function handleRevokeShare(shareId: number) {
    if (!confirm('Are you sure you want to revoke this sharing?')) return;

    loading = true;
    error = null;

    try {
      await api.revokeSharing(shareId);
      await loadSharedData();
      success = 'Sharing revoked successfully';
      dispatch('revoked');
    } catch (err: any) {
      error = err.message || 'Failed to revoke sharing';
    } finally {
      loading = false;
    }
  }

  function handleClose() {
    isOpen = false;
    shareEmail = '';
    error = null;
    success = null;
    dispatch('close');
  }

  function getPermissionBadgeColor(permission: string): string {
    return permission === 'edit' ? 'bg-warning-100 text-warning-800' : 'bg-primary-100 text-primary-800';
  }
</script>

<svelte:window on:keydown={(e) => e.key === 'Escape' && handleClose()} />

{#if isOpen && password}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
              <span class="text-xl">🔗</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Share Password</h2>
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
      <div class="p-6 space-y-6">
        {#if error}
          <div class="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p class="text-danger-800 text-sm">{error}</p>
          </div>
        {/if}

        {#if success}
          <div class="bg-success-50 border border-success-200 rounded-lg p-4">
            <p class="text-success-800 text-sm">{success}</p>
          </div>
        {/if}

        {#if loading}
          <div class="flex flex-col items-center justify-center py-8 gap-4">
            <div class="w-8 h-8 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
            <p class="text-gray-600">Loading...</p>
          </div>
        {:else}
          <!-- Share Form -->
          <div class="space-y-4">
            <h3 class="font-medium text-gray-900">Share with someone</h3>
            
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Email address
                </label>
                <input
                  type="email"
                  class="form-input"
                  bind:value={shareEmail}
                  placeholder="user@example.com"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Permission
                </label>
                <div class="flex gap-4">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="permission"
                      value="view"
                      bind:group={sharePermission}
                      class="text-primary-600 focus:ring-primary-500"
                    />
                    <div>
                      <span class="font-medium text-gray-900">View only</span>
                      <p class="text-xs text-gray-500">Can view but not edit</p>
                    </div>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="permission"
                      value="edit"
                      bind:group={sharePermission}
                      class="text-primary-600 focus:ring-primary-500"
                    />
                    <div>
                      <span class="font-medium text-gray-900">Can edit</span>
                      <p class="text-xs text-gray-500">Can view and edit</p>
                    </div>
                  </label>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Expires in
                </label>
                <select class="form-input" bind:value={expiryDays}>
                  <option value={1}>1 day</option>
                  <option value={7}>7 days</option>
                  <option value={30}>30 days</option>
                  <option value={90}>90 days</option>
                  <option value={365}>1 year</option>
                </select>
              </div>

              <button
                type="button"
                class="btn btn-primary w-full"
                on:click={handleShare}
                disabled={loading}
              >
                {#if loading}
                  <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {/if}
                🔗 Share Password
              </button>
            </div>
          </div>

          <!-- Shared By Me -->
          {#if sharedData?.shared_by_me && sharedData.shared_by_me.length > 0}
            <div class="border-t border-gray-200 pt-6">
              <h3 class="font-medium text-gray-900 mb-4">Shared by you</h3>
              <div class="space-y-3">
                {#each sharedData.shared_by_me as share}
                  <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                        <span class="text-sm">👤</span>
                      </div>
                      <div>
                        <p class="font-medium text-gray-900">{share.shared_with_username}</p>
                        <p class="text-xs text-gray-500">
                          {share.expires_at 
                            ? `Expires ${formatDistanceToNow(new Date(share.expires_at), { addSuffix: true })}`
                            : 'Never expires'
                          }
                        </p>
                      </div>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="px-2 py-1 rounded text-xs font-medium {getPermissionBadgeColor(share.permission)}">
                        {share.permission}
                      </span>
                      <button
                        type="button"
                        class="text-gray-400 hover:text-danger-600"
                        on:click={() => handleRevokeShare(share.id)}
                        title="Revoke sharing"
                      >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          <!-- Shared With Me -->
          {#if sharedData?.shared_with_me && sharedData.shared_with_me.length > 0}
            <div class="border-t border-gray-200 pt-6">
              <h3 class="font-medium text-gray-900 mb-4">Shared with you</h3>
              <div class="space-y-3">
                {#each sharedData.shared_with_me as share}
                  <div class="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-full bg-success-100 flex items-center justify-center">
                        <span class="text-sm">👤</span>
                      </div>
                      <div>
                        <p class="font-medium text-gray-900">{share.shared_by_username}</p>
                        <p class="text-xs text-gray-500">
                          {share.password_title}
                        </p>
                      </div>
                    </div>
                    <span class="px-2 py-1 rounded text-xs font-medium {getPermissionBadgeColor(share.permission)}">
                      {share.permission}
                    </span>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-200 flex justify-between items-center">
        <p class="text-xs text-gray-500">
          🔒 Shared passwords are encrypted
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
