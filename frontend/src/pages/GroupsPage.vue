<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />
    <div class="row">
      <q-table
        class="col-12"
        :title="$t('usergroups.groups')"
        :columns="columns"
        :rows="filteredGroups"
        :loading="loadingGroups"
        :no-data-label="$t('common.noData')"
      >
        <template #top>
          <q-input
            class="col-3"
            :label="t('common.search')"
            v-model="search"
            type="search"
          >
            <template #append>
              <q-icon :name="fasMagnifyingGlass" />
            </template>
          </q-input>
          <q-space class="col-5" />
          <q-btn
            :v-if="canAddGroup"
            :icon="fasPlus"
            class="white-text"
            color="primary"
            outlined
            :to="{ path: '/admin/groups/add'}"
            :label="$t('usergroups.addGroup')"
          />
        </template>
        <template #body-cell-actions="id">
          <q-td :props="id">
            <span class="q-gutter-sm q-my-md">
              <q-btn
                class="bg-primary text-white"
                @click="viewGroup(id.value)"
                :icon="fasBinoculars"
                :label="t('common.view')"
              />
              <q-btn
                class="bg-primary text-white"
                @click="editGroup(id.value)"
                :icon="fasPencil"
                :label="t('common.edit')"
              />
              <q-btn
                class="bg-primary text-white"
                :icon="fasTrashCan"
                :label="t('common.delete')"
                @click="() => presentDeleteGroupDialog(id)"
              />
            </span>
          </q-td>
        </template>
      </q-table>
    </div>
    <q-dialog
      v-model="showDeleteDialog"
      persistent
    >
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm">Delete: {{ groupToDelete.row.groupName }}? </span>
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
            :label="t('common.delete')"
            color="primary"
            @click="() => deleteGroupAndRefresh(groupToDelete.row.id)"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import {ref, onMounted, computed} from 'vue'
import { useI18n } from 'vue-i18n'
import {useRouter} from "vue-router";

import {
  fasBinoculars,
  fasPencil,
  fasPlus,
  fasMagnifyingGlass,
  fasTrashCan

} from '@quasar/extras/fontawesome-v6'

import { hasPermission } from 'stores/auth'
import { useGroupStore } from 'src/stores/group';
import { useUserStore } from "stores/user"
import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'

const { t } = useI18n()
const search = ref('')
const router = useRouter()

const { fetchGroups } = useUserStore()
const { deleteGroup } = useGroupStore()
const { availableGroups, loadingGroups } = storeToRefs(useUserStore())

const showDeleteDialog = ref(false)
const groupToDelete = ref({})

const columns = [
  {name: 'groupName', label: t('usergroups.groupName'), field: 'groupName', sortable: true, align: "left"},
  {name: 'actions', label: t('common.actions'), field: 'id', align: "right"}
]

const canAddGroup = hasPermission('create_group')

onMounted( async () => {
  await fetchGroups()
})

const filteredGroups = computed ( () =>{
  if (!search.value.length) return availableGroups.value
  return availableGroups.value.filter( group =>
      group.group_name.toLowerCase().includes(search.value.toLowerCase())
  )
})

const editGroup = function (groupId) {
  router.push(`/admin/groups/${groupId}/edit`)
}

const viewGroup = function (groupId) {
  router.push(`/admin/groups/${groupId}`)
}

const presentDeleteGroupDialog = function (group) {
  showDeleteDialog.value = true
  groupToDelete.value = group
}

const deleteGroupAndRefresh = async function (groupId) {
  await deleteGroup(groupId)
  await fetchGroups()
  router.push('/admin/groups')
}

</script>
