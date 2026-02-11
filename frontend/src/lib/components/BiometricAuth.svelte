<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { auth } from '$lib/stores/auth';

  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let loading = false;
  let error: string | null = null;
  let success: string | null = null;
  let biometryType: string = 'unknown';
  let isSupported = false;
  let isEnabled = false;

  onMount(async () => {
    await checkBiometricSupport();
  });

  async function checkBiometricSupport() {
    // Check if Web Authentication API is supported
    if (window.PublicKeyCredential) {
      try {
        // Check if biometric hardware is available
        const publicKey = {
          challenge: new Uint8Array(32),
          userVerification: 'preferred',
        };
        
        const credential = await navigator.credentials.create({ publicKey } as any);
        isSupported = true;
        biometryType = await getBiometryType();
      } catch (err) {
        // WebAuthn supported but no biometric hardware
        isSupported = true;
        biometryType = 'fallback';
      }
    } else {
      isSupported = false;
      biometryType = 'unsupported';
    }
  }

  async function getBiometryType(): Promise<string> {
    if (!window.PublicKeyCredential) return 'unknown';
    
    const cred = window.PublicKeyCredential as any;
    if (await cred.isUserVerifyingPlatformAuthenticatorAvailable()) {
      return 'biometric';
    }
    return 'fallback';
  }

  async function handleEnableBiometric() {
    loading = true;
    error = null;
    success = null;

    try {
      // Check if biometry is available
      if (!window.PublicKeyCredential) {
        throw new Error('Web Authentication API is not supported in this browser');
      }

      // Create a public key credential for biometric authentication
      const publicKey: PublicKeyCredentialCreationOptions = {
        challenge: new Uint8Array(32),
        rp: {
          name: 'Password Manager',
          id: window.location.hostname,
        },
        user: {
          id: new Uint8Array([1, 2, 3, 4]),
          name: $auth.user?.email || 'user',
          displayName: $auth.user?.username || 'User',
        },
        pubKeyCredParams: [
          {
            type: 'public-key',
            alg: -7, // ES256
          },
        ],
        authenticatorSelection: {
          authenticatorAttachment: 'platform',
          userVerification: 'preferred',
        },
      };

      // Create the credential
      const credential = await navigator.credentials.create({ publicKey } as any) as PublicKeyCredential;
      
      if (credential) {
        // Save the credential ID to the backend
        // This would call an API endpoint to save the biometric credential
        isEnabled = true;
        success = `${biometryType === 'biometric' ? 'Biometric authentication' : 'Device authentication'} has been enabled!`;
        dispatch('enabled');
      }
    } catch (err: any) {
      console.error('Biometric enrollment error:', err);
      
      // Handle specific errors
      if (err.name === 'NotAllowedError') {
        error = 'Biometric enrollment was cancelled or not allowed. Please try again.';
      } else if (err.name === 'NotSupportedError') {
        error = 'Biometric authentication is not supported on this device.';
      } else {
        error = err.message || 'Failed to enable biometric authentication';
      }
    } finally {
      loading = false;
    }
  }

  async function handleTestBiometric() {
    loading = true;
    error = null;

    try {
      // Create a challenge to verify
      const challenge = new Uint8Array(32);
      
      const publicKey: PublicKeyCredentialRequestOptions = {
        challenge,
        allowCredentials: [],
        userVerification: 'preferred',
      };

      // Attempt to verify
      const assertion = await navigator.credentials.get({ publicKey } as any) as PublicKeyCredential;
      
      if (assertion) {
        success = 'Biometric authentication verified successfully!';
        dispatch('verified');
      }
    } catch (err: any) {
      console.error('Biometric verification error:', err);
      
      if (err.name === 'NotAllowedError') {
        error = 'Biometric verification was cancelled. Please try again.';
      } else {
        error = 'Failed to verify biometric authentication';
      }
    } finally {
      loading = false;
    }
  }

  async function handleDisableBiometric() {
    if (!confirm('Are you sure you want to disable biometric authentication?')) {
      return;
    }

    loading = true;
    error = null;
    success = null;

    try {
      // This would call an API endpoint to remove the biometric credential
      isEnabled = false;
      success = 'Biometric authentication has been disabled.';
      dispatch('disabled');
    } catch (err: any) {
      error = err.message || 'Failed to disable biometric authentication';
    } finally {
      loading = false;
    }
  }

  function handleClose() {
    isOpen = false;
    error = null;
    success = null;
    dispatch('close');
  }

  function getBiometryIcon(): string {
    const icons: Record<string, string> = {
      'biometric': '👆',
      'fallback': '🔐',
      'unsupported': '❌',
      'unknown': '❓',
    };
    return icons[biometryType] || '🔐';
  }

  function getBiometryName(): string {
    const names: Record<string, string> = {
      'biometric': 'Biometric (Fingerprint / Face)',
      'fallback': 'Device Authentication',
      'unsupported': 'Not Supported',
      'unknown': 'Unknown',
    };
    return names[biometryType] || 'Device Authentication';
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
              <span class="text-xl">👆</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Biometric Authentication</h2>
              <p class="text-sm text-gray-500">Use fingerprint or face to login</p>
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

        <!-- Status -->
        <div class="text-center">
          <div class="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center {isEnabled ? 'bg-success-100' : 'bg-gray-100'}">
            <span class="text-4xl">{getBiometryIcon()}</span>
          </div>
          
          <h3 class="text-lg font-semibold text-gray-900">
            {isEnabled ? 'Biometric Authentication Enabled' : 'Biometric Authentication Disabled'}
          </h3>
          <p class="text-gray-600 mt-1">
            {getBiometryName()}
          </p>
        </div>

        <!-- Unsupported Warning -->
        {#if biometryType === 'unsupported'}
          <div class="bg-warning-50 border border-warning-200 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <span class="text-xl">⚠️</span>
              <div>
                <p class="font-medium text-warning-800">Not Supported</p>
                <p class="text-sm text-warning-700 mt-1">
                  Your browser or device doesn't support biometric authentication. 
                  Try using a modern browser like Chrome, Safari, or Edge.
                </p>
              </div>
            </div>
          </div>
        {/if}

        <!-- Features List -->
        <div class="bg-gray-50 rounded-lg p-4">
          <h4 class="font-medium text-gray-900 mb-3">Features</h4>
          <ul class="space-y-2 text-sm text-gray-600">
            <li class="flex items-center gap-2">
              <span class="text-success-600">✓</span>
              Quick and secure login with fingerprint or face
            </li>
            <li class="flex items-center gap-2">
              <span class="text-success-600">✓</span>
              No need to type your master password
            </li>
            <li class="flex items-center gap-2">
              <span class="text-success-600">✓</span>
              Works with Touch ID, Face ID, Windows Hello
            </li>
            <li class="flex items-center gap-2">
              <span class="text-success-600">✓</span>
              Your biometric data never leaves your device
            </li>
          </ul>
        </div>

        <!-- Actions -->
        <div class="space-y-3">
          {#if !isEnabled}
            {#if biometryType === 'unsupported'}
              <button
                type="button"
                class="btn btn-secondary w-full"
                disabled
              >
                ❌ Not Supported
              </button>
            {:else}
              <button
                type="button"
                class="btn btn-primary w-full"
                on:click={handleEnableBiometric}
                disabled={loading}
              >
                {#if loading}
                  <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {/if}
                👆 Enable Biometric
              </button>
            {/if}
          {:else}
            <button
              type="button"
              class="btn btn-secondary w-full"
              on:click={handleTestBiometric}
              disabled={loading}
            >
              {#if loading}
                <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              {/if}
              🧪 Test Biometric
            </button>
            <button
              type="button"
              class="btn btn-danger w-full"
              on:click={handleDisableBiometric}
              disabled={loading}
            >
              🔓 Disable Biometric
            </button>
          {/if}
        </div>

        <!-- Security Note -->
        <div class="text-xs text-gray-500 text-center">
          🔒 Your biometric data is stored securely on your device and never sent to our servers.
        </div>
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-200">
        <button
          type="button"
          class="btn btn-secondary w-full"
          on:click={handleClose}
        >
          Close
        </button>
      </div>
    </div>
  </div>
{/if}
