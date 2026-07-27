/**
 * Single accessor for the runtime environment settings.
 *
 * At boot, `public/env.js` fetches `env.json` and stores it (stringified) in
 * `localStorage` under the `env_data` key, before the app mounts. Every part of
 * the app that needs an environment value reads it back through here, so the
 * storage key, the JSON shape, and the parse live in exactly one place.
 *
 */

export interface EnvEntry {
    sensitive: boolean;
    type: string;
    value: string;
}

export type EnvData = Record<string, EnvEntry>;

const ENV_DATA_KEY = "env_data";

/**
 * Returns the parsed environment settings, or `null` if `env_data` is absent or
 * malformed. Non-throwing — for callers that can degrade gracefully.
 */
export const getEnvData = (): EnvData | null => {
    const raw = window.localStorage.getItem(ENV_DATA_KEY);
    if (!raw) {
        return null;
    }
    try {
        return JSON.parse(raw) as EnvData;
    } catch {
        return null;
    }
};

/**
 * Convenience reader for a single env value (trimmed), or `undefined` if the
 * env data or the key is missing / empty.
 */
export const getEnvValue = (key: string): string | undefined =>
    getEnvData()?.[key]?.value?.trim() || undefined;

/**
 * Like `getEnvData` but throws if the env data is absent. For boot-critical
 * callers (e.g. Amplify config) that cannot function without it and want a
 * meaningful fail-fast error.
 */
export const requireEnvData = (): EnvData => {
    const env = getEnvData();
    if (!env) {
        throw new Error(`Missing ${ENV_DATA_KEY} in localStorage`);
    }
    return env;
};
