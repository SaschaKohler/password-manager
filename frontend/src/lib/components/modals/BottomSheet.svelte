<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { browser } from '$app/environment';

  export let isOpen = false;
  export let title = '';

  const dispatch = createEventDispatcher<{
    close: void;
  }>();

  let sheetElement: HTMLDivElement;
  let startY = 0;
  let currentY = 0;
  let isDragging = false;

  function handleClose() {
    isOpen = false;
    dispatch('close');
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      handleClose();
    }
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  }

  function handleTouchStart(event: TouchEvent) {
    startY = event.touches[0].clientY;
    isDragging = false;
  }

  function handleTouchMove(event: TouchEvent) {
    currentY = event.touches[0].clientY;
    const diff = startY - currentY;
    
    // Only start dragging if moving down significantly
    if (diff > 10) {
      isDragging = true;
    }
    
    if (isDragging) {
      event.preventDefault();
      const translateY = Math.max(0, diff);
      sheetElement.style.transform = `translateY(${translateY}px)`;
    }
  }

  function handleTouchEnd() {
    if (isDragging && startY - currentY > 100) {
      handleClose();
    }
    isDragging = false;
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen && browser}
  <div class="bottom-sheet-backdrop" on:click={handleBackdropClick}>
    <div
      class="bottom-sheet"
      bind:this={sheetElement}
      on:touchstart={handleTouchStart}
      on:touchmove={handleTouchMove}
      on:touchend={handleTouchEnd}
      role="dialog"
      aria-modal="true"
      aria-labelledby="sheet-title"
    >
      <div class="bottom-sheet-handle">
        <div class="bottom-sheet-handle-bar"></div>
      </div>

      <div class="bottom-sheet-header">
        <h2 id="sheet-title" class="bottom-sheet-title">{title}</h2>
        <button
          type="button"
          class="bottom-sheet-close"
          on:click={handleClose}
          aria-label="Close"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="bottom-sheet-body">
        <slot />
      </div>
    </div>
  </div>
{/if}

<style>
  .bottom-sheet-backdrop {
    position: fixed;
    inset: 0;
    background-color: var(--bg-overlay);
    backdrop-filter: blur(4px);
    z-index: var(--z-modal-backdrop);
    animation: fadeIn var(--transition-base) var(--transition-timing-default);
  }

  .bottom-sheet {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: var(--bg-primary);
    border-top-left-radius: var(--radius-2xl);
    border-top-right-radius: var(--radius-2xl);
    box-shadow: var(--shadow-2xl);
    max-height: 85vh;
    overflow: hidden;
    z-index: var(--z-modal);
    animation: slideUp var(--transition-base) var(--transition-timing-default);
  }

  .bottom-sheet-handle {
    display: flex;
    justify-content: center;
    padding: var(--space-2) var(--space-4);
    cursor: grab;
  }

  .bottom-sheet-handle:active {
    cursor: grabbing;
  }

  .bottom-sheet-handle-bar {
    width: 3rem;
    height: 0.25rem;
    background-color: var(--border-default);
    border-radius: var(--radius-full);
  }

  .bottom-sheet-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-6);
    border-bottom: 1px solid var(--border-default);
  }

  .bottom-sheet-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  .bottom-sheet-close {
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

  .bottom-sheet-close:hover {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
  }

  .bottom-sheet-close svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .bottom-sheet-body {
    padding: var(--space-6);
    overflow-y: auto;
    max-height: calc(85vh - 8rem);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideUp {
    from {
      transform: translateY(100%);
    }
    to {
      transform: translateY(0);
    }
  }

  /* Desktop - Hide bottom sheet */
  @media (min-width: 768px) {
    .bottom-sheet-backdrop {
      display: none;
    }
  }
</style>
