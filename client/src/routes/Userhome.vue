<script setup>
import UserProfile from '../components/UserProfile.vue';
import Button from '../components/Button.vue';

</script>

<template>
    <div style="grid-area: l;" class="flex flex-col p-5 bg-zinc-900 rounded-2xl justify-between">
        <UserProfile />
        <Button class="text-5xl py-10">Play</Button>
        <Button class="text-5xl py-10 bg-zinc-800 hover:bg-slate-800">Sign out</Button>
    </div>
    <div style="grid-area: r;"></div>
</template>

<style scoped></style>
