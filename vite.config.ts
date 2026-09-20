import { defineConfig } from 'vite'
import { VitePlugin } from 'vite-plugin-sillo-inertia'
import vue from '@vitejs/plugin-vue'
import { viteStaticCopy } from 'vite-plugin-static-copy'
import { fileURLToPath, URL } from 'node:url'
import type { ConfigEnv } from 'vite'

/** The append-only tail of the starter's per-twin config: */
export default defineConfig(() => {
  const isProduction = process.env.NODE_ENV === 'production'

  return {
    root: '.',
    publicDir: 'public',
    plugins: [
      // The shared adapter in app/inertia.py hands the entry and the shell its
      // tags; this plugin only exists to mirror how the twin does it.
      VitePlugin({ entry: 'js/main.ts', rootId: 'app' }),
      vue(),
      viteStaticCopy({
        targets: [{ src: 'public/*', dest: '.' }],
      }),
    ],

    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./js', import.meta.url)),
      },
    },

    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      manifest: 'manifest.json',
      rollupOptions: {
        input: 'js/main.ts',
      },
    },
  }
})
