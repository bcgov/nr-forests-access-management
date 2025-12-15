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
import { DATE_FORMAT_YYYY_MM_DD } from "@/constants/DateFormats";
import { formatDateToYYYYMMDD } from "@/utils/DateUtils";
import Calendar from "primevue/calendar";
import { ref, watch } from "vue";

const selectedDate = ref<Date | null>(null);
const PRIMEVUE_DATE_FORMAT = "yy-mm-dd";  // YYYY-MM-DD format for PrimeVue Calendar

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
    <div v-if="title && description" class="title-description-area">
      <div class="title">{{ title }}</div>
      <div class="description">{{ description }}</div>
    </div>
    <div class="date-picker-area">
      <div class="picker-title" v-if="title">Expiry date:</div>
      <Calendar
        v-model="selectedDate"
        :placeholder="DATE_FORMAT_YYYY_MM_DD"
        :minDate="minDate || undefined"
        :maxDate="maxDate || undefined"
        :dateFormat="PRIMEVUE_DATE_FORMAT"
        showIcon
        iconDisplay="input"
        inputId="icondisplay"
        :style="{ width: '100%' }"
        :showInput="false"
      ></Calendar>
    </div>
  </div>
</template>

<style scoped>
.date-picker-container {
  display: flex;
  flex-direction: row;
  gap: 4.5rem;
  align-items: flex-end;
}

.date-picker-container > .title-description-area {
  flex: 1 1 60%;
  .title {
    font-family: BC Sans;
    font-weight: 700;
    font-size: 14px;
    line-height: 20px;
    letter-spacing: 0.16px;
  }
}

.date-picker-container > .date-picker-area {
  flex: 1 1 40%;
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

.date-picker-area {
  flex: 1;
}

.picker-title {
    font-weight: 400;
    font-size: 12px;
    line-height: 16px;
    letter-spacing: 0.32px;
}
</style>