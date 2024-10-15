/// <reference types="vitest" />

import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import Components from "unplugin-vue-components/vite";
import { BootstrapVueNextResolver } from "unplugin-vue-components/resolvers";
import { fileURLToPath, URL } from "url";
import path from "path";

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), "");
    const port = parseInt(env.VITE_PORT || "5173");

    return {
        plugins: [
            vue(),
            Components({
                resolvers: [BootstrapVueNextResolver()],
            }),
        ],
        test: {
            globals: true,
            environment: "jsdom",
            coverage: {
                reporter: ["text", "lcov"],
            },
        },
        build: {
            chunkSizeWarningLimit: 1600,
        },
        resolve: {
            alias: {
                "@": fileURLToPath(new URL("./src", import.meta.url)),
                "~bootstrap": path.resolve(__dirname, "node_modules/bootstrap"),
                "./runtimeConfig": "./runtimeConfig.browser",
                vue: "vue/dist/vue.esm-bundler.js",
            },
            extensions: [".js", ".ts", ".jsx", ".tsx", ".vue"],
        },
        server: {
            port: port,
        },
        css: {
            preprocessorOptions: {
                scss: {
                    additionalData: `
            @use '@bcgov-nr/nr-theme/design-tokens/colors.scss' as colors;
            @use '@carbon/type' as type;
          `,
                },
            },
        },
    };
});
