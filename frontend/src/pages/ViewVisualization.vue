<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />
    <q-banner
      v-if="error"
      class="text-white bg-red"
    >
      {{ error }}
    </q-banner>
    <div
      v-if="visualization"
    >
      <div class="col-4 ">
        <h6>{{ visualization.visualization_name }}</h6>
      </div>
      <combined-visualization-widget class="visualization" :visualization="visualization" />
    </div>
  </q-page>
</template>

<script setup>
import {useRoute, useRouter} from 'vue-router'
import { ref, onMounted} from 'vue'
import {useI18n} from 'vue-i18n'

import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'

import {getRequest} from "boot/axios";
import CombinedVisualizationWidget from "components/visualization/CombinedVisualizationWidget.vue";

// Local Variables
const {t} = useI18n()
const router = useRouter()

const error = ref('')
const visualizationId = ref('')
const visualization = ref(null)

onMounted(async () => {

  const route = useRoute()
  visualizationId.value =  route.params.visualizationId

  if (visualizationId.value) {
    try {
      visualization.value = (await getRequest('visualization/' + visualizationId.value)).data
    }
    catch (err) {
      error.value = 'Unable to load visualization.'
    }
  }
})

</script>

<style scoped>

.visualization {
  height: 80%;
  display: flex;
  flex-direction: column;
}

</style>
