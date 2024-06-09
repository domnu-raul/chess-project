<script setup>
import FormHeader from "./FormHeader.vue";
import FormInput from "./FormInput.vue";
import SwitchButton from "./SwitchButton.vue";
import { ref } from "vue";

let username = ref("");
let password = ref("");
let confirmPassword = ref("");
let isMember = ref(false);
</script>

<template>
  <form class="flex flex-col gap-5 bg-zinc-900 rounded-2xl p-5">
    <FormHeader />
      <FormInput
        placeholder="Username"
        type="text"
        name="username"
        v-model="username"
      />
      <FormInput
        placeholder="Password"
        type="password"
        name="password"
        v-model="password"
      />
      <FormInput v-if="!isMember"
        placeholder="Confirm Password"
        type="password"
        name="confirm-password"
        v-model="confirmPassword"
      />
    <button type="submit" class="bg-green-700 font-roboto font-black text-4xl text-slate-100 w-full py-6 rounded-lg cursor-default hover:bg-green-800 hover:text-slate-50">
      Signup
    </button>
    <div class="flex flex-row justify-between items-center">
      <p class="font-roboto text-xl text-slate-100">Already a member?</p>
      <SwitchButton v-model="isMember" id="is-member-checkbox"/>
    </div>
  </form>
</template>

<style scoped></style>
