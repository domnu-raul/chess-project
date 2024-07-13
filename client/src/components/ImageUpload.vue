<script setup>
import { defineProps, ref, reactive } from 'vue';
import VuePictureCropper, { cropper } from 'vue-picture-cropper';

const props = defineProps({
    sideEffect: {
        type: Function,
        required: false,
        default: () => () => { }
    }
})

const size = '96px'
const pic = ref('')
const isShowModal = ref(false)
const uploadInput = ref(null)
const result = reactive({
    dataURL: '',
    blobURL: '',
})

function uploadImage(blob) {
    const formData = new FormData();
    formData.append('file', blob, 'profile.png');

    fetch('http://localhost:8000/user/me/picture', {
        method: 'POST',
        credentials: 'include',
        body: formData
    })
        .then((res) => res.json())
        .then((data) => console.log(data))
        .then(() => {
            props.sideEffect();
        })
        .catch((err) => console.error(err));
}

function getImage(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = () => {
        pic.value = String(reader.result)

        isShowModal.value = true

        if (!uploadInput.value) return
        uploadInput.value.value = ''
    }
    reader.readAsDataURL(file);
}

async function setImage() {
    if (!cropper) return
    const base64 = cropper.getDataURL()
    const blob = await cropper.getBlob()
    if (!blob) return

    result.dataURL = base64
    result.blobURL = URL.createObjectURL(blob)
    uploadImage(blob)
    isShowModal.value = false
}


function ready() {
    console.log('Cropper is ready.')
}

function reset() {
    if (!cropper) return
    cropper.reset()
}
</script>

<template>
    <div class="flex relative group">
        <slot />
        <input class="absolute w-full h-full opacity-0 cursor-pointer" type="file" accept="image/*"
            @change="(event) => getImage(event)" />
        <span
            class="absolute w-full h-full bg-slate-800 bg-opacity-0 group-hover:bg-opacity-50 rounded-md pointer-events-none flex flex-row justify-center items-center">
            <svg xmlns="http://www.w3.org/2000/svg" :height="size" viewBox="0 -960 960 960" :width="size" fill="#e2e8f0"
                class="group-hover:opacity-100 opacity-0 fill-slate-50">
                <path
                    d="M240-160q-33 0-56.5-23.5T160-240v-80q0-17 11.5-28.5T200-360q17 0 28.5 11.5T240-320v80h480v-80q0-17 11.5-28.5T760-360q17 0 28.5 11.5T800-320v80q0 33-23.5 56.5T720-160H240Zm200-486-75 75q-12 12-28.5 11.5T308-572q-11-12-11.5-28t11.5-28l144-144q6-6 13-8.5t15-2.5q8 0 15 2.5t13 8.5l144 144q12 12 11.5 28T652-572q-12 12-28.5 12.5T595-571l-75-75v286q0 17-11.5 28.5T480-320q-17 0-28.5-11.5T440-360v-286Z" />
            </svg> </span>
    </div>

    <div v-show="isShowModal" class="flex absolute w-screen h-screen top-0 left-0  bg-zinc-800 bg-opacity-75">
        <div class="flex flex-col gap-5 w-fit h-fit m-auto items-center">
            <VuePictureCropper :boxStyle="{
                width: 'auto',
                height: 'calc(100vh * 2/3)',
                backgroundColor: '#f8f8f8',
            }" :img="pic" :options="{
                viewMode: 1,
                dragMode: 'crop',
                aspectRatio: 1,
            }" @ready="ready" />
            <div class="flex flex-row w-full gap-5 h-fit self-start">
                <button @click="setImage" class="bg-green-600 hover:bg-green-700 p-2 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" height="48px" viewBox="0 -960 960 960" width="48px"
                        fill="#e2e8f0">
                        <path
                            d="m389-369 299-299q10.91-11 25.45-11Q728-679 739-668t11 25.58q0 14.58-10.61 25.19L415-292q-10.91 11-25.45 11Q375-281 364-292L221-435q-11-11-11-25.5t11-25.5q11-11 25.67-11 14.66 0 25.33 11l117 117Z" />
                    </svg>
                </button>
                <button @click="isShowModal = false" class="bg-slate-700 hover:bg-slate-600 p-2 rounded-full w-16 h-16">
                    <svg xmlns="http://www.w3.org/2000/svg" height="48px" viewBox="0 -960 960 960" width="48px"
                        fill="#e2e8f0">
                        <path
                            d="m249-207-42-42 231-231-231-231 42-42 231 231 231-231 42 42-231 231 231 231-42 42-231-231-231 231Z" />
                    </svg>
                </button>
            </div>
        </div>
    </div>
</template>
