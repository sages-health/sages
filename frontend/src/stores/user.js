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

import { defineStore } from 'pinia'
import {$api, getRequest} from 'boot/axios'

const API_URL = 'user'


export const useUserStore = defineStore('user', {
  state() {
    return {
      username: '',
      email: '',
      organization: '',
      lastName: '',
      firstName: '',
      phoneNumber: '',
      role: '',
      groups: [],
      password: '',
      userId: null,
      enabled: true,
      remote: false,

      users: [],

      availableRoles: [],
      availableGroups: [],
      loginTracking: [],

      loadingUsers: false,
      loadingRoles: false,
      loadingGroups: false,
      loadingUser: false,
      deletingUser: false
    }
  },
  getters: {
    getAll: (state) => {
      return state.users
    },
  },
  actions: {
    async fetchUsers() {
      try {
        this.loadingUsers = true

        let users = (await getRequest(API_URL)).data
        users.forEach(function (u) {
          u.roles_formatted = Object.keys(u.roles).join(',')
        })

        this.users = users.map((user) => ({ ...user }))
      }
      catch (cause) {
        const error = new Error('Unable to retrieve: all users')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.loadingUsers = false
      }
    },
    async fetchRoles() {
      try {
        this.loadingRoles = true
        this.availableRoles = Object.keys((await $api.get('role')).data)
      }
      catch (cause) {
        const error = new Error('Unable to retrieve: all users')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.loadingRoles = false
      }
    },
    async fetchGroups() {
      try {
        this.loadingGroups = true
        this.availableGroups = (await $api.get('group')).data.map(
          (group) => {
            return {
              groupName: group.group_name,
              id: group.id
            }
          }
        )
      }
      catch (cause) {
        const error = new Error('Unable to retrieve all groups')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.loadingGroups = false
      }
    },
    async fetchUser(userId) {
      try {
        this.loadingUser = true
        const user = (await $api.get(`${API_URL}/${userId}`)).data
        this.username = user.username
        this.email = user.email
        this.organization = user.organization
        this.firstName = user.first_name
        this.lastName = user.last_name
        this.phoneNumber = user.phone_number
        this.role = Object.keys(user.roles)[0]
        this.groups = user.groups
        this.enabled = user.enabled
        this.remote = user.remote
        this.userId = user.id
      }
      catch (cause) {
        const error = new Error('Unable to retrieve: all users')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.loadingUser = false
      }
    },
    async saveUser() {
      try {
        this.loadingUser = true
        const roles = {}
        roles[this.role] = true
        if (this.userId === null) {
          await $api.post(API_URL, {
            first_name: this.firstName,
            last_name: this.lastName,
            username: this.username,
            email: this.email,
            organization: this.organization,
            phone_number: this.phoneNumber,
            enabled: this.enabled,
            remote: this.remote,
            roles: roles,
            groups: this.groups,
            password: this.password
          })
        }
        else {
          await $api.put(`${API_URL}/${this.userId}`, {
            first_name: this.firstName,
            last_name: this.lastName,
            username: this.username,
            email: this.email,
            organization: this.organization,
            phone_number: this.phoneNumber,
            enabled: this.enabled,
            remote: this.remote,
            roles: roles,
            groups: this.groups
          })

        }
      }
      catch (cause) {
        const error = new Error('Unable to retrieve: all users')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.loadingUser = false
      }
    },
    async deleteUser() {
      try {
        this.deletingUser = true
        await $api.delete(`${API_URL}/${this.userId}`)
      }
      catch (cause) {
        const error = new Error('Unable to retrieve: all users')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.deletingUser = false
      }
    },
    async validateUsername(username) {
      let valid = false
      try {
        valid = await $api.get('/user/validate-username', {params: {username: username}})
      }
      catch (_) {}
      return valid
    },
    async validateEmail(email) {
      let valid = false
      try {
        valid = await $api.get('/user/validate-email', {params: {email: email}})
      }
      catch (_) {}
      return valid
    },
    async unlockUserAccount(userId) {
      try {
        await getRequest(`${API_URL}/unlock/${userId}`)
      }
      catch (_) {}
    },
  }
})
