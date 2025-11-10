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
    <div class="row">
      <div class="col-4 ">
        <q-input
          v-model="title"
          :label="t('common.title')"
          disable
          :loading="mapLoading"
        />
      </div>
    </div>
    <div v-if="mapLoading">
      <q-spinner
        color="primary"
        size="2em"
        class="center"
      />
    </div>
    <div
      class="row"
      v-else
    >
      <div
        class="col-12 q-pr-md"
        id="map-container"
      >
        <!-- https://github.com/vue-leaflet/vue-leaflet/issues/278#issuecomment-1448388783 -->
        <l-map
          v-if="center !== undefined"
          id="map"
          :use-global-leaflet="false"
          :zoom="zoom"
          :center="center"
        >
          <l-geo-json
            :geojson="geoJSONs"
            :options="mapOptions"
            :options-style="mapStyle"
          />
          <l-control>
            <div
              v-if="highlightedRegion !== undefined"
              class="control"
            >
              <b>{{ highlightedRegion }}</b>
            </div>
          </l-control>
        </l-map>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import PageBreadcrumbs from "components/PageBreadcrumbs.vue"
import { useI18n } from 'vue-i18n'
import { LMap, LGeoJson, LControl } from "@vue-leaflet/vue-leaflet"
import "leaflet/dist/leaflet.css"
import {computed, ref, onMounted} from "vue"

import { $api } from "boot/axios"

const { t } = useI18n()
const router = useRouter()

const mapLoading = ref(false)
const mapId = ref(null)
const title = ref('')
const zoom = ref(undefined)
const geoJSONs = ref([])
const center = ref(undefined)
const highlightedRegion = ref(undefined)

// Map fns.
const highlightFeature = function (e) {
   const layer = e.target
    layer.setStyle({
      weight: 3,
      fillOpacity: 1
    })
    highlightedRegion.value = layer.feature.properties.DISPLAY_NAME
}
const resetHighlight = function (e) {
  const layer = e.target
  layer.setStyle({
    weight: 1,
    fillOpacity: 0.6
  })
  highlightedRegion.value = undefined
}
const onEachFeature = function (feature, layer) {
  layer.on({
    mouseover: highlightFeature,
    mouseout: resetHighlight
  })
}
const mapOptions = computed ( () =>{
  return {onEachFeature: onEachFeature}
})

const mapStyle = function (feature) {
  return {
    color: '#303e4e',
    fillColor: 'white',
    weight: 1,
    opacity: 1,
    dashArray: '1',
    fillOpacity: 0.6,
    radius: 1000
  }
}


onMounted (async () => {
  const route = useRoute()
  mapId.value = route.params.mapId
  mapLoading.value = true
  const response = (await $api.get('map/' + mapId.value)).data
  title.value = response.display_name
  zoom.value = response.zoom
  center.value = response.center
  geoJSONs.value = response.regions.map(x => x.geojson)
  mapLoading.value = false
})

</script>

<style scoped>
  #map-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  #map {
    min-height: 500px;
  }

</style>
