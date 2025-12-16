/**
 * DatePicker Component
 *
 * Purpose:
 * Provides an interface for selecting dates using the PrimeVue Calendar component.
 *
 * Props:
 * - `title` (String, optional): Title displayed above the date picker to provide context.
 * - `description` (String, optional): Description displayed below the title to explain the purpose of the date picker.
 * - `initialDate` (Date, optional): Sets the initial selected date. Defaults to `null`.
 * - `minDate` (Date, optional): The earliest selectable date. Defaults to `null` (no restriction).
 * - `maxDate` (Date, optional): The latest selectable date. Defaults to `null` (no restriction).
 *
 * Events:
 * - `update:datePickerValue`: Emitted when the selected date changes, providing the new date in `YYYY-MM-DD` format.
 *
 * Special Handling:
 * - Ensures the selected date is formatted using Luxon for consistency.
 * - Dynamically handles `minDate` and `maxDate` restrictions if provided.
 */

<script setup lang="ts">
import { PRIMEVUE_DATE_FORMAT_MM_DD_YY } from "@/constants/DateFormats";
import { formatDateToYYYYMMDD } from "@/utils/DateUtils";
import Calendar from "primevue/calendar";
import { ref, watch } from "vue";

const selectedDate = ref<Date | null>(null);

const props = defineProps({
  title: {
    type: String,
    required: false,
    default: "Expiry date (optional)",
  },
  description: {
    type: String,
    required: false,
    default: "By default, this role does not expire. Set an expiry date if you want the permission to end automatically.",
  },
  initialDate: {
    type: Date,
    required: false,
    default: null,
  },
  minDate: {
    type: Date,
    required: false,
    default: null,
  },
  maxDate: {
    type: Date,
    required: false,
    default: null,
  },
});

const emit = defineEmits(["update:datePickerValue"]);

watch(
  selectedDate,
  (newValue) => {
    if (newValue) {
      const formattedDate = formatDateToYYYYMMDD(newValue);
      emit("update:datePickerValue", formattedDate);
    }
  }
);

selectedDate.value = props.initialDate;
</script>


<template>
  <div class="date-picker-container">
    <div v-if="props.title && props.description" class="title-description-area">
      <div class="title">{{ props.title }}</div>
      <div class="description">{{ props.description }}</div>
    </div>

    <div class="date-picker-area">
      <div class="picker-title" v-if="props.title">Expiry date:</div>
      <Calendar
        v-model="selectedDate"
        :placeholder="'mm/dd/yyyy'"
        :minDate="props.minDate || undefined"
        :maxDate="props.maxDate || undefined"
        :dateFormat="PRIMEVUE_DATE_FORMAT_MM_DD_YY"
        showIcon
        iconDisplay="input"
        inputId="icondisplay"
        :style="{ width: '100%' }"
        :showInput="false"
      />
    </div>
  </div>
</template>


<style lang="scss" scoped>
@use "@/assets/styles/design-tokens" as tokens;
@use "@/assets/styles/utility-mixins" as mixins;


.date-picker-container {
  // Apply the two-column responsive container mixin
  @include mixins.two-column-container-responsive();
}

.date-picker-container > .title-description-area {
  .title {
    font-family: BC Sans;
    font-weight: 700;
    font-size: 14px;
    line-height: 20px;
    letter-spacing: 0.16px;
  }
}

.date-picker-container > .date-picker-area {
  width: 100%; // ensure inner controls fill the flex item
}

.date-picker-container > .title-description-area:empty {
  display: none;
}

.description {
  margin-top: 0.5rem;
  font-size: 14px;
  line-height: 20px;
  color: #6c757d;
}

.picker-title {
  font-weight: 400;
  font-size: 12px;
  line-height: 16px;
  letter-spacing: 0.32px;
}
</style>