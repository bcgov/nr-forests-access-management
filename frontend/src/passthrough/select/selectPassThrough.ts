/**
 * PrimeVue v4 PassThrough Configuration for Dropdown/Select Component
 * Migrated from primevue-components-overrides.scss
 *
 * Uses FAM custom tokens (semantic design variables) for consistent theming:
 * - Border colors from semantic-color-border-*
 * - Layer/surface colors from semantic-color-surface-layer-*
 * - Text colors from semantic-color-text-*
 * - Focus/interactive colors from semantic-color-*-interactive
 */

export const SELECT_PASS_THROUGH = {
  // Root dropdown container
  root: {
    class: 'fam-select fam-dropdown-root',
  },

  // Dropdown trigger button/label
  trigger: {
    class: 'fam-dropdown-trigger',
  },

  // Label inside the dropdown trigger
  label: {
    class: 'fam-dropdown-label',
  },

  // Icon inside the dropdown trigger
  icon: {
    class: 'fam-dropdown-icon',
  },

  // Panel (dropdown menu container)
  panel: {
    class: 'fam-dropdown-panel',
  },

  // Items wrapper (list container)
  items: {
    class: 'fam-dropdown-items',
  },

  // Individual item in the dropdown list
  item: {
    class: 'fam-dropdown-item',
  },

  // Highlighted/selected item
  itemGroup: {
    class: 'fam-dropdown-item-group',
  },

  // Empty message when no items
  emptyMessage: {
    class: 'fam-dropdown-empty-message',
  },
};
