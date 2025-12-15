/**
 * DatePicker Component
 *
 * Purpose:
 * Provides a interface for selecting dates using the PrimeVue Calendar component.
 * It supports features for customizable titles and descriptions.
 *
 * Usage and Props:
 * - `modelValue` (String, optional): Bind this prop to enable two-way data binding. Represents the selected date in `YYYY-MM-DD` format.
 * - `title` (String, optional): Title displayed above the date picker to provide context.
 * - `description` (String, optional): Description displayed below the title to explain the purpose of the date picker.
 *
 * Events:
 * - `update:modelValue`: Emitted when the selected date changes, providing the new date in `YYYY-MM-DD` format.
 *
 * Special Handling:
 * - Ensures the selected date cannot be earlier than the current date.
 * - Dates are formatted using Luxon for consistency.
 * - `minDate` is dynamically set to the current date in the BC timezone (America/Vancouver).
 */

<script setup lang="ts">
import { DATE_FORMAT_YYYY_MM_DD } from "@/constants/DateFormats";
import { currentDateInBCTimezone, formatDateToYYYYMMDD } from "@/utils/DateUtils";
import Calendar from "primevue/calendar";
import { ref, watch } from "vue";

const selectedDate = ref<Date | null>(null);
const minDate = ref(currentDateInBCTimezone());

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
    type: String,
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

if (props.initialDate) {
  selectedDate.value = new Date(props.initialDate);
}
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
        dateFormat="yy-mm-dd"
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