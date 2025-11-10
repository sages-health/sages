<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />
    <div class="row">
      <div class="col-3">
        <q-input
          :label="t('map.search')"
          outlined
          v-model="search"
        >
          <template #append>
            <q-icon :name="fasMagnifyingGlass" />
          </template>
        </q-input>
      </div>
      <div class="col-3 offset-2 text-black">
        <q-btn
          :icon="fasTable"
          @click="showAsGrid = true"
          :label="t('common.grid')"
        />
        <q-btn
          :icon="fasList"
          @click="showAsGrid = false"
          :label="t('common.list')"
        />
      </div>
      <div class="col-3 offset-1 text-right">
        <q-btn
          v-if="displayAdd"
          :icon="fasPlus"
          class="primary white-text"
          outlined
          :to="{ path: '/data/maps/add' }"
          :label="t('map.addMap')"
        />
      </div>
    </div>
    <div v-if="showAsGrid">
      <div class="q-pa-md row items-start q-gutter-md">
        <transition-group name="list">
          <q-card
            v-for="map in filteredMaps"
            :key="map.id"
            class="col-4"
          >
            <q-card-section class="bg-primary text-white">
              <div class="text-h6">
                {{ map.display_name }}
              </div>
            </q-card-section>

            <q-separator dark />

            <q-card-actions class="float-right">
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/data/maps/' + map.id }"
                :icon="fasBinoculars"
                :label="t('common.view')"
              />
              <q-btn
                v-if="displayEdit"
                class="bg-primary text-white"
                :to="{ path: '/data/maps/' + map.id + '/edit' }"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                v-if="displayDelete"
                class="bg-primary text-white"
                :icon="fasTrashCan"
                :label="t('common.delete')"
                @click="() => presentDeleteMapDialog(map)"
              />
            </q-card-actions>
          </q-card>
        </transition-group>
      </div>
    </div>
    <div
      class="q-pa-md"
      v-if="!showAsGrid"
    >
      <q-list>
        <q-item
          v-for="(map) in filteredMaps"
          :key="map.id"
        >
          <q-item-section>
            <q-item-label>{{ map.display_name }}</q-item-label>
          </q-item-section>
          <q-item-section
            side
            top
          >
            <span class="q-pa-md q-gutter-sm">
              <q-btn
                class="bg-primary text-white"
                :to="{ path: '/data/maps/' + map.id }"
                :icon="fasBinoculars"
                :label="t('common.view')"
              />
              <q-btn
                v-if="displayEdit"
                class="bg-primary text-white"
                :to="{ path: '/data/maps/' + map.id + '/edit' }"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                v-if="displayDelete"
                class="bg-primary text-white"
                :icon="fasTrashCan"
                :label="t('common.delete')"
                @click="() => presentDeleteMapDialog(map)"
              />
            </span>
          </q-item-section>
        </q-item>
      </q-list>
    </div>
    <q-dialog
      v-model="showDeleteDialog"
      persistent
    >
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm">Delete: {{ mapToDelete.display_name }}? </span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancel"
            color="primary"
            v-close-popup
          />
          <q-btn
            flat
            :loading="mapLoading"
            :label="t('common.delete')"
            color="primary"
            @click="() => deleteMap(mapToDelete.id)"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import PageBreadcrumbs from "components/PageBreadcrumbs.vue"
import { useI18n } from 'vue-i18n'
import {
  fasTable,
  fasList,
  fasPlus,
  fasMagnifyingGlass,
  fasPencil,
  fasBinoculars,
  fasTrashCan
} from '@quasar/extras/fontawesome-v6'
import { useMapUIStore } from 'stores/map-ui'
import {storeToRefs} from "pinia"
import {computed, onMounted, ref} from "vue"
import {hasPermission} from "stores/auth";
import {$api} from "boot/axios";

const { t } = useI18n()

const { showAsGrid } = storeToRefs(useMapUIStore())

const showDeleteDialog = ref(false)
const mapToDelete = ref({})
const mapLoading = ref(false)
const search = ref('')
const maps = ref([])

const filteredMaps = computed ( () =>{
  if (!search.value.length) return maps.value
  return maps.value.filter( map => map.display_name.toLowerCase().includes(search.value.toLowerCase()))
})

const presentDeleteMapDialog = function (map) {
  showDeleteDialog.value = true
  mapToDelete.value = map
}

const displayAdd = hasPermission('create_map')
const displayEdit = hasPermission('update_map')
const displayDelete = hasPermission('delete_map')

const fetchMaps = async function () {
  mapLoading.value = true
  maps.value = (await $api.get('map')).data
  mapLoading.value = false
}

const deleteMap = async function (mapId) {
  mapLoading.value = true
  await $api.delete('map/' + mapId)
  maps.value = maps.value.filter(x => x.id !== mapId)
  mapLoading.value = false
}

onMounted(async () => {
  await fetchMaps()
})

</script>
