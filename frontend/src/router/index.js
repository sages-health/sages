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

import { route } from 'quasar/wrappers'
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory
} from 'vue-router'
import { pinia } from 'stores/index'
import { useAuthStore } from 'stores/auth'
import routes from './routes'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

const router = createRouter({
  scrollBehavior: () => ({ left: 0, top: 0 }),
  routes,

  // Leave this as is and make changes in quasar.conf.js instead!
  // quasar.conf.js -> build -> vueRouterMode
  // quasar.conf.js -> build -> publicPath
  history: createWebHashHistory(process.env.VUE_ROUTER_BASE)
})

router.beforeEach((to, _) => {
  const authStore = useAuthStore(pinia)
  let refreshSuccess = false
  const publicPages = ['login', 'forgot-password', 'set-password', 'force-password-reset']
  authStore.refresh().then(success => {
    refreshSuccess = success
  })

  if (!refreshSuccess && !authStore.isAuthenticated && !publicPages.includes(to.name)) {
    const next = { name: 'login' }
    if (!to.name || to.name !== 'home') {
      next.query = { next: to.fullPath }
    }
    return next
  }

  if (authStore.isAuthenticated && authStore.mustChangePassword && to.name !== 'force-password-reset') {
    return { name: 'force-password-reset' }
  }

  if (authStore.isAuthenticated && !authStore.mustChangePassword && to.name === 'force-password-reset') {
    return { name: 'home' }
  }
})

export default route(function (/* { store, ssrContext } */) {
  // const createHistory = createWebHashHistory //process.env.SERVER
    // ? createWebHashHistory
    // : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)
  return router
})

export { router }
