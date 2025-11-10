<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <div style="padding:5px">
    <div v-if="dataSetLoading">
      <q-spinner
        color="primary"
        size="2em"
        class="center"
      />
    </div>
    <q-banner
      v-if="error"
      class="text-white bg-red"
    >
      {{ error }}
    </q-banner>
    <div v-if="config.visualization_type === 'table'">
      <!-- eslint-disable -->
      <q-table
          :title="`${t('common.rowCount')}: ${queryTotal}`"
          :columns="columns"
          :loading="tableLoading"
          :rows="queryRows"
          v-model:pagination="pagination"
          :pagination="pagination"
          @request="updateTable"
          :no-data-label="$t('common.noData')"
          :rows-per-page-options="[5, 10, 25, 50]"
      />
      <!-- eslint-enable -->
    </div>

    <div
      class="visualization"
      v-if="config.visualization_type === 'line' && !dataSetLoading"
    >
      <div v-if="linePlotData[0]">
        <VuePlotly
          :data="linePlotData"
          :layout="plotLayout"
        />
      </div>
    </div>

    <div
      class="visualization"
      v-if="config.visualization_type === 'bar' && !dataSetLoading"
    >
      <div v-if="barPlotData[0]">
        <VuePlotly
          :data="barPlotData"
          :layout="plotLayout"
        />
      </div>
    </div>
    <div
      class="visualization"
      v-if="config.visualization_type === 'pie' && !dataSetLoading"
    >
      <div v-if="piePlotData[0]">
        <VuePlotly
          :data="piePlotData"
          :layout="plotLayout"
        />
      </div>
    </div>
    <div
      class="visualization"
      v-show="config.visualization_type === 'pivot' && !dataSetLoading"
    >
      <div
        v-once
        :id="'pivot-' + uniqueId"
        class="pivot"
      />
    </div>
    <div
      class="visualization"
      v-if="config.visualization_type === 'map' && !dataSetLoading && !mapLoading"
    >
      <div
        class="col-12 q-pr-md"
        id="map-container"
      >
        <l-map
          :loading="mapLoading"
          v-if="mapCenter.hasOwnProperty(props.config.visualization_options.regionMapId)"
          :key="props.config.visualization_options.regionMapId"
          id="map"
          :use-global-leaflet="false"
          :zoom="mapZoom[props.config.visualization_options.regionMapId]"
          :center="mapCenter[props.config.visualization_options.regionMapId]"
        >
          <l-geo-json
            :geojson="mapGeoJSONs[props.config.visualization_options.regionMapId]"
            :options="mapOptions"
            :options-style="mapStyle"
          />
          <l-control>
            <div
              v-if="mapHighlightedRegion !== undefined"
              class="control"
            >
              <b>{{ mapHighlightedRegion.title }}</b>
              <br />
              {{ mapHighlightedRegion.count }}
            </div>
          </l-control>
          <l-control position="bottomright">
            <div
              v-for="bin in mapBins"
              :key="bin.id.toString() + '-bin'"
              class="row"
            >
              <div
                :key="bin.id.toString() + '-bin-box'"
                :style="bin.style"
                class="bin-box"
              />
              <div
                :key="bin.id.toString() + '-bin-text'"
                class="bin-text control"
              >
                {{ bin.text }}
              </div>
            </div>
          </l-control>
        </l-map>
      </div>
    </div>
  </div>
</template>

<script setup>
import {useRouter} from 'vue-router'
import {ref, onMounted, defineProps, toRaw, nextTick, watch, computed} from 'vue'
import {debounce} from 'quasar'
import {useI18n} from 'vue-i18n'
import {VuePlotly} from 'vue3-plotly'
import debug from 'debug'
import {scaleLinear} from 'd3-scale'
import {interpolateReds} from 'd3-scale-chromatic'
import {uuidv4} from "src/composables/utilities"

import jQuery from '../../plugins/jquery'

import 'jquery-ui/dist/jquery-ui.min'

