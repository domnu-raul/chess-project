import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
<<<<<<< Updated upstream
    host: true,
    port: 5173, 
=======
>>>>>>> Stashed changes
    watch: {
      usePolling: true,
    },
  },
<<<<<<< Updated upstream
});
=======

})
>>>>>>> Stashed changes
