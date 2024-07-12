<script setup>
import Button from '../components/Button.vue';
import UserProfile from '../components/UserProfile.vue';
import ChessBoard from '../components/ChessBoard.vue';
import { game } from '../services/game';
import { onBeforeMount, computed } from 'vue';

const opponent = computed(() => {
    console.log(game.opponent);
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
    <div style="grid-area: l;" class="flex flex-col p-5 bg-zinc-900 rounded-2xl justify-between">
        <UserProfile :user="opponent" :is-self="false" />
        <Button class="text-3xl py-9" :on-click="buttonClick">Play</Button>
        <Button class="text-3xl py-9 bg-zinc-800 hover:bg-slate-800" :on-click="signOut">Sign out</Button>
    </div>
    <div style="grid-area: r;">
        <ChessBoard />
    </div>
</template>

<style scoped></style>
