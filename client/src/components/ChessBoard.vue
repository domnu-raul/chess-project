<script setup>
import { computed, ref } from 'vue';
import { game } from '../services/game';

function translatePos(x, y) {
    if (game.myColor == 'B')
        y = 7 - y;
    return `${String.fromCharCode(97 + x)}${8 - y}`;
}

function isEven(x, y) {
    if (game.myColor == 'B') {
        return (x + y) % 2 == 1;
    }
    return (x + y) % 2 == 0;
}

function isOdd(x, y) {
    return !isEven(x, y);
}

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

const boardIter = computed(() => {
    let boardCopy = board.value;
    if (game.myColor == 'B') {
        boardCopy = boardCopy.reverse();
    }
    return boardCopy.flat().map((v, i) => {
        let x = i % 8;
        let y = Math.floor(i / 8);
        let pos = translatePos(x, y);

        return {
            piece: v,
            pos: pos,
            x: x,
            y: y,
        }
    });
});

const moveTree = computed(() => {
    let tree = new Map();
    let moves = game.moves;
    let uniqueStarts = new Set(moves.map((move) => move.slice(0, 2)));
    for (let start of uniqueStarts) {
        tree.set(start, moves.filter((move) => move.slice(0, 2) == start).map((move) => move.slice(2, 4)));
    }
    console.log(tree);
    return tree;
});


const endMoves = computed(() => {
    return moveTree.value.get(startMove.value) || [];
});

const startMove = ref(null);

const endMsg = computed(() => {
    if (game.isGameOver) {
        if (game.winner == game.myColor) {
            return 'You won!';
        } else if (game.winner == null) {
            return 'Draw!';
        } else {
            return 'You lost!';
        }
    }
    return null;
});

function getPieceImg(piece) {
    if (piece == piece.toUpperCase()) {
        piece = piece.toLowerCase() + '-white';
    } else {
        piece = piece + '-black';
    }
    return `/pieces/${piece}.png`;
}

function isOccupied(square) {
    return square != ' ';
}

function onClickSquare(square) {
    if (startMove.value == null) {
        if (moveTree.value.has(square.pos)) {
            startMove.value = square.pos;
        }
    } else {
        if (endMoves.value.includes(square.pos)) {
            game.makeMove(startMove.value + square.pos);
        }
        startMove.value = null;
        onClickSquare(square);
    }
}
</script>

<template>
    <div class="grid grid-cols-8 grid-rows-8 rounded-xl relative">
        <div v-if="endMsg != null"
            class="bg-zinc-800 bg-opacity-50 absolute w-full h-full flex justify-center items-center z-10">
            <h1 class="font-roboto font-bold text-6xl text-slate-100 select-none">{{ endMsg }}</h1>
        </div>
        <div v-for="square in boardIter" :key="square" @click="onClickSquare(square)"
            class="relative h-[4.5rem] w-[4.5rem] bg-clip-border overflow-hidden b-0 p-0 flex items-center justify-center cursor-pointer"
            :class="{
                'bg-stone-300': isEven(square.x, square.y),
                'bg-green-700': isOdd(square.x, square.y),
                'ring-4 ring-inset ring-orange-500': endMoves.includes(square.pos) && isOccupied(square.piece),
            }">
            <span v-if="endMoves.includes(square.pos) && !isOccupied(square.piece)"
                class="absolute w-6 h-6 bg-slate-600 rounded-full" />
            <img v-if="isOccupied(square.piece)" :src="getPieceImg(square.piece)" :alt="`chess-piece-${square.pos}`"
                class="pointer-events-none">
        </div>

    </div>
</template>