import 'pivottable/dist/pivot.min.css'
import 'jquery-ui/dist/themes/base/jquery-ui.min.css'
import { $api, postRequest } from "boot/axios";
import { LMap, LGeoJson, LControl } from "@vue-leaflet/vue-leaflet"
import "leaflet/dist/leaflet.css"
import {floor} from "lodash";
import {convertLastNBack, overrideDate} from "src/composables/visualization";
import {isActive} from "src/composables/dataset";

const vizLogger = debug('vims:visualizationWidget')

// Local Variables
const {t} = useI18n()
const router = useRouter()

const plotLayout = ref({
  height: 0,
  width: 0,
  autosize: true
})

const props = defineProps({
  config: Object,
  viewOnly: {
    type: Boolean,
    default: true
  },
  startDate: String,
  endDate: String
})

watch(props.config, (newValue, oldValue) => {
  if (newValue) {
    updateTabPanelDebounce()
  }
});

watch(() => props.startDate, () => {
  // Only need to update if we have a date field set to override
  if (props.config.date_field) {
    updateTabPanelDebounce()
  }
});

watch(() => props.endDate, () => {
  // Only need to update if we have a date field set to override
  if (props.config.date_field) {
    updateTabPanelDebounce()
  }
});

// Refs
const linePlotData = ref([])
const barPlotData = ref([])
const piePlotData = ref([])
const mapData = ref({})
const mapGeoJSONs = ref([])
const mapZoom = ref({})
const mapCenter = ref({})
const mapRegionMapping = ref({})
const mapHighlightedRegion = ref(undefined)
const mapBins = ref([])

let dataSetLoading = ref(false)
let tableLoading = ref(false)
const mapLoading = ref(false)
let tableVisualization = ref(null)
let queryOpts = ref([])
let queryTotal = ref(0)
let queryRows = ref([])
let columns = ref([])
let uniqueId = uuidv4()

let pagination = ref({
  page: 1,
  rowsPerPage: 8,
  rowsNumber: queryTotal.value,
  sortBy: null,
  descending: false,
})

const error = ref(null)

const mapOptions = computed ( () =>{
  return {onEachFeature: onEachFeature}
})

const getRows = async function () {
  try {
    await query(getFormattedQuery(tableVisualization.value), queryOpts.value, tableVisualization.value.dataset_id)
  }
  catch (e) {
    queryTotal.value = 0
    queryRows.value = []
    error.value = e.message;
    vizLogger(e)
  }
}

const getPivotRows = async function (visualization) {
  try {
    dataSetLoading.value = true
    await query(getFormattedQuery(visualization), queryOpts.value, visualization.dataset_id)
  }
  catch (e) {
    queryTotal.value = 0
    queryRows.value = []
    error.value = e.message;
    vizLogger(e)
  }
  finally {
    dataSetLoading.value = false
  }
}

// Functions
const updateTabPanel = async function () {
  if (props.config.visualization_type === 'table') {
    await updateTable()
  }
  else if (props.config.visualization_type === 'line') {
    await updateLinePlot()
  }
  else if (props.config.visualization_type === 'bar') {
    await updateBarPlot()
  }
  else if (props.config.visualization_type === 'pie') {
    await updatePiePlot()
  }
  else if (props.config.visualization_type === 'pivot') {
    await nextTick()
    await loadPivotTable()
  }
  else if (props.config.visualization_type === 'map') {
    await updateMap()
  }
}
const updateTabPanelDebounce = debounce(updateTabPanel, 500)

const updateTable = async function (tableUpdate) {

  tableVisualization.value = overrideDate(convertLastNBack(props.config), props.startDate, props.endDate)

  columns.value = tableVisualization.value.visualization_options.columns.map(function (sf) {
    return {name: sf.name, label: sf.label, field: row => row[sf.name], sortable: true, align: 'left'}
  })
  if (tableUpdate) {
    pagination.value.sortBy = tableUpdate.pagination.sortBy
    pagination.value.descending = tableUpdate.pagination.descending
    pagination.value.rowsPerPage = tableUpdate.pagination.rowsPerPage
    pagination.value.page = tableUpdate.pagination.page
  }

  queryOpts.value = {
    querySortBy: pagination.value.sortBy,
    queryDescending: pagination.value.descending,
    queryRowsPerPage: pagination.value.rowsPerPage,
    queryPage: pagination.value.page
  }

  tableLoading.value = true
  error.value = null
  await getRows()
  tableLoading.value = false
}

