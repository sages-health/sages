<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page padding>
    <page-breadcrumbs />
    <div class="row">
      <div class="col-5">
        <div class="row">
          <q-input
            v-model="username"
            :label="t('user.username')"
            :rules="[
              role => !!username || t('common.requiredField')
            ]"
            bottom-slots
            :error="usernameError"
            :error-message="usernameErrorMessage"
            :readonly="editingUser"
            :disable="editingUser"
          />
        </div>
        <div class="row">
          <q-input
              v-model="email"
              :label="t('user.email')"
              bottom-slots
              type="email"
              :error="emailError"
              :error-message="emailErrorMessage"
          />
        </div>
        <div class="row">
          <q-input
            v-model="firstName"
            :label="t('user.firstName')"
            :rules="[
              firstName => !!firstName || t('common.requiredField')
            ]"
            lazy-rules
          />
        </div>
        <div class="row">
          <q-input
            v-model="lastName"
            :label="t('user.lastName')"
            :rules="[
              lastName => !!lastName || t('common.requiredField')
            ]"
            lazy-rules
          />
        </div>
        <div class="row">
          <q-input
            v-model="phoneNumber"
            :label="t('user.phoneNumber')"
            type="tel"
            lazy-rules
          />
        </div>
        <div class="row">
          <q-input
              v-model="organization"
              :label="t('user.organization')"
              lazy-rules
          />
        </div>
        <div class="row">
          <q-select
            v-model="role"
            :label="t('user.role')"
            :options="availableRoles"
            :rules="[
              role => !!role || t('common.requiredField')
            ]"
            lazy-rules
          />
        </div>
        <div class="row">
          <q-select
            v-model="groups"
            multiple
            clearable
            :label="t('usergroups.groups')"
            :options="availableGroups"
            :option-label="opt => Object(opt) === opt && 'groupName' in opt ? opt.groupName : '---'"
            :option-value="opt => Object(opt) === opt && 'id' in opt ? opt.id : null"
            emit-value
            map-options
          />
        </div>
        <div class="row">
          <q-checkbox
            dense
            v-model="enabled"
            :label="t('common.enabled')"
          />
        </div>
        <div class="row">
          <q-checkbox
            dense
            v-model="remote"
            :label="t('common.remote')"
          />
        </div>
        <div class="row spacer">
          <q-space />
        </div>
        <div class="row">
          <q-btn
            style="margin-right: 15px;"
            :label="t('common.cancel')"
            size="md"
            @click="cancel"
          />
          <q-btn
            color="primary"
            :label="t('common.save')"
            size="md"
            :disable="disableSave"
            text-color="white"
            :loading="loadingUser || loadingRoles"
            :icon="fasFloppyDisk"
            @click="save"
          />
          <q-space />
          <q-btn
            v-if="editingUser"
            :label="t('common.delete')"
            size="md"
            :icon="fasTrash"
            @click="() => showDeleteDialog = true"
          />
        </div>
      </div>

      <div class="col-1" />
      <div
        class="col-4"
        v-if="!editingUser"
      >
        <div class="row">
          <q-input
            v-model="password"
            :label="t('user.password')"
            type="password"
            :rules="passwordRules"
            lazy-rules
          />
        </div>
        <div class="row">
          <q-input
            v-model="verifyPassword"
            :label="t('user.verifyPassword')"
            type="password"
            :rules="[
              verifyPassword => !!verifyPassword || t('common.requiredField'),
              verifyPassword => verifyPassword === password || t('user.passwordsMustMatch')
            ]"
          />
        </div>
      </div>
    </div>
    <q-dialog
      v-model="showDeleteDialog"
      persistent
    >
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm">{{ t('common.delete') }}: {{ email }}? </span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            label="Cancel"
            v-close-popup
          />
          <q-btn
            :loading="loadingUser"
            :label="t('common.delete')"
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
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import {
  fasFloppyDisk,
    fasTrash
} from '@quasar/extras/fontawesome-v6'

import { useUserStore } from "stores/user"
import PageBreadcrumbs from 'components/PageBreadcrumbs.vue'
import {useRoute, useRouter} from "vue-router";

import { patterns } from 'quasar'
const { testPattern } = patterns
import {debounce} from "quasar";

const { t } = useI18n()
const router = useRouter()

useUserStore().$reset()

const { fetchUser, fetchRoles, fetchGroups, saveUser, validateUsername, deleteUser } = useUserStore()
const { username, email, organization, firstName, lastName, phoneNumber, enabled, remote, role, groups, userId, password, availableRoles, availableGroups, loadingUser, loadingRoles, deletingUser } = storeToRefs(useUserStore())

const verifyPassword = ref('')
const editingUser = ref(false)
const usernameError = ref(false)
const usernameErrorMessage = ref('')
const emailError = ref(false)
const emailErrorMessage = ref('')
const showDeleteDialog = ref(false)

const disableSave = computed ( () => {
  const validPassword = userId.value === null ? (password.value === verifyPassword.value && password.value !== '') : true

  return username.value === '' || firstName.value === '' || lastName.value === '' || role.value === '' || !validPassword
})

const save = async function () {
  await saveUser()
  router.push('/admin/users')
}
const cancel = function () {
  router.push('/admin/users')
}

const delete_ = async function () {
  await deleteUser(userId)
  router.push('/admin/users')
}

const passwordRules = computed(() => {
  return [
    password => !!password || t('common.requiredField'),
    password => password.length > 12 || t('user.passwordRequirement'),
    password =>
      /[A-Z]/.test(password) &&
      /[a-z]/.test(password) &&
      /\d/.test(password) &&
      /[\W_]/.test(password) ||
      t('user.passwordComplexityRequirement')
  ]
});

const checkEmail = debounce( async function (email) {
  if (editingUser.value) return
  else if (!testPattern.email(email)) {
    emailError.value = true
    emailErrorMessage.value = t('user.emailRequirement')
    return
  }

  emailError.value = false
  emailErrorMessage.value = ''

}, 500)

const checkUsername = debounce( async function (username) {
  if (editingUser.value) return
  if (username.length === 0) {
    usernameError.value = true
    usernameErrorMessage.value = t('common.requiredField')
    return
  }
  const valid = await validateUsername(username)
  if (!valid.data) {
    usernameError.value = true
    usernameErrorMessage.value = t('user.accountExists')
    return
  }

  usernameError.value = false
  usernameErrorMessage.value = ''

}, 500)

watch(username, checkUsername)
watch(email, checkEmail)


onMounted( async () => {
  const route = useRoute()
  const userId = 'userId' in route.params ? route.params.userId : null
  await fetchRoles()
  await fetchGroups()
  if (userId !== null) {
    editingUser.value = true
    await fetchUser(userId)
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
</style>
