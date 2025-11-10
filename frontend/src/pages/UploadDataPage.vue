<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />
    <div class="row">
      <div class="col-5">
        <q-form @submit="onSubmit" class="q-gutter-md">
          <div class="row">
            <q-file name="upload_file" outlined :label="$t('data.filename')" v-model="fileUpload" @update:model-value="fileUpdated">
              <template v-slot:prepend>
                <q-icon :name="fasPaperclip" />
              </template>
            </q-file>
            <q-checkbox :label="$t('data.autoSuggest')" @update:model-value="autoSuggestToggle" v-model="autoSuggest" />
          </div>
          <div class="row">
            <q-select
                filled
                use-input
                input-debounce="0"
                :disable="!fileUpload"
                v-model="uploadConfig"
                :options="options"
                @filter="filterFn"
                :label="$t('data.filetype')"
                option-label="title" />
          </div>
          <div v-if="uploadConfig && uploadConfig.description"
               class="row">
            <q-input
                v-model="uploadConfig.description"
                disable
                filled
                :label="$t('common.description')"
                type="textarea"
            />
          </div>
          <div class="row">
            <q-linear-progress :indeterminate="running" size="25px" :value="ingestionProgress" :color="color">
              <div class="absolute-full flex flex-center">
                <q-badge color="white" text-color="primary" :label="$t(dagRunIdstate)" />
              </div>
            </q-linear-progress>
          </div>
          <div class="row">
            <q-btn :disable="running || !(fileUpload && uploadConfig)" :label="$t('data.submit')" type="submit" color="primary"/>
          </div>
        </q-form>
      </div>
    </div>
  </q-page>
</template>


<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {$api, getRequest, postRequest} from 'boot/axios'
import levenshtein from 'fast-levenshtein'

import {
  fasFloppyDisk,
    fasPaperclip
} from '@quasar/extras/fontawesome-v6'

import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import {useRoute, useRouter} from "vue-router";

const { t } = useI18n()
const router = useRouter()

let fileUpload = ref(null)
let uploadConfig = ref(null)
const uploadConfigs = ref([])
let dagRunIdstate = ref('data.notRunning')
let pollInterval = ref(null)
let visible = ref(false)
let running = ref(false)
let color = ref('secondary')
let ingestionProgress = ref(0)
let options = ref([])
let autoSuggest = ref(false)

onMounted(async () => {
  const response = (await getRequest('etl/config'))
  uploadConfigs.value = Object.values(response.data)
  options.value = uploadConfigs.value
  // console.log('uploadConfigs loaded:', uploadConfigs.value)

})

function fetchStatus(dagRunId) {
  getRequest('etl/dagrun/' + dagRunId + '/status')
      .then((response) => {
        ingestionProgress.value = 50
        //check if status is completed, if it is stop polling
        if (response.data.state === 'success' || response.data.state === 'failed') {
          clearInterval(pollInterval.value) //won't be polled anymore
          visible.value = false
          running.value = false
          ingestionProgress.value = 100
          if (response.data.state === 'success')
            color.value = 'green'
          if (response.data.state === 'failed')
            color.value = 'red'
        }
        dagRunIdstate.value = 'data.' + response.data.state;
      });
}

const onSubmit = async function (evt) {
  try {
    let formData = new FormData(evt.target)
    let filename = ""

    for (const [name, value] of formData.entries()) {
      if (value.name.length > 0) {
        filename = value.name
      }
    }

    formData = new FormData()
    formData.append("file", fileUpload.value);
    running.value = true
    color.value = 'secondary'
    dagRunIdstate.value = 'data.uploading'
    await $api.post('etl/upload', formData, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'multipart/form-data'
      }
    })

    const fullConfig = {
      "conf": {
        "filename": filename,
        "filetype": uploadConfig.value.filetype
      }
    }

    fullConfig["conf"][uploadConfig.value.filetype] = uploadConfig.value
    ingestionProgress.value = 0
    dagRunIdstate.value = 'data.running'
    visible.value = true
    // console.log("fullConfig", fullConfig)
    const response = (await postRequest("etl/dagrun", fullConfig))

    visible.value = false
    running.value = false
    ingestionProgress.value = 100

    if (response.data.state === 'success')
      color.value = 'green'
    if (response.data.state === 'failed')
      color.value = 'red'

    dagRunIdstate.value = 'data.' + response.data.state;

    // pollInterval.value = setInterval(fetchStatus, 3000, dagRunId)
  }
  catch (e) {
    dagRunIdstate.value = 'data.failed'
    color.value = 'red'
    running.value = false
    clearInterval(pollInterval.value)
    fileUpload.value = null

  }


}

const autoSuggestToggle = function (val, update) {
  autoSuggest.value = val
  if(val) {
    fileUpdated(fileUpload.value)
  }
}

const fileUpdated = function (val, update) {
  // console.log('fileUpload updated:', val)
  // console.log('uploadConfig', uploadConfig.value)
  if (autoSuggest.value) {
    let score = 100
    let topMatch = null
    const filename = val.name
    uploadConfigs.value.forEach(config => {
      const newScore = levenshtein.get(filename, config.title, {useCollator: true})

      if (newScore < score) {
        score = newScore
        topMatch = config
      }
    })


    uploadConfig.value = topMatch
    // console.log('uploadConfig set via autoSuggest:', topMatch)

  }
}

const filterFn = function (val, update) {
  if (val === '') {
    update(() => {
      options.value = uploadConfigs.value

      // here you have access to "ref" which
      // is the Vue reference of the QSelect
    })
    return
  }

  update(() => {
    const needle = val.toLowerCase()
    options.value = uploadConfigs.value.filter(v => v.title.toLowerCase().indexOf(needle) > -1)
  })
}

</script>

<style scoped>
  .q-field {
    min-width: 100%;
  }
  .spacer {
    min-height: 100px;
  }
</style>

