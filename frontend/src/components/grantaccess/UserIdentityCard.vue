<script setup lang="ts">
import Card from 'primevue/card';
import Icon from '@/components/common/Icon.vue';
import { IconSize } from '@/enum/IconEnum';
import type { IdimProxyBceidInfoSchema } from 'fam-app-acsctl-api';

const props = defineProps<{
    userIdentity: IdimProxyBceidInfoSchema;
    errorMsg: string;
}>(); // Vue3 alternative way for Type the defineProps().
</script>

<template>
    <Card class="custom-card">
        <template #header>
            <Icon id="checkmarkIcon" icon="checkmark--filled" :size="IconSize.small" v-if="props.userIdentity.found" />
            <Icon id="errorIcon" class="custom-carbon-icon-misuse" icon="misuse" :size="IconSize.small" v-else />
            <p>Verified user information</p>
        </template>
        <template #content>
            <div v-if="props.errorMsg == ''" class="col" style="margin-left: 2rem">
                <label for="userId" class="row">Username</label>
                <span id="userId" name="userId" class="row">
                    {{ props.userIdentity.userId }}
                </span>
            </div>
            <div class="col" v-if="props.userIdentity.found">
                <label for="firstName" class="row">First Name</label>
                <span class="row" id="firstName" name="firstName">
                    {{ props.userIdentity.firstName }}
                </span>
            </div>
            <div class="col" v-if="props.userIdentity.found">
                <label for="lastName" class="row"> Last Name </label>
                <span id="lastName" name="lastName" class="row">
                    {{ props.userIdentity.lastName }}
                </span>
            </div>
            <div class="col" v-if="
                props.userIdentity.found &&
                props.userIdentity.businessLegalName
            ">
                <label for="organizationName" class="row">
                    Organization Name
                </label>
                <span id="organizationName" name="organizationName" class="row">
                    {{ props.userIdentity.businessLegalName }}
                </span>
            </div>
            <div class="col-6 d-flex" v-if="!props.userIdentity.found && props.errorMsg == ''">
                <span class="px-0 invalid" id="userNotExist">
                    User does not exist
                </span>
            </div>
            <div class="col d-flex" v-if="props.errorMsg != ''">
                <span class="px-0 invalid" id="errorMsg">
                    {{ props.errorMsg }}
                </span>
            </div>
        </template>
    </Card>
</template>
