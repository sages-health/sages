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
            <q-img fit="scale-down" src="images/logo.png">
            </q-img>
          </q-card-section>
          <q-card-section class="q-pa-none">
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
                v-model="username"
                class="q-px-md q-pt-md"
                outlined
                :label="t('login.username')"
              />
              <q-input
                v-model="password"
                class="q-px-md"
                outlined
                :label="t('login.password')"
                type="password"
              />
              <q-input
                v-if="otpRequired"
                v-model="otp"
                class="q-px-md"
                outlined
                :label="t('login.otp')"
                type="password"
              />
              <q-separator />
              <div class="row items-center justify-between">
                <q-btn
                  flat
                  dense
                  color="primary"
                  @click="router.push({ name: 'forgot-password' })"
                  class="text-caption q-ml-md q-mb-md"
                >
                  {{ t('login.forgotPassword') }}
                </q-btn>
                <q-btn
                  class="q-mr-md q-mb-md"
                  color="primary"
                  type="submit"
                >
                  {{ t('login.submit') }}
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
import { storeToRefs } from 'pinia'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'

import { useAuthStore } from 'stores/auth'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const authStore = useAuthStore()
const { login } = authStore
const { isAuthenticated, otpRequired, mustChangePassword } = storeToRefs(authStore)

const error = ref('')
const username = ref('')
const password = ref('')
const otp = ref('')

async function onSubmit () {
  try {
    error.value = ''
    await login(username.value.toLowerCase(), password.value, otp.value)
    if (isAuthenticated.value) {
      if (mustChangePassword) {
        return router.replace( { name: 'force-password-reset' })
      }
      const next = (route.query.next)
        ? { path: route.query.next }
        : { name: 'home' }
      router.replace(next)
    }
  }
  catch (err) {
    error.value = err.message
  }
}
</script>
