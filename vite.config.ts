import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/joplin_notes_page/",
  plugins: [react()],
});
