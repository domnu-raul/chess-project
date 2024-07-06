<script setup>
import UserProfile from '../components/UserProfile.vue';
import Button from '../components/Button.vue';
import { ref, onMounted } from 'vue';

const user = ref({});

function getUser() {
    fetch('http://localhost:8000/user/me', {
        method: 'GET',
        credentials: 'include',
    })
        .then((res) => res.json())
        .then((data) => {
            user.value.username = data.username;
            user.value.elo = data.details.elo_rating;
            user.value.gamesPlayed = data.details.games_played;
            user.value.victories = data.details.victories;
            user.value.losses = data.details.losses;
            user.value.draws = data.details.draws;
        })
        .catch((err) => console.error(err));

    console.log(user.value);
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

onMounted(() => {
    getUser();
});

</script>

<template>
    <div style="grid-area: l;" class="flex flex-col p-5 bg-zinc-900 rounded-2xl justify-between">
        <UserProfile :user="user" :is-self="true" />
        <Button class="text-5xl py-9">Play</Button>
        <Button class="text-5xl py-9 bg-zinc-800 hover:bg-slate-800" :on-click="signOut">Sign out</Button>
    </div>
    <div style="grid-area: r;"></div>
</template>

<style scoped></style>
