<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <div>
    <q-drawer
      v-model="leftDrawerOpen"
      bordered
      behavior="desktop"
      :width="325"
    >
      <q-scroll-area class="fit">
        <q-list>
          <q-expansion-item
            v-if="hasReadDashboards"
            expand-separator
            :icon="fasTableColumns"
            :content-inset-level="1"
            :label="t('nav.dashboard.category')"
            default-opened
          >
            <q-list>
              <q-item
                clickable
                :to="{ path: '/dashboard/create', force: true }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasFolderPlus" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.dashboard.new') }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                clickable
                :to="{ path: '/dashboard' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasFolderOpen" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.dashboard.open') }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-expansion-item>
          <q-expansion-item
            v-if="hasReadVisualizations"
            expand-separator
            :icon="fasChartPie"
            :content-inset-level="1"
            :label="t('nav.visualization.category')"
            default-opened
          >
            <q-list>
              <q-item
                clickable
                :to="{ path: '/visualization/create' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasChartLine" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.visualization.new') }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                clickable
                :to="{ path: '/visualization/overlay/create' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasChartSimple" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.visualization.newOverlay') }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                clickable
                :to="{ path: '/visualization' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasPenToSquare" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.visualization.open') }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-expansion-item>
          <q-expansion-item
            v-if="hasReadData"
            expand-separator
            :icon="fasTableList"
            :content-inset-level="1"
            :label="t('nav.data.category')"
            default-opened
          >
            <q-list>
              <q-item
                v-if="hasReadDataSets"
                clickable
                :to="{ path: '/data/datasets' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasBorderAll" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.dataset.category') }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                v-if="hasReadDataSets"
                clickable
                :to="{ path: '/data/dataentry' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasPlus" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ "Data Entry" }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                v-if="hasCreateDataSources"
                clickable
                :to="{ path: '/data/datasources' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasDatabase" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.datasource.category') }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                v-if="hasReadMaps"
                clickable
                :to="{ path: '/data/maps' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasMap" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.map.category') }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                  v-if="hasCreateDataSources"
                  clickable
                  :to="{ path: '/data/upload' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasPaperclip" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.data.upload') }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-expansion-item>
          <q-expansion-item
            v-if="hasAdmin"
            expand-separator
            :icon="fasScrewdriverWrench"
            :content-inset-level="1"
            :label="t('nav.admin.category')"
            default-opened
          >
            <q-list>
              <q-item
                v-if="hasReadUsers"
                clickable
                :to="{ path: '/admin/users' }"
              >
                <q-item-section avatar>
                  <q-icon :name="fasUserGear" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ t('nav.admin.users') }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                v-if="hasReadGroups"
                clickable
                :to="{ path: '/admin/groups'}"
                >
                <q-item-section avatar>
                  <q-icon :name="fasUsers" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ $t('usergroups.groups') }}</q-item-label>
                </q-item-section>
                </q-item>
            </q-list>
          </q-expansion-item>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-page-container>
      <router-view :key="$route.path + '_site'" />
    </q-page-container>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'

import {
  fasChartSimple,
  fasBorderAll,
  fasMap,
  fasChartLine,
  fasChartPie,
  fasDatabase,
  fasFolderOpen,
  fasFolderPlus,
  fasPenToSquare,
  fasScrewdriverWrench,
  fasTableColumns,
  fasTableList,
  fasUsers,
  fasUserGear,
  fasPaperclip,
  fasPlus
} from '@quasar/extras/fontawesome-v6'

import { useStore } from 'stores/main'
import { hasPermission } from 'stores/auth'

const { t } = useI18n()

const store = useStore()
const { leftDrawerOpen } = storeToRefs(store)

const hasReadDashboards = hasPermission('read_dashboards')
const hasReadVisualizations = hasPermission('read_visualizations')
const hasReadMaps = hasPermission('read_maps')

const hasReadData = hasPermission(
    'read_datasets_all',
    'read_datasets_shared',
    'read_datasources'
)
const hasReadDataSets = hasPermission('read_datasets_shared', 'read_datasets_all')
const hasCreateDataSources = hasPermission('create_datasources')

const hasAdmin = hasPermission(
  'read_users'
)
const hasReadUsers = hasPermission('read_users')

const hasReadGroups = hasPermission('read_groups')
</script>
