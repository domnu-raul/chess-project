<script setup>
const props = defineProps({
    user: {
        type: Object,
        required: false,
    },
});
</script>

<template>
    <div class="grid grid-cols-2 bg-sky-600 rounded-lg">
        <div class="flex flex-col p-3">
            <h1
                class="text-4xl my-auto leading-relaxed text-slate-100 font-robotoslab font-bold cursor-default select-none">
                Username
            </h1>
            <img src="https://i.imgur.com/KjTdWGH.png" class="w-full rounded-md">
        </div>
        <div class="flex flex-col p-3 justify-end leading-10 text-slate-100 font-roboto font-medium">
            <p>Elo N/A</p>
            <p>Games played: N/A</p>
            <p>Victories: N/A</p>
            <p>Losses: N/A</p>
            <p>Draws: N/A</p>
        </div>

    </div>
</template>

<style scoped></style>
