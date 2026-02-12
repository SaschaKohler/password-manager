<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { browser } from '$app/environment';

  export let isOpen = false;
  export let title = '';
  export let position: 'right' | 'left' = 'right';
  export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';

  const dispatch = createEventDispatcher<{
    close: void;
  }>();

  let panelElement: HTMLDivElement;

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

  // Focus trap
  function handleFocusIn(event: FocusEvent) {
    if (!panelElement) return;
    
    const focusableElements = panelElement.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
    
    if (event.relatedTarget && !panelElement.contains(event.relatedTarget as Node)) {
      firstElement?.focus();
    }
  }

  function handleTabKey(event: KeyboardEvent) {
    if (event.key !== 'Tab') return;
    
    const focusableElements = panelElement?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (!focusableElements) return;
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
    
    if (event.shiftKey) {
      if (document.activeElement === firstElement) {
        event.preventDefault();
        lastElement?.focus();
      }
    } else {
      if (document.activeElement === lastElement) {
        event.preventDefault();
        firstElement?.focus();
      }
    }
  }
</script>

<svelte:window on:keydown={handleTabKey} />

{#if isOpen && browser}
  <div class="slide-panel-backdrop" on:click={handleBackdropClick}>
    <div
      class="slide-panel slide-panel-{position} slide-panel-{size}"
      bind:this={panelElement}
      on:focusin={handleFocusIn}
      on:keydown={handleKeydown}
      role="dialog"
      aria-modal="true"
      aria-labelledby="panel-title"
    >
      <div class="slide-panel-header">
        <h2 id="panel-title" class="slide-panel-title">{title}</h2>
        <button
          type="button"
          class="slide-panel-close"
          on:click={handleClose}
          aria-label="Close"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="slide-panel-body">
        <slot />
      </div>
    </div>
  </div>
{/if}

<style>
  .slide-panel-backdrop {
    position: fixed;
    inset: 0;
    background-color: var(--bg-overlay);
    backdrop-filter: blur(4px);
    z-index: var(--z-modal-backdrop);
    animation: fadeIn var(--transition-base) var(--transition-timing-default);
  }

  .slide-panel {
    position: fixed;
    top: 0;
    bottom: 0;
    background-color: var(--bg-primary);
    box-shadow: var(--shadow-2xl);
    display: flex;
    flex-direction: column;
    animation: slideIn var(--transition-base) var(--transition-timing-default);
  }

  .slide-panel-right {
    right: 0;
    width: 100%;
    max-width: 32rem;
  }

  .slide-panel-left {
    left: 0;
    width: 100%;
    max-width: 32rem;
  }

  .slide-panel-sm {
    max-width: 24rem;
  }

  .slide-panel-lg {
    max-width: 48rem;
  }

  .slide-panel-xl {
    max-width: 64rem;
  }

  .slide-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-6);
    border-bottom: 1px solid var(--border-default);
  }

  .slide-panel-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  .slide-panel-close {
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

  .slide-panel-close:hover {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
  }

  .slide-panel-close svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .slide-panel-body {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-6);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(100%);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .slide-panel-left {
    animation-name: slideInLeft;
  }

  @keyframes slideInLeft {
    from {
      opacity: 0;
      transform: translateX(-100%);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  /* Mobile Adjustments */
  @media (max-width: 768px) {
    .slide-panel-right,
    .slide-panel-left {
      max-width: 100%;
    }

    .slide-panel-body {
      padding: var(--space-4);
    }
  }
</style>
