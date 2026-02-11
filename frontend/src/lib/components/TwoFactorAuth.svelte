<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { api } from '$lib/services/api';

  export let isOpen = false;
  export let currentStatus: { enabled: boolean; method: string | null } = { enabled: false, method: null };

  const dispatch = createEventDispatcher();

  let loading = false;
  let error: string | null = null;
  let success: string | null = null;
  let step: 'status' | 'setup' | 'verify' | 'disabled' = 'status';
  let setupData: { secret: string; qr_code: string; backup_codes: string[] } | null = null;
  let verificationCode = '';
  let disableCode = '';

  $: if (isOpen) {
    step = 'status';
    verificationCode = '';
    disableCode = '';
    error = null;
    success = null;
  }

  async function handleEnable2FA() {
    loading = true;
    error = null;

    try {
      setupData = await api.enable2FA();
      step = 'setup';
    } catch (err: any) {
      error = err.message || 'Failed to enable 2FA';
    } finally {
      loading = false;
    }
  }

  async function handleVerifySetup() {
    if (!verificationCode || verificationCode.length !== 6) {
      error = 'Please enter a 6-digit code';
      return;
    }

    loading = true;
    error = null;

    try {
      await api.verify2FASetup(verificationCode);
      success = 'Two-factor authentication has been enabled successfully!';
      step = 'status';
      currentStatus.enabled = true;
      currentStatus.method = 'TOTP';
      dispatch('updated');
    } catch (err: any) {
      error = err.message || 'Invalid verification code';
    } finally {
      loading = false;
      verificationCode = '';
    }
  }

  async function handleDisable2FA() {
    if (!disableCode || disableCode.length !== 6) {
      error = 'Please enter your current 6-digit code';
      return;
    }

    loading = true;
    error = null;

    try {
      await api.disable2FA(disableCode);
      success = 'Two-factor authentication has been disabled.';
      step = 'status';
      currentStatus.enabled = false;
      currentStatus.method = null;
      dispatch('updated');
    } catch (err: any) {
      error = err.message || 'Invalid verification code';
    } finally {
      loading = false;
      disableCode = '';
    }
  }

  function handleClose() {
    isOpen = false;
    step = 'status';
    error = null;
    success = null;
    dispatch('close');
  }

  function copyBackupCode(code: string) {
    navigator.clipboard.writeText(code);
    success = 'Backup code copied to clipboard!';
    setTimeout(() => success = null, 2000);
  }
</script>

<svelte:window on:keydown={(e) => e.key === 'Escape' && handleClose()} />

