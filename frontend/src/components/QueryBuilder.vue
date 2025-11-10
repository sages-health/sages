<!--
  - Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
  -
  -->

<template>
  <div class="container">
    <template v-if="isReference">
      <div class="reference-field-value-container">
        {{ t("common.include") }}:
        <q-scroll-area
          class="reference-field-value-scroll"
          visible
        >
          <q-option-group
            v-model="referenceSelection"
            :options="referenceOptions"
            type="checkbox"
            debounce="500"
            color="primary"
            dense
          />
        </q-scroll-area>
        <div class="reference-field-value-btns">
          <q-btn
            :label="t('common.selectAll')"
            @click="() => referenceSelection = referenceOptions.map(x=>x.value)"
            color="primary"
          />
          <q-btn
            :label="t('common.clear')"
            @click="() => referenceSelection = []"
          />
        </div>
      </div>
    </template>
    <template v-else>
      <div class="join-op-selection text-center">
        <q-option-group
          dense
          inline
          v-model="joinOp"
          :options="joinOperatorOptions"
          :label="t('queryBuilder.joinOperator')"
        />
      </div>
      <div
        class="filter-container"
        v-for="condition of conditions"
        :key="condition.id"
      >
        <div class="filter-removal-btn">
          <q-btn
            dense
            round
            flat
            size="sm"
            :icon="fasCircleXmark"
            @click="() => removeCondition(condition.id)"
          />
        </div>

        <template v-if="['str'].includes(type)">
          <q-select
            class="filter-op-selection"
            :label="t('common.operator')"
            :options="allowedOps"
            :option-label="opt => $t('ops.' + opt)"
            v-model="condition.operator"
            dense
            outlined
            :display-value="$t('ops.' + condition.operator)"
          />
          <q-input
            class="filter-value"
            :label="t('common.value')"
            v-model="condition.value"
            debounce="500"
            dense
            outlined
            :display-value="$t('ops.' + condition.operator)"
          />
        </template>

        <template v-else-if="['float', 'int'].includes(type)">
          <q-option-group
            :options="unitOptions"
            type="radio"
            v-model="ageAndNumber"
            class="age-and-number-radio"
            @click="ageAndNumber"
            :display-value="val => $t('common.' + val.toLowerCase())"
          />
          <q-select
            class="filter-op-selection"
            :label="t('common.operator')"
            :options="allowedOps"
            :option-label="opt => $t('ops.' + opt)"
            v-model="condition.operator"
            dense
            outlined
            :display-value="$t('ops.' + condition.operator)"
          />
          <div
            class="row"
            style="margin: 10px 30px 10px 10px"
          >
            <q-input
              class="col-5"
              v-if="ageAndNumber === 'age'"
              :label="t('common.value')"
              v-model="condition.value"
              debounce="500"
              dense
              outlined
              :display-value="$t('ops.' + condition.operator)"
            />
            <q-select
              class="col-7"
              v-if="ageAndNumber === 'age'"
              :label="t('common.ageUnit')"
              v-model="condition.age"
              :options="ageUnits"
              :option-label="ageUnit => $t('common.' + ageUnit.toLowerCase())"
              dense
              outlined
            />
            <q-input
              class="col"
              v-if="ageAndNumber === 'number'"
              :label="t('common.value')"
              v-model="condition.value"
              debounce="500"
              dense
              outlined
              :display-value="$t('ops.' + condition.operator)"
            />
          </div>
        </template>

        <template v-else-if="type === 'datetime'">
          <q-select
            class="filter-op-selection"
            v-show="condition.value === '' || !isObject(condition.value)"
            :label="t('common.operator')"
            :options="allowedOps"
            :option-label="opt => $t('ops.' + opt)"
            v-model="condition.operator"
            :display-value="$t('ops.' + condition.operator)"
            dense
            outlined
          />
          <q-input
            v-show="condition.value === '' || !isObject(condition.value)"
            type="date"
            class="filter-value"
            v-model="condition.value"
            debounce="500"
            dense
            outlined
          />
          <q-select
            v-show="condition.value === '' || isObject(condition.value)"
            class="filter-op-selection"
            :label="t('common.lastNBack')"
            :options="lastNBackOptions"
            v-model="condition.value"
            clearable
            @update:model-value="setLastNBack(condition)"
            dense
            outlined
          />
        </template>
      </div>
      <div class="add-filter text-center">
        <q-btn
          :icon="fasCirclePlus"
          dense
          round
          flat
          @click="addCondition"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineProps, defineEmits, watch } from 'vue'
