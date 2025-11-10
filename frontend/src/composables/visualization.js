/*
*  Copyright (c) 2013-2025. The Johns Hopkins University Applied Physics Laboratory LLC
*
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* NO WARRANTY.   THIS MATERIAL IS PROVIDED "AS IS."  JHU/APL DISCLAIMS ALL
* WARRANTIES IN THE MATERIAL, WHETHER EXPRESS OR IMPLIED, INCLUDING (BUT NOT
* LIMITED TO) ANY AND ALL IMPLIED WARRANTIES OF PERFORMANCE,
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF
* INTELLECTUAL PROPERTY RIGHTS. ANY USER OF THE MATERIAL ASSUMES THE ENTIRE
* RISK AND LIABILITY FOR USING THE MATERIAL.  IN NO EVENT SHALL JHU/APL BE
* LIABLE TO ANY USER OF THE MATERIAL FOR ANY ACTUAL, INDIRECT,
* CONSEQUENTIAL, SPECIAL OR OTHER DAMAGES ARISING FROM THE USE OF, OR
* INABILITY TO USE, THE MATERIAL, INCLUDING, BUT NOT LIMITED TO, ANY DAMAGES
* FOR LOST PROFITS.
 */

import {useI18n} from 'vue-i18n'
import moment from "moment/moment";

// The ES compiler doesn't like it when I call getLastNBackOptions in functions, so I'm creating
// a local copy.  Yuck.
let lastNOptions = [
  'LAST_30_DAYS_BACK',
  'LAST_60_DAYS_BACK',
  'LAST_90_DAYS_BACK',
  'LAST_180_DAYS_BACK',
  'LAST_365_DAYS_BACK'
];

/**
 * Default visualization creation function, based on current state.  Filters/dataset values might
 * already have been set.
 *
 * @returns default base visualization object.
 */
export function getDefaultBaseVisualization(dataSet, filters, sharedFields) {
  return {
    dataset_id: dataSet ? dataSet.id : null,
    dataset_filtered_shared_fields: [],
    dataset_field_requests: filters,
    date_field: dataSet && dataSet.date_field ? dataSet.date_field : null,
    visualization_options: {
      projection: sharedFields.reduce(function (map, sf) {
        map[sf] = 1;
        return map;
      }, {})
    }
  }
}

/**
 * Extract the visualization filters from the config
 * @param config the config for the visualization
 * @param filters the filters hash to set
 * @param filterFields the filter fields array to populate
 */
export function extractVisualizationFilters (config, filters, filterFields) {

  // Get the field requests.
  if (config.dataset_field_requests) {
    Object.keys(config.dataset_field_requests).forEach(fieldName => {
      filters[fieldName] = config.dataset_field_requests[fieldName]
    })
  }

  // Get the fields we're filtering on in the visualization.
  if (config.dataset_filtered_shared_fields) {
    config.dataset_filtered_shared_fields.forEach(sharedField => {
      filterFields.push(sharedField)
    })
  }
}

export function overrideDate (config, startDate, endDate) {

  var overridenConfig = JSON.parse(JSON.stringify(config))

  // There's a date to overwrite
  if (config.date_field && (startDate || endDate)) {
    // Delete current config
    delete overridenConfig.dataset_field_requests[config.date_field]

    let dateFilters = []
    if (startDate) {
      let startDateFilter = {}
      startDateFilter[config.date_field] = {'$gt' : startDate}
      dateFilters.push(startDateFilter)
    }
    if (endDate) {
      let endDateFilter = {}
      endDateFilter[config.date_field] = {'$lt' : endDate}
      dateFilters.push(endDateFilter)
    }
    overridenConfig.dataset_field_requests[config.date_field] = { '$and' : dateFilters}
  }
  return overridenConfig;
}

/**
 * Supported visualizations
 * @returns an array of the supported visualizations as an array of {name: 'xxx', label: 'yyy'} with an i18n label.
 */
export function getVisualizationTypes() {
  const {t} = useI18n({ useScope: 'global'})

  return [
    {'name': 'table', 'label': t('visualization.table')},
    {'name': 'line', 'label': t('visualization.line')},
    {'name': 'bar', 'label': t('visualization.bar')},
    {'name': 'pivot', 'label': t('visualization.pivot')},
    {'name': 'pie', 'label': t('visualization.pie')},
    {'name': 'map', 'label': t('visualization.map')},
  ]
}

/**
 * Gets the supported overlay visualization types.
 * @returns the visualization types filtered down to the ones supported by overlays.
 */
export function getOverlayVisualizationTypes() {
  return getVisualizationTypes().filter(t => t.name === 'line' || t.name === 'bar')
}

/**
 * Supported aggregations
 * @returns an array of the supported aggregations as an array of {value: 'xxx', label: 'yyy'} with an i18n label.
 */
export function getAggregationFunctions() {
  const {t} = useI18n({ useScope: 'global'})

  return [
    {'value': 'rows', 'label': t('common.rows')},
    {'value': 'count', 'label': t('common.count')},
    {'value': 'sum', 'label': t('common.sum')},
    {'value': 'min', 'label': t('common.min')},
    {'value': 'max', 'label': t('common.max')}
  ]
}

export function getDetectionAlgorithms() {
  const {t} = useI18n({ useScope: 'global'})

  return [
    {'value': 'cdc1', 'label': t('visualization.algorithm.CDC1')},
    {'value': 'cdc2', 'label': t('visualization.algorithm.CDC2')},
    {'value': 'cdc3', 'label': t('visualization.algorithm.CDC3')},
    {'value': 'cusum', 'label': t('visualization.algorithm.CUSUM')},
    {'value': 'ewma', 'label': t('visualization.algorithm.EWMA')},
  ]
}

/**
 * Gets the i18n label for the visualization
 * @param type the visualization type.
 * @returns the i18n label for the visualization, or a blank if the type is not found.
 */
export function getDisplayNameOfType(type) {
  return getVisualizationTypes().filter(t => t.name === type).map(t => t.label).join('')
}

export function getLastNBackOptions() {
  const {t} = useI18n({ useScope: 'global'})

  return [
    {'value': 'LAST_30_DAYS_BACK', 'label': t('common.last30Back')},
    {'value': 'LAST_60_DAYS_BACK', 'label': t('common.last60Back')},
    {'value': 'LAST_90_DAYS_BACK', 'label': t('common.last90Back')},
    {'value': 'LAST_180_DAYS_BACK', 'label': t('common.last180Back')},
    {'value': 'LAST_365_DAYS_BACK', 'label': t('common.last365Back')}
  ]
}

/**
 * This will replace any of the LAST_N_DAYS_BACK strings with correct dates.
 * @param config the config.
 * @returns the config with all LAST_N_DAYS_BACK replaced with the appropriate date string.
 */
export function convertLastNBack(config) {

  let convertedConfig = JSON.stringify(config)
  lastNOptions.forEach(option => {

    let daysBack = option.match(/(\d+)/)[0]
    let dateSub = moment().subtract(daysBack, 'days').format("YYYY-MM-DD")

    if (convertedConfig.indexOf(option) !== -1) {
      convertedConfig = convertedConfig.replaceAll(option, dateSub)
    }
  })
  return JSON.parse(convertedConfig)
}