const updateLinePlot = async function () {

  let visualization = overrideDate(convertLastNBack(props.config), props.startDate, props.endDate)
  linePlotData.value = []
  if (visualization.visualization_options['groupBy'] && visualization.visualization_options['aggregateFunction']
      && (visualization.visualization_options['aggregateFunction'] === 'rows' || visualization.visualization_options['aggregateField'])) {

    visualization.dataset_filtered_shared_fields = [visualization.visualization_options['groupBy'], visualization.visualization_options['aggregateField']]

    const queryOpts = {
      querySortBy: visualization.visualization_options['groupBy'],
      queryDescending: false,
      queryRowsPerPage: null,
      queryPage: 1,
      queryGroupBy: (visualization.visualization_options['stratification'] ?
          [visualization.visualization_options['groupBy'], visualization.visualization_options['stratification']] :
          visualization.visualization_options['groupBy']),
      queryAggregateField: visualization.visualization_options['aggregateField'],
      queryAggregateFunction: visualization.visualization_options['aggregateFunction'],
      queryTransformation: visualization.visualization_options['transformation'],
      queryTransformationGroupBy: visualization.visualization_options['groupBy'],
      queryTransformationStratification: visualization.visualization_options['stratification'],
    }

    dataSetLoading.value = true
    error.value = null
    try {
      await query(getFormattedQuery(visualization), queryOpts, visualization.dataset_id)

      if (visualization.visualization_options['stratification']) {
        let plotData = {}

        queryRows.value.forEach(row => {
          const stratVal = row[visualization.visualization_options['stratification']]

          if (!(stratVal in plotData)) {
            plotData[stratVal] = {
              x: [],
              y: [],
              type: 'scatter',
              mode: 'lines',
              name: stratVal ? stratVal : 'null'
            }
          }

          plotData[stratVal].x.push(row[visualization.visualization_options['groupBy']])
          plotData[stratVal].y.push(row[queryOpts.queryAggregateFunction])
        })

        linePlotData.value = Object.values(plotData)
      }
      // Non stratified
      else {
        linePlotData.value = [
          {
            x: queryRows.value.map(res => res[queryOpts.queryGroupBy]),
            y: queryRows.value.map(res => res[queryOpts.queryAggregateFunction]),
            type: 'scatter',
            mode: 'lines',
            showlegend: false
          }
        ]
        const detectorParams = {
          data: queryRows.value.map(res => res[queryOpts.queryAggregateFunction])
        }
        const detectionAlgorithm = visualization.visualization_options["detectionAlgorithm"]
        if (detectionAlgorithm) {
          const detectorResponse = await $api.post( 'detector/' + detectionAlgorithm, detectorParams)
          let warnings = []
          let errors = []
          if ("pValues" in detectorResponse.data) {
            errors = detectorResponse.data["pValues"].map(pValue => pValue <= 0.01? pValue : null)
            warnings = detectorResponse.data["pValues"].map(pValue => 0.01 < pValue && pValue <= 0.05? pValue : null)
          }
          else if ("earStat" in detectorResponse.data) {
            errors = detectorResponse.data["earStat"].map(pValue => pValue > 2? pValue : null)
          }
          linePlotData.value.push(
            {
              x: queryRows.value.map(res => res[queryOpts.queryGroupBy]),
              y: queryRows.value.map((res, index) => errors[index] ? res[queryOpts.queryAggregateFunction] : null),
              type: 'scatter',
              mode: 'markers',
              marker: {
                color: 'rgb(255, 0, 0)',
              },
              name: t('visualization.detectionError'),
              customdata: errors,
              hovertemplate: '(%{x}: %{y}) <br> p-value: %{customdata:.2f}',
            },
            {
              x: queryRows.value.map(res => res[queryOpts.queryGroupBy]),
              y: queryRows.value.map((res, index) => warnings[index] ? res[queryOpts.queryAggregateFunction] : null),
              type: 'scatter',
              mode: 'markers',
              marker: {
                color: 'rgb(255, 225, 0)',
              },
              name: t('visualization.detectionWarning'),
              customdata: warnings,
              hovertemplate: '(%{x}: %{y}) <br> p-value: %{customdata:.2f}',
            }
          )
        }
      }
    }
    // Set the error message
    catch (e) {
      vizLogger(e)
      error.value = e.message;
    }
    dataSetLoading.value = false
  }
}

