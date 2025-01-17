/** @type {import('tailwindcss').Config} */
export default {
  content: [],
  theme: {
    fontFamily: {
      robotoslab: ["Roboto Slab", "serif"],
      roboto: ["Roboto", "sans-serif"],
    },
    extend: {
      transitionProperty: {
        'height': 'height'
      }
    },
  },
  plugins: [],
  purge: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
};
