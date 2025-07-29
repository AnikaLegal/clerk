import react from '@vitejs/plugin-react'
import { globSync } from 'glob'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  root: 'src',
  base: '/static/',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    manifest: 'manifest.json',
    sourcemap: true,
    rollupOptions: {
      input: globSync('src/pages/*.tsx').map((file) =>
        fileURLToPath(new URL(file, import.meta.url))
      ),
    },
  },
  server: {
    host: true,
  },
})
