<script setup>
import Header from './Header.vue';
const props = defineProps({
    layout: String
});
</script>

<template>
    <div id="base">
        <Header/>
        <div id="container" :class="layout">
            <slot/>
        </div>
    </div>
</template>