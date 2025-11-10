<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-layout view="hHh Lpr lFf">
    <q-dialog v-model="showQrCode">
      <q-card
        class="q-pa-sm"
        style="display: flex; flex-direction: column; align-items: center; width: 50%; height: 500px;"
      >
        <img
          :src="qrCodeSrc"
          width="250"
          height="250"
          style="width: 250px"
        >
        <div>
          {{ $t('login.scanOtp') }}
        </div>
        <div class="flex text-center q-py-md">
          {{ $t('login.verifyOtp') }}
        </div>
        <q-form
          class="q-gutter-md"
          @submit="onOtpVerify"
        >
          <q-input
            v-model="otp"
            style="width: 250px"
            outlined
            :label="$t('login.otp')"
            type="password"
            :error="!!otpError"
            :error-message="otpError"
          />

          <div class="flex justify-end">
            <q-btn
              color="primary"
              type="submit"
            >
              {{ $t('login.submit') }}
            </q-btn>
          </div>
        </q-form>
      </q-card>
    </q-dialog>
    <q-header elevated>
      <q-toolbar>
        <q-btn
          v-if="isAuthenticated && user"
          flat
          dense
          round
          :icon="fasBars"
          aria-label="Menu"
          @click="store.toggleLeftDrawer()"
        />

        <q-avatar>
          <img src="/favicon.ico">
        </q-avatar>

        <q-toolbar-title>
          {{ $t('appName') }}
        </q-toolbar-title>

        <q-btn
          v-if="isAuthenticated && user"
          :icon-right="fasCaretDown"
          no-caps
        >
          <span class="q-mr-sm">{{ user.first_name }} {{ user.last_name }}</span>
          <q-menu
            anchor="bottom left"
          >
            <q-list style="min-width: 200px;">
              <q-item-label header>
                2FA ({{ otpPending ? 'Pending' : (otpRequired ? 'Enabled' : 'Disabled') }})
              </q-item-label>
              <q-item>
                <q-item-section>
                  <q-toggle
                    color="blue"
                    v-model="otpEnabled"
                  />
                </q-item-section>
                <q-item-section
                  side
                  top
                >
                  <q-btn
                    v-if="otpRequired || otpPending"
                    :icon-right="fasQrcode"
                    no-caps
                    flat
                    @click="generateQrCode()"
                  />
                </q-item-section>
              </q-item>
              <q-separator />
              <q-item
                v-close-popup
                clickable
              >
                {{ $t('common.settings') }}
              </q-item>
              <q-separator />
              <q-item
                clickable
              >
                <q-select
                  @update:model-value="val => store.updateDefaultLocale(val)"
                  v-model="$i18n.locale"
                  :options="$i18n.availableLocales"
                  :label="$t('common.locale')" />
                <q-separator />
              </q-item>
              <q-item
                v-close-popup
                clickable
                @click="logout()"
              >
                {{ $t('common.logout') }}
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <router-view :key="$route.path" />
  </q-layout>
</template>

<script setup>
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter, useRoute } from 'vue-router'
import {
  fasBars,
  fasCaretDown,
  fasQrcode,
} from '@quasar/extras/fontawesome-v6'

import { useStore } from 'stores/main'
import { useAuthStore } from 'stores/auth'

import { useI18n } from 'vue-i18n';
const t = useI18n();

const router = useRouter()
const route = useRoute()

const store = useStore()
const authStore = useAuthStore()

t.locale.value = store.getDefaultLocale

const { isAuthenticated, user, otpRequired } = storeToRefs(authStore)

const otp = ref()
const otpEnabled = ref(otpRequired.value)
const otpPending = ref(false)
const otpError = ref('')
const showQrCode = ref(false)
const qrCodeSrc = ref('')

async function logout () {
  await authStore.logout()
  const next = { name: 'login' }
  if (!route.name || route.name !== 'home') {
    next.query = { next: route.fullPath }
  }
  await router.replace(next)
}

async function onOtpVerify() {
  try {
    await authStore.enable2fa(otp.value)
    otpPending.value = false
    otpRequired.value = true
    otpError.value = ''
    showQrCode.value = false
  }
  catch (err) {
    otpError.value = err.toString()
  }
}

async function disable2fa () {
  await authStore.disable2fa()
}

async function generateQrCode () {
  const qrcode = await authStore.generateQrCode()
  qrCodeSrc.value = qrcode
  showQrCode.value = true
}

watch(otpEnabled, (newValue) => {
  if (!newValue) {
    disable2fa()
  }
  else {
    otpPending.value = true
  }
})

watch(otpRequired, (newValue) => {
  otpEnabled.value = newValue
})
</script>
