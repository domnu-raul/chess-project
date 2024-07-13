<script setup>
import FormHeader from "./FormHeader.vue";
import FormInput from "./FormInput.vue";
import ToggleButton from "./ToggleButton.vue";
import { watchEffect, ref, onMounted } from "vue";
import Button from "../Button.vue";
import { auth } from "../../services/auth";

let username = ref("");
let email = ref("");
let password = ref("");
let errorMsg = ref("");

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

async function login() {
    const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
            username: username.value,
            password: password.value,
        }),
        credentials: "include",
    })
    const data = await response.json();
    if (response.status !== 200) {
        errorMsg.value = data.detail;
    } else {
        window.location.href = "/home";
    }
}

async function signup() {
    const response = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            username: username.value,
            email: email.value,
            password: password.value,
        }),
        credentials: "include",
    });
    const data = await response.json();

    if (response.status !== 200) {
        let emailError = undefined;
        let detailType = undefined;
        try {
            emailError = data.detail[0].ctx.reason;
            detailType = data.detail[0].type;
        } catch (e) {
            console.log(e);
        }

        if (typeof emailError !== "undefined") {
            errorMsg.value = data.detail[0].ctx.reason;
            return;
        }

        if (typeof detailType !== "undefined" && detailType === "string_too_short") {
            errorMsg.value = "Password must be at least 8 characters long."
            return;
        }

        errorMsg.value = data.detail;
    }
    else {
        auth.setRegistered(true);
        formSwitch.value = true;
    }
}

async function submitForm() {
    if (!username.value || !password.value) {
        errorMsg.value = "Please fill in all fields.";
        return;
    }

    if (formSwitch.value) {
        await login();
    } else {
        await signup();
    }
}

onMounted(() => {
    auth.updateRegisterStatus();
    if (auth.isRegistered) {
        formSwitch.value = true;
    }
});

</script>

<template>
    <form id="form" class="flex flex-col gap-4 bg-zinc-900 rounded-2xl p-5 relative" :class="[
        { 'slide-form-in': slideFormIn },
        { 'slide-form-out': slideFormOut },
    ]" @submit.prevent="submitForm">
        <FormHeader />
        <FormInput placeholder="Username" type="text" name="username" v-model="username" />
        <TransitionGroup name="slide-fade">
            <FormInput v-if="!formSwitch" placeholder="E-mail address" type="text" name="email" v-model="email"
                class="email-field" />
            <FormInput placeholder="Password" type="password" name="password" v-model="password" />
            <p class="font-roboto text-red-400 max-w-72">{{ errorMsg }}</p>
            <Button>{{ formSwitch ? 'Sign In' : 'Sign Up' }}</Button>
            <div class="flex flex-row justify-between items-center">
                <p class="font-roboto text-base text-slate-100 cursor-default select-none">
                    Already a member?
                </p>
                <ToggleButton v-model="formSwitch" id="is-member-checkbox" />
            </div>
        </TransitionGroup>
    </form>
</template>

<style scoped>
.slide-fade-move,
.slide-fade-enter-active,
.slide-fade-leave-active {
    transition: transform 0.3s ease-in-out, opacity 0.15s ease-in-out;
}

.slide-fade-leave-from {
    opacity: 25%;
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

@keyframes emailEnter {
    from {
        transform: translateY(-75%);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.slide-form-in {
    animation: slideFormIn 0.225s ease-in;
}

.slide-form-out {
    animation: slideFormOut 0.3s ease-in-out;
}

.email-field {
    animation: emailEnter 0.29s ease-in-out;
}
</style>
