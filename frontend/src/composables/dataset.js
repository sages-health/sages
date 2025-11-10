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

import {$api, getRequest} from "boot/axios";

export async function isActive(dataSetId) {
  const dataSet = (await getRequest( 'dataset/' + dataSetId)).data

  return dataSet.is_active
}
/**
 * Extract the dataset filters from the request logic.
 */
export function extractDataSetFilters(dataSet) {

  let filters = {}

  const request = dataSet.base_query.request
  if (request) {
    request.$and.forEach(fieldRequest => {
      // We need to pull the field name out of the field request. References have a different data structure than
      // standard and/or queries.
      let firstKey = Object.keys(fieldRequest)[0]
      let fieldName
      if (['$and', '$or'].includes(firstKey)) {
        const conditions = fieldRequest[firstKey]
        const firstCondition = conditions[0]
        fieldName = Object.keys(firstCondition)[0]
      }
      else {
        fieldName = firstKey
      }
      filters[fieldName] = fieldRequest
    })
  }
  return filters
}

/**
 * Create an easy way to access fields for a dataset
 */
export function createFieldsLookup(dataSet) {

  let fields = {}
  for (const field of dataSet.fields) {
    fields[field.data_field_name] = field
  }
  return fields
}

/**
 * Create an easy lookup for reference object values
 */
export function createReferenceOptionsLookup(dataSet) {

  let referenceOptions = {}
  const fields = dataSet.fields;

  fields.forEach(field =>  {
    if (field.region_map !== null && field.region_map !== undefined) {
      referenceOptions[field.data_field_name] = Object.keys(field.region_map_mapping).map((x) => ({label: x, value: x}))
    }
    else if (field.is_reference && field.values) {

      const options = field.values.map(function (fieldValue) {
        return {label: fieldValue === null ? '__null__' : fieldValue, value: fieldValue}
      })
      referenceOptions[field.data_field_name] = options;
    }
  })
  return referenceOptions;
}


/**
 * Go over the projection and get the shared fields.
 */
export function getSharedFields(dataSet) {
  let sharedFields = []

  dataSet.fields.forEach(field => sharedFields.push(field.data_field_name))

  return sharedFields
}

export async function query(dataSetBaseQuery, queryOpts, dataSetId) {
  let dataSetQuery = JSON.parse(JSON.stringify(dataSetBaseQuery))

  if (queryOpts.queryRowsPerPage) {
    dataSetQuery.limit = queryOpts.queryRowsPerPage
  }
  if (queryOpts.queryPage && queryOpts.queryRowsPerPage) {
    dataSetQuery.offset = queryOpts.queryRowsPerPage * (queryOpts.queryPage - 1)
  }
  if (queryOpts.querySortBy !== null) {
    dataSetQuery.order_by = [[queryOpts.querySortBy, queryOpts.queryDescending ? 'desc' : 'asc']]
  }

  if (queryOpts.queryGroupBy !== null
    && ((typeof queryOpts.queryGroupBy === 'string')
      || Array.isArray(queryOpts.queryGroupBy))) {

    dataSetQuery.group_by = {
      fields: Array.isArray(queryOpts.queryGroupBy) ? queryOpts.queryGroupBy : [queryOpts.queryGroupBy],
      aggregators: {
        [queryOpts.queryAggregateFunction]: {
          field: queryOpts.queryAggregateField,
          'function': queryOpts.queryAggregateFunction === 'rows' ? 'count' : queryOpts.queryAggregateFunction
        }
      }
    }
    if (queryOpts.aggregate){
      dataSetQuery.aggregate = queryOpts.aggregate
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

    const response = await $api.post( 'dataset/' + dataSetId + '/query', dataSetQuery)

    return response;
  }
}
