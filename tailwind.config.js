/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          blue: "#2563eb",
          dark: "#0f172a"
        }
      }
    },
  },
  plugins: [],
};
