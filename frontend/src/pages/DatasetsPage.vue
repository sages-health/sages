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
          :label="t('dataset.search')"
          outlined
          v-model="search"
        >
          <template #append>
            <q-icon :name="fasMagnifyingGlass" />
          </template>
        </q-input>
      </div>
      <div class="col-3">
        <q-select
          class="q-pl-sm"
          :options="dataSources"
          option-label="display_name"
          v-model="selectedDataSource"
          clearable
          :label="$t('datasource.single')"
          @update:model-value="dataSourcesChanged"
        />
      </div>
      <div class="col-2 offset-2 text-black">
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
      <div class="col-1 offset-1 text-right">
        <!--        TODO-Permissions: check permissions for adding datasets. -->
        <q-btn
          v-if="selectedDataSource"
          :icon="fasPlus"
          class="primary white-text"
          outlined
          :to="{ path: '/data/datasources/' + selectedDataSource.id + '/datasets/add' }"
          :label="t('dataset.addDataSet')"
        />
      </div>
    </div>
    <div v-if="showAsGrid">
      <div class="q-pa-md row items-start q-gutter-md">
        <transition-group name="list">
          <q-card
            v-for="dataSet in filteredDataSets"
            :key="dataSet.id"
            class="col-4"
          >
            <q-card-section class="bg-primary text-white">
              <div class="text-h6">
                {{ dataSet.display_name }} <span
                  v-if="!dataSet.is_active"
                  class="disabled"
                >(Inactive)</span>
              </div>
            </q-card-section>

            <q-card-section>
              <p><b>{{t('datasource.single')}}:</b>  {{ getDatasourceName(dataSet.datasource_id) }}</p>
              <p><b>{{t('common.description')}}:</b>  {{ dataSet.description }}</p>
            </q-card-section>

            <q-separator dark />

            <q-card-actions class="float-right">
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/data/datasets/' + dataSet.id }"
                :icon="fasBinoculars"
                :label="t('common.view')"
              />
              <q-btn
                v-if="displayEdit"
                class="bg-primary text-white"
                :to="{ path: '/data/datasets/' + dataSet.id + '/edit' }"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                v-if="displayDelete"
                class="bg-primary text-white"
                :icon="fasTrashCan"
                :label="t('common.delete')"
                @click="() => presentDeleteDataSetDialog(dataSet)"
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
          v-for="(dataSet) in filteredDataSets"
          :key="dataSet.id"
        >
          <q-item-section>
            <q-item-label>{{ dataSet.display_name }}</q-item-label>
            <q-item-label
              caption
              lines="2"
            >
              {{ dataSet.description }}
            </q-item-label>
          </q-item-section>
          <q-item-section
            side
            top
          >
            <span class="q-pa-md q-gutter-sm">
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/data/datasets/' + dataSet.id }"
                :icon="fasBinoculars"
                :label="t('common.view')"
              />
              <q-btn
                v-if="displayEdit"
                class="bg-primary text-white"
                :to="{ path: '/data/datasets/' + dataSet.id + '/edit' }"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                v-if="displayDelete"
                class="bg-primary text-white"
                :icon="fasTrashCan"
                :label="t('common.delete')"
                disable
              />
            </span>
          </q-item-section>
          <q-separator
            v-if="index < dataSets.length - 1"
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
          <span class="q-ml-sm">{{t('common.delete')}}: {{ dataSetToDelete.display_name }}? </span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            :label="t('common.cancel')"
            color="primary"
            v-close-popup
          />
          <q-btn
            flat
            :loading="dataSetLoading"
            :label="t('common.delete')"
            color="primary"
            @click="() => deleteDataSet(dataSetToDelete.id)"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <div v-if="!dataSetLoading && dataSets.length === 0">
      <h6 class="row justify-center items-center">
        {{ t('dataset.noneAvailable') }}
      </h6>
      <div class="row justify-center items-center">
        <q-btn
          v-if="createDataset"
          color="primary"
          :to="{ path: '/data/datasources'}"
          :label="t('dataset.create')"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup>

import { storeToRefs } from 'pinia'
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import {
  fasTable,
  fasList,
  fasPlus,
  fasMagnifyingGlass,
  fasPencil,
  fasBinoculars,
  fasTrashCan
} from '@quasar/extras/fontawesome-v6'

import { useDataSetUIStore } from 'stores/dataset-ui'
import { authStore, hasPermission } from 'stores/auth'
import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import {$api, deleteRequest, getRequest, request} from "boot/axios";

const { t } = useI18n()

const { showAsGrid } = storeToRefs(useDataSetUIStore())

const search = ref('')
const showDeleteDialog = ref(false)
const dataSetToDelete = ref({})
const dataSetLoading = ref(false)
const dataSets = ref([])
const dataSources = ref([])
const selectedDataSource = ref(null)

const filteredDataSets = computed ( () => {
  if (!search.value.length) return dataSets.value
  return dataSets.value.filter( dataSet => dataSet.display_name.toLowerCase().includes(search.value.toLowerCase()) || dataSet.description.toLowerCase().includes(search.value.toLowerCase()))
})

const presentDeleteDataSetDialog = function (dataSet) {
  showDeleteDialog.value = true
  dataSetToDelete.value = dataSet
}

const dataSourcesChanged = function (dataSource) {
  fetchDataSets()
}

const getDatasourceName = function (dataSourceId) {

  let dataSource = dataSources.value.filter(ds => ds.id === dataSourceId)
  if (dataSource.length > 0) {
    return dataSource[0].display_name
  }
  return ''
}
const displayEdit = hasPermission('update_dataset')
const displayDelete = hasPermission('delete_dataset')
const createDataset = hasPermission('create_dataset')

const fetchDataSets = async function () {
  dataSetLoading.value = true
  if (selectedDataSource.value === null) {
    dataSets.value = (await request({'url': 'dataset', 'method': 'get', 'errorMessage': 'Unable to retrieve data sets'})).data
  }
  else {
    dataSets.value = (await request({'url': 'dataset', 'method': 'get', 'errorMessage': 'Unable to retrieve data sets', 'params': {datasource_id: selectedDataSource.value.id}})).data
  }
  dataSetLoading.value = false
}

const deleteDataSet = async function (dataSetId) {
  dataSetLoading.value = true
  await deleteRequest('dataset/' + dataSetId)
  dataSets.value = dataSets.value.filter(x => x.id !== dataSetId)
  dataSetLoading.value = false
}

onMounted(async () => {
  const route = useRoute()
  dataSources.value = (await getRequest('datasource')).data
  let dataSourceId = 'dataSourceId' in route.params ? route.params.dataSourceId : null

  if (dataSourceId !== null) {
    let dataSource = dataSources.value.filter(ds => ds.id === dataSourceId)
    if (dataSource.length > 0) {
      selectedDataSource.value = dataSource[0]
    }
  }
  await fetchDataSets()

})

</script>
