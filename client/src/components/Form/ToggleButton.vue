<script setup>
import { ref, watchEffect } from "vue";
const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(["update:modelValue"]);

const checked = ref(props.modelValue);

watchEffect(() => {
  checked.value = props.modelValue;
});

const updateValue = (event) => {
  emit("update:modelValue", event.target.checked);
};
</script>

<template>
  <div class="relative">
    <input
      type="checkbox"
      :id="id"
      name="already-member"
      class="hidden"
      @change="updateValue"
      :checked="checked"
    />

    <label
      :for="id"
      class="w-12 h-6 bg-slate-50 rounded-full cursor-pointer shadow-md flex flex-row items-center p-1"
    >
      <svg height="16px" width="16px" class="w-full">
        <circle
          cx="8"
          cy="8"
          r="8"
          stroke-width="3"
          class="transform transition-transform duration-200 z-10"
          :class="[checked ? 'fill-green-600 translate-x-6' : 'fill-slate-600 translate-x-0']"
        />
      </svg>
    </label>
  </div>
</template>