import { useI18n } from "vue-i18n"
import { fasCirclePlus, fasCircleXmark } from '@quasar/extras/fontawesome-v6'
import {getLastNBackOptions} from "src/composables/visualization";
import {isObject} from "lodash";

const props = defineProps({
  request: Object,
  field: String,
  type: String,
  isReference: Boolean,
  referenceOptions: Array[Object]
})
const emits = defineEmits(['update:request'])
const { t } = useI18n()

const joinOp = ref('$and')
const conditions = ref([])
const currId = ref(0)
const referenceSelection = ref([])
const allowedOps = computed ( () => {
  return props.type === 'str' ? strOps : ops
})
const ageAndNumber = ref('age')

const lastNBackOptions = getLastNBackOptions()
const strOps = [
  'like', 'likeCaseInsensitive', 'notLike', 'notLikeCaseInsensitive',
  'startsWith', 'endsWith', 'contains'
]
const ops = [
  'equalTo', 'notEqualTo', 'greaterThan', 'greaterThanEqualTo',
  'lessThan', 'lessThanEqualTo'
]
const unitOptions = [
  {label: t("common.age"), value: "age"},
  {label: t("common.number"), value: "number"}
]
const joinOperatorOptions = [
  {label: t("common.and"), value: "$and"},
  {label: t("common.or"), value: "$or"}
]
const ageUnits = [
  'Days', 'Weeks', 'Months', 'Years'
]
const mapOpToLabel = function (op) {
  switch (op) {
    case '$eq':
      return 'equalTo'
    case '$ne':
      return 'notEqualTo'
    case '$gt':
      return 'greaterThan'
    case '$ge':
      return 'greaterThanEqualTo'
    case '$lt':
      return 'lessThan'
    case '$le':
      return 'lessThanEqualTo'
    case '$like':
      return 'like'
    case '$ilike':
      return 'likeCaseInsensitive'
    case '$notlike':
      return 'notLike'
    case '$notilike':
      return 'notLikeCaseInsensitive'
    case '$startswith':
      return 'startsWith'
    case '$endswith':
      return 'endsWith'
    case '$contains':
      return 'contains'
    default:
      return false
  }
}
const mapLabelToOp = function (label) {
  switch (label) {
    case 'equalTo':
      return '$eq'
    case 'notEqualTo':
      return '$ne'
    case 'greaterThan':
      return '$gt'
    case 'greaterThanEqualTo':
      return '$ge'
    case 'lessThan':
      return '$lt'
    case 'lessThanEqualTo':
      return '$le'
    case 'like':
      return '$like'
    case 'likeCaseInsensitive':
      return '$ilike'
    case 'notLike':
      return '$notlike'
    case 'notLikeCaseInsensitive':
      return '$notilike'
    case 'startsWith':
      return '$startswith'
    case 'endsWith':
      return '$endswith'
    case 'contains':
      return '$contains'
    default:
      return false
  }
}

