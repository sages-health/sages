<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />
    <div class="row">
      <div class="col-3">
        <q-input
          :label="t('dashboard.search')"
          outlined
          v-model="search"
        >
          <template #append>
            <q-icon :name="fasMagnifyingGlass" />
          </template>
        </q-input>
      </div>
      <div class="col-3 offset-2 text-black">
        <q-btn
          :icon="fasTable"
          @click="showAsGrid = true"
          :label="t('common.grid')"
        />
        <q-btn
          :icon="fasList"
          @click="showAsGrid = false"
          :label="t('common.list')"
        />
      </div>
    </div>
    <div v-if="showAsGrid">
      <div class="q-pa-md row items-start q-gutter-md">
        <transition-group name="list">
          <q-card
            v-for="dashboard in filteredDashboards"
            :key="dashboard.id"
            class="col-5"
          >
            <q-card-section class="bg-primary text-white">
              <div class="text-h6">
                {{ dashboard.name }}
              </div>
            </q-card-section>

            <q-separator dark />

            <q-card-actions class="float-right">
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/dashboard/' + dashboard.id }"
                :icon="fasBinoculars"
                :label="t('common.open')"
              />
              <q-btn
                v-if="displayEdit"
                class="bg-primary text-white"
                :to="{ path: '/dashboard/' + dashboard.id + '/edit'}"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                v-if="displayDelete"
                class="bg-primary text-white"
                :icon="fasTrashCan"
                :label="t('common.delete')"
                @click="() => presentDeleteDialog(dashboard)"
              />
            </q-card-actions>
          </q-card>
        </transition-group>
      </div>
    </div>
    <div
      class="q-pa-md"
      v-if="!showAsGrid"
    >
      <q-list>
        <q-item
          v-for="(dashboard) in filteredDashboards"
          :key="dashboard.id"
        >
          <q-item-section>
            <q-item-label>{{ dashboard.name }}</q-item-label>
            <!--            <q-item-label caption>{{ t('datasource.pointOfContact') }}: {{ dataSource.point_of_contact_email}}</q-item-label>-->
            <!--            <q-item-label caption>{{ t('datasource.type') }}: {{ dataSource.database_type }}</q-item-label>-->
          </q-item-section>
          <q-item-section
            side
            top
          >
            <span class="q-pa-md q-gutter-sm">
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/dashboard/' + dashboard.id }"
                :icon="fasBinoculars"
                :label="t('common.open')"
              />
              <q-btn
                v-if="displayEdit"
                class="bg-primary text-white"
                :to="{ path: '/dashboard/' + dashboard.id + '/edit'}"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                v-if="displayDelete"
                class="bg-primary text-white"
                :icon="fasTrashCan"
                :label="t('common.delete')"
                @click="() => presentDeleteDialog(dashboard)"
              />
            </span>
          </q-item-section>
          <q-separator
            v-if="index < dashboards.length - 1"
            spaced
            inset
          />
        </q-item>
      </q-list>
    </div>
    <q-dialog
      v-model="showDeleteDialog"
      persistent
    >
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm">Delete: {{ dashboardToDelete.name }}? </span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancel"
            color="primary"
            v-close-popup
          />
          <q-btn
            flat
            :label="t('common.delete')"
            color="primary"
            @click="() => deleteDashboard(dashboardToDelete.id)"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <div v-if="!dashboardLoading && dashboards.length === 0">
      <h6 class="row justify-center items-center">
        {{ t('dashboard.noneAvailable') }}
      </h6>
      <div class="row justify-center items-center">
        <q-btn
          color="primary"
          :to="{ path: '/dashboard/create'}"
          :label="t('dashboard.create')"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup>

import { storeToRefs } from 'pinia'
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

import { useDashboardUIStore } from 'stores/dashboard-ui'
import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import {
  fasMagnifyingGlass,
  fasFolderOpen,
  fasTable,
  fasTrashCan,
  fasList,
  fasPencil,
  fasBinoculars
} from '@quasar/extras/fontawesome-v6'
import {deleteRequest, getRequest} from "boot/axios";
import {hasPermission} from "stores/auth";

const { t } = useI18n()

const { showAsGrid } = storeToRefs(useDashboardUIStore())

const filterDashboards = ref([])
const dashboardLoading = ref(false)
const dashboards = ref([])
const search = ref('')
const showDeleteDialog = ref(false)
const dashboardToDelete = ref({})

const displayEdit = hasPermission('update_dashboard')
const displayDelete = hasPermission('delete_dashboard')

onMounted(async () => {
  dashboardLoading.value = true
  dashboards.value = (await getRequest('dashboard')).data
  dashboardLoading.value = false
})

const deleteDashboard = async function (dashboardId) {
  dashboardLoading.value = true
  await deleteRequest('dashboard/' + dashboardId)
  dashboards.value = dashboards.value.filter(x => x.id !== dashboardId)
  dashboardLoading.value = false
}

const presentDeleteDialog = function (dashboard) {
  showDeleteDialog.value = true
  dashboardToDelete.value = dashboard
}

const filteredDashboards = computed ( () =>{
  if (!search.value.length) return dashboards.value
  return dashboards.value.filter( dashboard => dashboard.name.toLowerCase().includes(search.value.toLowerCase()) )
})

</script>
