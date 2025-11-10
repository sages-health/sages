<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page
    padding
  >
    <page-breadcrumbs />
    <div class="row">
      <div class="col-4">
        <q-input
          v-model="displayName"
          :label="t('datasource.displayName')"
          bottom-slots
          error-message="Please enter a display name"
          :error="!displayNameValid"
          @update:model-value="updateDisplayName"
        />
        <q-input
          v-model="pointOfContactEmail"
          type="email"
          :label="t('datasource.pointOfContactEmail')"
          bottom-slots
          error-message="Please enter a valid email"
          :error="!emailValid"
          @update:model-value="updateEmail"
        />
      </div>
    </div>
    <div class="row">
      <div class="col-8">
        <q-input
          v-model="url"
          :label="t('datasource.connectionUrl')"
          bottom-slots
          error-message="Please enter a valid connection url"
          :error="!urlValid"
          @update:model-value="updateUrl"
        />
      </div>
    </div>
    <div class="row">
      <div class="col-3">
        <q-input
          v-model="password"
          :type="passwordVisible ? 'text' : 'password'"
          :label="t('datasource.password')"
          bottom-slots
          error-message="Please enter a valid password"
          :error="!passwordValid"
          @update:model-value="updatePassword"
        >
          <template #append>
            <q-icon
              :name="passwordVisible ? fasEye : fasEyeSlash"
              class="cursor-pointer"
              @click="passwordVisible = !passwordVisible"
            />
          </template>
        </q-input>
      </div>
    </div>
    <div class="row">
      <div class="col-4">
        <q-select
          :options="datasourcetypes"
          v-model="selectedDataSourceType"
          option-label="label"
          option-value="key"
          :label="t('datasource.datasourceType')"
          @update:model-value="updateDataSourceType"
        />
      </div>
    </div>

    <template v-if="selectedDataSourceType.key === 'sql_alchemy'">
      <div class="row q-gutter-md" style="align-items: baseline;">
        <div class="col-1">
          <q-checkbox
            v-model="ssl"
            :label="t('datasource.ssl')"
          />
        </div>
        <div class="col-2">
          <q-input
            v-model="minConnectionSize"
            type="number"
            :label="t('datasource.minConnectionSize')"
            @update:model-value="updateMinConnectionSize"
          />
        </div>
        <div class="col-2">
          <q-input
            v-model="maxConnectionSize"
            type="number"
            :label="t('datasource.maxConnectionSize')"
            @update:model-value="updateMaxConnectionSize"
          />
        </div>
      </div>
    </template>
    <template v-else>
      <div class="row q-gutter-md" style="align-items: baseline;">
        <div class="col-4">
          <q-input
            v-model="username"
            :label="t('datasource.username')"
            bottom-slots
            error-message="Please enter a valid username"
            :error="!usernameValid"
            @update:model-value="updateUsername"
          />
        </div>
      </div>
    </template>

    <div class="row btn-container">
      <div class="col-9">
        <q-btn
          class="cancel-btn"
          :label="t('common.cancel')"
          size="md"
          :icon="fasXmark"
          @click="cancel"
        />
        <template v-if="connectionTestRequired">
          <q-btn
            class="test-connection-btn"
            color="primary"
            :label="t('datasource.testConnection')"
            size="md"
            text-color="white"
            :loading="dataSourceLoading"
            :icon="fasGlobe"
            :disable="!saveable"
            @click="testConnection"
          />
        </template>
        <template v-else>
          <q-btn
            class="save-btn"
            color="primary"
            :label="t('common.save')"
            size="md"
            text-color="white"
            :loading="dataSourceLoading"
            :icon="fasFloppyDisk"
            :disable="!saveable"
            @click="saveDataSource"
          />
        </template>
      </div>
    </div>

  </q-page>
</template>


<script setup>
import { useI18n } from 'vue-i18n'
import { ref, onMounted, computed, watch } from 'vue'
import PageBreadcrumbs from "components/PageBreadcrumbs.vue"
import {useRoute, useRouter} from "vue-router"
import { patterns } from 'quasar'
const { testPattern } = patterns
import {
  fasEye,
  fasEyeSlash,
  fasXmark,
  fasFloppyDisk,
  fasGlobe
 } from '@quasar/extras/fontawesome-v6'
import {postRequest} from "boot/axios";


const { t } = useI18n()
const router = useRouter()

const displayName = ref('')
const pointOfContactEmail = ref('')
const selectedDataSourceType = ref('')
const url = ref('')
const dataSourceId = ref(null)
const dataSourceLoading = ref(false)

