<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { pagination, getPageNumbers } from '$lib/stores/pagination';

  export let currentPage: number = 1;
  export let totalPages: number = 1;
  export let totalCount: number = 0;
  export let pageSize: number = 20;
  export let showPageSizeSelector: boolean = true;
  export let pageSizeOptions: number[] = [10, 20, 50, 100];

  const dispatch = createEventDispatcher<{
    pageChange: number;
    pageSizeChange: number;
  }>();

  $: pageNumbers = getPageNumbers(currentPage, totalPages);

  function handlePageClick(page: number | string) {
    if (typeof page === 'number') {
      dispatch('pageChange', page);
    }
  }

  function handlePageSizeChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    const newSize = parseInt(select.value, 10);
    dispatch('pageSizeChange', newSize);
  }

  function handlePrevious() {
    if (currentPage > 1) {
      dispatch('pageChange', currentPage - 1);
    }
  }

  function handleNext() {
    if (currentPage < totalPages) {
      dispatch('pageChange', currentPage + 1);
    }
  }

  $: startItem = totalCount === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  $: endItem = Math.min(currentPage * pageSize, totalCount);
</script>

<div class="pagination-container">
  <!-- Page Size Selector -->
  {#if showPageSizeSelector && totalCount > 0}
    <div class="page-size-selector">
      <label for="page-size" class="text-sm text-gray-600 dark:text-gray-400">
        Items per page:
      </label>
      <select
        id="page-size"
        class="page-size-select"
        value={pageSize}
        on:change={handlePageSizeChange}
      >
        {#each pageSizeOptions as size}
          <option value={size}>{size}</option>
        {/each}
      </select>
    </div>
  {/if}

  <!-- Results Info -->
  {#if totalCount > 0}
    <div class="results-info">
      <span class="text-sm text-gray-600 dark:text-gray-400">
        Showing {startItem} to {endItem} of {totalCount} results
      </span>
    </div>
  {/if}

  <!-- Page Numbers -->
  {#if totalPages > 1}
    <nav class="pagination-nav" aria-label="Pagination">
      <!-- Previous Button -->
      <button
        type="button"
        class="pagination-btn pagination-btn-nav"
        disabled={currentPage === 1}
        on:click={handlePrevious}
        aria-label="Previous page"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Page Numbers -->
      {#each pageNumbers as page}
        {#if page === '...'}
          <span class="pagination-ellipsis">...</span>
        {:else}
          <button
            type="button"
            class="pagination-btn pagination-btn-number"
            class:pagination-btn-active={page === currentPage}
            on:click={() => handlePageClick(page)}
            aria-label="Page {page}"
            aria-current={page === currentPage ? 'page' : undefined}
          >
            {page}
          </button>
        {/if}
      {/each}

      <!-- Next Button -->
      <button
        type="button"
        class="pagination-btn pagination-btn-nav"
        disabled={currentPage === totalPages}
        on:click={handleNext}
        aria-label="Next page"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </nav>
  {/if}
</div>

<style>
  .pagination-container {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem 0;
    border-top: 1px solid var(--border-color, #e5e7eb);
  }

  .page-size-selector {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .page-size-select {
    padding: 0.375rem 0.75rem;
    border: 1px solid var(--border-color, #d1d5db);
    border-radius: 0.375rem;
    background-color: var(--bg-color, #fff);
    color: var(--text-color, #374151);
    font-size: 0.875rem;
    cursor: pointer;
  }

  .page-size-select:focus {
    outline: none;
    border-color: var(--primary-color, #2563eb);
    ring: 2px solid var(--primary-color, #2563eb);
  }

  .results-info {
    flex: 1;
    text-align: center;
  }

  .pagination-nav {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .pagination-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 2.25rem;
    height: 2.25rem;
    padding: 0 0.5rem;
    border: 1px solid var(--border-color, #d1d5db);
    border-radius: 0.375rem;
    background-color: var(--bg-color, #fff);
    color: var(--text-color, #374151);
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .pagination-btn:hover:not(:disabled) {
    background-color: var(--hover-bg, #f3f4f6);
  }

  .pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .pagination-btn-nav {
    padding: 0 0.75rem;
  }

  .pagination-btn-number {
    min-width: 2.25rem;
  }

  .pagination-btn-active {
    background-color: var(--primary-color, #2563eb);
    border-color: var(--primary-color, #2563eb);
    color: #fff;
  }

  .pagination-btn-active:hover {
    background-color: var(--primary-hover, #1d4ed8);
  }

  .pagination-ellipsis {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 2.25rem;
    height: 2.25rem;
    padding: 0 0.5rem;
    color: var(--text-muted, #9ca3af);
    font-size: 0.875rem;
  }

  @media (max-width: 640px) {
    .pagination-container {
      flex-direction: column;
      gap: 0.75rem;
    }

    .results-info {
      order: -1;
    }
  }
</style>
