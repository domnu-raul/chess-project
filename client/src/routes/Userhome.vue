<script setup>
import UserProfile from '../components/UserProfile.vue';
import Button from '../components/Button.vue';
import GameHistory from '../components/GameHistory.vue';
import { ref, onMounted } from 'vue';
import { connection, } from '../services/connection';
import { auth } from '../services/auth';
import { game } from '../services/game';


const user = ref({});
const history = ref([]);

const matchmakingMsg = "Finding a match...";
const playButtonMsg = ref('Play');
const timer = ref(0);
let interval;

function getUser() {
    fetch('http://localhost:8000/user/me', {
        method: 'GET',
        credentials: 'include',
    })
        .then((res) => res.json())
        .then((data) => {
            user.value = data.details;
            user.value.username = data.username;
        })
        .catch((err) => console.error(err));
}

function getHistory() {
    fetch('http://localhost:8000/user/games', {
        method: 'GET',
        credentials: 'include',
    })
        .then((res) => res.json())
        .then((data) => {
            history.value = data;
        })
        .catch((err) => console.error(err));

}

function signOut() {
    fetch('http://localhost:8000/auth/logout', {
        method: 'POST',
        credentials: 'include',
    })
        .then((res) => {
            if (res.status === 200) {
                window.location.href = '/';
            }
        })
        .catch((err) => console.error(err));
}

function getFormattedTimer() {
    const minutes = Math.floor(timer.value / 60);
    const seconds = timer.value % 60;
    const formattedMinutes = minutes.toString().padStart(2, '0');
    const formattedSeconds = seconds.toString().padStart(2, '0');
    return `${formattedMinutes}:${formattedSeconds}`;
}

function buttonClick() {
    if (connection.isConnected) {
        connection.disconnect();
        clearInterval(interval);
        timer.value = 0;
        playButtonMsg.value = 'Play';
        return;
    }
    connection.makeConnection("ws://localhost:8000/matchmaking?token=" + auth.token);

    connection.setListener(() => {

        playButtonMsg.value = `${matchmakingMsg}\n(${getFormattedTimer()})`;
        timer.value = timer.value + 1;

        interval = setInterval(() => {
            playButtonMsg.value = `${matchmakingMsg}\n(${getFormattedTimer()})`;
            timer.value = timer.value + 1;
        }, 1000);
        connection.setListener((message) => {
            const data = JSON.parse(message.data);
            window.location.href = `/game?gameId=${data.game_id}`;
        });
    });
}

onMounted(() => {
    getUser();
    getHistory();
});

</script>

<template>
    <div style="grid-area: l;" class="flex flex-col p-5 bg-zinc-900 rounded-2xl justify-between">
        <UserProfile :user="user" :is-self="true" />
        <Button class="text-3xl py-12" :on-click="buttonClick">{{ playButtonMsg }}</Button>
        <Button class="text-3xl py-12 bg-zinc-800 hover:bg-slate-800" :on-click="signOut">Sign out</Button>
    </div>
    <div style="grid-area: r;">
        <GameHistory :data="history" />
    </div>
</template>

<style scoped></style>
