<script lang="ts" setup>
import Dialog from 'primevue/dialog';
import { ref, onMounted } from 'vue';

const visible = ref(false);

onMounted(() => {
    visible.value = true;
});

const terms = [
    {
        term: {
            heading: 'Definitions',
            data: {
                topic: [
                    {
                        subHeading:
                            'In this Agreement the following words have the following meanings:',
                        terms: [
                            {
                                term: 'Applications',
                                definition:
                                    'means any applications to which Users may be granted access by the Delegated Administrator through FAM;',
                            },
                            {
                                term: 'Business BCeID',
                                definition:
                                    'means the Master Login ID and User Login IDs (both as defined in the Business BCeID Terms) issued to the Subscriber and individuals within the Subscriber’s organization pursuant to the Business BCeID Terms;',
                            },
                            {
                                term: 'Business BCeID Terms',
                                definition:
                                    `means the terms found at:  <a href="https://www.bceid.ca/aboutbceid/agreements.aspx" target="_blank">https://www.bceid.ca/aboutbceid/agreements.aspx</a>`,
                            },
                            {
                                term: 'Delegated Administrator',
                                definition:
                                    'means the individual within the Subscriber’s organization who is responsible for granting Users access to Applications through FAM;',
                            },
                            {
                                term: 'Device',
                                definition:
                                    'means a computer, mobile device or any other device capable of accessing FAM or any Application;',
                            },
                            {
                                term: 'Documentation',
                                definition:
                                    'means documentation for FAM or an Application that describes the features and functionality of FAM or the Application;',
                            },
                            {
                                term: 'FOIPPA',
                                definition:
                                    'means the Freedom of Information and Protection of Privacy Act, R.S.B.C. 1996, c. 165, as amended or replaced from time to time;',
                            },
                            {
                                term: 'Users',
                                definition:
                                    'means individuals within the Subscriber’s organization who have been granted access to any Application by the Delegated Administrator through FAM; and',
                                subDefinitions: [
                                    {
                                        term: '"Works"',
                                        definition:
                                            'means, collectively, FAM, the Applications and the Documentation.',
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        },
    },
    {
        term: {
            heading: 'Authority and Ability to Accept Terms ',
            data: {
                topic: [
                    {
                        subHeading:
                            'The Delegated Administrator accepting the terms of this Agreement on behalf of the Subscriber represents and warrants that:',
                        terms: [
                            {
                                term: '',
                                definition:
                                    'they are at least 19 years of age; and',
                            },
                            {
                                term: '',
                                definition:
                                    'they have all necessary authority to accept this Agreement on behalf of the Subscriber.',
                            },
                        ],
                    },
                    {
                        subHeading:
                            'The Delegated Administrator accepting the terms of this Agreement on behalf of the Subscriber represents and warrants that:',
                    },
                    {
                        subHeading:
                            'The Delegated Administrator accepting the terms of this Agreement on behalf of the Subscriber represents and warrants that:',
                        terms: [
                            {
                                term: '',
                                definition:
                                    'they are at least 19 years of age; and',
                            },
                        ],
                    },
                ],
            },
        },
    },
];
</script>

<template>
    <Dialog
        v-model:visible="visible"
        header="FAM Terms of Use"
        :style="{ width: '50rem' }"
        :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    >
        <template v-for="term in terms">
            <p>
                <strong>{{ term.term.heading }}</strong>
            </p>
            <ol
                type="1"
                v-for="subHeading in term.term.data.topic"
            >
                <li>
                    {{ subHeading.subHeading }}
                </li>
                <Terms :definitions="subHeading.terms" />
            </ol>
        </template>

        <template #footer> buttons here </template>
    </Dialog>
</template>
