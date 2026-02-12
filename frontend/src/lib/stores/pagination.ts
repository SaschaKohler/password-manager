import { writable } from 'svelte/store';

interface PaginationState {
  currentPage: number;
  totalPages: number;
  totalCount: number;
  pageSize: number;
}

export function createPaginationStore(initialState: Partial<PaginationState> = {}) {
  const defaultState: PaginationState = {
    currentPage: 1,
    totalPages: 1,
    totalCount: 0,
    pageSize: 20,
    ...initialState,
  };

  const { subscribe, set, update } = writable<PaginationState>(defaultState);

  return {
    subscribe,
    
    setPage(page: number) {
      update((state: PaginationState) => ({
        ...state,
        currentPage: Math.max(1, Math.min(page, state.totalPages)),
      }));
    },
    
    nextPage() {
      update((state: PaginationState) => ({
        ...state,
        currentPage: Math.min(state.currentPage + 1, state.totalPages),
      }));
    },
    
    prevPage() {
      update((state: PaginationState) => ({
        ...state,
        currentPage: Math.max(state.currentPage - 1, 1),
      }));
    },
    
    setPageSize(size: number) {
      update((state: PaginationState) => ({
        ...state,
        pageSize: size,
        currentPage: 1, // Reset to first page
      }));
    },
    
    setTotalPages(totalPages: number) {
      update((state: PaginationState) => ({
        ...state,
        totalPages,
      }));
    },
    
    setTotalCount(count: number) {
      update((state: PaginationState) => ({
        ...state,
        totalCount: count,
        totalPages: Math.ceil(count / state.pageSize),
      }));
    },
    
    reset() {
      set(defaultState);
    },
  };
}

export const pagination = createPaginationStore();

export function getPageNumbers(currentPage: number, totalPages: number, maxVisible: number = 5): (number | string)[] {
  const pages: (number | string)[] = [];
  
  if (totalPages <= maxVisible * 2 + 1) {
    // Show all pages if total is small
    for (let i = 1; i <= totalPages; i++) {
      pages.push(i);
    }
  } else {
    // Always show first page
    pages.push(1);
    
    // Calculate range around current page
    const start = Math.max(2, currentPage - Math.floor(maxVisible / 2));
    const end = Math.min(totalPages - 1, currentPage + Math.floor(maxVisible / 2));
    
    // Add ellipsis if there's a gap at the start
    if (start > 2) {
      pages.push('...');
    }
    
    // Add pages around current
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    // Add ellipsis if there's a gap at the end
    if (end < totalPages - 1) {
      pages.push('...');
    }
    
    // Always show last page
    if (totalPages > 1) {
      pages.push(totalPages);
    }
  }
  
  return pages;
}
