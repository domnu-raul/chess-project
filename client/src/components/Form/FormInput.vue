<script setup>
import VisibilityButton from './VisibilityButton.vue';
import { computed, ref } from 'vue';

const props = defineProps({
  type: String,
  name: String,
  placeholder: String,
  modelValue: String,
  classValue: String,
});

const buttonId = props.name + "-visibility";
const isPassword = props.type === "password";

const viewPassword = ref(false);
const inputType = computed(() => {
  if (isPassword) {
    return viewPassword.value ? "text" : "password";
  }
  return props.type;
});

const emit = defineEmits(["update:modelValue"]);
function updateValue(event) {
  emit("update:modelValue", event.target.value);
}
</script>

<template>
  <div class="relative" :class="classValue">
  <input
    :type="inputType"
    :placeholder="placeholder"
    :name="name"
    :value="modelValue"
    @input="updateValue"
    class=" w-full pr-14 bg-zinc-800 px-3 py-5 rounded-lg placeholder:text-gray-400 placeholder:font-roboto placeholder:text-xl caret-slate-100 text-slate-100 text-xl"
    >
    </input>
    <VisibilityButton v-if="isPassword" :id="buttonId" v-model="viewPassword"/>

    
  </div>
</template>
