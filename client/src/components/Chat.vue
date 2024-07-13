<script setup>
import { game } from '../services/game';
import { computed, ref, onUpdated } from 'vue';
const messages = computed(() => {
    return game.chat;
});

const currentMessage = ref('');

function sendMessage() {
    if (currentMessage.value === '/resign') {
        game.resign();
        currentMessage.value = '';
        return;
    }
    game.sendChatMessage(currentMessage.value);
    currentMessage.value = '';
}

onUpdated(() => {
    const chatbox = document.getElementById('chatbox');
    chatbox.scrollTop = chatbox.scrollHeight;
});

</script>

<template>
    <form @submit.prevent="sendMessage" class="flex flex-col w-full h-full">
        <div id="chatbox" class="flex flex-col h-[280px] gap-2 overflow-y-auto">
            <div v-for="message in messages" :key="message.id" class="flex flex-col w-full rounded-xl px-2 relative">
                <p class="font-roboto font-bold text-zinc-100">{{ message.sender }} at {{ message.time }}:</p>
                <p class="font-roboto text-zinc-100 text-wrap min-w-full hyphens-auto">{{ message.message }}</p>
            </div>
            <span id="bottom" />
        </div>
        <input type="text" v-model="currentMessage"
            class=" w-full pr-14 bg-zinc-800 px-3 py-1 rounded-lg placeholder:text-gray-400 placeholder:font-roboto placeholder:text-xl caret-slate-100 text-slate-100 text-xl font-roboto text-md"
            placeholder="Type a message...">
        <p class="font-roboto text-sm text-zinc-500 h-1 mt-1"><b>Commands:</b> /resign</p>
    </form>
</template>
