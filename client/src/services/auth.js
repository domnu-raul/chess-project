import { reactive } from "vue";

export const auth = reactive({
    isAuthenticated: false,
    isRegistered: false,
    token: '',

    updateAuthStatus() {
        const request = new XMLHttpRequest();
        request.open("GET", "http://localhost:8000/auth/token", false); // `false` makes the request synchronous
        request.withCredentials = true;
        request.send(null);
        let status = request.status;
        let response = JSON.parse(request.responseText);
        this.isAuthenticated = status === 200;
        if (status === 200) 
            this.token = response.token.access_token;
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
    },
});



