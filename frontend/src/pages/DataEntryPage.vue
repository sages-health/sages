<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page class="q-pa-md">
    <page-breadcrumbs />
    <div class="row q-mb-md">
      <div class="col-4">
        <q-select
          v-model="selectedDataSource"
          :options="dataSources"
          option-label="display_name"
          option-value="id"
          label="Select Data Source"
          @update:model-value="onDataSourceChange"
          dense
          outlined
        />
      </div>
    </div>

    <div v-if="selectedDataSource">
      <q-list>
        <q-item v-for="entry in uniqueTables" :key="entry.table">
          <q-item-section>
            <div class="text-body1">{{ entry.table }}</div>
            <div class="text-caption text-grey-7">
              {{ entry.datasets.map(d => d.display_name || d.dataset_display_name).join(', ') }}
            </div>
          </q-item-section>
          <q-item-section side>
            <q-btn
              label="Edit Data"
              color="primary"
              size="sm"
              :to="{ path: '/data/dataentry/' + selectedDataSource.id + '/' + entry.table }"
            />
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getRequest } from 'boot/axios'
import PageBreadcrumbs from 'src/components/PageBreadcrumbs.vue'

const dataSources = ref([])
const selectedDataSource = ref(null)
const datasets = ref([])

const uniqueTables = computed(() => {
  const byTable = new Map()
  datasets.value.forEach(ds => {
    const table = ds.dataset_name
    if (!byTable.has(table)) byTable.set(table, [])
    byTable.get(table).push(ds)
  })
  return Array.from(byTable.entries()).map(([table, list]) => ({
    table,
    datasets: list
  }))
})

const fetchDataSources = async () => {
  const res = await getRequest('datasource')
  dataSources.value = res.data
}

const fetchDatasetsForSource = async (datasourceId) => {
  const res = await getRequest(`dataset?datasource_id=${datasourceId}`)
  datasets.value = res.data
}

const onDataSourceChange = async () => {
  if (selectedDataSource.value?.id) {
    await fetchDatasetsForSource(selectedDataSource.value.id)
  }
  else {
    datasets.value = []
  }
}

onMounted(fetchDataSources)
</script>
