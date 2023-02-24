<template>
    <vue-final-modal
        v-slot="{ close }"
        v-bind="$attrs"
        classes="modal-container"
        content-class="modal-content"
    >
        <div class="modal__content">
            <div class="modal-header">
                <h5 class="modal-title">{{ title }}</h5>
                <button
                    type="button"
                    class="btn-close"
                    data-dismiss="modal"
                    aria-label="Close"
                    @click="close"
                ></button>
            </div>
            <div class="modal-body">
                <p>{{ message }}</p>
            </div>
            <div class="modal-footer modal__action">
                <button
                    type="button"
                    class="btn btn-danger"
                    v-on:click="$emit('confirm', close)"
                >
                    {{ confirmText }}
                </button>
                <button type="button" class="btn btn-info" @click="close">
                    {{ cancelText }}
                </button>
            </div>
        </div>
    </vue-final-modal>
</template>

<script setup lang="ts">
const props = defineProps({
    message: String,
    title: String,
    confirmText: { type: String, default: 'Confirm' },
    cancelText: { type: String, default: 'Cancel' },
});
</script>

<style scoped>
::v-deep(.modal-container) {
    display: flex;
    justify-content: center;
    align-items: center;
}

::v-deep(.modal-content) {
    position: relative;
    display: flex;
    flex-direction: column;
    margin: 0 1rem;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.25rem;
    background: #fff;
    width: auto;
}

.modal-header {
    align-items: flex-start;
}

.modal__title {
    margin: 0 2rem 0 0;
    font-size: 1.5rem;
    font-weight: 700;
}

.modal-title {
    padding-bottom: 15px;
}

.modal-body {
    padding-top: 15px;
    padding-bottom: 15px;
    border-top: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
}

.modal-footer {
    padding-top: 15px;
}

.modal__close {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
}
.btn {
    margin-left: 15px;
}
.dark-mode div::v-deep(.modal-content) {
    border-color: #2d3748;
    background-color: #1a202c;
}
</style>
