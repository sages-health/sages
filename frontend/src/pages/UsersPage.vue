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
        :title="t('common.user.plural')"
        :columns="columns"
        :rows="filteredUsers"
        :loading="loadingUsers || loadingGroups"
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
            :icon="fasPlus"
            class="white-text"
            color="primary"
            outlined
            :to="{ path: '/admin/users/add'}"
            :label="t('user.addUser')"
          />
        </template>
        <template #body-cell-groups="groups">
          <q-td
            class="group-names"
            :props="groups">
            {{ renderGroupNames(groups.value) }}
          </q-td>
        </template>
        <template #body-cell-enabled="enabled">
          <q-td :props="enabled">
            <q-icon :name="enabled.value ? fasCheck : fasX" />
          </q-td>
        </template>
        <template #body-cell-remote="remote">
          <q-td :props="remote">
            <q-icon :name="remote.value ? fasCheck : fasX" />
          </q-td>
        </template>
        <template #body-cell-locked="locked">
          <q-td :props="locked">
            <q-icon
              v-if="locked.value"
              alt="Unlock Account"
              :name="fasLock"
              style="cursor: pointer"
              @click="unlock(locked.row.id)"
            >
              <q-tooltip>Unlock account</q-tooltip>
            </q-icon>
            <q-icon
              v-else
              :name="fasLockOpen"
            />
          </q-td>
        </template>
        <template #body-cell-otp="otp_enabled">
          <q-td :props="otp_enabled">
            <q-btn
              v-if="otp_enabled.value"
              color="blue"
              label="Disable"
              @click="disableUser2fa(otp_enabled.row.id)"
            />
          </q-td>
        </template>
        <template #body-cell-actions="id">
          <q-td :props="id">
            <q-btn
              @click="editUser(id.value)"
              color="primary"
              :icon="fasPencil"
            />
          </q-td>
        </template>
      </q-table>
    </div>
  </q-page>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import {ref, onMounted, computed} from 'vue'
import { useI18n } from 'vue-i18n'

import {
  fasPencil,
  fasCheck,
  fasX,
  fasPlus,
  fasMagnifyingGlass,
  fasLock,
  fasLockOpen,
} from '@quasar/extras/fontawesome-v6'

import { useUserStore } from "stores/user"
import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import {useRouter} from "vue-router";
import { useGroupStore } from 'src/stores/group'
import { useAuthStore } from 'src/stores/auth'

const { t } = useI18n()
const router = useRouter()

useGroupStore().$reset()

const editUser = function (userId) {
  router.push(`/admin/users/${userId}`)
}

const search = ref('')

const { fetchUsers, unlockUserAccount } = useUserStore()
const { users, loadingUsers } = storeToRefs(useUserStore())
const { fetchAllGroups, renderGroupNames } = useGroupStore()
const { loadingGroups } = storeToRefs(useGroupStore())
const { disableUser2fa } = useAuthStore()

const columns = [
  {name: 'username', label: t('user.username'), field: 'username', sortable: true, align: "left"},
  {name: 'first_name', label: t('user.firstName'), field: 'first_name', sortable: true, align: "left"},
  {name: 'last_name', label: t('user.lastName'), field: 'last_name', sortable: true, align: "left"},
  {name: 'roles', label: t('user.roles'), field: 'roles_formatted', sortable: true, align: "left"},
  {name: 'groups', label: t('usergroups.usergroups'), field: 'groups', sortable: true, align: "left"},
  {name: 'phone_number', label: t('user.phoneNumber'), field: 'phone_number', sortable: false, align: "left"},
  {name: 'enabled', label: t('common.enabled'), field: 'enabled', sortable: true, align: "center"},
  {name: 'remote', label: t('common.remote'), field: 'remote', sortable: true, align: "center"},
  {name: 'locked', label: t('common.locked'), field: 'locked_until', sortable: true, align: "center"},
  {name: 'otp', label: t('login.otp'), field: 'otp_enabled', sortable: true, align: "center"},
  {name: 'actions', label: t('common.actions'), field: 'id'}
]

onMounted( async () => {
  await fetchUsers()
  await fetchAllGroups()
})

const filteredUsers = computed ( () =>{
  if (!search.value.length) return users.value
  return users.value.filter( user =>
      user.first_name.toLowerCase().includes(search.value.toLowerCase()) ||
      user.last_name.toLowerCase().includes(search.value.toLowerCase()) ||
      user.username.toLowerCase().includes(search.value.toLowerCase()) ||
      user.phone_number.toLowerCase().includes(search.value.toLowerCase()) ||
      user.roles_formatted.toLowerCase().includes(search.value.toLowerCase())
  )
})

const getGroupNames = function (groups) {
  const groupList = groups.map(
    (group) => {
      const fullGroupInfo = allGroups.value.find(
        (allGroup) => {
          return allGroup.id === group
        }
      )
      return (fullGroupInfo === undefined ? 'Unknown Group' : fullGroupInfo.groupName)
    }
  )
  return groupList.join(", ")
}

const unlock = async function (userId) {
  await unlockUserAccount(userId)
  await fetchUsers()
}
</script>

<style>

.group-names {
    max-width: 10rem;
    overflow: hidden;
    text-overflow: ellipsis;
  }

</style>
