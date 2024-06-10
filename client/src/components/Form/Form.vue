<script setup>
import FormHeader from "./FormHeader.vue";
import FormInput from "./FormInput.vue";
import ToggleButton from "./ToggleButton.vue";
import { Transition, watchEffect } from "vue";
import { ref } from "vue";

let username = ref("");
let password = ref("");
let confirmPassword = ref("");
let isMember = ref(false);
// if isMember was false and is now true, slide form in
// if isMember was true and is now false, slide form out
let lastIsMember = ref(false);
let slideFormIn = ref(false);
let slideFormOut = ref(false);

watchEffect(() => {
  if (isMember.value !== lastIsMember.value) {
    if (isMember.value) {
      slideFormIn.value = true;
      slideFormOut.value = false;
    } else {
      slideFormIn.value = false;
      slideFormOut.value = true;
    }

    lastIsMember.value = isMember.value;
  }
});
</script>

<template>
  <form
    id="form"
    class="flex flex-col gap-4 bg-zinc-900 rounded-2xl p-5"
    :class="[
      { 'slide-form-in': slideFormIn },
      { 'slide-form-out': slideFormOut },
    ]"
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
        v-if="!isMember"
        placeholder="Confirm Password"
        type="password"
        name="confirm-password"
        v-model="confirmPassword"
      />
      <button
        type="submit"
        class="bg-green-700 font-roboto font-black text-3xl text-slate-100 w-full py-4 rounded-lg cursor-default hover:bg-green-800 hover:text-slate-50"
      >
        Signup
      </button>
      <div class="flex flex-row justify-between items-center">
        <p class="font-roboto text-xl text-slate-100">Already a member?</p>
        <ToggleButton v-model="isMember" id="is-member-checkbox" />
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
    min-height: 95%;
  }
  to {
    min-height: calc(95% - 4.5rem)
  }
}

@keyframes slideFormOut {
  from {
    max-height: calc(95% - 4.5rem)
  }

  to {
    max-height: 100%;
  }
}

.slide-form-in {
  animation: slideFormIn 0.3s ease-in;
}

.slide-form-out {
  animation: slideFormOut 0.3s ease-out;
}
</style>