const getFormattedQuery = function (visualization) {
  const formattedQuery = {}
  const reqs = []
  Object.values(visualization.dataset_field_requests).forEach(function (req) {
    if (Object.keys(req).length > 0) {
      reqs.push(toRaw(req))
    }
  })
  if (reqs.length > 0) {
    formattedQuery.request = {$and: reqs}
  }
  formattedQuery.projection = visualization.visualization_options.projection

  return formattedQuery
}

const updateBarPlot = async function () {
  let visualization = overrideDate(convertLastNBack(props.config), props.startDate, props.endDate)

  // Reset plot layout
  plotLayout.value = {
    height: 0,
    width: 0,
    autosize: true
  }

  // Different styles for stacked; make this configurable?
  if (visualization.visualization_options.stacked) {
    plotLayout.value.barmode = 'stack'
  }
  else {
    plotLayout.value.barmode = 'group'
  }

  if (visualization.visualization_options.normalized) {
    plotLayout.value.barnorm = 'percent'
  }

  barPlotData.value = []

  if (visualization.visualization_options['groupBy'] && visualization.visualization_options['aggregateFunction']
      && (visualization.visualization_options['aggregateFunction'] === 'rows' || visualization.visualization_options['aggregateField'])) {
    barPlotData.value = []
    visualization.dataset_filtered_shared_fields = [visualization.visualization_options['groupBy'], visualization.visualization_options['aggregateField']]

    const queryOpts = {
      querySortBy: visualization.visualization_options['groupBy'],
      queryDescending: false,
      queryRowsPerPage: null,
      queryPage: 1,
      queryGroupBy: (visualization.visualization_options.stratification ? [visualization.visualization_options.groupBy, visualization.visualization_options.stratification] : visualization.visualization_options.groupBy),
      queryAggregateField: visualization.visualization_options['aggregateField'],
      queryAggregateFunction: visualization.visualization_options['aggregateFunction']
    }

    dataSetLoading.value = true
    error.value = null
    try {
      await query(getFormattedQuery(visualization), queryOpts, visualization.dataset_id)

      if (visualization.visualization_options['stratification']) {
        let plotData = {}

        queryRows.value.forEach(row => {
          const stratVal = row[visualization.visualization_options['stratification']]

          if (!(stratVal in plotData)) {
            plotData[stratVal] = {
              x: [],
              y: [],
              type: 'bar',
              name: stratVal ? stratVal : 'null'
            }
          }

          plotData[stratVal].x.push(row[visualization.visualization_options.groupBy])
          plotData[stratVal].y.push(row[queryOpts.queryAggregateFunction])
        })
        barPlotData.value = Object.values(plotData)
      }
      else {
        barPlotData.value = [{
          x: queryRows.value.map(res => res[queryOpts.queryGroupBy]),
          y: queryRows.value.map(res => res[queryOpts.queryAggregateFunction]),
          type: 'bar',
          name: name
        }]
      }
    }
    // Set the error message
    catch (e) {
      vizLogger(e)
      error.value = e.message;
    }
    dataSetLoading.value = false
  }
}

