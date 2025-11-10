<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <div>
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
      <div
        v-if="selectedDataSet"
        class="col-3 q-pl-md"
      >
        <q-input
          v-model="visualizationConfig.visualization_options.yaxis_title"
          :label="$t('common.name')"
        />
      </div>
      <div v-if="selectedDataSet" class="col-3 q-pl-md">
        <div
          v-if="selectedDataSet"
          class="q-pl-md q-pt-md"
        >
          <q-checkbox
            v-if="!primary"
            v-model="visualizationConfig.visualization_options.separate_yaxis"
            :label="$t('visualization.newYAxis')"
          />
        </div>
        <div
          v-if="visualizationConfig.visualization_type=='bar'"
          class="q-pl-md"
        >
          <q-checkbox
            v-model="visualizationConfig.visualization_options.stacked"
            :label="$t('visualization.barConfig.stacked')"
          />
        </div>
        <div
          v-if="visualizationConfig.visualization_type=='bar'"
          class="q-pl-md"
        >
          <q-checkbox
            v-model="visualizationConfig.visualization_options.normalized"
            :label="$t('visualization.barConfig.normalized')"
          />
        </div>
      </div>
      <div class="col-1">
        <q-btn
          class="apply-button"
          color="primary"
          :label="$t('common.apply')"
          text-color="white"
          :disabled="!dataModified"
          @click="applyConfig()"
        />
      </div>
    </div>
    <FilterConfig
      v-if="selectedDataSet"
      :data-set="selectedDataSet"
      :current-filters="filters"
      :current-filter-fields="visualizationFilterFields"
      @update:filters="updateFilters"
    />
    <div
      v-if="selectedDataSet"
      class="row visualization-row"
    >
      <div class="col-12">
        <q-card>
          <div class="row visualization-row">
            <div class="col-2 chart-options">
              <q-select
                :options="visualizationConfig.visualization_type === 'line' ? availableFields.filter(f => f.data_field_name !== visualizationConfig.visualization_options.aggregateField
                  && f.data_field_name !== visualizationConfig.visualization_options.stratification) : availableFields"
                option-label="display_name"
                option-value="data_field_name"
                emit-value
                v-model="visualizationConfig.visualization_options.groupBy"
                label="X"
              />
            </div>
            <div
              class="col-2 chart-options"
              v-show="visualizationConfig.visualization_options.groupBy"
            >
              <q-select
                :options="aggregateFunctions.map(item => item.value)"
                :option-label="(item) => aggregateFunctions.filter(ref => ref.value === item)[0].label"
                v-model="visualizationConfig.visualization_options.aggregateFunction"
                :label="$t('common.queryAggregateFunction')"
              />
            </div>
            <div
              class="col-2 chart-options"
              v-show="visualizationConfig.visualization_options.aggregateFunction !== 'rows'"
            >
              <q-select
                :options="availableFields.map(f => f.data_field_name).filter(f => f !== visualizationConfig.visualization_options.groupBy && f !== visualizationConfig.visualization_options.stratification)"
                option-label="display_name"
                option-value="data_field_name"
                v-model="visualizationConfig.visualization_options.aggregateField"
                label="Y"
              />
            </div>
            <div
              class="col-2 chart-options"
              v-show="visualizationConfig.visualization_options.groupBy"
            >
              <q-select
                :options="availableFields.map(f => f.data_field_name).filter(f => f !== visualizationConfig.visualization_options.groupBy && f !== visualizationConfig.visualization_options.aggregateField)"
                option-label="display_name"
                option-value="data_field_name"
                clearable
                v-model="visualizationConfig.visualization_options.stratification"
                :label="$t('visualization.stratification')"
              />
            </div>
          </div>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import {merge as _merge} from 'lodash'
import {useRouter} from 'vue-router'
import {ref, computed, onMounted, defineProps, defineEmits, watch} from 'vue'
import {useI18n} from 'vue-i18n'
import FilterConfig from 'components/visualization/FilterConfig.vue'
import {$api} from "boot/axios";

import {clearAndMerge} from "src/composables/utilities"
import {
  getSharedFields,
  createFieldsLookup,
  createReferenceOptionsLookup
} from "src/composables/dataset"

import {
  getDefaultBaseVisualization, extractVisualizationFilters, getAggregationFunctions
} from "src/composables/visualization"

// Local Variables
const {t} = useI18n()
const router = useRouter()
const aggregateFunctions = getAggregationFunctions()
const emits = defineEmits(['update:config'])

