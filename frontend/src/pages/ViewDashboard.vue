<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />
    <div v-if="dashboardLoading">
      <q-spinner
        color="primary"
        size="2em"
        class="center"
      />
    </div>
    <div
      v-if="dashboard"
      class="row"
      style="margin-bottom: 10px"
    >
      <div class="col-3 text-h5">
        {{ dashboard.name }}
      </div>
      <div class="col-4 q-pl-sm">
        <q-checkbox
          class="float-right"
          v-model="updateDashboard"
          :label="t('dashboard.autorefresh')"
          @click="() => refreshPage()"
          left-label
        />
      </div>
      <div class="col-2 q-pl-sm">
        <q-select
          v-model="autoRefreshDashboard"
          :options="autoRefreshOptions"
          :option-label="label"
          :option-value="value"
          :label="t('dashboard.updatetimetotal')"
          :disable="!updateDashboard"
          dense
          outlined
        />
      </div>
      <div class="col-2 q-pl-sm">
        <q-input
          outlined
          :label="t(timeLeft)"
          disable
          dense
        />
      </div>
    </div>
    <div
      v-if="dashboard"
      class="row"
      style="margin-bottom: 10px"
    >
      <div class="col-5 q-pl-sm">
        <q-checkbox
          class="float-right"
          left-label
          v-model="overrideDate"
          :label="t('dashboard.overrideDate')"
        />
      </div>
      <div class="col-2 q-pl-sm">
        <q-input
          type="date"
          debounce="500"
          v-model="startDate"
          :disable="!overrideDate || lastNBack !== null"
          @update:model-value="setStartDateModified()"
          dense
          clearable
          outlined
        />
      </div>
      <div class="col-2 q-pl-sm">
        <q-input
          type="date"
          debounce="500"
          v-model="endDate"
          :disable="!overrideDate || lastNBack !== null"
          @update:model-value="setEndDateModified()"
          dense
          clearable
          outlined
        />
      </div>
      <div class="col-2 q-pl-sm">
        <q-select
          :label="t('common.lastNBack')"
          :options="lastNBackOptions"
          v-model="lastNBack"
          :disable="!overrideDate || !startDate || !endDate"
          clearable
          @update:model-value="setDataModified()"
          dense
          outlined
        />
      </div>
      <div class="col-1 q-pl-sm">
        <q-btn
          class="float-left"
          color="primary"
          :label="$t('common.apply')"
          text-color="white"
          :disable="!overrideDate || !dataModified"
          @click="applyDateChanges()"
        />
      </div>
    </div>
    <!-- eslint-disable -->
    <grid-layout
      v-if="dashboard && dashboard.visualizations"
      v-model:layout="dashboard.visualizations"
      :col-num="12"
      :row-height="30"
      :isResizable="false"
      :isDraggable="false"
      :containerWidth="1"
      :colNum="dashboard.colNum"
    >
      <template #default="{ gridItemProps }">
        <grid-item
            v-for="item in dashboard.visualizations"
            :key="item.i"
            v-bind="gridItemProps"
            :x="item.x"
            :y="item.y"
            :w="item.w"
            :h="item.h"
            :i="item.i"
        >
        <q-card class="my-card" v-if="userCanSeeVisualization(item.visualization)">
            <div class="row">
              <div class="col-6">
                <q-item>
                  <q-item-section>
                    <q-item-label>{{ item.visualization.visualization_name }}</q-item-label>
                    <!-- <q-item-label caption>Visualization</q-item-label> -->
                  </q-item-section>
                </q-item>
              </div>
              <div class="col-5">
              </div>
            </div>
            <combined-visualization-widget class="visualization" :visualization="item.visualization" :start-date="selectedStartDate" :end-date="selectedEndDate"/>
          </q-card>
          <q-card class="my-card" v-else>
                <q-banner
                  class="text-white bg-red"
                >
                  {{ t('common.unauthorized') }}
                </q-banner>
          </q-card>
        </grid-item>
      </template>
    </grid-layout>
  </q-page>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { GridLayout, GridItem } from 'vue3-drr-grid-layout'
