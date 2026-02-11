<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';

  // Theme store
  const theme = writable<'light' | 'dark'>('light');

  onMount(() => {
    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
    setTheme(initialTheme);

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light');
      }
    });
  });

  function setTheme(newTheme: 'light' | 'dark') {
    theme.set(newTheme);
    localStorage.setItem('theme', newTheme);
    
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  function toggleTheme() {
    const newTheme = $theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleTheme();
    }
  }
</script>

<button
  type="button"
  class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
  class:bg-primary-600={$theme === 'dark'}
  class:bg-gray-200={$theme === 'light'}
  on:click={toggleTheme}
  on:keydown={handleKeydown}
  role="switch"
  aria-label="Toggle theme"
  aria-checked={$theme === 'dark'}
>
  <span
    class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm"
    class:translate-x-6={$theme === 'dark'}
    class:translate-x-1={$theme === 'light'}
  />
</button>

<span class="ml-2 text-sm { $theme === 'dark' ? 'text-gray-300' : 'text-gray-700' }">
  {#if $theme === 'dark'}
    🌙
  {:else}
    ☀️
  {/if}
</span>
