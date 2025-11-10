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
          :label="t('visualization.search')"
          :append-icon="fasMagnifyingGlass"
          outlined
          v-model="search"
        />
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
            v-for="visualization in filteredVisualizations"
            :key="visualization.id"
            class="col-4"
          >
            <q-card-section class="bg-primary text-white">
              <div class="text-h6">
                {{ visualization.visualization_name }}
              </div>
            </q-card-section>

            <q-card-section>
              <p>
                <b> {{ $t('dataset.plural') }}:</b> {{ extractDatasets(visualization) }}
              </p>
              <p><b>{{ $t('visualization.type') }}:</b> {{ extractVisTypes(visualization) }}</p>
            </q-card-section>

            <q-separator dark />

            <q-card-actions class="float-right">
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/visualization/' + visualization.id}"
                :icon="fasBinoculars"
                :label="t('common.view')"
              />
              <q-btn
                v-if="!visualization.overlay"
                class="bg-primary text-white"
                :to="{ path: '/visualization/' + visualization.id + '/edit'}"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                v-if="visualization.overlay === true"
                class="bg-primary text-white"
                :to="{ path: '/visualization/overlay/' + visualization.id + '/edit'}"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                class="bg-primary text-white"
                :icon="fasTrashCan"
                :label="t('common.delete')"
                @click="() => presentDeleteVisualizationDialog(visualization)"
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
          v-for="(visualization) in filteredVisualizations"
          :key="visualization.id"
        >
          <q-item-section>
            <q-item-label>{{ visualization.visualization_name }}</q-item-label>
            <q-item-label caption>
              Dataset(s): {{ extractDatasets(visualization) }},
              Visualization Type: {{ extractVisTypes(visualization) }}
            </q-item-label>
          </q-item-section>
          <q-item-section
            side
            top
          >
            <span class="q-pa-md q-gutter-sm">
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/visualization/' + visualization.id }"
                :icon="fasBinoculars"
                :label="t('common.view')"
              />
              <q-btn
                v-if="!visualization.overlay"
                class="bg-primary text-white"
                :to="{ path: '/visualization/' + visualization.id + '/edit'}"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                v-if="visualization.overlay === true"
                class="bg-primary text-white"
                :to="{ path: '/visualization/overlay/' + visualization.id + '/edit'}"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                class="bg-primary text-white"
                :icon="fasTrashCan"
                :label="t('common.delete')"
                @click="() => presentDeleteVisualizationDialog(visualization)"
              />
            </span>
          </q-item-section>
          <q-separator
            v-if="index < visualizations.length - 1"
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
          <span class="q-ml-sm">Delete: {{ visualizationToDelete.visualization_name }}? </span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancel"
            color="primary"
            v-close-popup
          />
          <q-btn
            flat
            :loading="visualizationLoading"
            :label="t('common.delete')"
            color="primary"
            @click="() => deleteVisualizationAndRefresh(visualizationToDelete.id)"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <div v-if="!visualizationLoading && visualizations.length === 0">
      <h6 class="row justify-center items-center">
        {{ t('visualization.noneAvailable') }}
      </h6>
      <div class="row justify-center items-center">
        <q-btn
          color="primary"
          :to="{ path: '/visualization/create'}"
          :label="t('visualization.create')"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup>

import {storeToRefs} from 'pinia'
import {ref, computed, onMounted} from 'vue'
import {useI18n} from 'vue-i18n'
import {
  fasTable,
  fasList,
  fasMagnifyingGlass,
  fasBinoculars,
  fasPencil,
  fasTrashCan
} from '@quasar/extras/fontawesome-v6'

import { useVisualizationUIStore } from 'stores/visualization-ui'
import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import {deleteRequest, getRequest} from "boot/axios";
import {getDisplayNameOfType} from 'src/composables/visualization'

const {t} = useI18n()

const { showAsGrid } = storeToRefs(useVisualizationUIStore())

const dataSets = ref([])
const search = ref('')
const showDeleteDialog = ref(false)
const visualizationToDelete = ref({})
const visualizations = ref([])
const visualizationLoading = ref(false)

/**
 * Helper function to extract the dataset names from all the configs.
 * @param visualization the visualization to get the dataset names from.
 * @returns a comma delimited string of the display names of the datasets.
 */
const extractDatasets = function(visualization) {
  let dataSetNames = {};
  visualization.configs.forEach(config => {
    let dataSetName =  dataSets.value.filter(f => f.id === config.dataset_id)[0] ? dataSets.value.filter(f => f.id === config.dataset_id)[0].display_name : config.dataset_id
    dataSetNames[dataSetName] = 1
  })
  return Object.keys(dataSetNames).join(", ")
}

/**
 * Helper function to extract the visualization types from all the configs
 * @param visualization the visualization to get the visualization type labels from.
 * @returns a comma delimited string of the i18n labels of the visualization types
 */
const extractVisTypes = function(visualization) {
  let visTypes = [];
  visualization.configs.forEach(config => {
    visTypes.push(getDisplayNameOfType(config.visualization_type))
  })
  return visTypes.join(", ");
}

/**
 * Filter the visualizations based on the search value.  Looks in the name and description.
 */
const filteredVisualizations = computed(() => {
  if (!search.value.length) return visualizations.value
  return visualizations.value.filter(visualization =>
      (visualization.visualization_name && visualization.visualization_name.toLowerCase().includes(search.value.toLowerCase())) ||
      (visualization.description && visualization.description.toLowerCase().includes(search.value.toLowerCase()))
  )
})

const deleteVisualizationAndRefresh = async function (visualizationId) {
  await deleteRequest('visualization/' + visualizationId)
  await refreshVisualizations()
}
const refreshVisualizations = async function () {
  visualizations.value = (await getRequest('visualization')).data
}
const presentDeleteVisualizationDialog = function (visualization) {
  showDeleteDialog.value = true
  visualizationToDelete.value = visualization
}

onMounted(async () => {
  await refreshVisualizations()
  dataSets.value = (await getRequest('dataset')).data.filter(d => d.is_active)
})

</script>
