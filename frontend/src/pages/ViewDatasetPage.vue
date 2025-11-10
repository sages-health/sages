<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page
    padding
    class="q-gutter-y-md"
  >
    <page-breadcrumbs />
    <!--  Title  Edit Row   -->
    <div class="row">
      <div class="col-4 ">
        <h6><strong>{{ t('common.title') }}:</strong> <i>{{ title }}</i></h6>
      </div>
      <div class="col-7">
        <h6><strong>{{ t('dataset.description') }}:</strong> <i id="description">{{ description }}</i></h6>
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <q-table
          :title="`${t('common.rowCount')}: ${queryTotal}`"
          :columns="columns"
          :loading="dataSetLoading"
          :rows="queryRows"
          :pagination="pagination"
          @request="updateTable"
          :no-data-label="$t('common.noData')"
          :rows-per-page-options="[5, 10, 25, 50]"
        />
      </div>
    </div>
  </q-page>
</template>


<script setup>

import { useRoute } from 'vue-router'
import { computed, onMounted, ref } from 'vue'
import { debounce } from 'quasar'
import { useI18n } from 'vue-i18n'

import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'

import {getRequest, postRequest} from "boot/axios";
import {convertLastNBack} from "src/composables/visualization";

const { t } = useI18n()

// DataSet refs
const dataSetId = ref(null)
const title = ref('')
const description = ref('')
const dataSetLoading = ref(false)
const fields = ref({})

// Query refs
const queryRows = ref([])
const queryTotal = ref(0)
const queryRowsPerPage = ref(10)
const queryPage = ref(1)
const querySortBy = ref(null)
const queryDescending = ref(false)

const columns = ref([])

// Data Table Computed Values
const pagination = computed ( () => {
  return {
    page: queryPage,
    rowsPerPage: queryRowsPerPage,
    rowsNumber: queryTotal,
    sortBy: querySortBy,
    descending: queryDescending,
  }
})

// =============== Data Table Functions ===============
const getRows = debounce(async function () {
  let queryOpts = {}
  queryOpts.queryRowsPerPage = queryRowsPerPage.value;
  queryOpts.queryPage = queryPage.value;
  if (querySortBy.value !== null) {
    queryOpts.querySortBy = querySortBy.value;
    queryOpts.queryDescending = queryDescending.value;
  }
  await query(dataSetId.value, queryOpts)
}, 500)

const updateTable = function (tableUpdate) {
  querySortBy.value = tableUpdate.pagination.sortBy
  queryDescending.value = tableUpdate.pagination.descending
  queryRowsPerPage.value = tableUpdate.pagination.rowsPerPage
  queryPage.value = tableUpdate.pagination.page
  getRows()
}

// =============== Dataset Functions ===============
/*
 * Fetch dataset from the backend.
 */
const fetchDataSet = async function (dataSetId) {
  dataSetLoading.value = true
  const dataSet = (await getRequest( 'dataset/' + dataSetId)).data
  description.value = dataSet.description
  title.value = dataSet.display_name

  dataSet.fields.forEach(function (field) {
    columns.value.push({name: field.data_field_name, label: field.display_name, field: row => row[field.data_field_name], sortable: true, align: 'left'})
  })
  dataSetLoading.value = false
}

const query = async function (dataSetId, queryOpts) {
  dataSetLoading.value = true
  let dataSetQuery = {}
  if (queryOpts.queryRowsPerPage) {
    dataSetQuery.limit = queryOpts.queryRowsPerPage
  }
  if (queryOpts.queryPage && queryOpts.queryRowsPerPage) {
    dataSetQuery.offset = queryOpts.queryRowsPerPage * (queryOpts.queryPage - 1)
  }
  if (queryOpts.querySortBy !== null && queryOpts.querySortBy) {
    dataSetQuery.order_by = [[queryOpts.querySortBy, queryOpts.queryDescending ? 'desc' : 'asc']]
  }
  const response = await postRequest('dataset/' + dataSetId + '/query', dataSetQuery)
  queryRows.value = response.data[0].values
  queryTotal.value = response.data[0].total

  dataSetLoading.value = false
}

onMounted( async () => {
  const route = useRoute()
  dataSetId.value = 'dataSetId' in route.params ? route.params.dataSetId : null
  await fetchDataSet(dataSetId.value)
  await getRows()
})

</script>

<style scoped>
  #description {
    font-size: 16px;
  }

</style>
