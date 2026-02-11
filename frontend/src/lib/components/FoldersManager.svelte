<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { api } from '$lib/services/api';
  import type { PasswordEntry } from '$lib/types/password';

  export let isOpen = false;
  export let passwords: PasswordEntry[] = [];

  const dispatch = createEventDispatcher();

  let loading = true;
  let error: string | null = null;
  let folders: {
    id: number;
    name: string;
    icon: string;
    color: string;
    password_count: number;
    created_at: string;
    updated_at: string;
    parent_id: number | null;
  }[] = [];
  let selectedFolder: number | null = null;
  let showCreateModal = false;
  let newFolderName = '';
  let newFolderIcon = '📁';
  let newFolderColor = '#3b82f6';
  let icons = ['📁', '📂', '🏠', '💼', '📧', '🔐', '🎯', '💰', '🎮', '📚', '🎵', '🍽️', '✈️', '🚗', '🏥', '🎓'];
  let colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#ef4444', '#f59e0b', '#22c55e', '#14b8a6', '#6366f1'];

  onMount(() => {
    if (isOpen) {
      loadFolders();
    }
  });

  $: if (isOpen) {
    loadFolders();
  }

  async function loadFolders() {
    loading = true;
    error = null;

    try {
      folders = await api.getFolders();
    } catch (err: any) {
      error = err.message || 'Failed to load folders';
    } finally {
      loading = false;
    }
  }

  async function handleCreateFolder() {
    if (!newFolderName.trim()) return;

    try {
      const folder = await api.createFolder({
        name: newFolderName.trim(),
        icon: newFolderIcon,
        color: newFolderColor,
      });
      folders = [...folders, { ...folder, password_count: 0, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), parent_id: null }];
      showCreateModal = false;
      newFolderName = '';
      dispatch('folder-created', folder);
    } catch (err: any) {
      error = err.message || 'Failed to create folder';
    }
  }

  async function handleMoveToFolder(passwordId: number, folderId: number | null) {
    try {
      if (folderId === null) {
        // Moving out of folder - this would be handled by the parent
        dispatch('move-to-root', passwordId);
      } else {
        await api.moveToFolder(passwordId, folderId);
        dispatch('move', { passwordId, folderId });
      }
      selectedFolder = null;
    } catch (err: any) {
      error = err.message || 'Failed to move password';
    }
  }

  function handleClose() {
    isOpen = false;
    dispatch('close');
  }

  function filterPasswordsByFolder(folderId: number | null): PasswordEntry[] {
    if (folderId === null) {
      // Return passwords not in any folder
      return passwords.filter(p => !p.category); // Using category as folder for now
    }
    return passwords.filter(p => p.category === folders.find(f => f.id === folderId)?.name);
  }

  function handleSelectFolder(folderId: number | null) {
    selectedFolder = folderId;
    dispatch('select', folderId);
  }
</script>

<svelte:window on:keydown={(e) => e.key === 'Escape' && handleClose()} />

{#if isOpen}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <span class="text-xl">📁</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Folders</h2>
              <p class="text-sm text-gray-500">Organize your passwords</p>
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
      <div class="flex-1 overflow-y-auto p-6">
        {#if loading}
          <div class="flex flex-col items-center justify-center py-12 gap-4">
            <div class="w-8 h-8 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
            <p class="text-gray-600">Loading folders...</p>
          </div>
        {:else if error}
          <div class="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p class="text-danger-800">{error}</p>
            <button class="btn btn-secondary mt-4" on:click={loadFolders}>
              🔄 Retry
            </button>
          </div>
        {:else}
          <!-- Folder List -->
          <div class="space-y-2">
            <!-- All Passwords -->
            <button
              class="w-full flex items-center gap-3 p-3 rounded-lg transition-colors {selectedFolder === null ? 'bg-primary-50 border border-primary-200' : 'hover:bg-gray-50'}"
              on:click={() => handleSelectFolder(null)}
            >
              <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                <span class="text-xl">📋</span>
              </div>
              <div class="flex-1 text-left">
                <p class="font-medium text-gray-900">All Passwords</p>
                <p class="text-sm text-gray-500">{passwords.length} passwords</p>
              </div>
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>

            <!-- Folders -->
            {#each folders as folder}
              <button
                class="w-full flex items-center gap-3 p-3 rounded-lg transition-colors {selectedFolder === folder.id ? 'bg-primary-50 border border-primary-200' : 'hover:bg-gray-50'}"
                on:click={() => handleSelectFolder(folder.id)}
              >
                <div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background-color: {folder.color}20">
                  <span class="text-xl">{folder.icon}</span>
                </div>
                <div class="flex-1 text-left">
                  <p class="font-medium text-gray-900">{folder.name}</p>
                  <p class="text-sm text-gray-500">{folder.password_count} passwords</p>
                </div>
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            {/each}

            <!-- Create Folder -->
            {#if !showCreateModal}
              <button
                class="w-full flex items-center gap-3 p-3 rounded-lg border border-dashed border-gray-300 hover:bg-gray-50 transition-colors text-gray-500"
                on:click={() => showCreateModal = true}
              >
                <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                  <span class="text-xl">➕</span>
                </div>
                <div class="flex-1 text-left">
                  <p class="font-medium">Create New Folder</p>
                </div>
              </button>
            {/if}
          </div>

          <!-- Create Folder Form -->
          {#if showCreateModal}
            <div class="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 class="font-medium text-gray-900 mb-3">Create New Folder</h4>
              
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
                  <input
                    type="text"
                    class="form-input"
                    bind:value={newFolderName}
                    placeholder="Folder name"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Icon</label>
                  <div class="flex flex-wrap gap-2">
                    {#each icons as icon}
                      <button
                        type="button"
                        class="w-8 h-8 rounded-lg flex items-center justify-center text-lg {newFolderIcon === icon ? 'bg-primary-100 border border-primary-300' : 'bg-white border border-gray-200 hover:bg-gray-50'}"
                        on:click={() => newFolderIcon = icon}
                      >
                        {icon}
                      </button>
                    {/each}
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
                  <div class="flex flex-wrap gap-2">
                    {#each colors as color}
                      <button
                        type="button"
                        class="w-8 h-8 rounded-full {newFolderColor === color ? 'ring-2 ring-offset-2 ring-gray-400' : ''}"
                        style="background-color: {color}"
                        on:click={() => newFolderColor = color}
                      />
                    {/each}
                  </div>
                </div>

                <div class="flex gap-2 pt-2">
                  <button
                    type="button"
                    class="btn btn-secondary flex-1"
                    on:click={() => { showCreateModal = false; newFolderName = ''; }}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    class="btn btn-primary flex-1"
                    disabled={!newFolderName.trim()}
                    on:click={handleCreateFolder}
                  >
                    Create
                  </button>
                </div>
              </div>
            </div>
          {/if}
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-200 flex justify-between items-center">
        <p class="text-sm text-gray-500">
          {folders.length} folders
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
