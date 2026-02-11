<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let email = '';
  let username = '';
  let password = '';
  let confirmPassword = '';
  let masterPassword = '';
  let firstName = '';
  let lastName = '';
  let loading = false;
  let showPassword = false;
  let showConfirmPassword = false;
  let showMasterPassword = false;

  let errors: Record<string, string> = {};

  // Check if user is already authenticated and redirect
  onMount(async () => {
    if ($auth.isAuthenticated) {
      await goto('/');
    }
  });

  // Watch for authentication changes
  $: if ($auth.isAuthenticated) {
    goto('/');
  }

  function validateForm(): boolean {
    errors = {};

    if (!email) errors.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = 'Invalid email format';

    if (!username) errors.username = 'Username is required';
    else if (username.length < 3) errors.username = 'Username must be at least 3 characters';

    if (!password) errors.password = 'Password is required';
    else if (password.length < 8) errors.password = 'Password must be at least 8 characters';

    if (!confirmPassword) errors.confirmPassword = 'Please confirm your password';
    else if (password !== confirmPassword) errors.confirmPassword = 'Passwords do not match';

    if (!masterPassword) errors.masterPassword = 'Master password is required';
    else if (masterPassword.length < 12) errors.masterPassword = 'Master password must be at least 12 characters';

    if (!firstName) errors.firstName = 'First name is required';
    if (!lastName) errors.lastName = 'Last name is required';

    return Object.keys(errors).length === 0;
  }

  function clearBackendErrors() {
    // Clear only backend validation errors, keep client-side validation errors
    const backendErrorFields = ['email', 'username'];
    backendErrorFields.forEach(field => {
      if (errors[field] && errors[field].includes('already exists')) {
        delete errors[field];
      }
    });
  }

  async function handleRegister() {
    if (!validateForm()) return;

    loading = true;
    try {
      const result = await auth.register({
        email,
        username,
        password,
        master_password: masterPassword,
      });
      
      if (result.success) {
        // Successful registration - redirect to dashboard
        await goto('/');
      } else {
        // Registration failed - handle field-specific errors
        if (result.fieldErrors) {
          errors = { ...errors, ...result.fieldErrors };
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
    } finally {
      loading = false;
    }
  }

  function togglePassword(field: 'password' | 'confirmPassword' | 'masterPassword') {
    if (field === 'password') showPassword = !showPassword;
    else if (field === 'confirmPassword') showConfirmPassword = !showConfirmPassword;
    else showMasterPassword = !showMasterPassword;
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleRegister();
    }
  }

  function clearFieldError(field: string) {
    if (errors[field]) {
      errors = { ...errors, [field]: undefined };
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <div>
      <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
        <span class="text-2xl">🔐</span>
      </div>
      <h2 class="mt-6 text-center text-3xl font-bold text-gray-900">
        Create your account
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Or
        <a href="/login" class="font-medium text-primary-600 hover:text-primary-500">
          sign in to your existing account
        </a>
      </p>
    </div>

    <form class="mt-8 space-y-6" on:submit|preventDefault={handleRegister}>
      {#if $auth.error}
        <div class="bg-danger-50 border border-danger-200 rounded-lg p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <span class="text-danger-400">⚠️</span>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-danger-800">Error</h3>
              <div class="mt-2 text-sm text-danger-700">
                {$auth.error}
              </div>
            </div>
          </div>
        </div>
      {/if}

      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="firstName" class="block text-sm font-medium text-gray-700">
              First Name
            </label>
            <div class="mt-1">
              <input
                id="firstName"
                name="firstName"
                type="text"
                autocomplete="given-name"
                required
                class="form-input"
                placeholder="First name"
                bind:value={firstName}
                class:border-danger-500={errors.firstName}
                on:keydown={handleKeydown}
              />
              {#if errors.firstName}
                <p class="mt-1 text-sm text-danger-600">{errors.firstName}</p>
              {/if}
            </div>
          </div>

          <div>
            <label for="lastName" class="block text-sm font-medium text-gray-700">
              Last Name
            </label>
            <div class="mt-1">
              <input
                id="lastName"
                name="lastName"
                type="text"
                autocomplete="family-name"
                required
                class="form-input"
                placeholder="Last name"
                bind:value={lastName}
                class:border-danger-500={errors.lastName}
                on:keydown={handleKeydown}
              />
              {#if errors.lastName}
                <p class="mt-1 text-sm text-danger-600">{errors.lastName}</p>
              {/if}
            </div>
          </div>
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">
            Email address
          </label>
          <div class="mt-1">
            <input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="form-input"
              placeholder="Enter your email"
              bind:value={email}
              class:border-danger-500={errors.email}
              on:keydown={handleKeydown}
              on:input={() => clearFieldError('email')}
            />
            {#if errors.email}
              <p class="mt-1 text-sm text-danger-600">{errors.email}</p>
            {/if}
          </div>
        </div>

        <div>
          <label for="username" class="block text-sm font-medium text-gray-700">
            Username
          </label>
          <div class="mt-1">
            <input
              id="username"
              name="username"
              type="text"
              autocomplete="username"
              required
              class="form-input"
              placeholder="Choose a username"
              bind:value={username}
              class:border-danger-500={errors.username}
              on:keydown={handleKeydown}
              on:input={() => clearFieldError('username')}
            />
            {#if errors.username}
              <p class="mt-1 text-sm text-danger-600">{errors.username}</p>
            {/if}
          </div>
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">
            Password
          </label>
          <div class="mt-1 relative">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autocomplete="new-password"
              required
              class="form-input pr-10"
              placeholder="Create a password"
              bind:value={password}
              class:border-danger-500={errors.password}
              on:keydown={handleKeydown}
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
              on:click={() => togglePassword('password')}
            >
              <span class="text-gray-400 hover:text-gray-600">
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </span>
            </button>
          </div>
          {#if errors.password}
            <p class="mt-1 text-sm text-danger-600">{errors.password}</p>
          {/if}
        </div>

        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
            Confirm Password
          </label>
          <div class="mt-1 relative">
            <input
              id="confirmPassword"
              name="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              autocomplete="new-password"
              required
              class="form-input pr-10"
              placeholder="Confirm your password"
              bind:value={confirmPassword}
              class:border-danger-500={errors.confirmPassword}
              on:keydown={handleKeydown}
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
              on:click={() => togglePassword('confirmPassword')}
            >
              <span class="text-gray-400 hover:text-gray-600">
                {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
              </span>
            </button>
          </div>
          {#if errors.confirmPassword}
            <p class="mt-1 text-sm text-danger-600">{errors.confirmPassword}</p>
          {/if}
        </div>

        <div>
          <label for="masterPassword" class="block text-sm font-medium text-gray-700">
            Master Password
            <span class="text-xs text-gray-500 ml-1">(for encryption)</span>
          </label>
          <div class="mt-1 relative">
            <input
              id="masterPassword"
              name="masterPassword"
              type={showMasterPassword ? 'text' : 'password'}
              autocomplete="new-password"
              required
              class="form-input pr-10"
              placeholder="Create a master password"
              bind:value={masterPassword}
              class:border-danger-500={errors.masterPassword}
              on:keydown={handleKeydown}
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
              on:click={() => togglePassword('masterPassword')}
            >
              <span class="text-gray-400 hover:text-gray-600">
                {showMasterPassword ? '👁️' : '👁️‍🗨️'}
              </span>
            </button>
          </div>
          {#if errors.masterPassword}
            <p class="mt-1 text-sm text-danger-600">{errors.masterPassword}</p>
          {/if}
          <p class="mt-1 text-xs text-gray-500">
            This master password is used to encrypt your passwords. Keep it safe and never share it with anyone.
          </p>
        </div>
      </div>

      <div class="flex items-center">
        <input
          id="agree-terms"
          name="agree-terms"
          type="checkbox"
          required
          class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
        />
        <label for="agree-terms" class="ml-2 block text-sm text-gray-900">
          I agree to the
          <a href="/terms" class="text-primary-600 hover:text-primary-500">Terms of Service</a>
          and
          <a href="/privacy" class="text-primary-600 hover:text-primary-500">Privacy Policy</a>
        </label>
      </div>

      <div>
        <button
          type="submit"
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading}
        >
          {#if loading}
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
            Creating account...
          {:else}
            Create account
          {/if}
        </button>
      </div>
    </form>
  </div>
</div>
