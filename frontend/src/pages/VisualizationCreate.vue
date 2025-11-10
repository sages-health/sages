<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />

    <div class="row visualization-row">
      <div class="col-4">
        <q-select
          :options="dataSets"
          option-label="display_name"
          v-model="selectedDataSet"
          :label="$t('dataset.single')"
          @update:model-value="dataSetChanged()"
        />
      </div>
      <div class="col-1" />
      <div class="col-4">
        <q-input
          v-model="visualizationName"
          :label="$t('common.name')"
        />
      </div>
      <div class="col-3 btn-container">
        <q-btn
          class="save-btn"
          color="primary"
          :label="$t('common.save')"
          text-color="white"
          :icon="fasFloppyDisk"
          :disable="!visualizationName"
          @click="save"
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
    <div class="row visualization-row">
      <div
        v-if="selectedDataSet"
        class="col-4"
      >
        <q-btn-dropdown
          color="primary"
          :label="$t('common.addFilter')"
        >
          <q-list
            v-for="field in availableFields"
            :key="field"
          >
            <q-item
              clickable
              v-close-popup
              @click="addFilter(field)"
            >
              <q-item-section>
                <q-item-label>{{ field.display_name }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </div>
    </div>
    <div
      v-if="selectedDataSet"
      class="row visualization-row"
    >
      <div
        v-for="field in visualizationFilterFields"
        :key="field"
        class="col-3 filter-card-group"
      >
        <q-card>
          <q-expansion-item
            :default-opened="true"
            switch-toggle-side
            expand-separator
          >
            <template v-slot:header>
              <q-item-section>
                <div class="row">
                  <div class="col-10 justify-center flex">
                    <div
                      class="text-h6"
                      style="padding-right: 12px"
                    >
                      {{ fields[field].display_name }}
                    </div>
                  </div>
                  <div class="col-2">
                    <q-btn
                      dense
                      round
                      flat
                      :icon="fasCircleXmark"
                      @click="removeFilter(field)"
                    />
                  </div>
                </div>
              </q-item-section>
            </template>
            <q-card-section class="filter-card-section filter-query-card-section">
              <QueryBuilder
                :is-reference="fields[field].is_reference"
                :reference-options="referenceOptions[field]"
                :field="field"
                :request="filters[field]"
                :type="fields[field].data_field_type"
                @update:request="updateFilter"
                :key="field"
              />
            </q-card-section>
          </q-expansion-item>
        </q-card>
      </div>
    </div>
    <q-banner
      v-if="error"
      class="text-white bg-red"
    >
      {{ error }}
    </q-banner>
    <div
      v-if="selectedDataSet"
      class="row visualization-row"
    >
      <div class="col-12">
        <q-card>
          <q-tabs
            v-model="visualizationType"
            dense
            class="text-grey"
            active-color="primary"
            indicator-color="primary"
            align="justify"
            narrow-indicator
          >
            <div
              v-for="type in visualizationTypes"
              :key="type.name"
            >
              <q-tab
                :name="type.name"
                :label="type.label"
              />
            </div>
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="visualizationType">
            <!-- eslint-disable -->
            <q-tab-panel name="table">
              <div v-if="visualizationType === 'table'">
                <visualization-widget :config="configs['table']"/>
              </div>
            </q-tab-panel>
            <!-- eslint-enable -->
            <q-tab-panel
              name="line"
            >
              <div class="row visualization-row">
                <div class="col-2 chart-options">
                  <q-select
                    :options="availableFields.filter(f => f.data_field_name !== configs['line'].visualization_options['aggregateField']
                      && f.data_field_name !== configs['line'].visualization_options['stratification'])"
                    option-label="display_name"
                    option-value="data_field_name"
                    emit-value
                    map-options
                    v-model="configs['line'].visualization_options['groupBy']"
                    label="X"
                  />
                </div>
                <div
                  class="col-2 chart-options"
                  v-show="isTimeResolutionField(configs['line'].visualization_options['groupBy'])"
                >
                  <q-select
                    v-model="configs['line'].visualization_options['transformation']"
                    :options="[$t('common.day'), $t('common.week'), $t('common.month'), $t('common.year'), $t('common.epiweek')]"
                    :label="$t('visualization.timeResolution')"
                    clearable
                  />
                </div>
                <div
                  class="col-2 chart-options"
                  v-show="configs['line'].visualization_options['groupBy']"
                >
                  <q-select
                    :options="aggregateFunctions.map(item => item.value)"
                    :option-label="(item) => aggregateFunctions.filter(ref => ref.value === item)[0].label"
                    v-model="configs['line'].visualization_options['aggregateFunction']"
                    :label="$t('common.queryAggregateFunction')"
                  />
                </div>
                <div
                  class="col-2 chart-options"
                  v-show="configs['line'].visualization_options['aggregateFunction'] !== 'rows'"
                >
                  <q-select
                    :options="availableFields.filter(f => f.data_field_name !== configs['line'].visualization_options['groupBy']
                      && f.data_field_name !== configs['line'].visualization_options['stratification'])"
                    option-label="display_name"
                    option-value="data_field_name"
                    emit-value
                    map-options
                    v-model="configs['line'].visualization_options['aggregateField']"
                    label="Y"
                  />
                </div>
                <div class="col-2" />
                <div
                  class="col-2 chart-options"
                  v-show="configs['line'].visualization_options['groupBy']"
                >
                  <q-select
                    :disable="configs['line'].visualization_options['detectionAlgorithm'] != null"
                    :options="availableFields.filter(f => f.data_field_name !== configs['line'].visualization_options['groupBy'] && f.data_field_name !== configs['line'].visualization_options['aggregateField'])"
                    option-label="display_name"
                    option-value="data_field_name"
                    clearable
                    emit-value
                    map-options
                    v-model="configs['line'].visualization_options['stratification']"
                    :label="$t('visualization.stratification')"
                  />
                </div>
                <div
                  class="col-2 chart-options"
                >
                  <q-select
                    :disable="configs['line'].visualization_options['stratification'] != null"
                    v-model="configs['line'].visualization_options['detectionAlgorithm']"
                    :options="detectionFunctions"
                    option-label="label"
                    option-value="value"
                    emit-value
                    map-options
                    :label="$t('visualization.detection')"
                    clearable
                  />
                </div>
              </div>
              <div v-if="visualizationType === 'line'">
                <visualization-widget :config="configs['line']" />
              </div>
            </q-tab-panel>

            <q-tab-panel
              name="bar"
            >
              <div class="row visualization-row">
                <div class="col-2 chart-options">
                  <q-select
                    :options="availableFields.filter(f => f.data_field_name !== configs['bar'].visualization_options['aggregateField'])"
                    option-label="display_name"
                    option-value="data_field_name"
                    emit-value
                    map-options
                    v-model="configs['bar'].visualization_options['groupBy']"
                    label="X"
                  />
                </div>
                <div
                  class="col-2 chart-options"
                  v-show="configs['bar'].visualization_options['groupBy']"
                >
                  <q-select
                    :options="aggregateFunctions.map(item => item.value)"
                    :option-label="(item) => aggregateFunctions.filter(ref => ref.value === item)[0].label"
                    v-model="configs['bar'].visualization_options['aggregateFunction']"
                    :label="$t('common.queryAggregateFunction')"
                  />
                </div>
                <div
                  class="col-2 chart-options"
                  v-show="configs['bar'].visualization_options['aggregateFunction'] !== 'rows'"
                >
                  <q-select
                    :options="availableFields.filter(f => f.data_field_name !== configs['bar'].visualization_options['groupBy'])"
                    option-label="display_name"
                    option-value="data_field_name"
                    emit-value
                    map-options
                    v-model="configs['bar'].visualization_options['aggregateField']"
                    label="Y"
                  />
                </div>
                <div
                  class="col-2 chart-options"
                  v-show="configs['bar'].visualization_options.groupBy"
                >
                  <q-select
                    :options="availableFields.filter(f => f.data_field_name !== configs['bar'].visualization_options.groupBy && f.data_field_name !== configs['bar'].visualization_options.aggregateField)"
                    option-label="display_name"
                    option-value="data_field_name"
                    emit-value
                    map-options
                    clearable
                    v-model="configs['bar'].visualization_options.stratification"
                    :label="$t('visualization.stratification')"
                  />
                </div>
                <div class="col-2 chart-options q-mt-md">
                  <q-checkbox
                    v-model="configs['bar'].visualization_options.stacked"
                    :label="$t('visualization.barConfig.stacked')"
                  />
                  <q-checkbox
                    v-model="configs['bar'].visualization_options.normalized"
                    :label="$t('visualization.barConfig.normalized')"
                  />
                </div>
              </div>
              <div v-if="visualizationType === 'bar'">
                <visualization-widget :config="configs['bar']" />
              </div>
            </q-tab-panel>
            <q-tab-panel
              name="pivot"
            >
              <div v-if="visualizationType === 'pivot'">
                <visualization-widget
                  :view-only="false"
                  :config="configs['pivot']"
                />
              </div>
            </q-tab-panel>
            <q-tab-panel
              name="pie"
            >
              <div class="row visualization-row">
                <div class="col-3 chart-options">
                  <q-select
                    :options="availableFields.filter(f => f.data_field_name !== configs['pie'].visualization_options['aggregateField'])"
                    option-label="display_name"
                    option-value="data_field_name"
                    emit-value
                    map-options
                    v-model="configs['pie'].visualization_options['groupBy']"
                    label="X"
                  />
                </div>
                <div
                  class="col-1 chart-options"
                  v-show="configs['pie'].visualization_options['groupBy']"
                >
                  <q-input
                    :label="$t('visualization.topN')"
                    v-model.number="configs['pie'].visualization_options['topN']"
                    type="number"
                    min="1"
                    max="20"
                  />
                </div>
                <div class="col-1" />
                <div
                  class="col-2 chart-options"
                  v-show="configs['pie'].visualization_options['groupBy']"
                >
                  <q-select
                    :options="aggregateFunctions.map(item => item.value)"
                    :option-label="(item) => aggregateFunctions.filter(ref => ref.value === item)[0].label"
                    v-model="configs['pie'].visualization_options['aggregateFunction']"
                    :label="$t('common.queryAggregateFunction')"
                  />
                </div>
                <div
                  class="col-2 chart-options"
                  v-show="configs['pie'].visualization_options['aggregateFunction'] !== 'rows'"
                >
                  <q-select
                    :options="availableFields.map(f => f.data_field_name).filter(f => f !== configs['pie'].visualization_options['groupBy'])"
                    option-label="display_name"
                    option-value="data_field_name"
                    v-model="configs['pie'].visualization_options['aggregateField']"
                    label="Y"
                  />
                </div>
              </div>
              <div v-if="visualizationType === 'pie'">
                <visualization-widget :config="configs['pie']" />
              </div>
            </q-tab-panel>
            <q-tab-panel
              name="map"
            >
              <div class="row visualization-row">
                <div class="col-3 chart-options">
                  <q-select
                    :options="mappableFields.map(f => f.data_field_name)"
                    v-model="configs['map'].visualization_options['groupBy']"
                    :label="$t('visualization.mappableField')"
                    @update:model-value="setRegionMapId"
                  />
                </div>
                <div class="col-1" />
                <div
                  class="col-2 chart-options"
                  v-show="configs['map'].visualization_options['groupBy']"
                >
                  <q-select
                    :options="aggregateFunctions.map(item => item.value)"
                    v-model="configs['map'].visualization_options['aggregateFunction']"
                    :label="$t('common.queryAggregateFunction')"
                  />
                </div>
                <div
                  class="col-2 chart-options"
                  v-show="configs['map'].visualization_options['groupBy']"
                >
                  <q-input
                    type="number"
                    v-model="configs['map'].visualization_options['numBins']"
                    :label="$t('common.queryNumBins')"
                    :rules="[ val => val > 0 && val < 15 || t('error.valueOutOfBounds') + '0 & 15']"
                    @update:model-value="updateMapBin"
                  />
                </div>
                <div
                  class="col-2 chart-options"
                  v-show="configs['map'].visualization_options['aggregateFunction'] !== 'rows'"
                >
                  <q-select
                    :options="availableFields.map(f => f.data_field_name).filter(f => f !== configs['map'].visualization_options['groupBy'])"
                    v-model="configs['map'].visualization_options['aggregateField']"
                    :label="$t('common.queryAggregateField')"
                  />
                </div>
              </div>
              <div v-if="visualizationType === 'map'">
                <visualization-widget
                  :view-only="false"
                  :config="configs['map']"
                />
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import {merge as _merge} from 'lodash'
import {useRoute, useRouter} from 'vue-router'
import {reactive, ref, computed, onMounted} from 'vue'
import {debounce} from 'quasar'
import {useI18n} from 'vue-i18n'
import {fasFloppyDisk, fasCircleXmark, fasXmark} from '@quasar/extras/fontawesome-v6'

