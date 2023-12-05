import { inject, type InjectionKey } from "vue";

// Helper functions for Vue's provide/inject to resolve with "undefined" case when component inject the dependency.
function requireInjection<T>(key: InjectionKey<T>, defaultValue?: T) {
    const resolved = inject(key, defaultValue);
    if (!resolved) {
        throw new Error(`${key} was not provided.`);
    }
    return resolved;
}

export { requireInjection }