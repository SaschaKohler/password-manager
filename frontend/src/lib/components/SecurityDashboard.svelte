<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { api } from '$lib/services/api';
  import type { PasswordEntry } from '$lib/types/password';

  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let loading = true;
  let error: string | null = null;
  let auditData: {
    total_passwords: number;
    weak_passwords: number;
    duplicate_passwords: number;
    old_passwords: number;
    shared_passwords: number;
    breached_passwords: number;
    last_audit: string;
  } | null = null;

  let weakPasswords: PasswordEntry[] = [];
  let duplicatePasswords: PasswordEntry[] = [];
  let oldPasswords: PasswordEntry[] = [];

  onMount(async () => {
    if (isOpen) {
      await loadSecurityData();
    }
  });

  $: if (isOpen && !auditData) {
    loadSecurityData();
  }

  async function loadSecurityData() {
    loading = true;
    error = null;

    try {
      auditData = await api.getSecurityAudit();
      
      // Load weak passwords
      const weakResult = await api.getPasswords({ search: '', is_favorite: false });
      // Note: In a real implementation, the API would filter by strength
      weakPasswords = weakResult.results.slice(0, 5);
      duplicatePasswords = weakResult.results.slice(0, 3);
      oldPasswords = weakResult.results.slice(0, 3);
    } catch (err: any) {
      error = err.message || 'Failed to load security data';
    } finally {
      loading = false;
    }
  }

  function handleClose() {
    isOpen = false;
    dispatch('close');
  }

  function getScoreColor(score: number): string {
    if (score >= 80) return 'text-success-600';
    if (score >= 60) return 'text-warning-600';
    return 'text-danger-600';
  }

  function getScoreBgColor(score: number): string {
    if (score >= 80) return 'bg-success-500';
    if (score >= 60) return 'bg-warning-500';
    return 'bg-danger-500';
  }

  $: securityScore = auditData 
    ? Math.round(((auditData.total_passwords - auditData.weak_passwords - auditData.duplicate_passwords - auditData.breached_passwords) / Math.max(auditData.total_passwords, 1)) * 100)
    : 0;
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-success-100 flex items-center justify-center">
              <span class="text-xl">🛡️</span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">Security Dashboard</h2>
              <p class="text-sm text-gray-500">Password health analysis</p>
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
        {#if loading}
          <div class="flex flex-col items-center justify-center py-12 gap-4">
            <div class="w-10 h-10 border-3 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
            <p class="text-gray-600">Analyzing passwords...</p>
          </div>
        {:else if error}
          <div class="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p class="text-danger-800">{error}</p>
            <button class="btn btn-secondary mt-4" on:click={loadSecurityData}>
              🔄 Retry
            </button>
          </div>
        {:else if auditData}
          <!-- Overall Score -->
          <div class="bg-gradient-to-r from-primary-50 to-success-50 rounded-xl p-6">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">Security Score</h3>
                <p class="text-sm text-gray-600 mt-1">
                  Last analyzed: {new Date(auditData.last_audit).toLocaleDateString()}
                </p>
              </div>
              <div class="flex items-center gap-4">
                <div class="text-5xl font-bold {getScoreColor(securityScore)}">
                  {securityScore}%
                </div>
                <div class="w-24 h-24 relative">
                  <svg class="transform -rotate-90 w-full h-full">
                    <circle
                      cx="48"
                      cy="48"
                      r="40"
                      stroke="#e5e7eb"
                      stroke-width="8"
                      fill="none"
                    />
                    <circle
                      cx="48"
                      cy="48"
                      r="40"
                      stroke="currentColor"
                      stroke-width="8"
                      fill="none"
                      stroke-dasharray="{251.2 * securityScore / 100} 251.2"
                      class="{getScoreColor(securityScore)}"
                    />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- Stats Grid -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-white border border-gray-200 rounded-xl p-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                  <span class="text-lg">🔐</span>
                </div>
                <div>
                  <p class="text-2xl font-bold text-gray-900">{auditData.total_passwords}</p>
                  <p class="text-sm text-gray-500">Total Passwords</p>
                </div>
              </div>
            </div>

            <div class="bg-white border border-gray-200 rounded-xl p-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-danger-100 flex items-center justify-center">
                  <span class="text-lg">⚠️</span>
                </div>
                <div>
                  <p class="text-2xl font-bold text-danger-600">{auditData.weak_passwords}</p>
                  <p class="text-sm text-gray-500">Weak Passwords</p>
                </div>
              </div>
            </div>

            <div class="bg-white border border-gray-200 rounded-xl p-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-warning-100 flex items-center justify-center">
                  <span class="text-lg">🔄</span>
                </div>
                <div>
                  <p class="text-2xl font-bold text-warning-600">{auditData.duplicate_passwords}</p>
                  <p class="text-sm text-gray-500">Duplicates</p>
                </div>
              </div>
            </div>

            <div class="bg-white border border-gray-200 rounded-xl p-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                  <span class="text-lg">📅</span>
                </div>
                <div>
                  <p class="text-2xl font-bold text-gray-600">{auditData.old_passwords}</p>
                  <p class="text-sm text-gray-500">Old Passwords</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Issues Section -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900">Security Issues</h3>
            
            {#if auditData.weak_passwords > 0}
              <div class="border border-danger-200 rounded-xl p-4">
                <div class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-full bg-danger-100 flex items-center justify-center flex-shrink-0">
                    <span class="text-danger-600">🔓</span>
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">Weak Passwords Detected</h4>
                    <p class="text-sm text-gray-600 mt-1">
                      {auditData.weak_passwords} passwords have been flagged as weak. 
                      Consider updating them with stronger passwords.
                    </p>
                    <button class="btn btn-danger mt-3 text-sm">
                      🔐 Update Weak Passwords
                    </button>
                  </div>
                </div>
              </div>
            {/if}

            {#if auditData.duplicate_passwords > 0}
              <div class="border border-warning-200 rounded-xl p-4">
                <div class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-full bg-warning-100 flex items-center justify-center flex-shrink-0">
                    <span class="text-warning-600">🔁</span>
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">Duplicate Passwords</h4>
                    <p class="text-sm text-gray-600 mt-1">
                      {auditData.duplicate_passwords} passwords are duplicates. 
                      Using unique passwords for each account improves security.
                    </p>
                    <button class="btn btn-warning mt-3 text-sm">
                      🔄 Review Duplicates
                    </button>
                  </div>
                </div>
              </div>
            {/if}

            {#if auditData.old_passwords > 0}
              <div class="border border-gray-200 rounded-xl p-4">
                <div class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <span class="text-gray-600">📅</span>
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">Aged Passwords</h4>
                    <p class="text-sm text-gray-600 mt-1">
                      {auditData.old_passwords} passwords haven't been changed in over 90 days.
                    </p>
                    <button class="btn btn-secondary mt-3 text-sm">
                      🔐 Update Aged Passwords
                    </button>
                  </div>
                </div>
              </div>
            {/if}

            {#if auditData.breached_passwords > 0}
              <div class="border border-danger-200 bg-danger-50 rounded-xl p-4">
                <div class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-full bg-danger-100 flex items-center justify-center flex-shrink-0">
                    <span class="text-danger-600">🚨</span>
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-danger-800">Breached Passwords Detected!</h4>
                    <p class="text-sm text-danger-700 mt-1">
                      {auditData.breached_passwords} passwords have appeared in known data breaches.
                      These should be changed immediately.
                    </p>
                    <button class="btn btn-danger mt-3 text-sm">
                      🚨 Change Breached Passwords
                    </button>
                  </div>
                </div>
              </div>
            {/if}

            {#if auditData.weak_passwords === 0 && auditData.duplicate_passwords === 0 && auditData.old_passwords === 0 && auditData.breached_passwords === 0}
              <div class="border border-success-200 bg-success-50 rounded-xl p-4">
                <div class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-full bg-success-100 flex items-center justify-center flex-shrink-0">
                    <span class="text-success-600">✅</span>
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-success-800">All Clear!</h4>
                    <p class="text-sm text-success-700 mt-1">
                      Your passwords are in great shape. No security issues detected.
                    </p>
                  </div>
                </div>
              </div>
            {/if}
          </div>

          <!-- Recommendations -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900">Recommendations</h3>
            <div class="grid gap-4 md:grid-cols-2">
              <div class="border border-gray-200 rounded-xl p-4">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-lg">💪</span>
                  <h4 class="font-medium text-gray-900">Enable 2FA</h4>
                </div>
                <p class="text-sm text-gray-600">
                  Add an extra layer of security to your account with two-factor authentication.
                </p>
                <button class="btn btn-primary mt-3 text-sm w-full">
                  🔐 Enable 2FA
                </button>
              </div>

              <div class="border border-gray-200 rounded-xl p-4">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-lg">📊</span>
                  <h4 class="font-medium text-gray-900">Review Activity</h4>
                </div>
                <p class="text-sm text-gray-600">
                  Check your recent account activity for any suspicious access.
                </p>
                <button class="btn btn-secondary mt-3 text-sm w-full">
                  📋 View Audit Logs
                </button>
              </div>

              <div class="border border-gray-200 rounded-xl p-4">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-lg">📤</span>
                  <h4 class="font-medium text-gray-900">Backup Passwords</h4>
                </div>
                <p class="text-sm text-gray-600">
                  Export your passwords as a backup in case of emergency.
                </p>
                <button class="btn btn-secondary mt-3 text-sm w-full">
                  💾 Export Passwords
                </button>
              </div>

              <div class="border border-gray-200 rounded-xl p-4">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-lg">🔔</span>
                  <h4 class="font-medium text-gray-900">Security Alerts</h4>
                </div>
                <p class="text-sm text-gray-600">
                  Get notified when your passwords appear in data breaches.
                </p>
                <button class="btn btn-secondary mt-3 text-sm w-full">
                  🔔 Enable Alerts
                </button>
              </div>
            </div>
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-200 flex justify-between items-center">
        <button
          type="button"
          on:click={loadSecurityData}
          class="btn btn-secondary"
        >
          🔄 Refresh Analysis
        </button>
        <button
          type="button"
          on:click={handleClose}
          class="btn btn-primary"
        >
          Close
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .btn-warning {
    background-color: #f59e0b;
    color: white;
  }

  .btn-warning:hover {
    background-color: #d97706;
  }
</style>
