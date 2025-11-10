<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <div>
    <div class="row filter-row">
      <div
        v-if="dataSet"
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
                <q-item-label>{{ field.data_field_name }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </div>
    </div>
    <div
      v-if="dataSet"
      class="row filter-row"
    >
      <div
        v-for="field in filterFields"
        :key="field"
        class="col-3 filter-card-group"
      >
        <q-card>
          <q-card-section class="filter-card-section">
            <div class="row items-center no-wrap">
              <div class="col">
                <div
                  class="text-h6"
                  style="padding-left: 12px"
                >
                  {{ field }}
                </div>
              </div>
              <div class="col-auto">
                <q-btn
                  dense
                  round
                  flat
                  :icon="fasCircleXmark"
                  @click="removeFilter(field)"
                />
              </div>
            </div>
          </q-card-section>
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
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, watch, defineProps, onMounted, defineEmits} from 'vue'
import {debounce} from 'quasar'
import {useI18n} from 'vue-i18n'
import {fasCircleXmark} from '@quasar/extras/fontawesome-v6'

import QueryBuilder from 'components/QueryBuilder.vue'

import {
  createFieldsLookup,
  getSharedFields
} from "src/composables/dataset"

// Local Variables
const {t} = useI18n()

const emits = defineEmits(['update:filters'])

// Reactive model variables
const sharedFields = ref([])
const fields = ref({})
const filters = ref({})
const filterFields = ref([])
const referenceOptions = ref({})

// Compute the available fields based on the current filters and the shared fields for the dataset
const availableFields = computed(() => {
  let filteredFieldName = Object.keys(filters.value)
  return props.dataSet.fields.filter(f => !filteredFieldName.includes(f.data_field_name) && sharedFields.value.includes(f.data_field_name))
})

/**
 * Run when a dataset is changed or set for the first time.  Will reset the current filter state and
 * load the base dataset filters
 */
const getDataSetFilters = function () {
  filterFields.value = []
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
  }
  emits('update:filters', JSON.parse(JSON.stringify(filters.value)))
}

/**
 * Add a filter. Need to debounce this because modifying the collection that renders the dropdown when selecting
 * something from the dropdown causes it to not close.
 */
const addFilter = debounce((field) => {
  filterFields.value.push(field.data_field_name)
  filters.value[field.data_field_name] = {};
}, 10);

/**
 * Remove a filter and update the visualizations.
 * @param fieldName
 */
const removeFilter = function (fieldName) {
  filterFields.value = filterFields.value.filter(f => f !== fieldName)
  delete filters.value[fieldName]
  emits('update:filters', JSON.parse(JSON.stringify(filters.value)))
}

/**
 * Dataset changed; need to clear out filters and set new visualizations.
 */
const dataSetChanged = function () {
  getDataSetFilters()
  sharedFields.value = getSharedFields(props.dataSet)
  fields.value = createFieldsLookup(props.dataSet)
}

const props = defineProps({
  dataSet: Object,
  currentFilters: Object,
  currentFilterFields: Object

})

watch(props.dataSet, (dataSet) => {
  if (dataSet) {
    dataSetChanged()
  }
}, { deep: true })

onMounted(async () => {

  if (props.currentFilters || props.currentFilterFields) {
    filters.value = props.currentFilters
    filterFields.value = props.currentFilterFields
    sharedFields.value = getSharedFields(props.dataSet)
    fields.value = createFieldsLookup(props.dataSet)
  }
  else if (props.dataSet) {
    dataSetChanged()
  }
})

</script>

<style scoped>

.filter-row {
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

.filter-card-group {
  padding: 5px;
}

</style>