import 'vue3-drr-grid-layout/dist/style.css'
import { useI18n } from 'vue-i18n'
import {ref, onMounted, watch} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {convertLastNBack, getLastNBackOptions} from "src/composables/visualization";
import { useVisualizationUIStore } from "stores/visualization-ui"

import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'

import {getRequest} from "boot/axios";
import CombinedVisualizationWidget from "components/visualization/CombinedVisualizationWidget.vue";
import moment from "moment";

const { t } = useI18n()
const router = useRouter()

useVisualizationUIStore().$reset()
const { checkUserAccess } = useVisualizationUIStore()
const { visualizations } = storeToRefs(useVisualizationUIStore())

const dashboard = ref({})
const dashboardLoading = ref(false)
const lastNBackOptions = getLastNBackOptions()
const overrideDate = ref(false)
const lastNBack = ref(null)
const startDate = ref(null)
const endDate = ref(null)
const selectedStartDate = ref(null)
const selectedEndDate = ref(null)
const dataModified = ref(false)
const updateDashboard = ref(false)
const autoRefreshDashboard = ref(null)
const defaultTime = ref(null)

const timestampString = new Date().toLocaleTimeString().toString()
const timeLeft = ref(t("dashboard.lastupdated") + timestampString)

const autoRefreshOptions = [
  {label: t("dashboard.oneminute"), value: 60000},
  {label: t("dashboard.fiveminutes"), value: 300000},
  {label: t("dashboard.thirtyminutes"), value: 1800000},
  {label: t("dashboard.onehour"), value: 3600000},
]

let observer = new MutationObserver(function(mutations) {
  window.dispatchEvent(new Event('resize'))
})

const applyDateChanges = function () {
  if (lastNBack.value) {
    selectedStartDate.value = convertLastNBack(lastNBack.value).value
    selectedEndDate.value = null
  }
  else {
    selectedStartDate.value = startDate.value;
    selectedEndDate.value = endDate.value;
  }
  dataModified.value = false
}
const resetDateChanges = function () {
  selectedStartDate.value = null;
  selectedEndDate.value = null;
}

const setStartDateModified = function () {

  setDataModified()

  // If end date is set, make sure it's after start date.
  if (endDate.value) {
    const momentStartDate = moment(startDate.value, 'YYYY-MM-DD')
    const momentEndDate = moment(endDate.value, 'YYYY-MM-DD')

    // Add one day
    if (momentEndDate <= momentStartDate) {
      endDate.value = momentStartDate.add(1,"day").format('YYYY-MM-DD')
    }
  }
}

const setEndDateModified = function () {

  setDataModified()

  // If start date is set, make sure it's before end date.
  if (startDate.value) {
    const momentStartDate = moment(startDate.value, 'YYYY-MM-DD')
    const momentEndDate = moment(endDate.value, 'YYYY-MM-DD')

    // Add one day
    if (momentStartDate >= momentEndDate) {
      startDate.value = momentEndDate.subtract(1,"day").format('YYYY-MM-DD')
    }
  }
}

const setDataModified = function () {
  dataModified.value = true
}

const userCanSeeVisualization = function (visualization) {
  return (visualizations.value.map((v) => { return v.id }).includes(visualization.id))
}

watch(autoRefreshDashboard, () => {
  if (updateDashboard.value === true) {
    setInterval(() => {
      window.location.reload(); // Reloads the current page
    }, autoRefreshOptions.value)
  }
  else
    timeLeft.value = defaultTime.value

});

watch(overrideDate, () => {
  if (overrideDate.value === true) {
    applyDateChanges()
  }
  else {
    resetDateChanges()
  }
});

onMounted(async () => {
  const route = useRoute()
  const dashboardId = route.params.dashboardId
  dashboardLoading.value = true
  const d = (await getRequest('dashboard/' + dashboardId)).data
  dashboard.value.id = d.id
  dashboard.value.name = d.name
  dashboard.value.visualizations = d.visualizations
  dashboard.value.colNum = d.colNum

  for (let visualization of dashboard.value.visualizations) {
    checkUserAccess(visualization.visualization.id)
  }

  dashboardLoading.value = false
})

</script>

<style>
.my-card {
  height: 100%;
  width: 100%;
}
.visualization {
  height: 80%;
  display: flex;
  flex-direction: column;
}
</style>
