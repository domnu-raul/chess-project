<script setup>
import { ref, computed, watchEffect } from "vue";
import Home from "./routes/Home.vue";
import Userhome from "./routes/Userhome.vue";
import Chessgame from "./routes/Chessgame.vue";
import BasePage from "./components/BasePage.vue";
//import NotFound from './routes/NotFound.vue'
import { store } from './services/auth'

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
    store.updateAuthStatus();
    if (!store.isAuthenticated) {
        return routes["/"]
    }
    if (store.isAuthenticated && currentPath.value == "/") {
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
