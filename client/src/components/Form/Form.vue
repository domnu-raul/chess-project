<script setup>
import FormHeader from "./FormHeader.vue";
import FormInput from "./FormInput.vue";
import ToggleButton from "./ToggleButton.vue";
import { Transition, watchEffect } from "vue";
import { ref } from "vue";

let username = ref("");
let password = ref("");
let confirmPassword = ref("");

let formSwitch = ref(false);
let lastFormSwitch = ref(false);

let slideFormIn = ref(false);
let slideFormOut = ref(false);

watchEffect(() => {
  if (formSwitch.value !== lastFormSwitch.value) {
    let form = document.getElementById("form");
    let initialHeight = form.clientHeight;
    form.style.setProperty("--initial-height", `${initialHeight}px`);

    if (formSwitch.value) {
      slideFormIn.value = true;
      slideFormOut.value = false;
    } else {
      slideFormIn.value = false;
      slideFormOut.value = true;
    }

    lastFormSwitch.value = formSwitch.value;
  }
});

function submitForm() {
  console.log({
    username: username.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
  });
}
</script>

<template>
  <form
    id="form"
    class="flex flex-col gap-4 bg-zinc-900 rounded-2xl p-5"
    :class="[
      { 'slide-form-in': slideFormIn },
      { 'slide-form-out': slideFormOut },
    ]"
    @submit.prevent="submitForm"
  >
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
      class="z-[1]"
    />
    <TransitionGroup name="slide-fade">
      <FormInput
        v-if="!formSwitch"
        placeholder="Confirm Password"
        type="password"
        name="confirm-password"
        v-model="confirmPassword"
      />
      <button
        type="submit"
        class="bg-green-700 font-roboto font-black text-3xl text-slate-100 w-full py-4 rounded-lg cursor-default hover:bg-green-800 hover:text-slate-50 select-none"
      >
        Signup
      </button>
      <div class="flex flex-row justify-between items-center">
        <p class="font-roboto text-base text-slate-100 cursor-default select-none">Already a member?</p>
        <ToggleButton v-model="formSwitch" id="is-member-checkbox" />
      </div>
    </TransitionGroup>
  </form>
</template>

<style scoped>
.slide-fade-move,
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: transform 0.3s ease-in-out, opacity 0.15s ease-out;
}

.slide-fade-leave-from {
  opacity: 100%;
}

.slide-fade-leave-to {
  opacity: 0%;
}

.slide-fade-leave-active {
  position: absolute;
}

@keyframes slideFormIn {
  from {
    min-height: var(--initial-height);
  }
  to {
    min-height: calc(var(--initial-height) - 5.5rem);
  }
}

@keyframes slideFormOut {
  from {
    max-height: var(--initial-height);
  }

  to {
    max-height: calc(var(--initial-height) + 5.5rem);
  }
}

.slide-form-in {
  animation: slideFormIn 0.225s ease-in;
}

.slide-form-out {
  animation: slideFormOut 0.3s ease-in-out;
}
</style>