import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import QueryBuilder from 'components/QueryBuilder.vue'
import VisualizationWidget from 'components/visualization/VisualizationWidget.vue'

import {clearAndMerge} from "src/composables/utilities"

import {
  getSharedFields,
  createFieldsLookup,
  createReferenceOptionsLookup
} from "src/composables/dataset"
import {getRequest, postRequest, putRequest} from "boot/axios";
import {getAggregationFunctions, getVisualizationTypes, getDetectionAlgorithms} from "src/composables/visualization";
import {query} from "src/composables/dataset"

// Local Variables
const {t} = useI18n()
const router = useRouter()

const aggregateFunctions = getAggregationFunctions()
const visualizationTypes = getVisualizationTypes()
const detectionFunctions = getDetectionAlgorithms()

// Visualization info.  Track common fields outside of individual visualization objects
const configs = reactive({'table': {}, 'line': {}, 'bar': {}, 'pivot': {}, pie: {}, map: {}})
const visualizationType = ref('table')
const visualizationName = ref('')
const visualizationId = ref(null)


// Reactive model variables
const error = ref('')
const dataSets = ref([])
const sharedFields = ref([])
const fields = ref({})
const filters = ref({})
const visualizationFilterFields = ref([])
const selectedDataSet = ref(undefined)
const aggregateFunction = ref('count')
const referenceOptions = ref({})

