<script lang="ts" setup>
const props = defineProps({
    definitions: {
        type: Array,
        required: false
    }
});

let currentLetterIndex = 0;

const getCurrentLetter = () => {
    return String.fromCharCode('a'.charCodeAt(0) + currentLetterIndex++);
};

const resetCurrentLetterIndex = () => {
    currentLetterIndex = 0;
};

const renderDefinitions = (definitions: any) => {
    if (!definitions) {
        return [];
    }
    return definitions.map((definition) => {
        return {
            ...definition,
            letter: getCurrentLetter(),
            subDefinitions: definition.subDefinitions
                ? renderDefinitions(definition.subDefinitions)
                : null,
        };
    });
};

resetCurrentLetterIndex();
const processedDefinitions = renderDefinitions(props.definitions);
</script>

<template>
    <article>
        <ul>
            <li
                v-for="(definition, index) in processedDefinitions"
                :key="index"
            >
                <span v-html="`${definition.letter}. ${definition.term} ${definition.definition}`"></span>
                <ul v-if="definition.subDefinitions">
                    <li
                        v-for="(subDefinition, subIndex) in definition.subDefinitions"
                        :key="subIndex"
                    >
                        <span v-html="`${subDefinition.letter}. ${subDefinition.term} ${subDefinition.definition}`"></span>
                    </li>
                </ul>
            </li>
        </ul>
    </article>
</template>

<style lang="scss" scoped>
ul {
    list-style-type: none;
}
</style>
