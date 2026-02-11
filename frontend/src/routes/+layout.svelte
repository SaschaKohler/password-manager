<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import favicon from '$lib/assets/favicon.svg';
  import '../app.css';

  let { children } = $props();

  onMount(async () => {
    // Check authentication status on app load
    await auth.checkAuth();
    
    // Redirect authenticated users away from auth pages
    if ($auth.isAuthenticated) {
      const currentPath = window.location.pathname;
      if (currentPath === '/login' || currentPath === '/register') {
        await goto('/');
      }
    }
  });
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