// Compute the available fields based on the current filters and the shared fields for the dataset
const availableFields = computed(() => {
  let filteredFieldName = Object.keys(filters)
  return selectedDataSet.value.fields.filter(f => !filteredFieldName.includes(f.data_field_name) && sharedFields.value.includes(f.data_field_name))
})

const mappableFields = computed( () => {
    return selectedDataSet.value.fields.filter(f => f.region_map_id !== null && sharedFields.value.includes(f.data_field_name))
})

const isTimeResolutionField = function(field) {
  const fieldType = fields.value[field]?.data_field_type
  return fieldType == 'date' || fieldType == 'datetime'
}
/**
 * Default visualization creation function, based on current state.  Filters/dataset values might
 * already have been set.
 *
 * @returns default base visualization object.
 */
const getDefaultBaseVisualization = function () {
  return {
    visualization_name: visualizationName.value,
    dataset_id: selectedDataSet.value ? selectedDataSet.value.id : null,
    dataset_filtered_shared_fields: [],
    dataset_field_requests: filters.value,
    date_field: selectedDataSet.value && selectedDataSet.value.date_field ? selectedDataSet.value.date_field : null,
    visualization_options: {
      projection: sharedFields.value.reduce(function (map, sf) {
        map[sf] = 1;
        return map;
      }, {})
    }
  }
}

