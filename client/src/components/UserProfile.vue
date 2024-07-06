<script setup>
import { ref, onMounted } from 'vue';
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

const imgUrl = ref('http://localhost:8000/user/me/picture');

function updateImgUrl() {
    imgUrl.value = 'http://localhost:8000/user/me/picture?t=' + new Date().getTime();
}

onMounted(() => {
    updateImgUrl();
    if (props.isSelf) {
        imgUrl.value = 'http://localhost:8000/user/me/picture';
    } else {
        imgUrl.value = 'http://localhost:8000/user/' + props.user.id + '/picture';
    }
})


</script>

<template>
    <div class="grid grid-cols-2 bg-sky-600 rounded-lg">
        <div class="flex flex-col p-3 col-start-1 ">
            <h1
                class="text-4xl my-2 leading-relaxed text-slate-100 font-robotoslab font-bold cursor-default select-none text-wrap ">
                {{ props.user.username }}
            </h1>
            <ImageUpload v-if="props.isSelf" :side-effect="updateImgUrl">

                <img :src="imgUrl" class="w-full rounded-md">
            </ImageUpload>
            <img v-else :src="imgUrl" class="w-full rounded-md">

        </div>
        <div class="flex flex-col p-3 justify-end leading-10 text-slate-100 font-roboto font-medium col-start-2">
            <p>Elo rating: {{ props.user.elo }}</p>
            <p>Games Played: {{ props.user.gamesPlayed }}</p>
            <p>Victories: {{ props.user.victories }}</p>
            <p>Losses: {{ props.user.losses }}</p>
            <p>Draws: {{ props.user.draws }}</p>
        </div>

    </div>
</template>

<style scoped></style>