const updatePiePlot = async function () {
  let visualization = overrideDate(convertLastNBack(props.config), props.startDate, props.endDate)

  piePlotData.value = []

  if (visualization.visualization_options['groupBy'] && visualization.visualization_options['aggregateFunction']
      && (visualization.visualization_options['aggregateFunction'] === 'rows' || visualization.visualization_options['aggregateField'])) {
    visualization.dataset_filtered_shared_fields = [visualization.visualization_options['groupBy'], visualization.visualization_options['aggregateField']]
    const queryOpts = {
      querySortBy: visualization.visualization_options['groupBy'],
      queryDescending: false,
      queryRowsPerPage: null,
      queryPage: 1,
      queryGroupBy: visualization.visualization_options['groupBy'],
      queryAggregateField: visualization.visualization_options['aggregateField'],
      queryAggregateFunction: visualization.visualization_options['aggregateFunction']
    }

    dataSetLoading.value = true
    error.value = null
    try {
      await query(getFormattedQuery(visualization), queryOpts, visualization.dataset_id)
      const ordered = queryRows.value.sort((i, j) => j[queryOpts.queryAggregateFunction] - i[queryOpts.queryAggregateFunction])
      let plotData = ordered.slice(0, visualization.visualization_options['topN'])

      if (ordered.length > visualization.visualization_options['topN']) {
        const other = ordered.slice(-1 * (ordered.length - visualization.visualization_options['topN']))
        const otherLabel = 'Other'
        const otherValue = other.map(val => Number(val[queryOpts.queryAggregateFunction])).reduce((running, next) => running + (next !== NaN? next : 0))
        plotData.push({
          [queryOpts.queryGroupBy]: otherLabel,
          [queryOpts.queryAggregateFunction]: otherValue
        })
      }

      piePlotData.value = [
        {
          labels: plotData.map(res => res[queryOpts.queryGroupBy]),
          values: plotData.map(res => res[queryOpts.queryAggregateFunction]),
          textinfo: "label+percent+value",
          insidetextorientation: "horizontal",
          automargin: true,
          type: 'pie'
        }
      ]
    }
    catch (e) {
      piePlotData.value = []
      error.value = e.message;
      vizLogger(e)
    }
    dataSetLoading.value = false
  }
}

const loadPivotTable = async function () {
  let visualization = overrideDate(convertLastNBack(props.config), props.startDate, props.endDate)

  queryOpts.value = {
    querySortBy: visualization.visualization_options['sortBy'],
    queryDescending: visualization.visualization_options['descending'],
  }
  await nextTick()
  dataSetLoading.value = true
  await getPivotRows(visualization)
  dataSetLoading.value = false

  if (props.viewOnly) {
    $('#pivot-' + uniqueId).pivot(
        queryRows.value, visualization.visualization_options.pivotOptions)
  }
  else {
    $('#pivot-' + uniqueId).pivotUI(
        queryRows.value, visualization.visualization_options.pivotOptions)
  }
}

