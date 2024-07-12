<script setup>
import { computed, ref } from 'vue';
import { game } from '../services/game';

const board = computed(() => {
    let fen = game.fen;

    let rows = fen.split(' ')[0].split('/');
    let board = [];
    for (let row of rows) {
        let boardRow = [];
        for (let char of row) {
            if (isNaN(char)) {
                boardRow.push(char);
            } else {
                for (let i = 0; i < parseInt(char); i++) {
                    boardRow.push(' ');
                }
            }
        }
        board.push(boardRow);
    }

    return board;
});


</script>

<template>
    <div class="grid grid-rows-8 grid-cols-8">
    </div>
</template>
