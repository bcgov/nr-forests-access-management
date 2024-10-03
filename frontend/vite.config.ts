/// <reference types="vitest" />

import { fileURLToPath, URL } from 'node:url';

import vue from '@vitejs/plugin-vue';
import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import Components from 'unplugin-vue-components/vite';
import { BootstrapVueNextResolver } from 'unplugin-vue-components/resolvers';

// https://vitejs.dev/config/
export default defineConfig(async ({ command, mode }) => {
    const env = loadEnv(mode, process.cwd(), '');
    const port = parseInt(env.VITE_PORT || '5173');

    return {
        plugins: [
            vue(),
            Components({
                resolvers: [BootstrapVueNextResolver()],
            }),
        ],
        test: {
            globals: true,
            environment: 'jsdom',
            coverage: {
                reporter: ['text', 'lcov'],
            },
        },
        build: {
            chunkSizeWarningLimit: 1600,
        },
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url)),
                '~bootstrap': path.resolve(__dirname, 'node_modules/bootstrap'),
                './runtimeConfig': './runtimeConfig.browser',
            },
            extensions: ['.js', '.ts', '.jsx', '.tsx', '.vue'],
        },
        // root: path.resolve(__dirname, 'src'),
        server: {
            port: port,
        },
        css: {
            preprocessorOptions: {
              scss: {
                additionalData: `
                  @use '@bcgov-nr/nr-theme/design-tokens/colors.scss' as colors;
                  @use '@carbon/type' as type;
                `
              }
            }
          }
        // Note: define 'global' to solve aws-amplify `global is not defined` error.
        // but does not work when using Vitest and configured as using 'jsdom' above.
        //    ,
        //    define: {
        //      "global": {}, // Important var defined for solving Aws-Amplify bug with Vite(https://dev.to/richardbray/how-to-fix-the-referenceerror-global-is-not-defined-error-in-sveltekitvite-2i49)
        //    },
    };
});
