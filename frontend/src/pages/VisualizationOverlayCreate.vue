<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />
    <div class="row visualization-row">
      <div class="col-2">
        <q-btn-dropdown
          color="primary"
          :label="$t('visualization.add')"
          class="q-pa-md"
        >
          <q-list
            v-for="type in availableVisualizationTypes"
            :key="type.name"
          >
            <q-item
              clickable
              v-close-popup
              @click="addVisualizationConfig(type.name)"
            >
              <q-item-section>
                <q-item-label>{{ type.label }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </div>
      <div class="col-6 q-pl-lg">
        <q-input
          v-model="visualizationName"
          :label="$t('common.name')"
        />
      </div>
      <div class="col-4 btn-container">
        <q-btn
          class="save-btn q-mr-sm"
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
    <div
      class="row"
      v-if="configs.length > 0 && configs[0].visualization_type"
    >
      <q-expansion-item
        class="col-12 visualization-row"
        switch-toggle-side
        v-for="(config,index) in configs"
        default-opened
        popup
        :key="config.key"
      >
        <template #header>
          <q-item-section>
            {{t('visualization.series')}} {{index + 1 }} - {{getDisplayNameOfType(config.visualization_type)}}
          </q-item-section>

          <q-item-section side>
            <q-btn
              v-if="config.visualization_type"
              class="float-right delete-btn"
              size="md"
              :icon="fasXmark"
              @click="deleteVisualizationConfig(index)"
            />
          </q-item-section>
        </template>
        <q-card>
          <q-card-section class="filter-card-section">
            <visualization-overlay-config
              :config="config"
              :type="config.visualization_type"
              :primary="index === 0"
              @update:config="updateVisualizationConfig"
            />
          </q-card-section>
        </q-card>
      </q-expansion-item>
    </div>
    <div>
      <visualization-overlay-widget :configs="configs" />
    </div>
  </q-page>
</template>

<script setup>
import {useRoute, useRouter} from 'vue-router'
import {reactive, ref, onMounted, computed} from 'vue'
import {useI18n} from 'vue-i18n'
import {fasFloppyDisk, fasCircleXmark, fasXmark} from '@quasar/extras/fontawesome-v6'

import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import VisualizationOverlayConfig from 'components/visualization/VisualizationOverlayConfig.vue'

import VisualizationOverlayWidget from "components/visualization/VisualizationOverlayWidget.vue";
import {$api} from "boot/axios";
import {debounce} from "quasar";
import {getDisplayNameOfType, getOverlayVisualizationTypes} from "src/composables/visualization";

// Local Variables
const {t} = useI18n()
const router = useRouter()
const visualizationTypes = getOverlayVisualizationTypes()

// Set default visualization list
const configs = reactive([])
const visualizationName = ref('')
const visualizationId = ref(null)

// Bar can only be the first series.  If you add later it will hide other series
const availableVisualizationTypes = computed( () => {
  if (configs.length > 0) {
    return visualizationTypes.filter(t => t.name !== 'bar')
  }
  else {
    return visualizationTypes
  }
})

// Called when the update event from the config is triggered
const updateVisualizationConfig = function (config) {

  for (let i = 0; i < configs.length; i++) {

    if (configs[i].key === config.key) {
      configs[i] = config;
      break;
    }
  }
}

// Need to debounce because it's modifying the dropdown list
const addVisualizationConfig = debounce((type) => {
  configs.push({visualization_type: type, key: new Date().getTime()})
}, 10);

const deleteVisualizationConfig = function (index) {
  configs.splice(index, 1)
}

/**
 * Save the current visualization.
 */
const save = async function () {

  let visualization = {
    overlay: true
  }

  // Set the id if known.
  if (visualizationId.value) {
    visualization.id = visualizationId.value
  }
  visualization.visualization_name = visualizationName.value
  visualization.configs = configs

  if (visualizationId.value) {
    await $api.put('visualization/' + visualizationId.value, visualization)
  }
  else {
    await $api.post('visualization', visualization)
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

  if (visualizationId.value) {

    // Used to let Vue handle in a table
    let baseKey = new Date().getTime()

    // Set the common variables
    const visualization = (await $api.get('visualization/' + visualizationId.value)).data
    visualizationName.value = visualization.visualization_name;
    visualization.configs.forEach(config => {
      config.key = baseKey++
      configs.push(config)
    })
  }
})
</script>

<style scoped>

.visualization-row {
  padding-top: 6px;
  padding-bottom: 6px;
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

.delete-btn {
  color: black;
}
.visualization-row {
  padding-top: 6px;
  padding-bottom: 6px;
}

.filter-card-section {
  padding: 6px;
}

</style>
