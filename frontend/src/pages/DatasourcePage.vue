<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding class="q-gutter-y-md">
    <page-breadcrumbs />
    <div class="row">
      <div
        v-if="ds"
        class="col-3"
      >
        <div class="text-h4">
          {{ ds.display_name }} ({{ ds.database_type }})
        </div>
        <div>
          <i>Point of Contact: </i><a :href="`mailto:${ds.point_of_contact_email}`"> {{ ds.point_of_contact_email }}</a>
        </div>

      </div>
    </div>
    <div class="row">
      {{ t('datasource.dataSourceWorkerHealthy') }}:
      <div v-show="!dataSourceLoading">
        <q-icon v-if="workerHealthy" :name="fasCheck" color="green" />
        <q-icon v-else :name="fasXmark" color="red"/>
      </div>
    </div>
    <div class="row">
      <div class="col-4">
        <q-select
          :options="dataSetNames"
          option-label="display_name"
          option-value="name"
          emit-value
          map-options
          v-model="selectedDataSetName"
          :label="$t('ds.Dataset')"
          :disable="!workerHealthy"
          @update:model-value="updateSelectedDataset"
        />
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <q-table
          :title="`${t('app.rowCount')}: ${queryTotal}`"
          :columns="columns"
          :loading="tableLoading"
          :rows="queryRows"
          :pagination="pagination"
          @request="updateTable"
          :rows-per-page-options="[5, 10, 25, 50]"
        />
      </div>
    </div>
    <q-inner-loading :showing="dataSourceLoading" :label="t('app.loading')"/>
  </q-page>
</template>

<script setup>
import { useRoute } from 'vue-router'
import {ref, onMounted, computed} from 'vue'
import { fasCheck, fasXmark } from '@quasar/extras/fontawesome-v6'

import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import { useI18n } from "vue-i18n"
import {debounce} from "quasar";
import {$api, getRequest, postRequest} from "boot/axios";

const { t } = useI18n()

const ds = ref()

// Loading
const dataSourceLoading = ref(false)
const tableLoading = ref(false)

// General
const workerHealthy = ref()
const selectedDataSetName = ref('')
const dataSetNames = ref([])
const dataSourceId = ref('')
const dataSetFields = ref({})
const columns = ref([])

// Table params
const queryRows = ref([])
const queryTotal = ref(0)
const queryRowsPerPage = ref(10)
const queryPage = ref(1)
const querySortBy = ref(null)
const queryDescending = ref(false)

const pagination = computed ( () => {
  return {
    page: queryPage,
    rowsPerPage: queryRowsPerPage,
    rowsNumber: queryTotal,
    sortBy: querySortBy,
    descending: queryDescending,
  }
})

const updateTable = function (tableUpdate) {
  querySortBy.value = tableUpdate.pagination.sortBy
  queryDescending.value = tableUpdate.pagination.descending
  queryRowsPerPage.value = tableUpdate.pagination.rowsPerPage
  queryPage.value = tableUpdate.pagination.page
  processQueryUpdate()
}

// Functions
const updateSelectedDataset = async function () {
  if (!dataSetFields.value.hasOwnProperty(selectedDataSetName.value)) {
    dataSetFields.value[selectedDataSetName.value] = (await getRequest('datasource/' + dataSourceId.value + '/datasets/' + selectedDataSetName.value + '/fields')).data[0].fields
  }

  columns.value = []
  for (const [key, value] of Object.entries(dataSetFields.value[selectedDataSetName.value])) {
    columns.value.push({
      name: key,
      label: key,
      field: row => row[key],
      sortable: true,
      align: 'left'
    })
  }
  await processQueryUpdate()
}

const getRows = async () => {
  tableLoading.value = true
  const projection = {}
  columns.value.forEach(function (c) {
    projection[c.name] = 1
  })
  const dataSetQuery = {projection: projection}
  if (Object.values(dataSetQuery.projection).some(x => x === 1)) {
    dataSetQuery.limit = queryRowsPerPage.value
    dataSetQuery.offset = queryRowsPerPage.value * (queryPage.value - 1)
    if (querySortBy.value !== null && dataSetQuery.projection[querySortBy.value] === 1) {
      dataSetQuery.order_by = [[querySortBy.value, queryDescending.value ? 'desc' : 'asc']]
    }
    const response = await postRequest('datasource/' + dataSourceId.value + '/datasets/' + selectedDataSetName.value + '/query', {
      dataset_metadata: dataSetFields.value[selectedDataSetName.value],
      query: dataSetQuery
    })
    queryRows.value = response.data[0].values
    queryTotal.value = response.data[0].total
  }
  tableLoading.value = false
}
const processQueryUpdate = debounce(getRows, 500)


onMounted( async () => {
  const route = useRoute()
  dataSourceId.value = route.params.dataSourceId
  dataSourceLoading.value = true
  ds.value = (await getRequest('datasource/' + dataSourceId.value)).data
  workerHealthy.value = (await getRequest('datasource/' + dataSourceId.value + '/health')).data
  if (workerHealthy.value) {
    dataSetNames.value = (await getRequest('datasource/' + dataSourceId.value + '/datasets')).data[0].datasets
  }
  dataSourceLoading.value = false
})

</script>
