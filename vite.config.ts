import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// The Vue twin's build. `render_vite_vue_tags` in app/inertia.py points at the
// same `manifest.json` this writes, and js/main.ts is the entry the adapter
// hands the browser.
export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./js', import.meta.url)),
    },
  },

  build: {
    manifest: 'manifest.json',
    rollupOptions: {
      input: 'js/main.ts',
    },
  },
})
