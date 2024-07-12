<script setup>
import { ref, onMounted, computed } from 'vue';
const props = defineProps({
    data: {
        type: Array,
        required: true,
    }
})

const perPage = 8;
const page = ref(1);
const numPages = computed(() => {
    return Math.ceil(props.data.length / perPage);
});
const items = computed(() => {
    return props.data.slice((page.value - 1) * perPage, page.value * perPage);
});

</script>

<template>
    <div class="flex flex-col w-full h-full bg-zinc-900 rounded-2xl p-5">
        <h2 class="font-roboto font-bold text-2xl text-slate-50 mb-4">Game History</h2>

        <table class="table-fixed mb-auto">
            <thead class="font-roboto text-xl text-slate-50">
                <th>
                    Opponent
                </th>
                <th>
                    Outcome
                </th>
                <th>
                    Elo Gain
                </th>
            </thead>
            <tbody class="font-roboto text-base text-slate-50">
                <tr v-for="game in items" :key="game.id" :class="{
                    'loss-row': game.winner == game.opponent.id,
                    'draw-row': game.winner == null,
                    'win-row': game.winner != null && game.winner != game.opponent.id,
                    ' border-y-slate-50 border-solid border-t-2': true
                }">
                    <td class="p-3">
                        {{ game.opponent.username }}
                    </td>
                    <td class="p-3" v-if="game.winner == game.opponent.id">
                        Loss
                    </td>
                    <td class="p-3" v-else-if="game.winner == null">
                        Draw
                    </td>
                    <td v-else>
                        Win
                    </td>
                    <td>
                        {{ game.gained_elo }}
                    </td>
                </tr>
            </tbody>
        </table>

        <div class="flex flex-row gap-2">
            <button v-for="i in numPages" :key="i" @click="page = i" :class="{
                'bg-zinc-700': i == page,
                'bg-zinc-800': i != page
            }" class="font-roboto text-xl text-slate-50 px-4 py-2 rounded-lg cursor-pointer">
                {{ i }}
            </button>
        </div>
    </div>
</template>

<style scoped></style>
