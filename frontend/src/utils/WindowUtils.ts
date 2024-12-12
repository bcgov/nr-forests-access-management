import type { Ref } from "vue";

export const scrollToRef = (view: Ref<any | null>) => {
    view.value?.scrollIntoView({ behavior: "smooth" });
};
