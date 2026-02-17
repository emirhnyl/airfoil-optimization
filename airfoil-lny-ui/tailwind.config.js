/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        lny: {
          yellow: "#f4c401",
          black: "#0b0b0c",
          gray: "#121216",
          line: "rgba(244,196,1,0.25)",
        },
      },
    },
  },
  plugins: [],
};
