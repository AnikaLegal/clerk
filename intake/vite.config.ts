import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  root: 'src',
  // base, static_url_prefix (settings/base.py DJANGO_VITE) and the docker
  // COPY destination (/dist/intake/) must stay in lockstep.
  base: '/static/intake/',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    manifest: 'manifest.json',
    sourcemap: true,
    rollupOptions: {
      input: fileURLToPath(new URL('src/main.tsx', import.meta.url)),
    },
  },
  server: {
    host: true,
    port: 5174,
    strictPort: true,
    // Django serves the page and django-vite loads the bundle from this dev
    // server, but assets imported in JS (e.g. the notice-to-vacate PDF) resolve
    // to base-relative URLs that the browser would request from Django (404).
    // Setting origin makes those URLs absolute to the Vite dev server so it
    // serves them directly. Dev only - ignored by the production build.
    origin: 'http://localhost:5174',
  },
})