const updateMap = async function () {
  mapLoading.value = true
  if (props.config.visualization_options.groupBy && props.config.visualization_options.regionMapId) {
    await Promise.all([fetchRegionMapping(props.config.dataset_id, props.config.visualization_options.groupBy), fetchRegionMap(props.config.visualization_options.regionMapId)])
  }
  mapLoading.value = false

  const regionMappingKey = `${props.config.dataset_id}-${props.config.visualization_options.groupBy}`
  const regionMapping = mapRegionMapping.value[regionMappingKey]

  mapData.value = {}
  let config = overrideDate(convertLastNBack(props.config), props.startDate, props.endDate)
  if (config.visualization_options['groupBy'] && config.visualization_options['aggregateFunction']
      && (config.visualization_options['aggregateFunction'] === 'rows' || config.visualization_options['aggregateField'])) {
    // Set all region mappings to base value.

    Object.values(regionMapping).forEach(function (rm) {
      mapData.value[rm] = undefined
    })
    config.dataset_filtered_shared_fields = [config.visualization_options['groupBy'], config.visualization_options['aggregateField']]
    const queryOpts = {
      querySortBy: config.visualization_options['groupBy'],
      queryDescending: false,
      queryRowsPerPage: null,
      queryPage: 1,
      queryGroupBy: config.visualization_options['groupBy'],
      queryAggregateField: config.visualization_options['aggregateField'],
      queryAggregateFunction: config.visualization_options['aggregateFunction']
    }

    dataSetLoading.value = true
    error.value = null
    try {
      await query(getFormattedQuery(config), queryOpts, config.dataset_id)

      // Sum result values that map to the same region.
      queryRows.value.forEach(function (row) {
        const key = row[config.visualization_options['groupBy']]
        const val = parseFloat(row[config.visualization_options['aggregateFunction']])
        if (regionMapping.hasOwnProperty(key) && !isNaN(val)) {
          if (mapData.value[regionMapping[key]] === undefined) {
            mapData.value[regionMapping[key]] = val
          }
          else {
            mapData.value[regionMapping[key]] += val
          }
        }
      })

      // Compute bins.
      let maxVal = Math.max(...Object.values(mapData.value).filter(x => x !== undefined))
      let minVal = Math.min(...Object.values(mapData.value).filter(x => x !== undefined))
      if (minVal === maxVal) {
        minVal = 0
      }
      const numBins = config.visualization_options['numBins']
      if (maxVal < numBins) {
        maxVal = numBins
      }
      const scale = scaleLinear().domain([minVal,maxVal]).range([0,1])
      mapBins.value = []
      if (maxVal > 0) {
        const binSize = floor((maxVal - minVal) / numBins)
        let runningMin = minVal
        for (let i = 0; i < numBins; i++) {
          if (i < numBins - 1) {
            const binVal = (i+1) * binSize + minVal
            mapBins.value.push({
              id: i,
              text: `${runningMin} - ${binVal}`,
              minVal: runningMin,
              maxVal: binVal,
              style: {
                backgroundColor: interpolateReds(scale(binVal))
              }
            })
            runningMin = binVal + 1
          }
          else {
            mapBins.value.push({
              id: i,
              text: `${runningMin} - ${maxVal}`,
              minVal: runningMin,
              maxVal: maxVal,
              style: {
                backgroundColor: interpolateReds(scale(maxVal))
              }
            })
          }
        }
      }

      // Write values into geoJSON
      mapGeoJSONs.value[props.config.visualization_options.regionMapId].forEach(function (geoJSON) {
        const regionName = geoJSON.properties.DISPLAY_NAME
        if (mapData.value.hasOwnProperty(regionName) && mapData.value[regionName] !== undefined) {
          geoJSON.properties.COUNT = mapData.value[regionName]
          let color = 'white'
          mapBins.value.forEach( function (mapBin) {
           if (mapData.value[regionName] >= mapBin.minVal && mapData.value[regionName] <= mapBin.maxVal) {
            color = mapBin.style.backgroundColor
           }
          })
          geoJSON.properties.COLOR = color
        }
        else {
          geoJSON.properties.COUNT = 'N/A'
          geoJSON.properties.COLOR = 'white'
        }
      })
    }
    catch (e) {
      mapData.value = []
      error.value = e.message;
      vizLogger(e)
    }
    dataSetLoading.value = false
  }
  else {
    // Reset geoJSON.
    if ( mapGeoJSONs.value.hasOwnProperty(props.config.visualization_options.regionMapId)) {
      mapGeoJSONs.value[props.config.visualization_options.regionMapId].forEach(function (geoJSON) {
        geoJSON.properties.COUNT = 'N/A'
        geoJSON.properties.COLOR = 'white'
      })
    }
    mapBins.value = []
  }
}

const fetchRegionMapping = async function (dataSetId, fieldName) {
  const cacheKey = `${dataSetId}-${fieldName}`
  if (!mapRegionMapping.value.hasOwnProperty(cacheKey)) {
    const response = await $api.get('dataset/' + dataSetId + '/' + fieldName + '/region_mapping')
    mapRegionMapping.value[cacheKey] = response.data
  }
}

const fetchRegionMap = async function (regionMapId) {
  const cacheKey = regionMapId
  if (!mapCenter.value.hasOwnProperty(cacheKey)) {
    const response = (await $api.get('map/' + regionMapId)).data
    mapZoom.value[cacheKey] = response.zoom
    mapCenter.value[cacheKey] = response.center
    mapGeoJSONs.value[cacheKey] = response.regions.map(x => x.geojson)
  }
}

