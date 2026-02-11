<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import '../app.css';

  onMount(async () => {
    // Wait for client-side hydration
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // Check authentication status on app load
    await auth.checkAuth();
    
    // Redirect authenticated users away from auth pages
    if ($auth.isAuthenticated) {
      const currentPath = window.location.pathname;
      if (currentPath === '/login' || currentPath === '/register') {
        goto('/');
      }
    }
  });
</script>

<svelte:head>
  <link rel="icon" href="/favicon.ico" />
</svelte:head>

<slot />
