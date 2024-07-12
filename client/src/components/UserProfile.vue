<script setup>
import { ref, onMounted, computed } from 'vue';
import ImageUpload from './ImageUpload.vue';


const props = defineProps({
    user: {
        type: Object,
        required: true
    },
    isSelf: {
        type: Boolean,
        required: false,
        default: false
    }
})

const random = ref(0);

const imgUrl = computed(() => {
    let url;
    if (props.isSelf) {
        url = 'http://localhost:8000/user/me/picture';
    } else {
        url = 'http://localhost:8000/user/' + props.user.id + '/picture';
    }

    return url + '?t=' + random.value;
})

function updateImgUrl() {
    random.value = Math.random();
}

</script>

<template>
    <div class="grid grid-cols-2 rounded-lg" :class="[props.isSelf ? 'bg-sky-600' : 'bg-red-700']">
        <div class="flex flex-col p-3 col-start-1 ">
            <h1
                class="text-3xl leading-relaxed text-slate-100 font-robotoslab font-bold cursor-default select-none text-wrap ">
                {{ props.user.username }}
            </h1>
            <ImageUpload v-if="props.isSelf" :side-effect="updateImgUrl">

                <img :src="imgUrl" class="w-full rounded-md">
            </ImageUpload>
            <img v-else :src="imgUrl" class="w-full rounded-md">

        </div>
        <div class="flex flex-col p-3 justify-end leading-10 text-slate-100 font-roboto font-medium col-start-2">
            <p>Elo rating: {{ props.user.elo_rating }}</p>
            <p>Games Played: {{ props.user.games_played }}</p>
            <p>Victories: {{ props.user.wins }}</p>
            <p>Losses: {{ props.user.losses }}</p>
            <p>Draws: {{ props.user.draws }}</p>
        </div>

    </div>
</template>

<style scoped></style>
