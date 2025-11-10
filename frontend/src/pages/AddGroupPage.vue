<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />
    <div class="col">
        <div class="row name-and-actions">
          <div class="col">
            <q-input
              v-model="groupName"
              :label="t('usergroups.groupName')"
              :rules="[
                groupName => !!groupName || t('common.requiredField'),
              ]"
              bottom-slots
              :error="groupNameError"
              :error-message="groupNameErrorMessage"
              maxlength="60"
            />
          </div>
          <div class="row btn-container">
            <q-btn
              class="action-btn"
              :label="t('common.cancel')"
              size="md"
              @click="cancel"
            />
            <q-space />
            <q-btn
              v-if="!viewingGroup"
              class="action-btn"
              color="primary"
              :label="t('common.save')"
              size="md"
              :disable="disableSave"
              text-color="white"
              :loading="loadingGroup"
              :icon="fasFloppyDisk"
              @click="save"
            />
            <q-space />
            <q-btn
              v-if="editingGroup"
              class="action-btn"
              :label="t('common.delete')"
              size="md"
              :icon="fasTrash"
              @click="() => showDeleteDialog = true"
            />
          </div>
        </div>

        <div
          id="groupUsers"
          class="row"
          v-if="editingGroup || viewingGroup"
          style="margin-bottom: 20px;"
          >
          <q-table
            class="col-12"
            :title="t('common.user.plural')"
            :columns="userColumns"
            :rows="groupUserList"
            :loading="loadingUsers"
            :no-data-label="$t('common.noData')"
          >
          </q-table>
        </div>

        <div
          id="groupDatasets"
          class="row"
          v-if="editingGroup || viewingGroup"
          >
          <q-table
            class="col-12"
            :title="$t('dataset.plural')"
            :columns="datasetColumns"
            :rows="groupDatasetList"
            :loading="loadingUsers"
            :no-data-label="$t('common.noData')"
          >
          </q-table>
        </div>
      </div>

    <q-dialog
      v-model="showDeleteDialog"
      persistent
    >
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm">{{ t('common.delete') }}: {{ groupName }}? </span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            :label="$t('common.cancel')"
            v-close-popup
          />
          <q-btn
            :loading="loadingAllGroups"
            :label="$t('common.delete')"
            color="primary"
            @click="delete_"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>


<script setup>
import { storeToRefs } from 'pinia'
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'

import {
  fasFloppyDisk,
    fasTrash
} from '@quasar/extras/fontawesome-v6'

import { useGroupStore } from "stores/group"
import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import {useRoute, useRouter} from "vue-router";

const { t } = useI18n()
const router = useRouter()

useGroupStore().$reset()

const { saveGroup, deleteGroup, fetchAllGroups, fetchGroup, fetchGroupDatasets, fetchGroupUsers } = useGroupStore()
const { groupName, groupDatasetList, groupUserList, loadingUsers, loadingAllGroups, loadingGroup } = storeToRefs(useGroupStore())
const groupNameError = ref(false)
const groupNameErrorMessage = ref('')
const showDeleteDialog = ref(false)
const addingGroup = ref(false)
const editingGroup = ref(false)
const viewingGroup = ref(true)

const userColumns = [
  {name: 'username', label: t('user.username'), field: 'username', sortable: true, align: "left"},
  {name: 'first_name', label: t('user.firstName'), field: 'first_name', sortable: true, align: "left"},
  {name: 'last_name', label: t('user.lastName'), field: 'last_name', sortable: true, align: "left"},
]

const datasetColumns = [
  {name: 'display_name', label: t('dataset.displayName'), field: 'display_name', sortable: true, align: "left"},
  {name: 'description', label: t('dataset.description'), field: 'description', sortable: true, align: "left"},
]

const disableSave = computed ( () => {
  return groupName.value === ''
})

const save = async function () {
  await saveGroup()
  router.push('/admin/groups')
}
const cancel = function () {
  router.push('/admin/groups')
}

const delete_ = async function () {
  await deleteGroup()
  router.push('/admin/groups')
}

onMounted( async () => {
  const route = useRoute()
  const groupId = 'groupId' in route.params ? route.params.groupId : null
  addingGroup.value = route.path.includes('/add')
  editingGroup.value = route.path.includes('/edit')
  viewingGroup.value = (!addingGroup.value && !editingGroup.value)
  await fetchAllGroups()
  if (groupId !== null) {
    fetchGroup(groupId)
  }
  if (editingGroup.value || viewingGroup.value) {
    fetchGroupDatasets(groupId)
    fetchGroupUsers(groupId)
  }
})


</script>

<style scoped>
  .q-field {
    min-width: 100%;
  }
  .spacer {
    min-height: 100px;
  }

  .group-names {
    max-width: 10rem;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .name-and-actions {
    padding-bottom: 2em;
  }

  .btn-container {
    display: flex;
    justify-content: center;
    padding-left: 10px;
    padding-top: 10px;
    padding-bottom: 10px;
  }

  .action-btn {
    margin-left: 2em;
    width: 150px;
    height: 50px;
  }
</style>