/**
 * Default line visualization.  Merges in the default visualization.
 * @returns default line visualization merged with default base visualization
 */
const getDefaultLineVisualization = function () {
  return _merge({}, {
        visualization_type: 'line',
        visualization_options: {
          groupBy: null,
          aggregateField: null,
          aggregateFunction: 'rows'
        }
      },
      getDefaultBaseVisualization()
  )
}

/**
 * Default bar visualization.  Merges in the default visualization.
 * @returns default bar visualization merged with default base visualization
 */
const getDefaultBarVisualization = function () {
  return _merge({}, {
        visualization_type: 'bar',
        visualization_options: {
          groupBy: null,
          aggregateField: null,
          aggregateFunction: 'rows',
          stacked: false,
          normalized: false
        }
      },
      getDefaultBaseVisualization()
  )
}

/**
 * Default table visualization.  Merges in the default visualization.
 * @returns default table visualization merged with default base visualization
 */
const getDefaultTableVisualization = function () {
  return _merge({}, {
        visualization_type: 'table',
        visualization_options: {
          sortBy: null,
          descending: false,
          rowsPerPage: 10,
          page: 1,
          columns: sharedFields.value.map(function (sf) {
            return {name: sf, label: availableFields.value.find(af => af.data_field_name === sf).display_name, field: row => row[sf], sortable: true, align: 'left'}
          })
        }
      },
      getDefaultBaseVisualization()
  )
}

