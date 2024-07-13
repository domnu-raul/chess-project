import { reactive } from "vue";
import {connection} from "./connection";
import {auth} from "./auth";
function getCurrentTime() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    hours = String(hours).padStart(2, '0');

    return `${hours}:${minutes} ${ampm}`;
}

export const game = reactive({
    gameId: '',
    opponent: {},
    me: {},
    fen: '',
    myColor: '',
    turn: '',
    winner: '',
    whiteId: -1,
    blackId: -1,
    moves: [],
    lastMove: '',
    isGameOver: false,
    chat: [],

    initGame(gameId) {
        connection.makeConnection(`ws://localhost:8000/game/${gameId}?token=${auth.token}`);
        connection.setListener((event) => {
            this.handleMessage(event);
            this.updatePlayers();
        });
        connection.setOnClose(() => {
            window.location.href = "/home";
        });
    },

    updatePlayers() {
        if (typeof this.opponent.id !== "undefined")
            return;
        let meRequest = new XMLHttpRequest();
        meRequest.open("GET", "http://localhost:8000/user/me", false); // `false` makes the request synchronous
        meRequest.withCredentials = true;
        meRequest.send(null);
        this.me = JSON.parse(meRequest.responseText);
        let opponentId = this.whiteId === this.me.id ? this.blackId : this.whiteId;

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
        if (message.type === "CHAT") {
            const senderUsername = message.content.sender_id === this.opponent.id ? this.opponent.username : this.me.username;
            const text = message.content.message;
            const time = getCurrentTime();
            const chatMessage = {
                time: time,
                sender: senderUsername,
                message: text
            };
            this.chat.push(chatMessage);
        }
    },

    makeMove(move) {
        let message = `MOVE: ${move}`;
        connection.sendMessage(message);
    },

    sendChatMessage(message) {
        let chatMessage = `CHAT: ${message}`;
        connection.sendMessage(chatMessage);
    },

    resign() {
        connection.sendMessage("resign");
    }
})
