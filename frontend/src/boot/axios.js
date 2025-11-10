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

import { boot } from 'quasar/wrappers'
import axios from 'axios'
import debug from 'debug'

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)

const axiosLogger = debug('vims:axiosError')
export const $api = axios.create({ baseURL: process.env.API_URL })

const defaultAPIHeaders = {
  Accept: 'application/json',
  'Content-Type': 'application/json'
}

export function updateAPIHeaders (headers) {
  $api.defaults.headers.common = {
    ...defaultAPIHeaders,
    ...headers
  }
}

const request = function(options) {
  const onSuccess = function (response) {
    return response;
  }

  const defaultOnError = function (cause) {
    axiosLogger('Request Failed:', cause.config);
    axiosLogger('Detail: ', cause.response.data.detail)

    let errorMsg = options.errorMessage ? options.errorMessage : ''
    if (cause.response.data.detail) {
      errorMsg = errorMsg + cause.response.data.detail
    }
    const error = new Error(errorMsg)

    const errorStack = (error.stack !== undefined) ? error.stack : ''
    const causeStack = (cause.stack !== undefined) ? cause.stack : ''
    if (causeStack.length > 0) error.stack = `${errorStack}\nCaused by:\n${causeStack}`
    throw error
  }

  return $api(options)
    .then(onSuccess)
    .catch(options.onError !== undefined ? onError : defaultOnError);
}

const getRequest = function(url, errorMessage) {
  return request({ method :'get', url: url, errorMessage: errorMessage })
}

const postRequest = function(url, data, errorMessage) {
  return request({ method :'post', url: url, data: data, errorMessage: errorMessage  })
}

const putRequest = function(url, data, errorMessage) {
  return request({ method :'put', url: url, data: data, errorMessage: errorMessage  })
}
const deleteRequest = function(url, data, errorMessage) {
  return request({ method :'delete', url: url, errorMessage: errorMessage  })
}

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = $api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
})



export { axios, request, getRequest, postRequest, deleteRequest, putRequest }

