<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-breadcrumbs class="q-mb-md">
    <q-breadcrumbs-el
      :icon="fasHouse"
      :to="{ name: 'home' }"
    />
    <q-breadcrumbs-el
      v-for="(part, index) in parts"
      :key="index"
      :label="part.label"
      :to="part.to"
    />
    <q-breadcrumbs-el
      v-if="last_part !== ''"
      :label="last_part"
    />
  </q-breadcrumbs>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fasHouse } from '@quasar/extras/fontawesome-v6'

const last_part = ref('')
const parts = ref([])

const { t } = useI18n()

const route = useRoute()
let url_parts = route.path.split(/\//)
if (url_parts.length > 0) {
  // Last part should just be text because we're on that page.
  const last_part_tmp = url_parts.pop()
  last_part.value = t(`breadcrumb.${last_part_tmp}`, last_part_tmp)
  url_parts.forEach(function(part, idx) {
    // Skip the first blank value and the collapsible part of the url that doesn't contain content
    // for the data page (e.g., data in /data/datasets).
    if (idx > 0 && !(idx === 1 && part === 'data')) {
      parts.value.push({
        to: [...url_parts].splice(0, idx+1).join('/'),
        label: t(`breadcrumb.${part}`, part)
      })
    }
  })


}
</script>
