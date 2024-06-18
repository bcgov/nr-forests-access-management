<script lang="ts" setup>
import Dialog from 'primevue/dialog';
import { ref, onMounted } from 'vue';
const visible = ref(false);

onMounted(() => {
    visible.value = true;
});

const definitions = [
    {
        term: '"Applications”',
        definition:
            'any applications to which Users may be granted access by the Delegated Administrator through FAM;',
    },
    {
        term: '“Business BCeID”',
        definition:
            'the Master Login ID and User Login IDs (both as defined in the Business BCeID Terms) issued to the Subscriber and individuals within the Subscriber’s organization pursuant to the Business BCeID Terms;',
    },
    {
        term: '“Business BCeID Terms”',
        definition:
            'the terms found at:  https://www.bceid.ca/aboutbceid/agreements.aspx;',
    },
    {
        term: '“Delegated Administrator”',
        definition:
            'the individual within the Subscriber’s organization who is responsible for granting Users access to Applications through FAM;',
    },
    {
        term: '“Device”',
        definition:
            'a computer, mobile device or any other device capable of accessing FAM or any Application;',
    },
    {
        term: '“Documentation”',
        definition:
            'documentation for FAM or an Application that describes the features and functionality of FAM or the Application;',
    },
    {
        term: '“FOIPPA”',
        definition:
            'the Freedom of Information and Protection of Privacy Act, R.S.B.C. 1996, c. 165, as amended or replaced from time to time;',
    },
    {
        term: '“Users”',
        definition:
            'individuals within the Subscriber’s organization who have been granted access to any Application by the Delegated Administrator through FAM; and',
        subDefinitions: [
            {
                term: '“Works”',
                definition:
                    'means, collectively, FAM, the Applications and the Documentation.',
            },
        ],
    },
];

const getType = (index: number): "a" | "i" | "1" | "A" | "I" | undefined => {
  return String.fromCharCode(97 + index) as "a" | "i" | "1" | "A" | "I" | undefined;
};
</script>
<template>
    <Dialog
        v-model:visible="visible"
        header="FAM Terms of Use"
        :style="{ width: '50rem' }"
        :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    >
        <article>
            <p>
                This Forest Access Management application (“FAM”) terms of use
                agreement (the "Agreement") is entered into between the legal
                entity that has received approval for Delegated Administrator
                access to FAM (the “Subscriber”) and His Majesty the King in
                right of the Province of British Columbia as represented by the
                Minister of Forests (the “Province"). By clicking the “I Accept”
                button (or any similar button or mechanism), and in
                consideration of the Province granting the Delegated
                Administrator access to FAM, the Subscriber, and the Delegated
                Administrator on behalf of the Subscriber, agree (and will be
                conclusively deemed to have agreed) to the following:
            </p>
            <p>
                <strong> Definitions </strong>
            </p>
            <ol>
                <li>
                    In this Agreement the following words have the following
                    meanings:
                    <ol type="a">
                        <li v-for="(definition, index) in definitions">
                            {{ `${definition.term} ${definition.definition}` }}
                            <ol
                                v-if="definition.subDefinitions"
                                type="a"
                            >
                                <li
                                    v-for="subDefinition in definition.subDefinitions"
                                >
                                    {{
                                        ` ${getType(index)} ${subDefinition.term} ${subDefinition.definition}`
                                    }}
                                </li>
                            </ol>
                        </li>
                    </ol>
                </li>
            </ol>
        </article>
        <template #footer> buttons here </template>
    </Dialog>
</template>
