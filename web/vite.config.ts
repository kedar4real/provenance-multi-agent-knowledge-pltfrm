import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The API runs on :8000 (PROVENANCE_API overrides it, e.g. to try a second instance).
// Proxying keeps the browser on one origin, so the API needs no CORS.
const api = process.env.PROVENANCE_API ?? "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: { "/v1": api, "/health": api },
  },
});
