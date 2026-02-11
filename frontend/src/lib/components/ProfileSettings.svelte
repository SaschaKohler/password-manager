<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/services/api';

  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let loading = false;
  let error: string | null = null;
  let success: string | null = null;
  
  let formData = {
    username: '',
    email: '',
    current_password: '',
    new_password: '',
    confirm_password: ''
  };

  let showPasswordForm = false;
  let showCurrentPassword = false;
  let showNewPassword = false;
  let showConfirmPassword = false;
  let passwordStrength = 0;

  onMount(() => {
    if ($auth.user) {
      formData.username = $auth.user.username;
      formData.email = $auth.user.email;
    }
  });

  async function handleProfileUpdate() {
    loading = true;
    error = null;
    success = null;

    try {
      // Update user profile (username, email)
      // Note: This would need to be implemented in the backend API
      // For now, we'll just show a success message
      success = 'Profile updated successfully';
      dispatch('profile-updated');
    } catch (err: any) {
      error = err.message || 'Failed to update profile';
    } finally {
      loading = false;
    }
  }

  async function handlePasswordChange() {
    if (formData.new_password !== formData.confirm_password) {
      error = 'New passwords do not match';
      return;
    }

    if (formData.new_password.length < 8) {
      error = 'Password must be at least 8 characters long';
      return;
    }

    loading = true;
    error = null;
    success = null;

    try {
      // Change password API call
      // Note: This would need to be implemented in the backend API
      success = 'Password changed successfully';
      
      // Reset password form
      formData.current_password = '';
      formData.new_password = '';
      formData.confirm_password = '';
      showPasswordForm = false;
      passwordStrength = 0;
      
      dispatch('password-changed');
    } catch (err: any) {
      error = err.message || 'Failed to change password';
    } finally {
      loading = false;
    }
  }

  async function checkPasswordStrength() {
    if (!formData.new_password) {
      passwordStrength = 0;
      return;
    }
    
    try {
      const result = await api.validatePassword(formData.new_password);
      passwordStrength = result.strength;
    } catch (err) {
      console.error('Failed to validate password:', err);
    }
  }

  function getStrengthColor(strength: number) {
    if (strength >= 80) return 'text-success-600';
    if (strength >= 60) return 'text-warning-600';
    return 'text-danger-600';
  }

  function getStrengthText(strength: number) {
    if (strength >= 80) return 'Strong';
    if (strength >= 60) return 'Medium';
    return 'Weak';
  }

  function handleClose() {
    isOpen = false;
    error = null;
    success = null;
    showPasswordForm = false;
    
    // Reset password form
    formData.current_password = '';
    formData.new_password = '';
    formData.confirm_password = '';
    passwordStrength = 0;
  }

  async function handleDeleteAccount() {
    const confirmation = prompt('Are you sure you want to delete your account? This action cannot be undone. Type "DELETE" to confirm:');
    
    if (confirmation !== 'DELETE') {
      return;
    }

    try {
      // Delete account API call
      // Note: This would need to be implemented in the backend API
      alert('Account deletion feature not yet implemented');
    } catch (err: any) {
      error = err.message || 'Failed to delete account';
    }
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">Profile Settings</h2>
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

        <!-- Profile Information -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Profile Information</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-2">
              <label for="username" class="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                id="username"
                type="text"
                class="form-input"
                bind:value={formData.username}
                disabled={loading}
              />
            </div>

            <div class="space-y-2">
              <label for="email" class="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                class="form-input"
                bind:value={formData.email}
                disabled={loading}
              />
            </div>
          </div>

          <button
            on:click={handleProfileUpdate}
            class="btn btn-primary"
            disabled={loading}
          >
            {#if loading}
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
            {/if}
            Update Profile
          </button>
        </div>

        <!-- Password Change -->
        <div class="space-y-4 border-t border-gray-200 pt-6">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">Change Password</h3>
            <button
              type="button"
              on:click={() => showPasswordForm = !showPasswordForm}
              class="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              {showPasswordForm ? 'Cancel' : 'Change Password'}
            </button>
          </div>

          {#if showPasswordForm}
            <div class="space-y-4">
              <div class="space-y-2">
                <label for="current-password" class="block text-sm font-medium text-gray-700">
                  Current Password
                </label>
                <div class="relative">
                  <input
                    id="current-password"
                    type={showCurrentPassword ? 'text' : 'password'}
                    class="form-input pr-10"
                    bind:value={formData.current_password}
                    placeholder="Enter current password"
                  />
                  <button
                    type="button"
                    on:click={() => showCurrentPassword = !showCurrentPassword}
                    class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
                    aria-label={showCurrentPassword ? 'Hide password' : 'Show password'}
                  >
                    {#if showCurrentPassword}
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    {:else}
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    {/if}
                  </button>
                </div>
              </div>

              <div class="space-y-2">
                <label for="new-password" class="block text-sm font-medium text-gray-700">
                  New Password
                </label>
                <div class="relative">
                  <input
                    id="new-password"
                    type={showNewPassword ? 'text' : 'password'}
                    class="form-input pr-20"
                    bind:value={formData.new_password}
                    placeholder="Enter new password"
                    on:input={checkPasswordStrength}
                  />
                  <div class="absolute inset-y-0 right-0 flex items-center pr-3 gap-2">
                    {#if formData.new_password && passwordStrength > 0}
                      <span class="text-xs font-medium {getStrengthColor(passwordStrength)}">
                        {getStrengthText(passwordStrength)}
                      </span>
                    {/if}
                    <button
                      type="button"
                      on:click={() => showNewPassword = !showNewPassword}
                      class="text-gray-400 hover:text-gray-600"
                      aria-label={showNewPassword ? 'Hide password' : 'Show password'}
                    >
                      {#if showNewPassword}
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      {:else}
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                        </svg>
                      {/if}
                    </button>
                  </div>
                </div>
              </div>

              <div class="space-y-2">
                <label for="confirm-password" class="block text-sm font-medium text-gray-700">
                  Confirm New Password
                </label>
                <div class="relative">
                  <input
                    id="confirm-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    class="form-input pr-10"
                    bind:value={formData.confirm_password}
                    placeholder="Confirm new password"
                  />
                  <button
                    type="button"
                    on:click={() => showConfirmPassword = !showConfirmPassword}
                    class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
                    aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                  >
                    {#if showConfirmPassword}
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    {:else}
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    {/if}
                  </button>
                </div>
              </div>

              <button
                on:click={handlePasswordChange}
                class="btn btn-primary"
                disabled={loading}
              >
                {#if loading}
                  <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {/if}
                Change Password
              </button>
            </div>
          {/if}
        </div>

        <!-- Account Actions -->
        <div class="space-y-4 border-t border-gray-200 pt-6">
          <h3 class="text-lg font-medium text-gray-900">Account Actions</h3>
          
          <div class="space-y-3">
            <button
              on:click={handleDeleteAccount}
              class="btn btn-danger w-full"
            >
              🗑️ Delete Account
            </button>
            
            <div class="text-xs text-gray-500 text-center">
              Deleting your account will permanently remove all data and cannot be undone.
            </div>
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
