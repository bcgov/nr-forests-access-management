import { reactive, ref } from 'vue'

const screenSize = ref(window.innerWidth)

export const useSideNavVisible = reactive({
    isSideNavVisible: screenSize.value >= 1024 ? true : false,
    toggleSideNavVisible() {
        this.isSideNavVisible = !this.isSideNavVisible
    }
})