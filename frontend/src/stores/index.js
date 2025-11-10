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

import { store } from 'quasar/wrappers'
import { createPinia } from 'pinia'
import { watch } from 'vue'

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Store instance.
 */

export const pinia = createPinia()

// You can add Pinia plugins here
// pinia.use(SomePiniaPlugin)

export default store((/* { ssrContext } */) => {
  return pinia
})

export function synchronizeState (store, key, options = {}) {
  const serialize = options.serialize || JSON.stringify
  const deserialize = options.deserialize || JSON.parse
  const setItem = options.setItem ||
    (options.storage && options.storage.setItem) ||
    window.localStorage.setItem.bind(window.localStorage)
  const getItem = options.getItem ||
    (options.storage && options.storage.getItem) ||
    window.localStorage.getItem.bind(window.localStorage)

  const rawState = getItem(key)
  if (rawState) {
    const state = deserialize(rawState)
    store.$patch(state)
    options.hydrate && options.hydrate(store)
  }

  watch(store.$state, (state) => {
    if (state) {
      setItem(key, serialize({
        isAuthenticated: state.isAuthenticated,
        accessToken: state.accessToken,
      }))
      options.update && options.update(store)
    }
  }, { deep: true })
}