/**
 * Default pivot visualization.  Merges in the default visualization.
 * @returns default pivot visualization merged with default base visualization
 */
const getDefaultPivotVisualization = function () {
  return _merge({}, {
        visualization_type: 'pivot',
        visualization_options: {
          pivotOptions: {
            rows: [],
            cols: [],
            aggregatorName: "Count",
            rendererName: "Table"
          }
        }
      },
      getDefaultBaseVisualization()
  )
}

/**
 * Default pie visualization.  Merges in the default visualization.
 * @returns default bar visualization merged with default base visualization
 */
const getDefaultPieVisualization = function () {
  return _merge({}, {
        visualization_type: 'pie',
        visualization_options: {
          groupBy: null,
          aggregateFunction: 'rows',
          aggregateField: null,
          topN: 5
        }
      },
      getDefaultBaseVisualization()
  )
}

const getDefaultMapVisualization = function () {
  return _merge({}, {
        visualization_type: 'map',
        // TODO--- UPDATE!
        visualization_options: {
          groupBy: null,
          aggregateFunction: 'rows',
          aggregateField: null,
          regionMapId: null,
          numBins: 5,
        }
      },
      getDefaultBaseVisualization()
  )
}

const updateMapBin = function (val) {
  if (val < 1) {
    configs['map'].visualization_options['numBins'] = 1
  }
  else if (val > 14) {
    configs['map'].visualization_options['numBins'] = 14
  }
}

const setRegionMapId = function () {
  configs['map'].visualization_options['regionMapId'] = selectedDataSet.value.fields.filter(x => x.data_field_name === configs['map'].visualization_options['groupBy'])[0].region_map_id
}

/**
 * Run when a dataset is changed or set for the first time.  Will reset the current filter state and
 * load the base dataset filters
 */
const getDataSetFilters = function () {
  filters.value = {}
  visualizationFilterFields.value = []
}

/**
 * Extract the filters set from the visualization on load.
 * TODO: This will be changed when we stop merging dataset and visualization filters.
 * @param visualization
 */
const extractVisualizationFilters = function (visualization) {

  filters.value = {};

  // Get the field requests.
  if (visualization.dataset_field_requests) {
    Object.keys(visualization.dataset_field_requests).forEach(fieldName => {
      filters.value[fieldName] = visualization.dataset_field_requests[fieldName]
    })
  }

  // Get the fields we're filtering on in the visualization.
  if (visualization.dataset_filtered_shared_fields) {
    visualization.dataset_filtered_shared_fields.forEach(sharedField => {
      visualizationFilterFields.value.push(sharedField)
    })
  }
}

/**
 * Update the filter emitted from the QueryBuilder and update the visualizations.
 * QueryBuilder should debounce.
 * @param req
 * @param field
 */
const updateFilter = function (req, field) {
  if (Object.keys(req).length > 0) {
    filters.value[field] = req
    updateFiltersForVisualizations()
  }
}

/**
 * Add a filter. Need to debounce this because modifying the collection that renders the dropdown when selecting
 * something from the dropdown causes it to not close.
 */
const addFilter = debounce((field) => {
  visualizationFilterFields.value.push(field.data_field_name)
  filters.value[field.data_field_name] = {};
}, 10);

/**
 * Remove a filter and update the visualizations.
 * @param fieldName
 */
const removeFilter = function (fieldName) {
  visualizationFilterFields.value = visualizationFilterFields.value.filter(f => f !== fieldName)
  delete filters.value[fieldName]
  updateFiltersForVisualizations()
}

/**
 * Filtering has changed.  Update the visualizations.  This will cause the visualization component to refresh.
 */
const updateFiltersForVisualizations = function () {
  // Update the visualizations
  Object.values(configs).forEach(visualization => {
    visualization.dataset_field_requests = filters.value;
    visualization.dataset_filtered_shared_fields = visualizationFilterFields.value;
  })
}

/**
 * Dataset changed; need to clear out filters and set new visualizations.
 */
const dataSetChanged = function () {
  error.value = ''
  getDataSetFilters()
  createVisualizationConfigs()
}

/**
 * Setup the various visualization structures based on the selected dataset, and clear/setup
 * any reference data needed for the UI.
 */
