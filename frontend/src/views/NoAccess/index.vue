<script setup lang="ts">
import LogoutIcon from "@carbon/icons-vue/es/logout/16";
import Button from "@/components/UI/Button.vue";
import useAuth from "@/composables/useAuth";
import NotificationMessage from "@/components/UI/NotificationMessage.vue";

const auth = useAuth();
</script>

<template>
    <div class="no-access-container">
        <div class="no-access-content">
            <NotificationMessage
                severity="error"
                message=" You do not have access in FAM"
            />
            <Button
                class-name="logout-button"
                outlined
                label="Sign out"
                :icon="LogoutIcon"
                @click="() => auth.logout()"
            />
        </div>
    </div>
</template>

<style lang="scss">
.no-access-container {
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    .p-message {
        width: 32rem;
    }

    .logout-button {
        margin-top: 2rem;
        width: 16rem;
    }
}
</style>
