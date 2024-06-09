<script setup>
import FormHeader from "./FormHeader.vue";
import FormFooter from "./FormFooter.vue";
import FormInput from "./FormInput.vue";
import { ref } from "vue";

let username = ref("");
</script>

<template>
  <form class="flex flex-col bg-zinc-900 rounded-2xl p-5">
    <FormHeader />
    <FormInput
      placeholder="Username"
      type="password"
      name="username"
      v-model="username"
    />
    <FormFooter />
  </form>
</template>

<style scoped></style>
