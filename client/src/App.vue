<script setup>
import { ref, computed } from "vue";
import Home from "./routes/Home.vue";
import Userhome from "./routes/Userhome.vue";
import Chessgame from "./routes/Chessgame.vue";
import BasePage from "./components/BasePage.vue";
//import NotFound from './routes/NotFound.vue'

const NotFound = {
    template: "<div>Not Found</div>"
};

const routes = {
    "/": {
        component: Home,
        layout: "home-layout"
    },
    "/home": {
        component: Userhome,
    },
    "/game": {
        component: Chessgame,
    }
}

const currentPath = ref(window.location.pathname);

window.addEventListener("hashchange", () => {
    currentPath.value = window.location.pathname;
});

const currentView = computed(() => {
    return routes[currentPath.value] || NotFound;
});
</script>

<template>
    <!-- <a href="/home">Home</a>
  <a href="/game">Game</a> -->
    <BasePage :layout="currentView.layout">
        <component :is="currentView.component" />
    </BasePage>
</template>

<style scoped></style>
