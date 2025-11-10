<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
    <q-page padding>
      <div class="row justify-center">
        <div style="width: 400px; min-width: 300px;">
          <q-card>
            <q-card-section class="text-white q-pt-sm q-pb-sm">
              <q-img
                fit="scale-down"
                src="images/logo.png"
              />
            </q-card-section>
            <q-card-section class="q-pa-none">
              <q-banner
                class="bg-warning text-black q-mx-md q-mt-md"
                dense
                rounded
              >
                {{ t('passwordReset.resetMessage') }}
              </q-banner>
              <q-banner
                v-if="error.length > 0"
                class="bg-negative text-white q-mx-md q-mt-md"
              >
                {{ error }}
              </q-banner>
              <q-form
                class="q-gutter-md"
                @submit="onSubmit"
              >
                <q-input
                  v-model="newPassword"
                  class="q-px-md q-pt-md"
                  outlined
                  :label="t('passwordReset.newPassword')"
                  type="password"
                  :rules="passwordRules"
                  lazy-rules
                />
                <q-input
                  v-model="verifyPassword"
                  class="q-px-md"
                  outlined
                  :label="t('passwordReset.confirmPassword')"
                  type="password"
                  :rules="[
                    verifyPassword => !!verifyPassword || t('common.requiredField'),
                    verifyPassword => verifyPassword === newPassword || t('user.passwordsMustMatch')
                  ]"
                />
                <q-separator />
                <div class="flex justify-end">
                  <q-btn
                    class="q-mr-md q-mb-md"
                    color="primary"
                    type="submit"
                  >
                    {{ t('passwordReset.submit') }}
                  </q-btn>
                </div>
              </q-form>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-page>
  </template>

  <script setup>
  import { ref, computed } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRouter, useRoute } from 'vue-router'

  import { useAuthStore } from 'stores/auth'

  const { t } = useI18n()
  const router = useRouter()
  const route = useRoute()

  const authStore = useAuthStore()

  const error = ref('')
  const newPassword = ref('')
  const verifyPassword = ref('')

  const passwordRules = computed(() => {
    return [
      password => !!password || t('common.requiredField'),
      password => password.length > 12 || t('user.passwordRequirement'),
      password =>
        /[A-Z]/.test(password) &&
        /[a-z]/.test(password) &&
        /\d/.test(password) &&
        /[\W_]/.test(password) ||
        t('user.passwordComplexityRequirement')
    ]
  });

  async function onSubmit () {
    error.value = ''
    const token = route.query.token
    if (!token) {
      error.value = 'Invalid reset token.'
    }
    try {
        await authStore.newPassword(token, newPassword.value)
        router.replace({ name: 'login' })
      }
      catch (err) {
        error.value = err.response.data.detail
      }
    }
  </script>
