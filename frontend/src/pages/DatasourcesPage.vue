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
          :label="t('datasource.search')"
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
            v-for="dataSource in filteredDataSources"
            :key="dataSource.id"
            class="col-5"
          >
            <q-card-section class="bg-primary text-white">
              <div class="text-h6">
                {{ dataSource.display_name }}
              </div>
            </q-card-section>

            <q-card-section>
              <p><i>{{ t('datasource.pointOfContact') }}:</i> {{ dataSource.point_of_contact_email }}</p>
              <span>
                {{ t('datasource.dataSourceWorkerHealthy') }}:
                <q-spinner v-if="dataSourceHealthLoading.hasOwnProperty(dataSource.id) && dataSourceHealthLoading[dataSource.id]" />
                <template v-else>
                  <q-icon
                    v-if="workerHealthy.hasOwnProperty(dataSource.id) && workerHealthy[dataSource.id]"
                    :name="fasCheck"
                    color="green"
                  />
                  <q-icon
                    v-else
                    :name="fasXmark"
                    color="red"
                  />
                </template>
              </span>
            </q-card-section>

            <q-separator dark />

            <q-card-actions class="float-right">
              <q-btn
                :disable="disableActions[dataSource.id] || dataSourceHealthLoading[dataSource.id]"
                class="bg-primary text-white"
                :to="{ path: '/data/datasources/' + dataSource.id }"
                :icon="fasFolderOpen"
                :label="t('common.view')"
              />
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/data/datasources/' + dataSource.id + '/datasets' }"
                :icon="fasFolderOpen"
                :label="t('datasource.viewDataSets')"
              />
              <q-btn
                :disable="disableActions[dataSource.id] || dataSourceHealthLoading[dataSource.id]"
                class="bg-primary text-white"
                :to="{ path: '/data/datasources/' + dataSource.id + '/datasets/add' }"
                :icon="fasPlus"
                :label="t('datasource.addDataSet')"
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
          v-for="(dataSource) in filteredDataSources"
          :key="dataSource.id"
        >
          <q-item-section>
            <q-item-label>{{ dataSource.display_name }}</q-item-label>
            <q-item-label caption>
              {{ t('datasource.pointOfContact') }}: {{ dataSource.point_of_contact_email }}
            </q-item-label>
            <q-item-label caption>
              {{ t('datasource.') }}: {{ dataSource.database_type }}
            </q-item-label>
            <q-item-label caption>
              {{ t('datasource.dataSourceWorkerHealthy') }}:
              <q-spinner v-if="dataSourceHealthLoading.hasOwnProperty(dataSource.id) && dataSourceHealthLoading[dataSource.id]" />
              <template v-else>
                <q-icon
                  v-if="workerHealthy.hasOwnProperty(dataSource.id) && workerHealthy[dataSource.id]"
                  :name="fasCheck"
                  color="green"
                />
                <q-icon
                  v-else
                  :name="fasXmark"
                  color="red"
                />
              </template>
            </q-item-label>
          </q-item-section>
          <q-item-section
            side
            top
          >
            <span class="q-pa-md q-gutter-sm">
              <q-btn
                :disable="disableActions[dataSource.id] || dataSourceHealthLoading[dataSource.id]"
                class="bg-primary text-white"
                :to="{ path: '/data/datasources/' + dataSource.id }"
                :icon="fasFolderOpen"
                :label="t('common.view')"
              />
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/data/datasources/' + dataSource.id + '/datasets' }"
                :icon="fasFolderOpen"
                :label="t('datasource.viewDataSets')"
              />
              <q-btn
                :disable="disableActions[dataSource.id] || dataSourceHealthLoading[dataSource.id]"
                class="bg-primary text-white"
                :to="{ path: '/data/datasources/' + dataSource.id + '/datasets/add' }"
                :icon="fasPlus"
                :label="t('datasource.addDataSet')"
              />
            </span>
          </q-item-section>
          <q-separator
            v-if="index < dataSources.length - 1"
            spaced
            inset
          />
        </q-item>
      </q-list>
    </div>
    <div v-if="!dataSourceLoading">
      <div class="row justify-center items-center">
        <q-btn
          v-if="createDatasource"
          color="primary"
          :to="{ path: '/data/datasources/add'}"
          :label="t('datasource.create')"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup>

import { storeToRefs } from 'pinia'
import {ref, computed, onMounted, watch} from 'vue'
import { useI18n } from 'vue-i18n'
import {getRequest} from "boot/axios";

import { useDataSourceUIStore } from 'stores/datasource-ui'
import { hasPermission } from 'stores/auth'
import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import {
  fasPlus,
  fasMagnifyingGlass,
  fasFolderOpen,
  fasTable,
  fasList,
  fasCheck,
  fasXmark
 } from '@quasar/extras/fontawesome-v6'

const { t } = useI18n()
const { showAsGrid } = storeToRefs(useDataSourceUIStore())

const dataSources = ref([])
const dataSourceHealthLoading = ref({})
const workerHealthy = ref({})
const dataSourceLoading = ref(false)
const disableActions = ref({})
let search = ref('')

const createDatasource = hasPermission('create_datasource')

onMounted(async () => {
  dataSourceLoading.value = true
  dataSources.value = (await getRequest('datasource')).data

  const checkHealth = async function(dataSourceId) {
    const result = await getRequest('datasource/' + dataSourceId + '/health')
    return result.data
  }

  dataSources.value.forEach(function(ds) {
    const dataSourceId = ds.id
    dataSourceHealthLoading.value[dataSourceId] = true
    checkHealth(dataSourceId).then( function (workerHealth) {
      workerHealthy.value[dataSourceId] = workerHealth
      disableActions.value[dataSourceId] = !workerHealth
    })
    .catch(() => {
      workerHealthy.value[dataSourceId] = false
      disableActions.value[dataSourceId] = true
    })
    .finally(() => dataSourceHealthLoading.value[dataSourceId] = false)
  })
  dataSourceLoading.value = false
})

const filteredDataSources = computed ( () =>{
  if (!search.value.length) return dataSources.value
  return dataSources.value.filter( dataSource => dataSource.display_name.toLowerCase().includes(search.value.toLowerCase()) )
})

</script>
