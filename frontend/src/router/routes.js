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

import MainLayout from 'layouts/MainLayout.vue'
import AuthLayout from 'layouts/AuthLayout.vue'
import SiteLayout from 'layouts/SiteLayout.vue'
import PageLayout from 'layouts/PageLayout.vue'

import AuthLogin from 'pages/AuthLogin.vue'
import ErrorNotFound from 'pages/ErrorNotFound.vue'

import { authStore } from 'stores/auth'

function requirePermission (...permissions) {
  return async function guardPermission (to) {
    if (!authStore.user ||
      !_some(['admin', ...permissions], (permission) => authStore.user.permissions[permission])
    ) {
      if (to.name && to.name === 'home') {
        await authStore.logout()
        return { name: 'login' }
      }
      else {
        return { name: 'home' }
      }
    }
  }
}

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '/login',
        component: AuthLayout,
        children: [
          { name: 'login', path: '', component: AuthLogin },
          {
            name: 'force-password-reset',
            path: 'reset-password',
            component: () => import('pages/ForcePasswordReset.vue')
          },
          {
            name: 'forgot-password',
            path: 'forgot-password',
            component: () => import('pages/ForgotPassword.vue')
          },
          {
            name: 'set-password',
            path: 'set-password',
            component: () => import('pages/SetPassword.vue')
          }
        ]
      },
      {
        name: 'home',
        path: '',
        component: SiteLayout,
        children: [
          {
            path: 'dashboard',
            component: PageLayout,
            beforeEnter: requirePermission('read_dashboards'),
            children: [
              {
                path: '',
                component: () => import('pages/DashboardPage.vue')
              },
              {
                path: 'create',
                component: () => import('pages/DashboardCreate.vue'),
                force: true
              },
              {
                path: ':dashboardId',
                component: () => import('pages/ViewDashboard.vue')
              },
              {
                path: ':dashboardId/edit',
                component: () => import('pages/DashboardCreate.vue')
              }
            ]
          },
          {
            path: 'visualization',
            component: PageLayout,
            beforeEnter: requirePermission('read_visualizations'),
            children: [
              {
                path: '',
                component: () => import('pages/VisualizationsPage.vue')
              },
              {
                path: 'create',
                component: () => import('pages/VisualizationCreate.vue')
              },
              {
                path: ':visualizationId',
                component: () => import('pages/ViewVisualization.vue')
              },
              {
                path: ':visualizationId/edit',
                component: () => import('pages/VisualizationCreate.vue')
              },
              {
                path: 'overlay/create',
                component: () => import('pages/VisualizationOverlayCreate.vue')
              },
              {
                path: 'overlay/:visualizationId/edit',
                component: () => import('pages/VisualizationOverlayCreate.vue')
              },
            ]
          },
          {
            path: 'data',
            component: PageLayout,
            children: [
              {
                path: 'datasets',
                beforeEnter: requirePermission('read_datasets_shared', 'read_datasets_all'),
                component: () => import('pages/DatasetsPage.vue')
              },
              {
                path: 'datasets/:dataSetId',
                beforeEnter: requirePermission('read_dataset_shared', 'read_dataset_all'),
                component: () => import('pages/ViewDatasetPage.vue')
              },
              {
                path: 'datasets/:dataSetId/edit',
                beforeEnter: requirePermission('read_dataset_shared', 'read_dataset_all', 'read_users'),
                component: () => import('pages/AddDatasetPage.vue')
              },
              {
                path: 'dataentry',
                // beforeEnter: requirePermission('read_datasources'),
                component: () => import('pages/DataEntryPage.vue')
              },
              {
                path: 'dataentry/:dataSourceId/:table',
                // beforeEnter: requirePermission('read_datasources'),
                component: () => import('pages/ViewDataEntryPage.vue')
              },
              {
                path: 'datasources',
                beforeEnter: requirePermission('read_datasources'),
                component: () => import('pages/DatasourcesPage.vue')
              },
              {
                path: 'datasources/add',
                beforeEnter: requirePermission('create_datasource'),
                component: () => import('pages/AddDatasourcePage.vue')
              },
              {
                path: 'datasources/:dataSourceId',
                beforeEnter: requirePermission('read_datasource'),
                component: () => import('pages/DatasourcePage.vue')
              },
              {
                path: 'datasources/:dataSourceId/edit',
                beforeEnter: requirePermission('update_datasource'), // TODO-Permissions: Should this be datasource dependent?
                component: () => import('pages/AddDatasourcePage.vue')
              },
              {
                path: 'datasources/:dataSourceId/datasets',
                beforeEnter: requirePermission('read_datasets_all'), // TODO-Permissions: Should this be datasource dependent?
                component: () => import('pages/DatasetsPage.vue')
              },
              {
                path: 'datasources/:dataSourceId/datasets/add',
                beforeEnter: requirePermission('create_dataset'),
                component: () => import('pages/AddDatasetPage.vue')
              },
              {
                path: 'maps',
                beforeEnter: requirePermission('read_maps'),
                component: () => import('pages/MapsPage.vue')
              },
              {
                path: 'maps/add',
                beforeEnter: requirePermission('create_map'),
                component: () => import('pages/MapCreate.vue')
              },
              {
                path: 'maps/:mapId/edit',
                beforeEnter: requirePermission('create_map', 'read_maps'),
                component: () => import('pages/MapCreate.vue')
              },
              {
                path: 'maps/:mapId',
                beforeEnter: requirePermission('read_maps'),
                component: () => import('pages/ViewMap.vue')
              },
              {
                path: 'upload',
                beforeEnter: requirePermission('create_dataset'),
                component: () => import('pages/UploadDataPage.vue')
              },
            ]
          },
          {
            path: 'admin',
            component: PageLayout,
            children: [
              {
                path: 'users',
                beforeEnter: requirePermission('read_users'),
                component: () => import('pages/UsersPage.vue')
              },
              {
                path: 'users/add',
                beforeEnter: requirePermission('read_users', 'add_user'),
                component: () => import('pages/AddUserPage.vue')
              },
              {
                path: 'users/:userId',
                beforeEnter: requirePermission('read_users', 'edit_user'),
                component: () => import('pages/AddUserPage.vue')
              },
              {
                path: 'groups',
                beforeEnter: requirePermission('read_groups'),
                component: () => import('pages/GroupsPage.vue')
              },
              {
                path: 'groups/add',
                beforeEnter: requirePermission('read_groups', 'create_group'),
                component: () => import('pages/AddGroupPage.vue')
              },
              {
                path: 'groups/:groupId',
                beforeEnter: requirePermission('read_groups'),
                component: () => import('pages/AddGroupPage.vue')
              },
              {
                path: 'groups/:groupId/edit',
                beforeEnter: requirePermission('read_groups', 'edit_group'),
                component: () => import('pages/AddGroupPage.vue')
              }
            ]
          }
        ]
      },
      { path: '/:catchAll(.*)*', component: ErrorNotFound }
    ]
  }
]

export default routes
