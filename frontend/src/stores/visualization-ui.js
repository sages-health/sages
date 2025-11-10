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

const API_URL = 'visualization'

/**
 * Have to break out UI store from other stores because we're resetting the store in page navigation for some reason
 * @type {StoreDefinition<"dashboard-ui", {}, {}, {}>}
 */
export const useVisualizationUIStore = defineStore('visualization-ui', {
  state () {
    return {
      showAsGrid: true,
      visualizations: [] // visualizations user has access to, according to their group
    }
  },
  actions: {
    async checkUserAccess(visualizationId) {
      try {
        const visualization = (await $api.get(`${API_URL}/${visualizationId}`)).data
        this.visualizations.push(visualization)
      }
      catch (cause) {
        const error = new Error('Unable to retrieve visualization')
        const errorStack = (error.stack !== undefined) ? error.stack : ''
        const causeStack = (cause.stack !== undefined) ? cause.stack : ''
        if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
        throw error
      }
    }
  }
})
