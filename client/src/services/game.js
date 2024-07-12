import { reactive } from "vue";
import {connection} from "./connection";
import {auth} from "./auth";

export const game = reactive({
    gameId: '',
    opponent: {},
    fen: '',
    myColor: '',
    turn: '',
    winner: '',
    whiteId: -1,
    blackId: -1,
    moves: [],
    lastMove: '',
    isGameOver: false,
    chat: ["Welcome to the chat!", "You can chat with your opponent here."],

    initGame(gameId) {
        connection.makeConnection(`ws://localhost:8000/game/${gameId}?token=${auth.token}`);
        connection.setListener((event) => {
            console.log(event);
            this.handleMessage(event);
            this.updateOpponent();
            connection.setListener(this.handleMessage);
        });
    },

    updateOpponent() {
        let meRequest = new XMLHttpRequest();
        meRequest.open("GET", "http://localhost:8000/user/me", false); // `false` makes the request synchronous
        meRequest.withCredentials = true;
        meRequest.send(null);
        let me = JSON.parse(meRequest.responseText);
        let opponentId = this.whiteId === me.id ? this.blackId : this.whiteId;

        let opponentRequest = new XMLHttpRequest();
        opponentRequest.open("GET", "http://localhost:8000/user/" + opponentId, false); // `false` makes the request synchronously
        opponentRequest.withCredentials = true;
        opponentRequest.send(null);
        let opponentResponse = JSON.parse(opponentRequest.responseText);
        this.opponent = opponentResponse.details;
        this.opponent.username = opponentResponse.username;
        this.opponent.id = opponentResponse.id;
    },

    handleMessage(event) {
        let message = JSON.parse(event.data);
        if (message.type === "GAME_UPDATE") {
            this.fen = message.content.fen;
            this.turn = message.content.turn;
            this.isGameOver = message.content.is_end;
            this.winner = message.content.winner;
            this.blackId = message.content.black_player_id;
            this.whiteId = message.content.white_player_id;
            this.myColor = message.content.color;
            this.moves = message.content.legal_moves;
            this.lastMove = message.content.last_move;
        }
    },
})
