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
            <q-img fit="scale-down" src="images/logo.png" />
          </q-card-section>
          <q-card-section class="q-pa-none">
            <q-banner
              class="bg-warning text-black q-mx-md q-mt-md"
              dense
              rounded
            >
              {{ t('forgotPassword.instruction') }}
            </q-banner>
            <q-banner
              v-if="error.length > 0"
              class="bg-negative text-white q-mx-md q-mt-md"
            >
              {{ error }}
            </q-banner>
            <q-banner
              v-if="success"
              class="bg-positive text-white q-mx-md q-mt-md"
            >
              {{ t('forgotPassword.successMessage') }}
            </q-banner>
            <q-form class="q-gutter-md" @submit="onSubmit">
              <q-input
                v-model="username"
                class="q-px-md q-pt-md"
                outlined
                :label="t('login.username')"
                :rules="[val => !!val || t('common.requiredField')]"
              />
              <q-separator />
              <div class="flex justify-end">
                <q-btn
                  class="q-mr-md q-mb-md"
                  color="primary"
                  type="submit"
                >
                  {{ t('forgotPassword.submit') }}
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
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'stores/auth'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const error = ref('')
const success = ref(false)

async function onSubmit () {
  error.value = ''
  success.value = false
  try {
    await authStore.sendResetEmail(username.value)
    success.value = true
  }
  catch (err) {
    error.value = err.response?.data?.detail
  }
}
</script>