const createVisualizationConfigs = function () {

  sharedFields.value = getSharedFields(selectedDataSet.value)
  referenceOptions.value = createReferenceOptionsLookup(selectedDataSet.value)
  fields.value = createFieldsLookup(selectedDataSet.value)

  if (!configs['table'] || configs['table'].dataset_id !== selectedDataSet.value.id) {
    clearAndMerge(configs['table'], getDefaultTableVisualization(selectedDataSet.value))
  }
  if (!configs['line'] || configs['line'].dataset_id !== selectedDataSet.value.id) {
    clearAndMerge(configs['line'], getDefaultLineVisualization(selectedDataSet.value))
  }
  if (!configs['bar'] || configs['bar'].dataset_id !== selectedDataSet.value.id) {
    clearAndMerge(configs['bar'], getDefaultBarVisualization(selectedDataSet.value))
  }
  if (!configs['pivot'] || configs['pivot'].dataset_id !== selectedDataSet.value.id) {
    clearAndMerge(configs['pivot'], getDefaultPivotVisualization(selectedDataSet.value))
  }
  if (!configs['pie'] || configs['pie'].dataset_id !== selectedDataSet.value.id) {
    clearAndMerge(configs['pie'], getDefaultPieVisualization(selectedDataSet.value))
  }
  if (!configs['map'] || configs['map'].dataset_id !== selectedDataSet.value.id) {
    clearAndMerge(configs['map'], getDefaultMapVisualization(selectedDataSet.value))
  }
}

/**
 * Save the current visualization.
 *
 * TODO: Should do some checking to make sure it's valid before saving.
 */
const save = async function () {

  let visualization = {
    overlay: false
  }

  // Set the id if known.
  if (visualizationId.value) {
    visualization.id = visualizationId.value
  }
  visualization.visualization_name = visualizationName.value

  // Horrible.
  if (visualizationType.value === 'pivot') {
    let config = $(".pivot").data("pivotUIOptions")
    let config_copy = JSON.parse(JSON.stringify(config))
    //delete some values which will not serialize to JSON
    delete config_copy["aggregators"]
    delete config_copy["renderers"]
    configs[visualizationType.value].visualization_options.pivotOptions.rows = config['rows']
    configs[visualizationType.value].visualization_options.pivotOptions.cols = config['cols']
  }


  // Save the visualization config.  Only one since it's not an overlay.
  visualization.configs = [configs[visualizationType.value]]

  if (visualizationId.value) {
    await putRequest('visualization/' + visualizationId.value, visualization)
  }
  else {
    await postRequest('visualization', visualization)
  }
  await router.push('/visualization')
}

/**
 * Cancel editing/creating.  Go back to main visualization page
 */
const cancel = function () {
  router.push('/visualization')
}

/**
 * Load the datasets and the visualization if we're editing an existing visualization.
 */
onMounted(async () => {

  const route = useRoute()
  visualizationId.value = 'visualizationId' in route.params ? route.params.visualizationId : null

  dataSets.value = (await getRequest('dataset')).data.filter(d => d.is_active)

  if (visualizationId.value) {

    // Set the common variables
    const visualization = (await getRequest('visualization/' + visualizationId.value)).data
    let config = visualization.configs[0];

    configs[config.visualization_type] = config;
    visualizationType.value = config.visualization_type;

    visualizationName.value = visualization.visualization_name;

    // Set the filters so that all the visualizations have access to them
    extractVisualizationFilters(config)

    // Set the dataset
    selectedDataSet.value = dataSets.value.filter(f => f['id'] === config.dataset_id)[0]
    if (selectedDataSet.value) {
      // Create the other visualization configs based on the current visualization
      createVisualizationConfigs()
    }
    else {
      error.value = 'The associated dataSet has been removed.'
    }
  }
})

</script>

<style scoped>

.my-card {
  height: 100%;
  width: 100%;
}

.visualization-row {
  padding-top: 6px;
  padding-bottom: 6px;
}

.filter-card-section {
  padding: 6px;
}

.filter-query-card-section {
  height: 270px;
  overflow: auto;
}

.chart-options {
  padding: 6px;
}

.btn-container {
  display: flex;
  justify-content: center;
}

.save-btn {
  width: 150px;
  margin-right: 5px;
}

.cancel-btn {
  width: 150px;
  margin-left: 5px;
}

.filter-card-group {
  padding: 5px;
}

</style>
