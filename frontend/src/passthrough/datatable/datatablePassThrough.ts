/**
 * PrimeVue v4 PassThrough Configuration for DataTable Component
 * Migrated from primevue-components-overrides.scss (lines 209–255)
 *
 * Merges paginator PT and adds FAM-branded classes for header/body cells,
 * body rows, and sort icon. All styling in datatablePassThrough.scss using
 * CSS custom properties from fam-custom-tokens.css.
 */

import { TABLE_PAGINATOR_PT } from '@/passthrough/paginator/paginatorPassThrough.js';

export const TABLE_DATATABLE_PT = {
  ...TABLE_PAGINATOR_PT,

  // Body row <tr> — used for row-level box-shadow border
  bodyRow: { class: 'fam-table-body-row' },

  column: {
    // Header <th> — typography, font-weight, text-align, border
    headerCell: { class: 'fam-table-header-cell' },

    // Div wrapper inside <th> — min-height constraint
    columnHeaderContent: { class: 'fam-table-header-content' },

    // <span> containing the column label — padding
    columnTitle: { class: 'fam-table-column-title' },

    // Sort icon element — margin-bottom alignment
    sorticon: { class: 'fam-table-sort-icon' },

    // Body <td> — typography, height, text-align, border
    bodyCell: { class: 'fam-table-body-cell' },
  },
};
