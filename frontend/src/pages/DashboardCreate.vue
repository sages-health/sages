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
      class="row"
      v-if="dashboard"
    >
      <div class="col-1 btn-container">
        <q-btn-dropdown
          :label="t('common.add')"
          color="primary"
          text-color="white"
        >
          <q-list>
            <q-item
              v-for="viz in availableVisualizations"
              :key="viz.id"
              clickable
              v-close-popup
              @click="addViz(viz)"
            >
              <q-item-section>
                <q-item-label>{{ viz.visualization_name }}</q-item-label>
                <q-item-label caption>
                  {{ viz.visualization_type }}
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </div>
      <div class="col-4 q-pl-sm">
        <q-input
          v-model="dashboard.name"
          :label="$t('common.name')"
        />
      </div>
      <div class="col-3" />
      <div class="col-4 edit-btn-container">
        <q-btn-dropdown
          class="save-btn"
          split
          color="primary"
          :label="$t('common.save')"
          @click="save"
          :icon="fasFloppyDisk"
          :disable="!dashboard.name"
        >
          <q-list>
            <q-item
              :disable="!dashboard.name"
              clickable
              v-close-popup
              @click="saveAsNew"
            >
              <q-item-section>
                <q-item-label>{{ $t('common.saveAsNew') }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
        <q-btn
          class="cancel-btn"
          :label="t('common.cancel')"
          size="md"
          :icon="fasXmark"
          @click="cancel"
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
      :containerWidth="1"
      :colNum="numColumns"
    >
      <template #default="{ gridItemProps }">
        <!-- | gridItemProps props from GridLayout | -->
        <!--breakpointCols: props.cols-->
        <!--colNum: props.colNum-->
        <!--containerWidth: width.value-->
        <!--isDraggable: props.isDraggable-->
        <!--isResizable: props.isResizable-->
        <!--lastBreakpoint: lastBreakpoint.value-->
        <!--margin: props.margin-->
        <!--maxRows: props.maxRows-->
        <!--responsive: props.responsive-->
        <!--rowHeight: props.rowHeight-->
        <!--useCssTransforms: props.useCssTransforms-->
        <!--width: width.value-->
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
          <q-card class="my-card">
            <div class="row">
              <div class="col-6">
                <q-item>
                  <q-item-section>
                    <q-item-label>{{ item.visualization.visualization_name }}</q-item-label>
                    <!-- <q-item-label caption>Visualization</q-item-label> -->
                  </q-item-section>
                </q-item>
              </div>

              <div class="col-3">
              </div>
              <div class="col-3">
                <q-btn
                    class="float-right"
                    :icon="fasCircleXmark"
                    dense
                    round
                    flat
                    @click="removeViz(item.i)"
                />
                <q-btn v-if="item.w != numColumns"
                    class="float-right"
                    :icon="fasCircleArrowRight"
                    dense
                    round
                    flat
                    @click="increaseSize(item)"
                />
                <q-btn v-if="item.w > 1"
                       class="float-right"
                       :icon="fasCircleArrowLeft"
                       dense
                       round
                       flat
                       @click="decreaseSize(item)"
                />
              </div>
            </div>
            <combined-visualization-widget class="visualization" :visualization="item.visualization" />
          </q-card>
        </grid-item>
      </template>
    </grid-layout>
    <!-- eslint-enable -->
  </q-page>
</template>

<script setup>
import { GridLayout, GridItem } from 'vue3-drr-grid-layout'
import 'vue3-drr-grid-layout/dist/style.css'
import { useI18n } from 'vue-i18n'
import {ref, onMounted, onUpdated, computed} from 'vue'
import { useRoute, useRouter } from 'vue-router'

import CombinedVisualizationWidget from 'components/visualization/CombinedVisualizationWidget.vue'

import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import { fasCircleXmark, fasFloppyDisk, fasXmark , fasCircleArrowRight, fasCircleArrowLeft} from '@quasar/extras/fontawesome-v6'

import {getRequest, postRequest, putRequest} from "boot/axios";
import {debounce} from "quasar";

const { t } = useI18n()
const router = useRouter()

const visualizations = ref([])
const dashboard = ref({})
const dashboardLoading = ref(false)
const numColumns = 4

/**
 * All visualizations that have not already been added to the dashboard.
 */
const availableVisualizations = computed( () => {
  const usedVisualizations = {}
  dashboard.value.visualizations.forEach(v => {
    usedVisualizations[v.visualization.id] = 1
  })
  return visualizations.value.filter(v => !usedVisualizations.hasOwnProperty(v.id) )
})

/**
 * Add a visualization to the dashboard, and do a simple calculation to see where it should go.
 * Need to debounce since adding this is modifying the dropdown list.
 *
 * @param vis the visualization to add to the dashboard.
 */
const addViz = debounce((viz) => {

  // Find the largest i and y; can't just go by length because items can be deleted in the middle of the list which
  // would cause the next vis added to "share" an i value with a previous visualization.
  // TODO: Should we modify the i values of visualizations when we delete?  What does i do?
  let maxIndex = 0;
  let maxY = 0;
  dashboard.value.visualizations.forEach(v => {
    maxIndex = v.i > maxIndex ? v.i : maxIndex
    maxY = v.y > maxY ? v.y : maxY
  })

  // Calculate total width
  let totalWidth = 0;
  dashboard.value.visualizations.forEach(v => totalWidth += v.w)

  dashboard.value.visualizations.push(  { x: totalWidth % numColumns, y: maxY, w: 1, h: 16, i: maxIndex + 1, visualization: viz })
}, 10);

/**
 * Remove a visualization from the dashbaord.
 * @param i the index of the visualziation to remove.
 */
function removeViz(i) {
  dashboard.value.visualizations = dashboard.value.visualizations.filter(function(e) { return e.i !== i })
}

/**
 * Make the widget take the entire width of the grid.  This code will go away when we fix all of the grid rendering issues.
 * @param item the visualization that's being made full width.
 */
function increaseSize(item) {

  // Do I need to add a row?
  let needToAddRow = false

  dashboard.value.visualizations.forEach(v => {
    if (v.i !== item.i && v.y === item.y) {
      needToAddRow = true
    }
  })
  if (needToAddRow) {
    dashboard.value.visualizations.forEach(v => {
      if (v.i != item.i && v.y >= item.y) {
        v.y = v.y + 16
      }
    })
  }
  item.w = item.w + 1
  item.x = 0
}

/**
 * Make the widget take half of the available display. This code will go away when we fix all of the grid rendering issues.
 * @param item the visualization that's being made half width.
 */
function decreaseSize(item) {
  if (item.w > 1) {
    item.w = item.w -1
  }
}

async function save() {
  if (dashboard.value.id === null) {
    var newDashboard = await postRequest('dashboard', dashboard.value)
    dashboard.value.id = newDashboard.data.id;
  }
  else {
    await putRequest('dashboard/' + dashboard.value.id, dashboard.value)
  }
}

async function saveAsNew() {
  dashboard.value.id = null
  await save()
}

const cancel = async function () {
  await router.push('/dashboard')
}

let observer = new MutationObserver(function(mutations) {
  window.dispatchEvent(new Event('resize'))
})

onMounted(async () => {

  const route = useRoute()
  const dashboardId = 'dashboardId' in route.params ? route.params.dashboardId : null
  dashboardLoading.value = true
  if (dashboardId !== null) {
    const d = (await getRequest('dashboard/' + dashboardId)).data
    dashboard.value.id = d.id
    dashboard.value.name = d.name
    dashboard.value.visualizations = d.visualizations
  }
  else {
    dashboard.value.id = null
    dashboard.value.name = null
    dashboard.value.visualizations = []
  }
  dashboard.value.colNum = numColumns

  visualizations.value = (await getRequest('visualization')).data
  dashboardLoading.value = false
})

// to handle clearing dashboard upon clicking 'new dashboard' again
onUpdated (async () => {
  dashboard.value.visualizations = []
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

.btn-container {
  display: flex;
  justify-content: left;
}

.edit-btn-container {
  display: flex;
  justify-content: right;
}

.save-btn {
  margin-right: 5px;
}
.cancel-btn {
  width: 150px;
  margin-left: 5px;
}

</style>
