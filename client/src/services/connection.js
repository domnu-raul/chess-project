import { reactive } from "vue";

export const connection = reactive({
    isConnected: false,
    socket: null,

    makeConnection(url) {
        this.socket = new WebSocket(url);
        this.isConnected = true;
    },

    setListener(action) {
        this.socket.onmessage = (event) => action(event);
    },

    sendMessage(message) {
        this.socket.send(message);
    },

    disconnect() {
        this.socket.close();
        this.isConnected = false;
    }
});