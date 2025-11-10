<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <div class="q-pa-md q-gutter-y-md">
    <div class="row">
      <div class="col-4">
        <h6><strong>Datasource:</strong> <i>{{ dataSource.display_name }}</i></h6>
      </div>
      <div class="col-7">
        <h6><strong>Table:</strong> <i>{{ tableName }}</i></h6>
      </div>
    </div>

    <div class="row q-mb-md items-end">
      <div class="col-3">
        <q-select
          dense
          outlined
          v-model="filterColumn"
          :options="columnOptions"
          label="Filter column"
          clearable
        />
      </div>
      <div class="col-4">
        <q-input
          dense
          outlined
          v-model="filterValue"
          :label="filterColumn ? `Filter ${filterColumn}` : 'Filter value'"
          :disable="!filterColumn"
          clearable
        />
      </div>
      <div class="col-2">
        <q-btn
          dense
          label="Clear filter"
          @click="clearFilter"
          :disable="!filterColumn && !filterValue"
        />
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <q-table
          :title="`Rows: ${filteredRows.length}`"
          :columns="columns"
          :loading="loading"
          :rows="filteredRows"
          :pagination="pagination"
          @request="updateTable"
          :no-data-label="'No data'"
          :rows-per-page-options="[5, 10, 25, 50]"
          flat
          dense
        >
          <template v-slot:body-cell="props">
            <q-td :props="props">
              <template v-if="props.col.name === 'delete'">
                <q-btn
                  dense
                  flat
                  round
                  color="red"
                  size="sm"
                  @click="deleteRow(props.row)"
                  :icon="fasTrashCan"
                  :disable="props.row._saving"
                />
              </template>
              <template v-else>
                <q-input
                  v-if="props.col.field_kind === 'str'"
                  dense
                  outlined
                  hide-bottom-space
                  v-model="props.row[props.col.name]"
                  @blur="markDirty(props.row, props.col.name)"
                  :disable="props.row._saving"
                />
                <q-input
                  v-else-if="props.col.field_kind === 'int' || props.col.field_kind === 'float' || props.col.field_kind === 'double'"
                  dense
                  outlined
                  hide-bottom-space
                  type="number"
                  v-model.number="props.row[props.col.name]"
                  @blur="markDirty(props.row, props.col.name)"
                  :disable="props.row._saving"
                />
                <q-input
                  v-else-if="props.col.field_kind === 'date' || props.col.field_kind === 'datetime'"
                  dense
                  outlined
                  hide-bottom-space
                  type="date"
                  v-model="props.row[props.col.name]"
                  @blur="markDirty(props.row, props.col.name)"
                  :disable="props.row._saving"
                />
                <q-toggle
                  v-else-if="props.col.field_kind === 'bool'"
                  v-model="props.row[props.col.name]"
                  @update:model-value="markDirty(props.row, props.col.name)"
                  :disable="props.row._saving"
                  dense
                />
                <q-input
                  v-else
                  dense
                  outlined
                  hide-bottom-space
                  v-model="props.row[props.col.name]"
                  @blur="markDirty(props.row, props.col.name)"
                  :disable="props.row._saving"
                />
              </template>
            </q-td>
          </template>
        </q-table>

        <q-btn
          label="Save Changes"
          color="primary"
          :disable="!hasDirtyRows"
          class="q-mt-md"
          @click="saveChanges"
        />
        <q-btn
          label="Add New Row"
          color="secondary"
          class="q-mt-md q-ml-sm"
          @click="addNewRow"
        />
        <div
          class="q-mt-sm"
          :style="{ color: saveStatusColor }"
        >
          {{ saveStatusMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { unref } from 'vue'
import { computed, onMounted, ref } from 'vue'
import { debounce } from 'quasar'
import { getRequest, postRequest } from 'boot/axios'
import { fasTrashCan } from '@quasar/extras/fontawesome-v6'

const route = useRoute()
const dataSourceId = route.params.dataSourceId
const dataSource = ref('')
const tableName = route.params.table

const loading = ref(false)
const fields = ref({})
const columns = ref([])

const rows = ref([])
const dataset_configs = ref(null)
const total = ref(0)
const queryRowsPerPage = ref(10)
const queryPage = ref(1)
const querySortBy = ref(null)
const queryDescending = ref(false)

const filterColumn = ref(null)
const filterValue = ref('')

const saveStatusMessage = ref('')
const saveStatusColor = ref('black')

const columnOptions = computed(() =>
  columns.value
    .filter(c => c.name !== 'delete')
    .map(col => ({ label: col.label, value: col.name }))
)

const filteredRows = computed(() => {
  if (!filterColumn.value || !filterValue.value) return rows.value
  return rows.value.filter(r => {
    const val = r[filterColumn.value.value]
    return val != null && String(val).toLowerCase().includes(filterValue.value.toLowerCase())
  })
})

const pk_cols = computed(() =>
  dataset_configs.value?.[tableName]?.primary_key_columns ?? []
)

const pagination = computed(() => ({
  page: queryPage.value,
  rowsPerPage: queryRowsPerPage.value,
  rowsNumber: total.value,
  sortBy: querySortBy.value,
  descending: queryDescending.value
}))

function mapType(t) {
  const s = String(t || '').toLowerCase()
  if (s.includes('bool')) return 'bool'
  if (s.includes('date') || s.includes('time')) return 'date'
  if (s.includes('int')) return 'int'
  if (s.includes('float') || s.includes('real') || s.includes('double') || s.includes('numeric')) return 'float'
  return 'str'
}

async function loadFields() {
  const res = await getRequest(`datasource/${dataSourceId}/datasets/${tableName}/fields`)
  fields.value = res.data[0].fields
  columns.value = [
    ...Object.entries(fields.value)
        // hide the vims_primary_key col
        .filter(([name]) => name !== 'vims_primary_key')
        .map(([name, type]) => ({
      name,
      label: name,
      field: row => row[name],
      field_kind: mapType(type),
      sortable: true,
      align: 'left'
    })),
    { name: 'delete', label: 'Delete', field: 'delete', align: 'center', sortable: false }
  ]
}

async function loadDatasetConfigs() {
  // load the configs from configurations.json
  try {
    const res = await getRequest('/etl/config')
    dataset_configs.value = res.data
  }
  catch (e) {
    // console.error('Failed to load /etl/config', e)
    dataset_configs.value = null
  }
}

async function loadRows(opts = {}) {
  loading.value = true
  const datasetMetadata = fields.value
  const query = {}
  if (opts.limit) {
    query.limit = opts.limit
    query.offset = opts.limit * (opts.page - 1)
  }
  if (opts.sortBy) {
    query.order_by = [[opts.sortBy, opts.desc ? 'desc' : 'asc']]
  }
  const res = await postRequest(
    `datasource/${dataSourceId}/datasets/${tableName}/query`,
    { dataset_metadata: datasetMetadata, query }
  )
  const vals = res.data[0].values
  rows.value = vals.map(r => ({ ...r, _original: { ...r } }))
  total.value = res.data[0].total
  loading.value = false
}

function markDirty(row, col) {
  const v = row[col]
  if (row._original[col] === v) return
  row._dirty = true
  row._pending = row._pending || {}
  row._pending[col] = v
}

const hasDirtyRows = computed(() => rows.value.some(r => r._dirty))

function buildPkString(row) {
  // If a pk value is needed for a new row/edited row, build one
  // Pk is built by concatenating the values in each of the pk_cols, which are found in the table's config
  return pk_cols.value
    .map(col => {
      const v = row[col]
      if (v == null || (typeof v === 'string' && v.trim() === ''))
        throw new Error(`Missing primary key value for "${col}"`)
      return String(v).trim()
    })
    .join('_')
}

function cleanRow(row) {
  const copy = { ...row }
  delete copy._original
  delete copy._dirty
  delete copy._pending
  delete copy._isNew
  delete copy.delete

  // Create a primary key entry in row being updated if missing
  const constructed_pk = buildPkString(copy)

  // If no vims_primary_key key in row (i.e. if a row was added), create one
  if (!Object.hasOwn(copy, 'vims_primary_key')){
    copy['vims_primary_key'] = constructed_pk
    // If vims_primary_key value was erased (is null or empty string from editing), repopulate value
  }
  else{}

  return copy
}

function generateEmptyRow() {
  const r = {}
  columns.value.forEach(c => {
    if (c.name !== 'delete') r[c.name] = ''
  })
  r._original = {}
  r._dirty = true
  r._pending = { ...r }
  r._isNew = true
  return r
}

function addNewRow() {
  rows.value.push(generateEmptyRow())
}

async function saveChanges() {
  const dirty = rows.value.filter(r => r._dirty)
  if (!dirty.length) return
  loading.value = true

  // Check that all pk fields are populated, throw error if not
  const missing = []
  // for each row in dirty
  for (const [key, val] of Object.entries(unref(dirty))) {
    // for each col in pk_cols
    for (const [i, col] of pk_cols.value.entries()){
      if (val[col] == null || val[col] === '') {
        missing.push(`row ${key + 1}: ${col}`)
    }
  }
  }

  if (missing.length) {
  saveStatusMessage.value = `Missing required primary key value(s): ${missing.join(', ')}`
  saveStatusColor.value = 'red'
  loading.value = false
  return
}

  try {
    await Promise.all(dirty.map(r =>
      postRequest(`datasource/${dataSourceId}/datasets/${tableName}/update_record`, {
        record: cleanRow(r),
        primary_key_field: 'vims_primary_key'
      })
    ))
    dirty.forEach(r => {
      Object.assign(r._original, r._pending || {})
      r._dirty = false
      r._pending = {}
      delete r._isNew
    })
    saveStatusMessage.value = 'Save successful.'
    saveStatusColor.value = 'green'
  }
  catch (e) {
    saveStatusMessage.value = 'Save failed.'
    saveStatusColor.value = 'red'
  }
  finally {
    loading.value = false
  }
}

async function deleteRow(row) {
  const ok = confirm('Delete this row?')
  if (!ok) return
  row._saving = true
  try {
    await postRequest(`datasource/${dataSourceId}/datasets/${tableName}/delete_record`, {
      primary_key_field: 'vims_primary_key',
      primary_key_value: row['vims_primary_key']
    })
    rows.value = rows.value.filter(r => r !== row)
    saveStatusMessage.value = 'Row deleted.'
    saveStatusColor.value = 'green'
  }
  catch (e) {
    saveStatusMessage.value = 'Delete failed.'
    saveStatusColor.value = 'red'
  }
  finally {
    row._saving = false
  }
}

function clearFilter() {
  filterColumn.value = null
  filterValue.value = ''
}

const getRows = debounce(async () => {
  const opts = {
    limit: queryRowsPerPage.value,
    page: queryPage.value
  }
  if (querySortBy.value) {
    opts.sortBy = querySortBy.value
    opts.desc = queryDescending.value
  }
  await loadRows(opts)
}, 300)

function updateTable(u) {
  querySortBy.value = u.pagination.sortBy
  queryDescending.value = u.pagination.descending
  queryRowsPerPage.value = u.pagination.rowsPerPage
  queryPage.value = u.pagination.page
  getRows()
}

onMounted(async () => {
  await loadFields()
  await loadDatasetConfigs()
  await getRows()
  const res = await getRequest(`datasource/${dataSourceId}`)
  dataSource.value = res.data
})
</script>
