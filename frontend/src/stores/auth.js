/*
*  Copyright (c) 2013-2025. The Johns Hopkins University Applied Physics Laboratory LLC
*
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* NO WARRANTY.   THIS MATERIAL IS PROVIDED "AS IS."  JHU/APL DISCLAIMS ALL
* WARRANTIES IN THE MATERIAL, WHETHER EXPRESS OR IMPLIED, INCLUDING (BUT NOT
* LIMITED TO) ANY AND ALL IMPLIED WARRANTIES OF PERFORMANCE,
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF
* INTELLECTUAL PROPERTY RIGHTS. ANY USER OF THE MATERIAL ASSUMES THE ENTIRE
* RISK AND LIABILITY FOR USING THE MATERIAL.  IN NO EVENT SHALL JHU/APL BE
* LIABLE TO ANY USER OF THE MATERIAL FOR ANY ACTUAL, INDIRECT,
* CONSEQUENTIAL, SPECIAL OR OTHER DAMAGES ARISING FROM THE USE OF, OR
* INABILITY TO USE, THE MATERIAL, INCLUDING, BUT NOT LIMITED TO, ANY DAMAGES
* FOR LOST PROFITS.
 */

import { some as _some } from 'lodash'

import { computed } from 'vue'
import { defineStore } from 'pinia'

import {$api, getRequest, updateAPIHeaders} from 'boot/axios'
import { pinia, synchronizeState } from 'stores/index'

import { router } from 'src/router'

const EXPIRE_TIME = 90 * 24 * 60 * 60 * 1000 // 90 Days

export const useAuthStore = defineStore('auth', {
  state () {
    return {
      isAuthenticated: false,
      accessToken: null,
      user: null,
      refreshInterval: null,
      idleTimeout: null,
      otpRequired: false,
      mustChangePassword: false,
    }
  },
  actions: {
    async login (username, password, otp) {
      const bodyFormData = new FormData()
      bodyFormData.append('username', username)
      bodyFormData.append('password', password)
      bodyFormData.append('otp', otp)

      const login = await $api.post('/auth/login', bodyFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        },
        ).catch(function (error) {
          throw new Error(error.response.data.detail)
      })
      if (login.data.otp_required) {
        this.otpRequired = true;
        throw new Error("OTP Required")
      }
      await this.update(login.data)
      this.startTrackingActivity()
      this.refreshInterval = setInterval(() => {
        this.refresh()
      }, 600000, ...[])
    },
    async update (update) {
      this.accessToken = update.access_token
      updateAPIHeaders({ Authorization: `Bearer ${this.accessToken}` })
      try {
        const user = await getRequest(`/user/self`)
        this.user = user.data
        this.isAuthenticated = true

        const otpCheck = await getRequest(`/auth/otp/check`)
        this.otpRequired = otpCheck.data.otp_enabled
        const lastUpdated = new Date(this.user.password_last_updated+"Z" || this.user.created)
        const timeSinceUpdate = (Date.now() - lastUpdated.getTime())
        this.mustChangePassword = timeSinceUpdate > EXPIRE_TIME
      }
      catch (cause) {
        this.isAuthenticated = false
        const error = new Error('Unable to update user')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}Caused by:\n${causeStack}`
        throw error
      }
    },
    async refresh () {
      try {
        const refresh = await $api.get('/auth/refresh')
        await this.update(refresh.data)

        return true
      }
      catch (err) {
        await this.logout()

        return false
      }
    },
    resetIdleTimeout() {
      clearTimeout(this.idleTimeout)
      this.idleTimeout = setTimeout(() => {
        this.logout()
        router.push({ path: '/login', query: { next: router.currentRoute.value.fullPath }})
      }, 30 * 60 * 1000) // Auto-logout after 30 min
    },
    startTrackingActivity() {
      document.addEventListener('mousemove', this.resetIdleTimeout)
      document.addEventListener('keydown', this.resetIdleTimeout)
      this.resetIdleTimeout()
    },
    async logout () {
      if (this.refreshInterval !== null) {
        clearInterval(this.refreshInterval)
      }
      if (this.idleTimeout !== null) {
        clearTimeout(this.idleTimeout)
      }
      try {
        if (this.isAuthenticated) {
          await $api.get('/auth/logout')
        }
      }
      catch (_) {}

      this.isAuthenticated = false
      this.accessToken = null
      this.user = null
      this.refreshInterval = null
      this.idleTimeout = null

      updateAPIHeaders({})
    },
    async enable2fa (otp) {
      const bodyFormData = new FormData()
      bodyFormData.append('otp', otp)
      await $api.post('/auth/otp/enable', bodyFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        },
        ).catch(function (error) {
          throw new Error(error.response.data.detail)
      })
      this.refresh()
    },
    async disable2fa () {
      try {
        await getRequest('/auth/otp/disable')
        this.refresh()
      }
      catch (_) {}
    },
    async disableUser2fa(userId) {
      try {
        await getRequest(`/auth/otp/disable/${userId}`)
      }
      catch (_) {}
    },
    async generateQrCode () {
      try {
        const qrcode = await getRequest('/auth/otp/generate')
        return `data:image/png;base64,${qrcode.data}`
      }
      catch (_) {}
    },
    async updatePassword (newPassword) {
      await $api.put('/user/self/password', { password: newPassword })
      await this.update({ access_token: this.accessToken })
      this.mustChangePassword = false
    },
    async newPassword (token, password) {
      await $api.post('/user/reset-password', {
          token: token,
          password: password
        })
      // await this.update({ access_token: this.accessToken })
      this.mustChangePassword = false
    },
    async sendResetEmail (username) {
      await $api.post('/user/forgot-password', null, { params: {username: username} })
    }
  }
})

export const authStore = useAuthStore(pinia)
synchronizeState(authStore, `vims.${authStore.$id}`, {
  hydrate (store) {
    updateAPIHeaders({ Authorization: `Bearer ${store.$state.accessToken}` })
    if (store.$state.refreshInterval) {
      store.$state.refreshInterval = setInterval(() => {
        store.refresh()
      }, 600000, ...[])
    }
  }
})

export function hasPermission (...permissions) {
  return computed(() => {
    return authStore.user && _some(
      ['admin', ...permissions],
      (permission) => authStore.user.permissions[permission]
    )
  })
}
