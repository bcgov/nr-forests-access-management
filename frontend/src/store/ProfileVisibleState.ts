import { reactive } from 'vue'

export const useProfileSidebarVisible = reactive({
    isProfileVisible: false,
    toggleVisible() {
        this.isProfileVisible = !this.isProfileVisible
    }
})