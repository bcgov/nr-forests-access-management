/**
 * PrimeVue v4 PassThrough Configuration for Dropdown/Select Component
 * Migrated from primevue-components-overrides.scss
 *
 * Uses FAM custom tokens (semantic design variables) for consistent theming
 */

export const SELECT_PASS_THROUGH = {
  // Root select container
  root: {
    class: 'fam-select',
  },

  // Label/value element inside select
  label: {
    class: 'fam-select-label',
  },

  // Dropdown button wrapper
  dropdown: {
    class: 'fam-select-dropdown',
  },

  // Chevron icon element inside dropdown button
  dropdownIcon: {
    class: 'fam-select-dropdown-icon',
  },

  // Overlay/panel container (portaled)
  overlay: {
    class: 'fam-select-overlay',
  },

  // List wrapper in overlay
  list: {
    class: 'fam-select-list',
  },

  // Individual option item
  option: {
    class: 'fam-select-option',
  },

  // Empty message item
  emptyMessage: {
    class: 'fam-select-empty-message',
  },
};
