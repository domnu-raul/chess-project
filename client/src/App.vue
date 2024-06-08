<script setup>
import HelloWorld from './components/HelloWorld.vue'
import {ref, computed} from Vue
import Home from './routes/Home.vue'
import Userhome from './routes/Userhome.vue'
import Chessgame from './routes/Chessgame.vue'

const routes = {
  "/": Home,
  "/home": Userhome,
  "/game": Chessgame,
}

const currentPath = ref.

</script>

<template>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
