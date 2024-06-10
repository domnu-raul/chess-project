<script setup>
import FormHeader from "./FormHeader.vue";
import FormInput from "./FormInput.vue";
import ToggleButton from "./ToggleButton.vue";
import { Transition } from "vue";
import { ref } from "vue";

let username = ref("");
let password = ref("");
let confirmPassword = ref("");
let isMember = ref(false);
</script>

<template>
  <Transition name="flex-slide">
    <form class="flex flex-col gap-4 bg-zinc-900 rounded-2xl p-5">
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
  </Transition>
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

.slide-fade-enter-to {
  opacity: 100%;
}

.slide-fade-enter-from {
  opacity: 100%;
}

.slide-fade-leave-active {
  position: absolute;
}

.flex-slide-enter-active,
.flex-slide-leave-active {
  transition: flex-grow 0.3s ease-in-out, flex-shrink 0.3s ease-in-out;
  max-height: min-content;
}

</style>
