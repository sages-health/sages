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
import {$api} from 'boot/axios'

const API_URL = 'group'

export const useGroupStore = defineStore('group', {
  state() {
    return {
      groupName: null,
      groupId: null,

      allGroups: [],
      groupUserList: [],
      groupDatasetList: [],
      loadingDatasets: false,
      loadingGroup: false,
      loadingUsers: false,
      loadingAllGroups: false,
      deletingGroup: false
    }
  },
  getters: {
    getAll: (state) => {
      return state.allGroups
    },
  },
  actions: {
    async fetchAllGroups() {
      try {
        this.loadingAllGroups = true
        this.allGroups = (await $api.get('group')).data.map(
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
        this.loadingAllGroups = false
      }
    },
    async fetchGroup(groupId) {
      try {
        this.loadingGroup = true
        const group = (await $api.get(`${API_URL}/${groupId}`)).data
        this.groupId = group.id
        this.groupName = group.group_name
      }
      catch (cause) {
        const error = new Error('Unable to retrieve group')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.loadingGroup = false
      }
    },
    async saveGroup() {
      try {
        this.loadingGroups = true
        if (this.groupId === null) {
          await $api.post(API_URL, {
            group_name: this.groupName,
          })
        }
        else {
          await $api.put(`${API_URL}/${this.groupId}`, {
            group_name: this.groupName
          })
        }
      }
      catch (cause) {
        const error = new Error('Unable to save group')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.loadingGroups = false
      }
    },
    async deleteGroup(group=null) {
      try {
        this.deletingGroup = true
        if (group != null) {
          await $api.delete( `${API_URL}/${group}`)
        }
        else {
          await $api.delete( `${API_URL}/${this.groupId}`)
        }
      }
      catch (cause) {
        const error = new Error('Unable to delete group')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.deletingGroup = false
      }
    },
    async fetchGroupUsers(groupId) {
      try {
        this.loadingUsers = true
        const users = (await $api.get(`${API_URL}/users/${groupId}`)).data
        this.groupUserList = users
      }
      catch (cause) {
        const error = new Error('Unable to retrieve group')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.loadingUsers = false
      }
    },
    async fetchGroupDatasets(groupId) {
      try {
        this.loadingDatasets = true
        const datasets = (await $api.get(`${API_URL}/datasets/${groupId}`)).data
        this.groupDatasetList = datasets
      }
      catch (cause) {
        const error = new Error('Unable to retrieve group')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
      finally {
        this.loadingDatasets = false
      }
    },
    renderGroupNames(groupIds) {
      if (!groupIds) {
        return ""
      }
      else {
        return groupIds.map(groupId =>
          this.allGroups.find(
            (group) => group.id === groupId
          )?.groupName).sort().join(", ")
      }
    }
}})
