import { fileURLToPath, URL } from 'node:url';

import vue from '@vitejs/plugin-vue';
import path from 'path';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(async ({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const port = parseInt(env.VITE_PORT || "5173");

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '~bootstrap': path.resolve(__dirname, 'node_modules/bootstrap'),
      }
    },
    root: path.resolve(__dirname, 'src'),
    server: {
      port: port,
    },
  }
});
