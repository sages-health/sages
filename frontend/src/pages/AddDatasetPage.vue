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
        <q-input
          ref="titleRef"
          class="title-input"
          v-model="title"
          :label="t('common.title')"
          :readonly="disableEditTitle"
          :rules="[
            val => val.length > 0 || t('common.requiredField') ,
            val => (!existingDatasetTitles.includes(val) || val === initialTitle) || t('dataset.titleExists')
          ]"
          reactive-rules
          @keyup.enter="() => disableEditTitle=true"
        >
          <template
            v-if="disableEditTitle"
            #append
          >
            <q-btn
              color="primary"
              :icon="fasLock"
              @click="disableEditTitle=false"
              round
              flat
            />
          </template>
          <template
            v-else
            #append
          >
            <q-btn
              color="primary"
              :icon="fasLockOpen"
              @click="disableEditTitle=true"
              round
              flat
            />
          </template>
        </q-input>
      </div>
      <div class="active-checkbox-container col-2">
        <q-checkbox
          v-model="isActive"
          indeterminate-value="true"
          size="sm"
          :label="t('dataset.isActive')"
        />
      </div>
      <div class="col-3" />
      <div class="col-3 btn-container">
        <q-btn
          class="save-btn"
          color="primary"
          :label="t('common.save')"
          size="md"
          text-color="white"
          :loading="dataSetLoading"
          :icon="fasFloppyDisk"
          :disable="!title"
          @click="saveDataset"
        />
        <q-btn
          class="cancel-btn"
          :label="t('common.cancel')"
          size="md"
          :icon="fasXmark"
          @click="cancel"
        />
      </div>
    </div>
    <!--  Dataset Select Row    -->
    <div class="row">
      <div class="col-4">
        <q-select
          :options="dataSetNames"
          option-label="display_name"
          option-value="name"
          v-model="selectedDataSetName"
          :label="$t('dataset.single')"
          @update:model-value="resetDataset"
          :disable="disableDataSetSelect"
        />
      </div>
    </div>
    <!--  Description Row    -->
    <div class="row">
      <div class="col-4">
        <q-input
          v-model="description"
          type="textarea"
          rows="3"
          dense
          :label="$t('dataset.description')"
        />
      </div>
    </div>
    <div
      class="row"
      style="margin-bottom: 15px"
    >
      <div class="col-3">
        <q-select
          :options="sharedDateFields"
          v-model="selectedDateField"
          :label="$t('dataset.dateField')"
          clearable
        />
      </div>
      <div class="col-3 q-pl-md">
        <q-select
          v-model="selectedGroups"
          :label="$t('usergroups.usergroups')"
          :options="groupOptions"
          multiple
          clearable
          :option-label="opt => Object(opt) === opt && 'groupName' in opt ? opt.groupName : '---'"
          :option-value="opt => Object(opt) === opt && 'id' in opt ? opt.id : null"
          emit-value
          map-options
        />
      </div>
    </div>
    <div style="margin-bottom: 15px">
      <div class="col-3">
        <q-btn
          :label="$t('dataset.addallfields')"
          color="primary"
          size="md"
          text-color="white"
          @click="addAllSelectedFields"
          style="margin-top: 10px; margin-right: 10px"
        />
        <q-btn
          :label="$t('dataset.removeallfields')"
          color="primary"
          size="md"
          text-color="white"
          @click="removeAllSelectedFields"
          style="margin-top: 10px"
        />
      </div>
    </div>
    <!--  Filter Selection      -->
    <div class="row q-col-gutter-md">
      <div class="col-2">
        <div class="text-h6">
          {{ $t('dataset.hiddenFields') }}
        </div>
        <div class="filters-containers">
          <div
            v-for="fieldName of hiddenFields"
            :key="fieldName"
            :class="[{ filterItemSelected: selectedHiddenFields.includes(fieldName) }]"
            class="filter-item"
            @click="selectHiddenField(fieldName)"
            @dblclick="moveHiddenField(fieldName)"
          >
            {{ fieldName }} ({{ fields[fieldName].displayName }})
            <q-icon
              :name="fasFilter"
              v-show="checkIfFieldFiltered(fieldName) && !fields[fieldName].isReference "
            />
            <q-icon
              :name="fasLink"
              v-show="fields[fieldName].isReference && !fields[fieldName].isMap"
            />
            <q-icon
              :name="fasMap"
              v-show="fields[fieldName].isMap"
            />
          </div>
        </div>
      </div>
      <div
        id="arrow-container"
        class="col-1"
      >
        <q-btn
          class="filter-arrows"
          :icon="fasAnglesRight"
          size="xl"
          @click="addSharedFields"
          flat
          round
        />
        <q-btn
          class="filter-arrows"
          :icon="fasAnglesLeft"
          size="xl"
          @click="removeSharedFields"
          flat
          round
        />
      </div>
      <div class="col-2">
        <div class="text-h6">
          {{ $t('dataset.sharedFields') }}
        </div>
        <div class="filters-containers">
          <div
            v-for="fieldName of sharedFields"
            :key="fieldName"
            :class="[{ filterItemSelected: selectedSharedFields.includes(fieldName) }]"
            class="filter-item"
            @click="selectSharedField(fieldName)"
            @dblclick="moveSharedField(fieldName)"
          >
            {{ fieldName }} ({{ fields[fieldName].displayName }})
            <q-icon
              :name="fasFilter"
              v-show="checkIfFieldFiltered(fieldName) && !fields[fieldName].isReference"
            />
            <q-icon
              :name="fasLink"
              v-show="fields[fieldName].isReference && !fields[fieldName].isMap"
            />
            <q-icon
              :name="fasMap"
              v-show="fields[fieldName].isMap"
            />
          </div>
        </div>
      </div>
      <div class="col-3">
        <div class="text-h6">
          {{ $t('dataset.fieldInfo') }}: {{ selectedField }}
        </div>
        <div class="filters-containers">
          <div
            class="multiple-fields-selected"
            v-show="selectedFields.length > 1"
          >
            {{ $t('dataset.multipleFieldsSelected') }}
          </div>
          <div
            v-if="fields.hasOwnProperty(selectedField)"
            v-show="selectedField !== ''"
            :key="selectedField"
            class="field-info-container"
          >
            <q-input
              v-model="fields[selectedField].displayName"
              :label="t('dataset.displayName')"
              dense
              outlined
            />
            <q-input
              :label="t('dataset.datatype')"
              v-model="dataType"
              dense
              outlined
              disable
            />
            <div v-if="selectedFieldType === 'datetime'">
              <q-select
                v-model="fields[selectedField].dateGranularity"
                :options="['daily', 'weekly', 'monthly', 'yearly', 'epiweek']"
                :label="t('dataset.dataGranularity')"
                dense
                outlined
              />
            </div>
            <div v-else-if="['str'].includes(selectedFieldType)">
              <q-checkbox
                v-model="fields[selectedField].isReference"
                :label="t('dataset.isReference')"
                dense
                outlined
                :disable="fields[selectedField].isMap"
              />
              <q-checkbox
                v-model="fields[selectedField].isMap"
                :label="t('dataset.isMappable')"
                @update:modelValue="updateIsMappable"
                dense
                outlined
              />
              <div
                class="field-info-reference-container"
                v-show="fields[selectedField].isReference && !fields[selectedField].isMap"
              >
                <q-input
                  v-model="referenceValueInput"
                  @keyup.enter="() => addReferenceValue()"
                  :error="referenceValueInputError"
                  :label="t('dataset.referenceValue')"
                  dense
                  outlined
                >
                  <template #append>
                    <q-btn
                      color="primary"
                      :icon="fasCirclePlus"
                      @click="addReferenceValue"
                      round
                      flat
                    />
                  </template>
                  <template #error>
                    {{ t("dataset.referenceValueAlreadyAdded") }}
                  </template>
                </q-input>
                <q-scroll-area
                  class="reference-value-scroll"
                  visible
                >
                  <div
                    class="reference-field-value"
                    v-for="fieldValue of fields[selectedField].values"
                    :key="`${selectedField}-${fieldValue}`"
                  >
                    <div>
                      {{ fieldValue === null ? '__null__' : fieldValue }}
                    </div>
                    <div class="reference-field-value-remove-btn">
                      <q-btn
                        :icon="fasTrash"
                        @click="() => removeReferenceValue(fieldValue)"
                        size="sm"
                        flat
                        dense
                      />
                    </div>
                  </div>
                </q-scroll-area>
                <div class="reference-value-btns">
                  <q-btn
                    :label="$t('common.fetch')"
                    color="primary"
                    @click="fetchDatasetFieldValues"
                    :loading="dataSourceLoading"
                  />
                  <q-btn
                    :label="$t('common.clear')"
                    @click="clearReferenceValues"
                  />
                </div>
              </div>
              <div
                class="field-info-map-container"
                v-show="fields[selectedField].isMap"
              >
                <div class="reference-value-btns">
                  <q-btn
                    :label="$t('dataset.configureMapping')"
                    @click="prepareMapDialog"
                    color="primary"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-3">
        <div class="text-h6">
          {{ $t('dataset.filterValues') }}: {{ selectedField }}
        </div>
        <div class="filters-containers">
          <div
            class="multiple-fields-selected"
            v-show="selectedFields.length > 1"
          >
            {{ $t('dataset.multipleFieldsSelected') }}
          </div>
          <QueryBuilder
            v-show="selectedField !== ''"
            v-if="fields.hasOwnProperty(selectedField)"
            :field="selectedField"
            :request="selectedFieldRequest"
            :type="selectedFieldType"
            :is-reference="fields[selectedField].isReference"
            :reference-options="referenceOptions"
            @update:request="updateQueryRequest"
            :key="selectedField"
          />
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <q-table
          :title="`${t('common.rowCount')}: ${queryTotal}`"
          :columns="columns"
          :loading="tableLoading"
          :rows="queryRows"
          :pagination="pagination"
          @request="updateTable"
          :rows-per-page-options="[5, 10, 25, 50]"
          :no-data-label="$t('common.noData')"
        />
      </div>
    </div>
    <q-dialog
      v-model="showConfigureMapDialog"
      medium
      persistent
      id="map-configuration-dialog"
    >
      <q-card style="width: 600px; min-width: 600px; min-height: 600px; max-height: 800px;">
        <q-card-section class="items-center">
          <div
            class="row"
            style="display: flex; flex-direction: column; align-items: center"
          >
            <div
              class="col"
              style="width: 600px;"
            >
              <q-select
                :options="regionMaps"
                option-value="objectId"
                option-label="name"
                v-model="fields[selectedField].regionMap"
                :label="$t('dataset.selectMap')"
                @update:model-value="updateSelectedMap"
                :emit-value="true"
                :map-options="true"
              >
                <template #no-option>
                  <q-item>
                    <q-item-section class="text-grey">
                      {{ t('common.noData') }}
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </div>
          </div>
        </q-card-section>
        <q-card-section>
          <div class="row">
            <div class="col-7">
              <q-input
                v-model="searchFieldValues"
                :label="t('common.search')"
              />
            </div>
            <div class="col-2">
              <q-checkbox
                v-model="showMappedFieldValues"
                :label="t('dataset.showMappedFieldValues')"
              />
            </div>
            <div class="col-2">
              <q-checkbox
                v-model="showUnmappedFieldValues"
                :label="t('dataset.showUnmappedFieldValues')"
              />
            </div>
          </div>
        </q-card-section>
        <q-card-section>
          <div
            class="row"
            style="min-width: 600px;"
          >
            <div class="col">
              <q-scroll-area
                class="reference-value-scroll"
                style="min-height: 500px;"
                v-if="fields[selectedField].regionMap"
                visible
              >
                <div
                  class="row"
                  v-for="fieldValue of filteredMappingFields"
                  :key="`${selectedField}-${fieldValue}`"
                >
                  <div class="col">
                    <q-select
                      v-if="fields[selectedField].regionMapMapping.hasOwnProperty(fieldValue)"
                      :label="fieldValue"
                      v-model="fields[selectedField].regionMapMapping[fieldValue]"
                      :options="selectedRegionMap.regions"
                      dense
                      :clearable="true"
                    />
                  </div>
                </div>
              </q-scroll-area>
            </div>
            <div
              class="col"
              v-if="fields[selectedField].regionMap"
              style="margin-left: 15px;"
            >
              <strong>{{ t('dataset.leftToMap') }}:</strong>
              <q-scroll-area
                style="min-height: 500px;"
                class="reference-value-scroll"
                visible
              >
                <div
                  v-for="region of regionsLeftToMap"
                  :key="`${selectedField}-${fields[selectedField].regionMap}-${region}`"
                >
                  <div
                    class="row"
                    style="align-items: center; margin-bottom: 5px;"
                  >
                    <div
                      class="col"
                      style="text-align: center;"
                    >
                      {{ region }}
                    </div>
                    <div class="col">
                      <q-btn
                        color="primary"
                        :label="t('common.add')"
                        :icon="fasCirclePlus"
                        @click="() => addRegionToValues(region)"
                      />
                    </div>
                  </div>
                </div>
              </q-scroll-area>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            :label="t('common.confirm')"
            color="primary"
            v-close-popup
          />
          <q-btn
            flat
            label="Cancel"
            color="primary"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <q-dialog v-model="showFormErrorDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">
            {{ t('common.error') }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          {{ t('dataset.titleError') }}
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="OK"
            color="primary"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>

import { useRoute, useRouter } from 'vue-router'
import {ref, computed, onMounted, watch, toRaw} from 'vue'
import { debounce } from 'quasar'
import { useI18n } from 'vue-i18n'
import { fasLock, fasLockOpen, fasFloppyDisk, fasAnglesLeft, fasAnglesRight, fasMap, fasCirclePlus, fasTrash, fasFilter, fasLink, fasXmark } from '@quasar/extras/fontawesome-v6'

import PageBreadcrumbs from 'src/components/PageBreadcrumbs.vue'
import QueryBuilder from 'src/components/QueryBuilder.vue'
import { extractDataSetFilters } from 'src/composables/dataset'

import {$api, getRequest, postRequest, putRequest, request} from "boot/axios";
import {convertLastNBack} from "src/composables/visualization";
import { authStore, hasPermission } from 'src/stores/auth'
import { useGroupStore } from 'src/stores/group'
import { storeToRefs } from 'pinia'

const { fetchAllGroups } = useGroupStore()
const { allGroups } = storeToRefs(useGroupStore())

// Local Variables
const { t } = useI18n()
const router = useRouter()

// User Group Refs
const groupOptions = ref([])

// Dataset Refs
const dataSourceId = ref(null)
const dataSetId = ref(null)
const description = ref('')
const title = ref('')
const initialTitle = ref('')
const selectedDataSetName = ref('')
const isActive = ref(true)
const selectedDateField = ref(null)
const fields = ref({})
const sharedFields = ref([])
const hiddenFields = ref([])
const fieldRequests = ref({})
const dataSetLoading = ref(false)
const dataSetFieldValues = ref({})
const existingDatasetTitles = ref([])
const selectedGroups = ref([])
const dataType = ref(null)

// Component Refs
const disableDataSetSelect = ref(false)
const disableEditTitle = ref(false)
const dataSetNames = ref([])
const dataSetFields = ref({})
const selectedHiddenFields = ref([])
const selectedSharedFields = ref([])
const referenceValueInput = ref('')
const titleRef = ref(null)
const showFormErrorDialog = ref(false)


// Query Refs
const queryRows = ref([])
const queryTotal = ref(0)
const queryRowsPerPage = ref(10)
const queryPage = ref(1)
const querySortBy = ref(null)
const queryDescending = ref(false)
const dataSourceLoading = ref(false)
const tableLoading = ref(false)

// Mapping Refs
const showConfigureMapDialog = ref(false)
const regionMaps = ref([])
const showMappedFieldValues = ref(true)
const showUnmappedFieldValues = ref(true)
const searchFieldValues = ref('')

// Region Mapping Computed Values
const selectedRegionMap = computed ( () => {
  const regionMapId = fields.value[selectedField.value].regionMap
  return regionMaps.value.filter(x => x.objectId === regionMapId)[0]
})
const regionsLeftToMap = computed ( () => {
  const currentlyAssignedRegions = Object.values(fields.value[selectedField.value].regionMapMapping)
  return selectedRegionMap.value.regions.filter(x => !currentlyAssignedRegions.includes(x))
})
const sharedDateFields = computed ( () => {
  return sharedFields.value.filter(sf => fields.value[sf].dataFieldType === 'datetime')
})

const filteredMappingFields = computed ( () => {
  const fieldValues = []
  fields.value[selectedField.value].values.forEach( function (val) {
    if (fields.value[selectedField.value].regionMapMapping.hasOwnProperty(val) && fields.value[selectedField.value].regionMapMapping[val] === null && showUnmappedFieldValues.value) {
      fieldValues.push(val)
    }
    if (fields.value[selectedField.value].regionMapMapping.hasOwnProperty(val) && fields.value[selectedField.value].regionMapMapping[val] !== null && showMappedFieldValues.value) {
      fieldValues.push(val)
    }
  })

  return fieldValues.filter(fv => fv !== null).filter(fv => fv.toLowerCase().includes(searchFieldValues.value.toLowerCase()))
})

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
const columns = computed ( () => {
  return sharedFields.value.map(function (sf) {
    return {name: sf, label: fields.value[sf].displayName, field: row => row[sf], sortable: true, align: 'left'}
  })
})

// Field Selector Computed Values
const selectedFields = computed ( () => {
  if (selectedSharedFields.value.length > 0) {
      return selectedSharedFields.value
  }
  else if (selectedHiddenFields.value.length > 0) {
    return selectedHiddenFields.value
  }
  return []
})
const selectedField = computed ( () => {
  return selectedFields.value.length === 1 ? selectedFields.value[0] : ''
})
const selectedFieldType = computed ( () => {
  return selectedField.value !== '' ? fields.value[selectedField.value].dataFieldType : undefined
})
const selectedFieldRequest = computed ( () => {
  getDataDisplayValue()
  return selectedField.value !== '' ? fieldRequests.value[selectedField.value] : undefined
})

// Reference Value Computed Values
const referenceValueInputError = computed ( () => {
  return fields.value[selectedField.value].values.includes(referenceValueInput.value)
})
const referenceOptions = computed ( () => {
  if (fields.value[selectedField.value].isMap ) {
    const refOps = []
    for (const [fieldValue, region] of Object.entries(fields.value[selectedField.value].regionMapMapping)) {
      if (region !== null) {
        refOps.push({label: fieldValue, value: fieldValue})
      }
    }
    return refOps
  }
  else {
    return fields.value[selectedField.value].values.map(function (fieldValue) {
      return {label: fieldValue === null ? '__null__' : fieldValue, value: fieldValue}
    })
  }
})

// DataSet Computed Values
/*
 * Format filter and field ref values into an object for interacting with the backend.
 */
const formattedQuery = computed ( () => {
  const fQuery = {}
  const reqs = []
  Object.values(fieldRequests.value).forEach(function (req) {
    if (Object.keys(req).length > 0) {
      reqs.push(toRaw(req))
    }
  })
  if (reqs.length > 0) {
    fQuery.request = { $and: reqs }
  }
  const projection = {}
  hiddenFields.value.forEach(function (hiddenField) {
    projection[hiddenField] = 0
  })
  sharedFields.value.forEach(function (sharedField) {
    projection[sharedField] = 1
  })
  fQuery.projection = projection
  return fQuery
})
/*
 * Format dataset field ref values into an object for interacting with the backend.
 */
const formattedDataSet = computed ( () => {
  const fieldsFormatted = []
  for (const [fieldName, fieldData] of Object.entries(fields.value)) {
    const regionMapping = {}
    for (const [field, region] of Object.entries(fieldData.regionMapMapping)) {
      if (region !== null) {
        regionMapping[field] = region
      }
    }

    fieldsFormatted.push({
      data_field_name: fieldName,
      display_name: toRaw(fieldData.displayName),
      data_field_type: fieldData.dataFieldType,
      date_granularity: fieldData.dateGranularity,
      is_reference: toRaw(fieldData.isReference),
      values: toRaw(fieldData.values),
      region_map_id: fieldData.regionMap,
      region_map_mapping: regionMapping
    })
  }
  const dataSet = {
    dataset_name: selectedDataSetName.value.name,
    dataset_display_name: selectedDataSetName.value.display_name,
    description: description.value,
    display_name: title.value,
    datasource_id: dataSourceId.value,
    fields: fieldsFormatted,
    is_active: isActive.value,
    primary_key_field: "vims_primary_key",
    date_field: selectedDateField.value,
    groups: selectedGroups.value,
    expiration: null,
    shared_with: null
  }

  if (Object.keys(formattedQuery.value).length > 0) {
    dataSet.base_query = formattedQuery.value
  }

  return dataSet
})

// =============== Data Table Functions ===============
/*
Fetch rows for the data table from the backend.
 */

const getExistingDatasetTitles = async () => {
  existingDatasetTitles.value =  (await request({'url': 'dataset', 'method': 'get', 'errorMessage': 'Unable to retrieve data sets'})).data.map(function (ds) {
    return ds.display_name
  })
}
const getRows = async () => {
  tableLoading.value = true
  let dataSetQuery = convertLastNBack(formattedQuery.value)
  if (Object.values(dataSetQuery.projection).some(x => x === 1)) {
    dataSetQuery.limit = queryRowsPerPage.value
    dataSetQuery.offset = queryRowsPerPage.value * (queryPage.value - 1)
    if (querySortBy.value !== null && dataSetQuery.projection[querySortBy.value] === 1) {
      dataSetQuery.order_by = [[querySortBy.value, queryDescending.value ? 'desc' : 'asc']]
    }
    const response = await postRequest('datasource/' + dataSourceId.value + '/datasets/' + selectedDataSetName.value.name + '/query', {
      dataset_metadata: dataSetFields.value[selectedDataSetName.value.name],
      query: dataSetQuery
    })
    queryRows.value = response.data[0].values
    queryTotal.value = response.data[0].total
  }
  tableLoading.value = false
}
const processQueryUpdate = debounce(getRows, 500)
const updateQueryRequest = function (req) {
  fieldRequests.value[selectedField.value] = req
  processQueryUpdate()
}
const updateTable = function (tableUpdate) {
  querySortBy.value = tableUpdate.pagination.sortBy
  queryDescending.value = tableUpdate.pagination.descending
  queryRowsPerPage.value = tableUpdate.pagination.rowsPerPage
  queryPage.value = tableUpdate.pagination.page
  processQueryUpdate()
}

// =============== Field Selector Functions ===============
const selectHiddenField = function (fieldName) {
  // Track the clicked available filter items.
  selectedSharedFields.value = []
  if (selectedHiddenFields.value.includes(fieldName)) {
    selectedHiddenFields.value.splice(selectedHiddenFields.value.indexOf(fieldName), 1)
  }
  else {
    selectedHiddenFields.value.push(fieldName)
  }
}
const selectSharedField = function (fieldName) {
  // Track the clicked available filter items.
  selectedHiddenFields.value = []
  if (selectedSharedFields.value.includes(fieldName)) {
    selectedSharedFields.value.splice(selectedSharedFields.value.indexOf(fieldName), 1)
  }
  else {
    selectedSharedFields.value.push(fieldName)
  }
}
const addSharedFields = function () {
  if (selectedHiddenFields.value.length > 0) {
    selectedHiddenFields.value.forEach(function(sharedField) {
      sharedFields.value.push(sharedField)
      hiddenFields.value.splice(hiddenFields.value.indexOf(sharedField), 1)
    })
    selectedHiddenFields.value = []
  }
}
const removeSharedFields = function () {
  if (selectedSharedFields.value.length > 0) {
    selectedSharedFields.value.forEach(function(hiddenField) {
      hiddenFields.value.push(hiddenField)
      sharedFields.value.splice(sharedFields.value.indexOf(hiddenField), 1)
      if (hiddenField === selectedDateField.value) {
        selectedDateField.value = null
      }
    })
    selectedSharedFields.value = []
  }
}
const moveHiddenField = function (fieldName) {
  sharedFields.value.push(fieldName)
  hiddenFields.value = hiddenFields.value.filter(x => x !== fieldName)
  selectedSharedFields.value.push(fieldName)
  selectedHiddenFields.value = []
}
const moveSharedField = function (fieldName) {
  hiddenFields.value.push(fieldName)
  sharedFields.value = sharedFields.value.filter(x => x !== fieldName)
  if (fieldName === selectedDateField.value) {
    selectedDateField.value = null
  }
  selectedSharedFields.value = []
  selectedHiddenFields.value.push(fieldName)
}

const checkIfFieldFiltered = function (fieldName) {
  return fieldRequests.value.hasOwnProperty(fieldName) && Object.keys(fieldRequests.value[fieldName]).length > 0
}

const addAllSelectedFields = function () {
  hiddenFields.value.forEach(function (field) {
    selectHiddenField(field)
    moveHiddenField(field)
    addSharedFields()
  })
  selectedSharedFields.value = []
}

const removeAllSelectedFields = function () {
  sharedFields.value.forEach(function (field) {
    selectSharedField(field)
    moveSharedField(field)
  })
  selectedHiddenFields.value = []
}

// =============== Reference Value Functions ===============
const addReferenceValue = function () {
  if (referenceValueInput.value.length > 0 && !referenceValueInputError.value) {
    fields.value[selectedField.value].values.push(referenceValueInput.value)
    fields.value[selectedField.value].values.sort()
    referenceValueInput.value = ''
  }
}
const removeReferenceValue = function (removedReferenceValue) {
  fields.value[selectedField.value].values.splice(fields.value[selectedField.value].values.indexOf(removedReferenceValue), 1);
}
const clearReferenceValues = function () {
  fields.value[selectedField.value].values.splice(0)
}

// =============== Region Map Functions ===============

const fetchRegionMaps = async function () {
  dataSourceLoading.value = true
  const response = (await $api.get('map')).data
  regionMaps.value = response.map((rm) => ({objectId: rm.id, name: rm.display_name, regions: rm.regions.map(x => x.display_name)}))
  dataSourceLoading.value = false
}

const updateSelectedMap = function () {
  Object.keys(fields.value[selectedField.value].regionMapMapping).forEach( function (fieldValue) {
    const regionIdx = selectedRegionMap.value.regions.map(x => x.toLowerCase()).indexOf(fieldValue.toLowerCase())
    fields.value[selectedField.value].regionMapMapping[fieldValue] = regionIdx !== -1 ? selectedRegionMap.value.regions[regionIdx] : null
  })
}

const addRegionToValues = function (region) {
  fields.value[selectedField.value].regionMapMapping[region] = region
  fields.value[selectedField.value].values.push(region)
}

const prepareMapDialog = async function () {
  showConfigureMapDialog.value = true
  await fetchDatasetFieldValues()

  fields.value[selectedField.value].values.forEach( function (val) {
    if (!fields.value[selectedField.value].regionMapMapping.hasOwnProperty(val)) {
      fields.value[selectedField.value].regionMapMapping[val] = null
    }
  })
}

const updateIsMappable = function () {
  fields.value[selectedField.value].isReference = true
  fields.value[selectedField.value].regionMap = null
  fields.value[selectedField.value].regionMapMapping = {}
}

// =============== Dataset Functions ===============
/*
 * Push dataset to the backend.
 */
const saveDataset = async function () {
  titleRef.value.validate()

  if (titleRef.value.hasError) {
    showFormErrorDialog.value = true
    return
  }

  dataSetLoading.value = true
  if (dataSetId.value === null) {
    await postRequest('dataset', formattedDataSet.value)
  }
  else {
    await putRequest('dataset/' + dataSetId.value, formattedDataSet.value)
  }
  dataSetLoading.value = false
  await router.push('/data/datasets')
}

/*
 * Fetch dataset from backend.
 */
const fetchDataSet = async function (dataSetId) {
  dataSetLoading.value = true
  const dataSet = (await getRequest( 'dataset/manage/' + dataSetId)).data

  // Set local ref values.
  dataSourceId.value = dataSet.datasource_id
  description.value = dataSet.description
  title.value = dataSet.display_name
  initialTitle.value = dataSet.display_name
  isActive.value = dataSet.is_active
  selectedDataSetName.value = {name: dataSet.dataset_name, display_name: dataSet.dataset_display_name}
  selectedDateField.value = dataSet.date_field
  selectedGroups.value = dataSet.groups

  // Reset fields for new dataset.
  fields.value = {}
  dataSet.fields.forEach(function (field) {
    const regionMapping = {}
    if (field.values !== null && field.region_map_id !== null) {
      field.values.forEach( function (val) {
        regionMapping[val] = field.region_map_mapping.hasOwnProperty(val) ? field.region_map_mapping[val] : null
      })
    }
    fields.value[field.data_field_name] = {
      dataFieldType: field.data_field_type,
      displayName: field.display_name,
      dateGranularity: field.date_granularity === null && field.data_field_type === 'datetime' ? 'daily': field.date_granularity, // provide a sane default
      isReference: field.is_reference,
      isMap: field.region_map_id !== null,
      regionMap: field.region_map_id,
      regionMapMapping: regionMapping,
      values: field.values === null ? [] : field.values
    }
  })

  // Reset shared fields for new dataset
  sharedFields.value = []
  hiddenFields.value = []
  for (const [fieldName, projection] of Object.entries(dataSet.base_query.projection)) {
    if (Object.keys(fields.value).includes(fieldName)) {
      if (projection) {
        sharedFields.value.push(fieldName)
      }
      else {
        hiddenFields.value.push(fieldName)
      }
    }
  }
  fieldRequests.value = extractDataSetFilters(dataSet)
  dataSetLoading.value = false
}

/*
 * Reset the all dataset related refs.
 */
const resetDataset = async function () {
  await fetchDatasetFields()
  selectedDateField.value = null
  selectedGroups.value = null
  fields.value = {}
  for (const [key, value] of Object.entries(dataSetFields.value[selectedDataSetName.value.name])) {
      fields.value[key] = {
        dataFieldType: value,
        displayName: key,
        dateGranularity: value === 'datetime' ? 'daily': null,
        isReference: false,
        values: [],
        regionMap: null,
        regionMapMapping: {}
      }
  }

  selectedHiddenFields.value = []
  selectedSharedFields.value = []
  hiddenFields.value.splice(0)
  Object.keys(fields.value).forEach((field) => {
    hiddenFields.value.push(field)
    fieldRequests.value[field] = {}
  })
  sharedFields.value.splice(0)
}

/*
 * Fetch fields for the given dataset and cache results.
 */
const fetchDatasetFields = async function () {
  if (!dataSetFields.value.hasOwnProperty(selectedDataSetName.value.name)) {
    dataSourceLoading.value = true
    dataSetFields.value[selectedDataSetName.value.name] = (await getRequest('datasource/' + dataSourceId.value + '/datasets/' + selectedDataSetName.value.name + '/fields')).data[0].fields
    dataSourceLoading.value = false
  }
}

/*
 * Fetch field values for the given dataset field and cache.
 */
const fetchDatasetFieldValues = async function () {
  dataSourceLoading.value = true
  const key = `${selectedDataSetName.value.name}-${selectedField.value}`
  // Cache previous fetch results.
  if (!dataSetFieldValues.value.hasOwnProperty(key)) {
    const result = await getRequest('datasource/' + dataSourceId.value + '/datasets/' + selectedDataSetName.value.name + '/' + selectedField.value + '/values')
    const values = result.data[0].values
    values.sort()
    dataSetFieldValues.value[key] = values
  }
  dataSetFieldValues.value[key].forEach(function (v) {
    if (!fields.value[selectedField.value].values.includes(v)) {
     fields.value[selectedField.value].values.push(v)
    }
  })
  dataSourceLoading.value = false
}

const getGroupOptions = function () {
  if (hasPermission('read_groups')) {
    groupOptions.value = allGroups.value
  }
  else {
    groupOptions.value = authStore.user.groups
  }
}

const getDataDisplayValue = function() {
  // TODO: Integrate i18n into these values
  if(selectedFieldType.value.includes(['str'])) {
    dataType.value = t('dataset.text')
  }
  else if(selectedFieldType.value.includes(['datetime'])) {
    dataType.value = t('dataset.date')
  }
  else if(selectedFieldType.value.includes(['int']) || selectedFieldType.value.includes(['float']) || selectedFieldType.value.includes(['double'])) {
    dataType.value = t('dataset.number')
  }
  else {
    dataType.value = ""
  }
}

const cancel = async function () {
  await router.push('/data/datasets')
}

onMounted( async () => {
  const route = useRoute()
  dataSetId.value = 'dataSetId' in route.params ? route.params.dataSetId : null
  if (dataSetId.value !== null) {
    await fetchDataSet(dataSetId.value)
    await fetchDatasetFields()
    disableEditTitle.value = true
    dataSetNames.value = [selectedDataSetName.value]
    disableDataSetSelect.value = true
  }
  else {
    dataSourceId.value = route.params.dataSourceId
    dataSetNames.value = (await getRequest('datasource/' + dataSourceId.value + '/datasets')).data[0].datasets
    selectedDataSetName.value = dataSetNames.value[0]
    await resetDataset()
  }
  await fetchRegionMaps()
  await processQueryUpdate()
  await getExistingDatasetTitles()

  if (hasPermission('read_groups')) {
    await fetchAllGroups()
  }
  getGroupOptions()
})
watch(sharedFields, processQueryUpdate, { deep: true })

</script>

<style scoped>
  .title-input {
    font-size: 24px;
  }
  .active-checkbox-container {
    display: flex;
    justify-content: center;
  }
  .btn-container {
    display: flex;
    justify-content: center;
  }
  .filters-containers {
    padding-top: 5px;
    height: 400px;
    background-color: white;
    border-color: rgb(155, 155, 155);
    border-style: solid;
    border-width: 1px;
    border-radius: 4px;
    overflow: auto;
  }
  .field-info-container {
    display: flex;
    flex-direction: column;
    margin: 15px;
    gap: 10px;
  }
  .field-info-reference-container {
    display: flex;
    flex-direction: column;
    margin-top: 10px;
    gap: 10px;
  }
  .reference-field-value {
    display: flex;
    flex-direction: row;
    width: 80%;
    margin-left: 10%;
  }
  .reference-value-scroll {
    height: 160px;
  }
  .reference-field-value-remove-btn {
    margin-left: auto;
  }
  .reference-value-btns {
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 10px;
  }
  .field-info-map-container {
    display: flex;
    flex-direction: column;
    margin-top: 10px;
    gap: 10px;
  }
  #map-configuration-dialog {
  }
  #arrow-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .filter-arrows {
    margin: 20px 0;
    color: #2c3e50;
  }
  .filter-item {
    padding-left: 10px;
    border-style: solid;
    border-width: 0 0 1px 0;
    border-color: rgb(155, 155, 155);
  }
  .filter-item:first-child {
    border-width: 1px 0 1px 0;
  }
  .filter-item:hover {
    color: white;
    border-color: rgb(155, 155, 155);
    background-color: #2c3e50BA;
  }
  .filterItemSelected {
    color: white;
    border-color: rgb(155, 155, 155);
    background-color: #2c3e50;
  }
  .multiple-fields-selected {
    text-align: center;
  }
  .save-btn {
    width: 150px;
    margin-right: 5px;
  }
  .cancel-btn {
    width: 150px;
    margin-left: 5px;
  }
</style>
