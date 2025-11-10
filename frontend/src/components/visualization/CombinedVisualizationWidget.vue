<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <div>
    <div v-if="visualization.overlay">
      <visualization-overlay-widget :configs="visualization.configs" :startDate="startDate" :endDate="endDate"/>
    </div>
    <div v-if="!visualization.overlay">
      <visualization-widget :config="visualization.configs[0]" :startDate="startDate" :endDate="endDate" :view-only="viewOnly" />
    </div>
  </div>
</template>

<script setup>

import VisualizationWidget from "components/visualization/VisualizationWidget.vue";
import VisualizationOverlayWidget from "components/visualization/VisualizationOverlayWidget.vue";

const props = defineProps({
  visualization: {
    type: Object,
    default: null
  },
  viewOnly: {
    type: Boolean,
    default: true
  },
  startDate: {
    type: String,
    default: null
  },
  endDate: {
    type: String,
    default: null
  }
})

</script>
<style scoped>
</style>
