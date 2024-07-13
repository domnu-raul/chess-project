<script setup>
import Button from '../components/Button.vue';
import UserProfile from '../components/UserProfile.vue';
import ChessBoard from '../components/ChessBoard.vue';
import Chat from '../components/Chat.vue';
import { game } from '../services/game';
import { onBeforeMount, computed } from 'vue';

const opponent = computed(() => {
    return game.opponent;
});

onBeforeMount(() => {
    // get gameId from path Query
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('gameId');
    game.initGame(gameId);
});
</script>

<template>
    <div style="grid-area: l;" class="flex flex-col p-5 bg-zinc-900 rounded-2xl justify-between w-auto h-full">
        <UserProfile :user="opponent" :is-self="false" />
        <Chat />
    </div>
    <div style="grid-area: r;" class="flex flex-col p-5 bg-zinc-900 rounded-2xl justify-between w-fit h-fit">
        <ChessBoard />
    </div>
</template>

<style scoped></style>
