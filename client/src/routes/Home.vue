<script setup>
import Form from '../components/Form/Form.vue';
</script>

<template>
    <div style="grid-area: l"
        class="flex flex-col text-5xl text-slate-100 font-robotoslab font-black justify-evenly items-center">
        <h1 class="w-fit cursor-default select-none">
            Play Chess anytime, <br />
            anywhere.
        </h1>
        <h1 class="w-fit mb-12 cursor-default select-none"> Join our community!</h1>
    </div>

    <div style="grid-area: r" class="flex flex-col justify-center items-center w-fit h-full max-w-full">
        <Form />
    </div>
</template>


<style scoped></style>
