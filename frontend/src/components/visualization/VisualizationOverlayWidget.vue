<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <div style="padding:5px">
    <div v-if="validConfigs && dataSetLoading">
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
    <q-banner
      v-if="configErrorMessage"
      class="bg-warning"
    >
      {{ configErrorMessage }}
    </q-banner>

    <div
      class="visualization"
      v-if="validConfigs && !dataSetLoading && !error"
    >
      <div>
        <VuePlotly
          :data="plotData"
          :layout="plotLayout"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import {useRouter} from 'vue-router'
import {ref, onMounted, defineProps, toRaw, watch, computed} from 'vue'
import {useI18n} from 'vue-i18n'
import {VuePlotly} from 'vue3-plotly'
import debug from 'debug'
import {query} from "src/composables/dataset"
import {convertLastNBack, overrideDate} from "src/composables/visualization"
import {debounce} from "quasar";

const vizLogger = debug('vims:visualizationWidget')

// Local Variables
const {t} = useI18n()
const router = useRouter()
const plotLayout = ref({
})

const props = defineProps({
  configs: {
    type: Array,
    default: null
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

// Update display when configs change.  Do deep watch so that changes inside the object register
watch(props.configs, (newValue, _oldValue) => {
  updateDebounce()
}, {deep: true});

watch(() => props.startDate, () => {

  let updateNeeded = false;
  // Only need to update if we have a date field set to override
  props.configs.forEach(config => {
    if (config.date_field) {
      updateNeeded = true
    }
  })
  if (updateNeeded) {
    updateDebounce()
  }
});

watch(() => props.endDate, () => {
  let updateNeeded = false;
  // Only need to update if we have a date field set to override
  props.configs.forEach(config => {
    if (config.date_field) {
      updateNeeded = true
    }
  })
  if (updateNeeded) {
    updateDebounce()
  }
});

// Refs
const plotData = ref([])
const dataSetLoading = ref(true);
const error = ref(null)

// Build up a string of any configuration error messages.
const configErrorMessage = computed ( () => {
  let errorMessages = []
  if (!props.configs || !props.configs.length > 0) {
    errorMessages.push(t('visualization.error.noValidConfigurations'))
  }
  else {
    let configNum = 1
    for (const config of props.configs) {
      if (!config.dataset_id ) {
        errorMessages.push(t('visualization.series') + " " + configNum +  " - " + t('visualization.error.noDatasetSelected'))
      }
      else {
        if (config.visualization_type !== 'line' && config.visualization_type !== 'bar') {
          errorMessages.push(t('visualization.series') + " " + configNum + " - " + t('visualization.error.notSupportedType') + " : " + config.visualization_type)
        }
        // No group by option is set.
        if (!config?.visualization_options?.groupBy) {
          errorMessages.push(t('visualization.series') + " " + configNum + " - " + t('visualization.error.noGroupBySelected'))
        }
        // Aggregate function is set, not equal to 'rows' and a Y field is not set.
        if (config?.visualization_options?.aggregateFunction && config.visualization_options.aggregateFunction !== 'rows' && !config.visualization_options.aggregateField) {
          errorMessages.push(t('visualization.series') + " " + configNum + " - " + t('visualization.error.noAggregateFieldSelected'))
        }
      }
      configNum++
    }
  }
  return errorMessages.join(", ");
})

// Configs are valid if there are no configuration error messages
const validConfigs = computed ( () => {
  return configErrorMessage.value.length === 0
})

// Functions
const update = async function () {

  if (validConfigs.value) {

    // Reset plot layout
    plotLayout.value = {
      height: 0,
      width: 0,
      autosize: true,
      xaxis: {domain: [0, 1]},
    }

    dataSetLoading.value = true;
    error.value = null
    plotData.value = [];
    let configNum = 1
    let isOverlay = false
    let numSeparateYAxis = 0

    // Set some base config values if a bar chart is set.
    for (const config of props.configs) {

      if (config.visualization_options.separate_yaxis) {
        numSeparateYAxis++
      }
      if (config.visualization_type === 'bar') {

        plotLayout.value.barmode = config.visualization_options.stacked ? 'stack' : 'group'
        if (config.visualization_options.normalized) {
          plotLayout.value.barnorm = 'percent'
        }

        // Things are going to overlay a  bar chart; might need to make them more obvious.
        isOverlay = true;
      }
    }

    // Adjust the x-domain so that we don't overlap when we have a bunch of separate axes
    if (numSeparateYAxis > 0) {
      plotLayout.value.xaxis =  {domain: [0, 1 - (numSeparateYAxis * .05)]}
    }

    let yAxisOffset = 0.05;

    for (const config of props.configs) {

      const seriesName = config.visualization_options.yaxis_title ? config.visualization_options.yaxis_title : "Series " + configNum;

      if (configNum === 1) {
        plotLayout.value.yaxis = {
          title: seriesName,
          width: 1,
        }
      }
      else if (config.visualization_options.separate_yaxis) {

        plotLayout.value['yaxis' + configNum] = {
          title: seriesName,
          anchor: 'free',
          overlaying: 'y',
          side: 'right',
          position: 1 - yAxisOffset
        }
        yAxisOffset += 0.05;
      }
      let seriesData = null;
      if (config.visualization_type === 'line') {
        seriesData = await getLinePlotData(config, configNum, seriesName, isOverlay)
      }
      else if (config.visualization_type === 'bar') {
        seriesData = await getBarPlotData(config, configNum, seriesName)
      }
      // Could be multiple if it's a stratification
      for (const data of seriesData) {
        plotData.value.push(data)
      }
      configNum++
    }
    dataSetLoading.value = false;
  }
}

const updateDebounce = debounce(update, 500)


const getLinePlotData = async function (lineConfig, configNum, name, isOverlay) {

  let config = overrideDate(convertLastNBack(lineConfig), props.startDate, props.endDate)

  let linePlotData = []

  if (config.visualization_options.groupBy && config.visualization_options.aggregateFunction
      && (config.visualization_options.aggregateFunction === 'rows' || config.visualization_options.aggregateField)) {

    config.dataset_filtered_shared_fields = [config.visualization_options.groupBy, config.visualization_options.aggregateField]

    const queryOpts = {
      querySortBy: config.visualization_options.groupBy,
      queryDescending: false,
      queryRowsPerPage: null,
      queryPage: 1,
      queryGroupBy: (config.visualization_options.stratification ? [config.visualization_options.groupBy, config.visualization_options.stratification] : config.visualization_options.groupBy),
      queryAggregateField: config.visualization_options.aggregateField,
      queryAggregateFunction: config.visualization_options.aggregateFunction
    }

    try {
      const responseData = await query(getFormattedQuery(config), queryOpts, config.dataset_id);
      let rows = responseData.data[0].values;

      if (config.visualization_options['stratification']) {
        let plotData = {}

        rows.forEach(row => {
          const stratVal = row[config.visualization_options['stratification']]

          if (!(stratVal in plotData)) {
            plotData[stratVal] = {
              x: [],
              y: [],
              type: 'scatter',
              mode: 'lines',
              line: {
                width: isOverlay ? 3 : 2,
              },
              name: stratVal ? stratVal : 'null'
            }

            if (configNum > 1 && config.visualization_options.separate_yaxis) {
              plotData[stratVal].yaxis = 'y' + configNum;
            }
          }

          plotData[stratVal].x.push(row[config.visualization_options.groupBy])
          plotData[stratVal].y.push(row[queryOpts.queryAggregateFunction])
        })
        linePlotData = Object.values(plotData)
      }
      // Non stratified
      else {
        linePlotData = [
          {
            x: rows.map(res => res[queryOpts.queryGroupBy]),
            y: rows.map(res => res[queryOpts.queryAggregateFunction]),
            type: 'scatter',
            mode: 'lines',
            line: {
              width: isOverlay ? 4 : 2,
            },
            name: name
          }
        ]
        if (configNum > 1 && config.visualization_options.separate_yaxis) {
          linePlotData[0].yaxis = 'y' + configNum;
        }
      }
    }
    // Set the error message
    catch (e) {
      vizLogger(e)
      setErrorMessage(e)
    }
    return linePlotData;
  }
}

const getBarPlotData = async function (barConfig, configNum, name) {

  let config = overrideDate(convertLastNBack(barConfig), props.startDate, props.endDate)

  let barPlotData = []

  if (config.visualization_options['groupBy'] &&
      config.visualization_options['aggregateFunction'] &&
      (config.visualization_options['aggregateFunction'] === 'rows' || config.visualization_options['aggregateField'])
  ) {

    config.dataset_filtered_shared_fields = [config.visualization_options['groupBy'], config.visualization_options['aggregateField']]
    const queryOpts = {
      querySortBy: config.visualization_options['groupBy'],
      queryDescending: false,
      queryRowsPerPage: null,
      queryPage: 1,
      queryGroupBy: (config.visualization_options.stratification ? [config.visualization_options.groupBy, config.visualization_options.stratification] : config.visualization_options.groupBy),
      queryAggregateField: config.visualization_options['aggregateField'],
      queryAggregateFunction: config.visualization_options['aggregateFunction']
    }

    try {
      const responseData = await query(getFormattedQuery(config), queryOpts, config.dataset_id)
      let rows = responseData.data[0].values

      if (config.visualization_options['stratification']) {
        let plotData = {}

        rows.forEach(row => {
          const stratVal = row[config.visualization_options['stratification']]

          if (!(stratVal in plotData)) {
            plotData[stratVal] = {
              x: [],
              y: [],
              type: 'bar',
              name: stratVal ? stratVal : 'null'
            }

            if (configNum > 1 && config.visualization_options.separate_yaxis) {
              plotData[stratVal].yaxis = 'y' + configNum;
            }
          }

          plotData[stratVal].x.push(row[config.visualization_options.groupBy])
          plotData[stratVal].y.push(row[queryOpts.queryAggregateFunction])
        })
        barPlotData = Object.values(plotData)
      }
      else {
        barPlotData.push({
          x: rows.map(res => res[queryOpts.queryGroupBy]),
          y: rows.map(res => res[queryOpts.queryAggregateFunction]),
          type: 'bar',
          name: name
        })
        if (configNum > 1 && config.visualization_options.separate_yaxis) {
          barPlotData[0].yaxis = 'y' + configNum;
        }
      }
    }
    // Set the error message
    catch (e) {
      vizLogger(e)
      setErrorMessage(e)
    }
  }
  return barPlotData
}

const setErrorMessage = function(e) {
  if (e.response && e.response.data && e.response.data.detail) {
    error.value = e.response.data.detail;
  }
  else {
    error.value = e.message;
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

onMounted(async () => {
  await update()
})

</script>

<style scoped>
</style>
