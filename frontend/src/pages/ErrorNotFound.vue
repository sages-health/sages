<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <q-page
    padding
    class="flex flex-center text-center"
  >
    <div>
      <div class="text-h3">
        404 - Page Not Found
      </div>
      <q-btn
        class="q-mt-xl"
        color="primary"
        unelevated
        :to="{ name: 'home' }"
        label="Home"
        no-caps
      />
    </div>
  </q-page>
</template>

<script setup>
</script>