const applyConfig = () =>   { dataModified.value = false; emits('update:config', JSON.parse(JSON.stringify(visualizationConfig.value))) }

// Visualization info.  Track common fields outside of individual visualization objects
const visualizationName = ref('')

// Reactive model variables
let dataSets = ref([])
const selectedDataSet = ref(undefined)
let visualizationConfig = ref({})
const sharedFields = ref([])
const fields = ref({})
const filters = ref({})
const visualizationFilterFields = ref([])
const referenceOptions = ref({})
const dataModified = ref(false)

// Compute the available fields based on the current filters and the shared fields for the dataset
const availableFields = computed(() => {
  let filteredFieldName = Object.keys(filters)
  return selectedDataSet.value.fields.filter(f => !filteredFieldName.includes(f.data_field_name) && sharedFields.value.includes(f.data_field_name))
})

const updateFilters = function (updatedFilters) {
  visualizationConfig.value.dataset_field_requests = updatedFilters;
  visualizationConfig.value.dataset_filtered_shared_fields = Object.keys(updatedFilters)
}

/**
 * Default line visualization.  Merges in the default visualization.
 * @returns default line visualization merged with default base visualization
 */
const getDefaultLineVisualization = function () {
  return _merge({}, {
        visualization_type: props.type,
        visualization_options: {
          groupBy: null,
          aggregateField: null,
          yaxis_title: null,
          separate_yaxis: false,
          aggregateFunction: 'rows'
        }
      },
      getDefaultBaseVisualization(selectedDataSet.value, filters.value, sharedFields.value)
  )
}

const getDefaultBarVisualization = function () {
  return _merge({}, {
        visualization_type: props.type,
        visualization_options: {
          groupBy: null,
          aggregateField: null,
          yaxis_title: null,
          separate_yaxis: false,
          stacked: false,
          normalized: false,
          aggregateFunction: 'rows'
        }
      },
      getDefaultBaseVisualization(selectedDataSet.value, filters.value, sharedFields.value)
  )
}

/**
 * Run when a dataset is changed or set for the first time.  Will reset the current filter state and
 * load the base dataset filters
 */
const getDataSetFilters = function () {
  visualizationFilterFields.value = []
}

/**
 * Dataset changed; need to clear out filters and set new visualizations.
 */
const dataSetChanged = function () {
  getDataSetFilters()
  createVisualizationConfig()
}

const props = defineProps({
  config: Object,
  type: String,
  primary: {
    type: Boolean,
    default: true
  }
})

// Data is modified when config changes; will enable apply button.
watch(visualizationConfig, (newValue, _oldValue) => {
  dataModified.value = true;
}, {deep: true});

/**
 * Visualization structure based on the selected dataset, and clear/setup
 * any reference data needed for the UI.
 */
const createVisualizationConfig = function () {

  let newConfig = JSON.parse(JSON.stringify(props.config))

  sharedFields.value = getSharedFields(selectedDataSet.value)
  referenceOptions.value = createReferenceOptionsLookup(selectedDataSet.value)
  fields.value = createFieldsLookup(selectedDataSet.value)

  if (!props.config.dataset_id || props.config.dataset_id !== props.dataSet.id) {
    if (props.type === 'line') {
      clearAndMerge(newConfig, getDefaultLineVisualization())
    }
    else {
      clearAndMerge(newConfig, getDefaultBarVisualization())
    }
  }
  if (props.config.key) {
    newConfig.key = props.config.key;
  }

  visualizationConfig.value = newConfig
}

onMounted(async () => {

  dataSets.value = (await $api.get('dataset')).data.filter(d => d.is_active)

  if (props.config && props.config.dataset_id) {

    visualizationConfig.value = JSON.parse(JSON.stringify(props.config))

    // Set the name
    visualizationName.value = props.config.visualization_name;

    // Set the filters so that all the visualizations have access to them
    extractVisualizationFilters(visualizationConfig.value, filters.value, visualizationFilterFields.value)

    // Set the dataset
    selectedDataSet.value = dataSets.value.filter(f => f['id'] === props.config.dataset_id)[0]
  }
})

</script>

<style scoped>

.visualization-row {
  padding-top: 6px;
  padding-bottom: 6px;
}

.chart-options {
  padding: 6px;
}

.apply-button {
  width: 150px;
  margin-left: 15px;
  margin-top: 20px;
}

</style>
