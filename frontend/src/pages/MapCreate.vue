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
          :loading="mapLoading"
        />
      </div>
      <div class="col-5" />
      <div class="col-3 btn-container">
        <q-btn
          class="save-btn"
          color="primary"
          :label="t('common.save')"
          size="md"
          text-color="white"
          :loading="mapLoading"
          :icon="fasFloppyDisk"
          @click="saveMap"
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
    <div class="row">
      <div
        class="col-6 q-pr-md"
        id="map-container"
      >
        <!-- https://github.com/vue-leaflet/vue-leaflet/issues/278#issuecomment-1448388783 -->
        <l-map
          v-if="center !== undefined"
          id="map"
          :use-global-leaflet="false"
          :zoom="zoom"
          :center="center"
          @update:zoom="zoomUpdated"
          @update:center="centerUpdated"
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
      <div class="col-6 q-pa-md q-gutter-md">
        <div class="row q-gutter-sm">
          <q-file
            outlined
            dense
            v-model="geoJsonFile"
            accept=".json"
            :label="t('map.geoJsonFile')"
          />
          <q-input
            outlined
            dense
            v-model="geoJsonPropertiesField"
            :label="t('map.geoJsonIdField')"
          />
          <q-btn
            color="primary"
            :disable="!geoJsonFile"
            @click="onUploadGeoJson"
            :icon="fasUpload"
            :label="t('common.upload')"
          />
        </div>
        <div class="row q-gutter-sm">
          <q-btn
            @click="addRegion"
            :icon="fasPlus"
            :label="t('region.addRegion')"
            color="primary"
          />
          <q-btn
            @click="clearRegions"
            :icon="fasTrash"
            :label="t('region.clearRegions')"
            color="primary"
          />
        </div>
        <div
          class="row"
          v-for="regionMap in regionMaps"
          :key="regionMap.key"
        >
          <div class="col-3 q-mr-sm">
            <q-input
              :outlined="true"
              :label="t('region.name')"
              v-model="regionMap.display_name"
              @change="(e) => updateDisplayName(regionMap, e)"
              dense
            />
          </div>
          <div class="col-8">
            <q-input
              :outlined="true"
              :label="t('region.geojson')"
              v-model="regionMap.geojson_str"
              @change="(e) => updateGeoJson(regionMap, e)"
              dense
            />
          </div>
        </div>
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
import {
  fasPlus,
  fasFloppyDisk,
  fasXmark,
  fasTrash,
  fasUpload
} from '@quasar/extras/fontawesome-v6'

import debug from 'debug'

const mapLogger = debug('vims:mapCreate')

import { $api } from "boot/axios"

const { t } = useI18n()
const router = useRouter()

const mapId = ref(null)
const geoJsonFile = ref(null)
const geoJsonPropertiesField = ref(null)
const mapLoading = ref(false)
const title = ref('')
const regionMaps = ref([])
const zoom = ref(undefined)
const center = ref(undefined)
const highlightedRegion = ref(undefined)
const nextKey = ref(0)

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
const zoomUpdated = function (new_zoom) {
  zoom.value = new_zoom
}
const centerUpdated = function (new_center) {
  center.value = new_center
}

const getNextKey = function () {
  const key = nextKey.value
  nextKey.value += 1
  return key
}
const updateGeoJson = function (regionMap, e) {
  try {
    regionMap.geojson = JSON.parse(e)
    regionMap.geojson.properties.DISPLAY_NAME = regionMap.display_name
    regionMap.geojson_str = e
  }
  catch (err) {
    regionMap.geojson = {}
    regionMap.geojson_str = ''
  }
}
const updateDisplayName = function (regionMap, e) {
  regionMap.display_name = e
  if (regionMap.geojson.hasOwnProperty('properties')) {
    regionMap.geojson.properties.DISPLAY_NAME = regionMap.display_name
  }
}

const geoJSONs = computed ( () => {
  return regionMaps.value.map(x => x.geojson)
})

const addRegion = function () {
  if (regionMaps.value.length === 0 || (regionMaps.value[0].display_name !== '' && regionMaps.value[0].geojson !== '')) {
    regionMaps.value.unshift({display_name: '', geojson: {}, geojson_str: '', key: getNextKey()})
  }
}

const saveMap = async function () {
  mapLoading.value = true
  const regions = regionMaps.value.map((x) => ({display_name: x.display_name, geojson: x.geojson}))
  const regionMap = {display_name: title.value, zoom: zoom.value, center: center.value, regions: regions}
  if (mapId.value === null) {
    await $api.post('map', regionMap)
  }
  else {
    await $api.put('map/' + mapId.value, regionMap)
  }

  mapLoading.value = false
  await router.push('/data/maps')
}

const cancel = async function () {
  await router.push('/data/maps')
}

const clearRegions = async function () {
  regionMaps.value = []
}

const onUploadGeoJson = async function () {
  // artificial delay due to an issue where the global loading screen
  // using quasar plugin does not show

  try {
    let geoJson = await readFileAsync(geoJsonFile.value)
    geoJson = JSON.parse(geoJson)

    let geoJsonPolygons = geoJson['features']

    for (const i in geoJsonPolygons) {
      const displayName = geoJsonPolygons[i]['properties'][geoJsonPropertiesField.value]
      geoJsonPolygons[i]['properties']['DISPLAY_NAME'] = displayName

      let regionMap = {
            display_name: displayName,
            geojson: geoJsonPolygons[i],
            geojson_str: JSON.stringify(geoJsonPolygons[i]),
            key: getNextKey()
          }

      regionMaps.value.unshift(regionMap)
    }
  }
  catch (ex) {
    mapLogger(ex)
  }
  finally {

  }
}
const readFileAsync = async function (file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = () => {
      resolve(reader.result)
    }
    reader.onerror = reject
    reader.readAsBinaryString(file) // or readAsArrayBuffer?
  })
}

onMounted (async () => {
  const route = useRoute()
  mapId.value = 'mapId' in route.params ? route.params.mapId : null
  mapLoading.value = true
  if (mapId.value !== null) {
    const response = (await $api.get('map/' + mapId.value)).data
    title.value = response.display_name
    zoom.value = response.zoom
    center.value = response.center
    response.regions.forEach(function (region) {
      regionMaps.value.push({display_name: region.display_name, geojson: region.geojson, geojson_str: JSON.stringify(region.geojson), key: getNextKey()})
    })
  }
  else {
    zoom.value = 0
    center.value = {lat: 0, lng: 0}
  }
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

</style>
