/**
 * PrimeVue v4 PassThrough Configuration for Paginator Component
 * Migrated from primevue-components-overrides.scss
 *
 * Maps PrimeVue paginator elements to FAM-branded classes for consistent styling.
 * All styling managed in paginatorPassThrough.scss using CSS custom properties
 * from fam-custom-tokens.css (semantic design tokens).
 */

export const TABLE_PAGINATOR_PT = {
  pcPaginator: {
    // Root paginator container - applies fam-paginator class for namespace specificity
    root: { class: 'fam-paginator' },

    // Flex container for paginator content/elements
    content: { class: 'fam-paginator-content' },

    // Current page indicator
    current: { class: 'fam-paginator-current' },
  },
};
