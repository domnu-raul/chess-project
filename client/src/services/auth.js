import { reactive } from "vue";

export const store = reactive({
    isAuthenticated: false,
    isRegistered: false,

    updateAuthStatus() {
        const request = new XMLHttpRequest();
        request.open("GET", "http://localhost:8000/auth/token", false); // `false` makes the request synchronous
        request.withCredentials = true;
        request.send(null);
        let status = request.status;
        this.isAuthenticated = status === 200;
    },

    updateRegisterStatus() {
        const cookie = document.cookie;
        this.isRegistered = cookie.includes("registered=true");
    },

    setRegistered(status) {
        const cookieValue = status ? "registered=true" : "registered=false";
        // Setting a new cookie with a path so it is correctly registered
        document.cookie = cookieValue + "; path=/";
        this.isRegistered = status;
    }
});



