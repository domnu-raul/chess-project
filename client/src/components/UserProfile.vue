<script setup>
import { onMounted, ref } from 'vue';

const user = ref({
    username: '',
    elo: 0,
    gamesPlayed: 0,
    victories: 0,
    losses: 0,
    draws: 0,
});

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

onMounted(() => {
    getUser();
});
</script>

<template>
    <div class="grid grid-cols-2 bg-sky-600 rounded-lg">
        <div class="flex flex-col p-3 col-start-1 ">
            <h1
                class="text-3xl my-2 leading-relaxed text-slate-100 font-robotoslab font-bold cursor-default select-none text-wrap ">
                {{ user.username }}
            </h1>
            <img src="http://localhost:8000/user/me/picture" class="w-full rounded-md">
        </div>
        <div class="flex flex-col p-3 justify-end leading-10 text-slate-100 font-roboto font-medium col-start-2">
            <p>Elo rating: {{ user.elo }}</p>
            <p>Games Played: {{ user.gamesPlayed }}</p>
            <p>Victories: {{ user.victories }}</p>
            <p>Losses: {{ user.losses }}</p>
            <p>Draws: {{ user.draws }}</p>
        </div>

    </div>
</template>

<style scoped></style>