{#if isOpen}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl max-w-md w-full">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <span class="text-xl">🔐</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Two-Factor Authentication</h2>
              <p class="text-sm text-gray-500">Secure your account</p>
            </div>
          </div>
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

      <!-- Content -->
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

        {#if step === 'status'}
          <!-- Current Status -->
          <div class="text-center">
            <div class="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center {currentStatus.enabled ? 'bg-success-100' : 'bg-gray-100'}">
              <span class="text-4xl">{currentStatus.enabled ? '✅' : '🔓'}</span>
            </div>
            
            {#if currentStatus.enabled}
              <h3 class="text-lg font-semibold text-gray-900">2FA is Enabled</h3>
              <p class="text-gray-600 mt-1">
                Your account is protected with {currentStatus.method}.
              </p>
            {:else}
              <h3 class="text-lg font-semibold text-gray-900">2FA is Not Enabled</h3>
              <p class="text-gray-600 mt-1">
                Add an extra layer of security to your account.
              </p>
            {/if}
          </div>

          <div class="space-y-3">
            {#if currentStatus.enabled}
              <button
                class="btn btn-danger w-full"
                on:click={() => step = 'disabled'}
              >
                🔓 Disable 2FA
              </button>
            {:else}
              <button
                class="btn btn-primary w-full"
                on:click={handleEnable2FA}
                disabled={loading}
              >
                {#if loading}
                  <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {/if}
                🔐 Enable 2FA
              </button>
            {/if}
          </div>

        {:else if step === 'setup'}
          <!-- Setup 2FA -->
          <div class="space-y-4">
            <div class="text-center">
              <h3 class="font-semibold text-gray-900">Scan QR Code</h3>
              <p class="text-sm text-gray-600 mt-1">
                Scan this QR code with your authenticator app
              </p>
            </div>

            {#if setupData?.qr_code}
              <div class="flex justify-center">
                <img 
                  src={setupData.qr_code} 
                  alt="2FA QR Code" 
                  class="w-48 h-48 border rounded-lg"
                />
              </div>
            {/if}

            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-600 mb-2">Or enter this code manually:</p>
              <code class="block bg-white p-2 rounded text-sm font-mono text-center">
                {setupData?.secret}
              </code>
            </div>

            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700">
                Enter verification code
              </label>
              <input
                type="text"
                class="form-input text-center text-2xl font-mono tracking-widest"
                bind:value={verificationCode}
                placeholder="000000"
                maxlength="6"
                pattern="[0-9]*"
                inputmode="numeric"
              />
            </div>

            <!-- Backup Codes -->
            {#if setupData?.backup_codes}
              <div class="border-t border-gray-200 pt-4">
                <h4 class="font-medium text-gray-900 mb-2">Backup Codes</h4>
                <p class="text-sm text-gray-600 mb-3">
                  Save these backup codes in a safe place. You can use them if you lose access to your authenticator.
                </p>
                <div class="grid grid-cols-2 gap-2">
                  {#each setupData.backup_codes as code}
                    <button
                      type="button"
                      class="bg-white border border-gray-200 rounded px-3 py-2 text-sm font-mono text-left hover:bg-gray-50"
                      on:click={() => copyBackupCode(code)}
                    >
                      {code}
                    </button>
                  {/each}
                </div>
              </div>
            {/if}

            <div class="flex gap-3 pt-4">
              <button
                type="button"
                class="btn btn-secondary flex-1"
                on:click={() => { step = 'status'; verificationCode = ''; }}
              >
                Cancel
              </button>
              <button
                type="button"
                class="btn btn-primary flex-1"
                on:click={handleVerifySetup}
                disabled={loading || verificationCode.length !== 6}
              >
                {#if loading}
                  <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {/if}
                Verify & Enable
              </button>
            </div>
          </div>

        {:else if step === 'disabled'}
          <!-- Disable 2FA -->
          <div class="space-y-4">
            <div class="text-center">
              <div class="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center bg-warning-100">
                <span class="text-3xl">⚠️</span>
              </div>
              <h3 class="font-semibold text-gray-900">Disable Two-Factor Authentication?</h3>
              <p class="text-sm text-gray-600 mt-1">
                This will make your account less secure.
              </p>
            </div>

            <div class="bg-warning-50 border border-warning-200 rounded-lg p-4">
              <p class="text-sm text-warning-800">
                ⚠️ Enter your current 2FA code to disable it. Make sure you have access to your authenticator app.
              </p>
            </div>

            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700">
                Enter your 2FA code
              </label>
              <input
                type="text"
                class="form-input text-center text-2xl font-mono tracking-widest"
                bind:value={disableCode}
                placeholder="000000"
                maxlength="6"
                pattern="[0-9]*"
                inputmode="numeric"
              />
            </div>

            <div class="flex gap-3 pt-4">
              <button
                type="button"
                class="btn btn-secondary flex-1"
                on:click={() => { step = 'status'; disableCode = ''; }}
              >
                Cancel
              </button>
              <button
                type="button"
                class="btn btn-danger flex-1"
                on:click={handleDisable2FA}
                disabled={loading || disableCode.length !== 6}
              >
                {#if loading}
                  <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {/if}
                Disable 2FA
              </button>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .font-mono {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
  }
  
  .tracking-widest {
    letter-spacing: 0.15em;
  }
</style>
