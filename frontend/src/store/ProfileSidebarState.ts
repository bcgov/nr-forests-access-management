import { reactive } from 'vue'

export const profileSidebarState = reactive({
    isVisible: false,
    toggleVisible() {
        this.isVisible = !this.isVisible
    }
})