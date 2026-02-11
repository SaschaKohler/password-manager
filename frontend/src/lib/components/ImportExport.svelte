<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { api } from '$lib/services/api';

  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let importFile: File | null = null;
  let importLoading = false;
  let exportLoading = false;
  let error: string | null = null;
  let success: string | null = null;
  let mergeStrategy: 'skip' | 'overwrite' | 'merge' = 'skip';
  let importResult: { imported: number; skipped: number; errors: string[] } | null = null;

  async function handleImport() {
    if (!importFile) {
      error = 'Please select a file to import';
      return;
    }

    importLoading = true;
    error = null;
    success = null;
    importResult = null;

    try {
      const result = await api.importPasswords(importFile, mergeStrategy);
      importResult = result;
      success = `Successfully imported ${result.imported} passwords`;
      
      if (result.skipped > 0) {
        success += ` (skipped ${result.skipped} duplicates)`;
      }
      
      if (result.errors.length > 0) {
        error = `Import completed with ${result.errors.length} errors`;
      }

      dispatch('import-complete', result);
    } catch (err: any) {
      error = err.message || 'Import failed';
    } finally {
      importLoading = false;
    }
  }

  async function handleExport(format: 'csv' | 'json') {
    exportLoading = true;
    error = null;
    success = null;

    try {
      const blob = await api.exportPasswords(format);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `passwords.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      success = `Passwords exported as ${format.toUpperCase()}`;
    } catch (err: any) {
      error = err.message || 'Export failed';
    } finally {
      exportLoading = false;
    }
  }

  function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.name.endsWith('.csv') && !file.name.endsWith('.json')) {
        error = 'Please select a CSV or JSON file';
        importFile = null;
        return;
      }
      
      importFile = file;
      error = null;
    }
  }

  function handleClose() {
    isOpen = false;
    error = null;
    success = null;
    importResult = null;
    importFile = null;
    
    // Reset file input
    const fileInput = document.getElementById('import-file') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl max-w-lg w-full">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">Import/Export Passwords</h2>
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

        <!-- Import Section -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Import Passwords</h3>
          
          <div class="space-y-3">
            <div>
              <label for="import-file" class="block text-sm font-medium text-gray-700 mb-2">
                Select File (CSV or JSON)
              </label>
              <input
                id="import-file"
                type="file"
                accept=".csv,.json"
                on:change={handleFileSelect}
                class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              />
            </div>

            {#if importFile}
              <div class="text-sm text-gray-600">
                Selected: <span class="font-medium">{importFile.name}</span> ({(importFile.size / 1024).toFixed(1)} KB)
              </div>
            {/if}

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Merge Strategy
              </label>
              <div class="space-y-2">
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="radio"
                    name="merge-strategy"
                    value="skip"
                    bind:group={mergeStrategy}
                    class="text-primary-600 focus:ring-primary-500"
                  />
                  <div>
                    <span class="font-medium">Skip duplicates</span>
                    <p class="text-xs text-gray-500">Don't import passwords with identical titles</p>
                  </div>
                </label>
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="radio"
                    name="merge-strategy"
                    value="overwrite"
                    bind:group={mergeStrategy}
                    class="text-primary-600 focus:ring-primary-500"
                  />
                  <div>
                    <span class="font-medium">Overwrite duplicates</span>
                    <p class="text-xs text-gray-500">Replace existing passwords with same title</p>
                  </div>
                </label>
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="radio"
                    name="merge-strategy"
                    value="merge"
                    bind:group={mergeStrategy}
                    class="text-primary-600 focus:ring-primary-500"
                  />
                  <div>
                    <span class="font-medium">Merge duplicates</span>
                    <p class="text-xs text-gray-500">Update existing passwords with new data</p>
                  </div>
                </label>
              </div>
            </div>

            <button
              on:click={handleImport}
              class="btn btn-primary w-full"
              disabled={!importFile || importLoading}
            >
              {#if importLoading}
                <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              {/if}
              Import Passwords
            </button>
          </div>

          {#if importResult}
            <div class="bg-gray-50 rounded-lg p-4 text-sm">
              <h4 class="font-medium text-gray-900 mb-2">Import Results:</h4>
              <ul class="space-y-1 text-gray-600">
                <li>✅ Imported: {importResult.imported}</li>
                <li>⏭️ Skipped: {importResult.skipped}</li>
                {#if importResult.errors.length > 0}
                  <li>❌ Errors: {importResult.errors.length}</li>
                  <ul class="mt-1 ml-4 space-y-1">
                    {#each importResult.errors as error}
                      <li class="text-danger-600 text-xs">• {error}</li>
                    {/each}
                  </ul>
                {/if}
              </ul>
            </div>
          {/if}
        </div>

        <!-- Export Section -->
        <div class="space-y-4 border-t border-gray-200 pt-6">
          <h3 class="text-lg font-medium text-gray-900">Export Passwords</h3>
          
          <div class="text-sm text-gray-600 mb-4">
            Export all your passwords in CSV or JSON format for backup or migration.
          </div>

          <div class="grid grid-cols-2 gap-3">
            <button
              on:click={() => handleExport('csv')}
              class="btn btn-secondary"
              disabled={exportLoading}
            >
              {#if exportLoading}
                <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              {/if}
              📄 Export CSV
            </button>
            <button
              on:click={() => handleExport('json')}
              class="btn btn-secondary"
              disabled={exportLoading}
            >
              {#if exportLoading}
                <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              {/if}
              📋 Export JSON
            </button>
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
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
  </div>
{/if}