const username = ref('')
const password = ref('')
const ssl = ref(false)
const minConnectionSize = ref(5)
const maxConnectionSize = ref(20)

const passwordVisible = ref(false)

const displayNameValid = ref(true)
const emailValid = ref(true)
const urlValid = ref(true)
const passwordValid = ref(true)
const usernameValid = ref(true)

const connectionTestRequired = ref(true)

const datasourcetypes = [
  {
    key: 'sql_alchemy',
    label: 'MySQL/PostgreSQL/SQLite'
  },
  {
    key: 'vims',
    label: 'VIMs Instance'
  }
]

onMounted( async () => {
  const route = useRoute()
  dataSourceId.value = 'dataSourceId' in route.params ? route.params.dataSourceId : null
  if (dataSourceId.value !== null) {
    await fetchDataSource(dataSourceId.value)
    // TODO:
  }
  else {
    selectedDataSourceType.value = datasourcetypes[0]

  }

})

const saveable = computed ( () => {
  return displayName.value.length > 0 && displayNameValid.value
         && url.value.length > 0 && urlValid.value
         && password.value.length > 0 && passwordValid.value
         && pointOfContactEmail.value.length > 0 && emailValid.value
         && ((selectedDataSourceType.value.key === 'vims' && username.value.length > 0) || (selectedDataSourceType.value.key !== 'vims'))
})

const updateDisplayName = function (val) {
  displayNameValid.value = displayName.value.length > 0
  connectionTestRequired.value = true
}

const updateEmail = function (val) {
  emailValid.value = testPattern.email(val)
  connectionTestRequired.value = true
}

const updateUrl = function (val) {
  urlValid.value = url.value.length > 0
  connectionTestRequired.value = true
}

const updatePassword = function (val) {
  passwordValid.value = password.value.length > 0
  connectionTestRequired.value = true
}

const updateMinConnectionSize = function (val) {
  if (val < 0) {
    minConnectionSize.value = 0
  }
  else if (val > maxConnectionSize.value) {
    minConnectionSize.value = maxConnectionSize.value
  }
  else {
    minConnectionSize.value = 0
  }
  connectionTestRequired.value = true
}

const updateMaxConnectionSize = function (val) {
  if (val < minConnectionSize.value) {
    maxConnectionSize.value = minConnectionSize.value
  }
  else if (val > 20) {
    maxConnectionSize.value = 20
  }
  else {
    maxConnectionSize.value = 20
  }
  connectionTestRequired.value = true
}

const updateDataSourceType = function () {
  connectionTestRequired.value = true
}

const updateUsername = function () {
  connectionTestRequired.value = true
  usernameValid.value = username.value.length > 0
}

const testConnection = async function () {
  dataSourceLoading.value = true
  const dataSource =  {
    display_name: displayName.value,
    point_of_contact_email: pointOfContactEmail.value,
    datasource_type: selectedDataSourceType.value.key,
    url: url.value,
    password: password.value,
  }
  if (selectedDataSourceType.value.key === 'vims') {
    dataSource.username = username.value
  }
  else {
    dataSource.ssl = ssl.value
    dataSource.min_connection_size = minConnectionSize.value
    dataSource.max_connection_size = maxConnectionSize.value
  }
  const response = await postRequest('datasource/test', dataSource)
  connectionTestRequired.value = !response.data
  dataSourceLoading.value = false
}

const saveDataSource = async function () {
  dataSourceLoading.value = true
  const dataSource =  {
    display_name: displayName.value,
    point_of_contact_email: pointOfContactEmail.value,
    datasource_type: selectedDataSourceType.value.key,
    url: url.value,
    password: password.value,
  }
  if (selectedDataSourceType.value.key === 'vims') {
    dataSource.username = username.value
  }
  else {
    dataSource.ssl = ssl.value
    dataSource.min_connection_size = minConnectionSize.value
    dataSource.max_connection_size = maxConnectionSize.value
  }
  const response = await postRequest('datasource', dataSource)

  dataSourceLoading.value = false
  await router.push('/data/datasources')
}

const cancel = async function () {
  await router.push('/data/datasources')
}

const fetchDataSource = async function (dataSourceId) {
  dataSourceLoading.value = true

  dataSourceLoading.value = false
}


</script>

<style scoped>
  .btn-container {
    display: flex;
    margin-top: 25px;
    min-width: 600px;
  }
  .save-btn {
    width: 150px;
    margin-left: 5px;
  }
  .test-connection-btn {
    width: 300px;
    margin-left: 5px;
  }
  .cancel-btn {
    width: 150px;
    margin-right: 5px;
  }
</style>