const highlightFeature = function (e) {
   const layer = e.target
    layer.setStyle({
      weight: 3,
      fillOpacity: 1
    })
    mapHighlightedRegion.value = {title: layer.feature.properties.DISPLAY_NAME, count: layer.feature.properties.COUNT}
}
const resetHighlight = function (e) {
  const layer = e.target
  layer.setStyle({
    weight: 1,
    fillOpacity: 1.0
  })
  mapHighlightedRegion.value = undefined
}
const onEachFeature = function (feature, layer) {
  layer.on({
    mouseover: highlightFeature,
    mouseout: resetHighlight
  })
}

const mapStyle = function (feature) {
  return {
    color: '#303e4e',
    fillColor: feature.properties.COLOR,
    weight: 1,
    opacity: 1,
    dashArray: '1',
    fillOpacity: 1.0,
    radius: 1000
  }
}

const query = async function (dataSetBaseQuery, queryOpts, dataSetId) {
  let dataSetQuery = JSON.parse(JSON.stringify(dataSetBaseQuery))

  if (Object.values(dataSetQuery.projection).some(x => x === 1)) {
    if (queryOpts.queryRowsPerPage) {
      dataSetQuery.limit = queryOpts.queryRowsPerPage
    }
    if (queryOpts.queryPage && queryOpts.queryRowsPerPage) {
      dataSetQuery.offset = queryOpts.queryRowsPerPage * (queryOpts.queryPage - 1)
    }
    if (queryOpts.querySortBy !== null && dataSetQuery.projection[queryOpts.querySortBy] === 1) {
      dataSetQuery.order_by = [[queryOpts.querySortBy, queryOpts.queryDescending ? 'desc' : 'asc']]
    }

    if (queryOpts.queryGroupBy !== null
      && ((typeof queryOpts.queryGroupBy === 'string' && dataSetQuery.projection[queryOpts.queryGroupBy] === 1)
      || Array.isArray(queryOpts.queryGroupBy) && queryOpts.queryGroupBy.every((field) => dataSetQuery.projection[field] === 1))) {

      dataSetQuery.group_by = {
        fields: Array.isArray(queryOpts.queryGroupBy) ? queryOpts.queryGroupBy : [queryOpts.queryGroupBy],
        aggregators: {
          [queryOpts.queryAggregateFunction]: {
            field: queryOpts.queryAggregateField,
            'function': queryOpts.queryAggregateFunction === 'rows' ? 'count' : queryOpts.queryAggregateFunction
          }
        }
      }
      delete dataSetQuery.projection
    }
    if (queryOpts.aggregate){
      dataSetQuery.aggregate = queryOpts.aggregate
    }

    if (queryOpts.queryTransformation) {
      dataSetQuery.transformations = {
        transformation_type: queryOpts.queryTransformation.toLowerCase(),
        transformation_columns: [queryOpts.queryTransformationGroupBy],
        drop_existing: true,
        aggregate: {
          group_by: {
            field: [
              `${queryOpts.queryTransformation.toLowerCase()}_${queryOpts.queryTransformationGroupBy}`,
              ...(queryOpts.queryTransformationStratification != null? [queryOpts.queryTransformationStratification] : [])],
            aggregators: {
              count: {
                field: queryOpts.queryAggregateFunction,
                function: 'sum'
              }
            }
          }
        }
      }
    }

    if (!await isActive(dataSetId)) {
      return {
        "data":[{
          "error": "inactive",
          "total": 0,
          "values": []
        }]
      }
    }

    const response = await postRequest('dataset/' + dataSetId + '/query', dataSetQuery)
    pagination.value.rowsNumber = response.data[0].total
    queryRows.value = response.data[0].values
    queryTotal.value = response.data[0].total
  }
}

onMounted(async () => {
  await updateTabPanel()
})

</script>

<style scoped>
.pivot {
  overflow: scroll;
  max-height: 500px;
}
#map-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}
#map {
  min-height: 500px;
}
.bin-box {
  float: left;
  height: 18px;
  width: 18px;
  margin: 0 6px;
  opacity: 1;
}
.bin-text {
  float: left;
  margin-right: 6px;
}
.control {
    font: 14px/16px Arial, Helvetica, sans-serif;
  }
</style>
