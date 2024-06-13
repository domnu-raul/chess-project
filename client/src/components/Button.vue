<script setup>
const props = defineProps({
    type: {
        type: String,
        required: true
    },
    classValue: {
        type: String,
        required: false
    },
    disabled: {
        type: Boolean,
        default: false
    },
    onClick: {
        type: Function,
        default: () => () => { }
    }
})
</script>

<template>
    <button :type="type"
        class="bg-green-700 font-roboto font-black text-3xl text-slate-100 w-full py-4 rounded-lg cursor-default hover:bg-green-800 hover:text-slate-50 select-none"
        :disabled="disabled" @click="onClick" :class="classValue">
        <slot />
    </button>
</template>

<style scoped></style>
