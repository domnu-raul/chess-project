<script setup>
import { ref, computed, watchEffect } from "vue";
import Home from "./routes/Home.vue";
import Userhome from "./routes/Userhome.vue";
import Chessgame from "./routes/Chessgame.vue";
import BasePage from "./components/BasePage.vue";
//import NotFound from './routes/NotFound.vue'
import { auth } from './services/auth'
import { game } from './services/game'

const NotFound = {
    template: "<div>Not Found</div>"
};

const routes = {
    "/": {
        component: Home,
        layout: "home-layout",
        path: "/"
    },
    "/home": {
        component: Userhome,
        layout: "left-pane-layout",
        path: "/home"
    },
    "/game": {
        component: Chessgame,
        layout: "left-pane-layout",
        path: "/game"
    }
}

const currentPath = ref(window.location.pathname);

window.addEventListener("hashchange", () => {
    currentPath.value = window.location.pathname;
});

const currentView = computed(() => {
    auth.updateAuthStatus();
    if (!auth.isAuthenticated) {
        return routes["/"]
    }
    if (auth.isAuthenticated && currentPath.value == "/") {
        return routes["/home"];
    }
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
