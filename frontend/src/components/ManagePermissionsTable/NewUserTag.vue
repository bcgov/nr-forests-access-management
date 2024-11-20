<script setup>
import Tag from 'primevue/tag';

</script>

<template>
    <Tag
        class="custom-tag"
        rounded
    >
        New
    </Tag>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';
.custom-tag {
    background-color: $light-background-inverse;
    padding: 0.18rem 0.5rem 0.2rem;
    margin-right: 0.3rem;
}
</style>
