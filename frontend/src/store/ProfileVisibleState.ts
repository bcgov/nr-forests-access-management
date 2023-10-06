import { reactive } from 'vue'

export const profileSidebarVisible = reactive({
    isVisible: false,
    toggleVisible() {
        this.isVisible = !this.isVisible
    }
})