const setLastNBack = function(condition) {
  condition.operator = 'greaterThan'
  if (condition.value === null) {
    condition.value = ''
  }
}
const serializeConditions = function () {
  const fieldName = props.field
  const serializedConditions = {}
  if (props.isReference) {
    serializedConditions[fieldName] = {"$in": referenceSelection.value}
  }
  else {
    // Transform a list of conditions into a request.
    const formattedConditions = []
    conditions.value.forEach(function (condition) {
      if (condition.value !== '') {
        const formattedCondition = {}
        formattedCondition[fieldName] = {}
        let ageUnitCalculation;
        if (condition.age === "Days" && ageAndNumber.value === "age") {
          ageUnitCalculation = (condition.value / 365)
        }
        else if (condition.age === "Weeks" && ageAndNumber.value === "age") {
          ageUnitCalculation = (condition.value / 52)
        }
        else if (condition.age === "Months" && ageAndNumber.value === "age") {
          ageUnitCalculation = (condition.value / 12)
        }
        else {
          ageUnitCalculation = (condition.value)
        }

        // Handle the LAST_N_DAYS_BACK object
        formattedCondition[fieldName][mapLabelToOp(condition.operator)] = isObject(ageUnitCalculation) ? ageUnitCalculation.value : ageUnitCalculation
        formattedConditions.push(formattedCondition)
      }
    })
    if (Object.values(formattedConditions).length > 0) {
      serializedConditions[joinOp.value] = formattedConditions
    }
  }
  return serializedConditions
}
const update = () => emits('update:request', serializeConditions(), props.field)
watch(conditions, update, { deep: true })
watch(joinOp, update)
watch(referenceSelection, update)
watch(ageAndNumber, update)
watch(() => props.isReference, update)
watch(() => props.referenceOptions, (curr, prev) => {
  // Ensure currently selected values are removed if the reference option is removed.
  const currOptions = curr.map(x => x.value)
  referenceSelection.value = referenceSelection.value.filter(x => currOptions.includes(x))
  // Auto-select newly added reference options.
  const prevOptions = prev.map(x => x.value)
  currOptions.forEach(function (currOption) {
    if (!prevOptions.includes(currOption)) {
      referenceSelection.value.push(currOption)
    }
  })
})

const removeCondition = function (id) {
  const idx = conditions.value.findIndex((x) => x.id === id)
  if (idx !== -1) {
    conditions.value.splice(idx, 1)
  }
}
const addCondition = function () {
  conditions.value.push({ id: currId.value, operator: allowedOps.value[0], value: '' })
  currId.value += 1
}

onMounted( () => {
  if (props.request !== undefined && Object.keys(props.request).length > 0) {
    if (props.isReference) {
      referenceSelection.value = props.request[props.field]["$in"]
    }
    else {
      // Parse the given request into a list of conditions.
      if ('$or' in props.request) {
        joinOp.value = '$or'
      }
      props.request[joinOp.value].forEach(function (condition) {
        const op = mapOpToLabel(Object.keys(condition[props.field])[0])
        let val = Object.values(condition[props.field])[0]
        let matchingLastNBack = lastNBackOptions.filter(o => o.value === val)
        if (matchingLastNBack.length > 0) {
          val = matchingLastNBack[0]
        }
        conditions.value.push({id: currId.value, operator: op, value: val})
        currId.value += 1
      })
    }
  }
})


</script>

<style scoped>
  .container {
    display: flex;
    flex-direction: column;
    margin: 15px;
  }
  .join-op-selection {
    margin-bottom: 10px;
  }
  .filter-op-selection {
    margin: 10px 30px 10px 10px;
  }
  .filter-value {
    margin: 0px 30px 15px 10px;
  }
  .reference-field-value-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .reference-field-value-scroll {
    height: 150px;
  }
  .reference-field-value-btns {
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 10px;
  }
  .add-filter {
    /*display: flex;*/
    margin-top: 5px;
    margin-bottom: 5px;
  }
  .filter-container {
    border-color: rgb(155, 155, 155);
    border-style: solid;
    border-width: 1px;
    border-radius: 4px;
    margin-bottom: 10px;
    position: relative;
  }
  .filter-removal-btn {
    position: absolute;
    right: 3px;
    top: 3px;
  }
  .age-and-number-radio {
    display: flex;
    margin: 5px 30px 5px 0px;
  }
</style>
