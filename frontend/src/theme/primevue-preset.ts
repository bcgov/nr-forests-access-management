/**
 * PrimeVue Theme Preset Configuration for FAM
 *
 * This file centralizes PrimeVue v4 theme configuration using nr-theme design tokens.
 * Design token mapping ensures consistency with BCGov brand colors and visual standards.
 *
 * See: .github/references/primevue4-theme-overrides-finding.md for architecture details
 */

import Lara from '@primeuix/themes/lara';
import { definePreset } from '@primeuix/themes';

/**
 * nr-theme Design Token Color Mapping
 * Source: @bcgov-nr/nr-theme/design-tokens/colors.scss
 */
const NR_THEME_COLORS = {
  // Blue Scale
  blue60: '#0073E6',  // button-primary
  blue65: '#0066CC',  // button-primary-hover
  blue70: '#005CB8',  // button-tertiary
  blue75: '#0052A3',  // button-tertiary-hover
  blue80: '#00478F',  // button-primary-active, button-tertiary-active

  // Gray Scale
  gray10: '#F3F3F5',  // layer-01
  gray15: '#ECECEE',  // layer-hover-01
  gray20: '#DFDFE1',  // border-subtle-00
  gray30: '#C6C6C8',  // button-disabled, button-primary-disabled
  gray50: '#939395',  // text-disabled
  gray55: '#868688',  // from color scale
  gray70: '#606062',  // text-secondary
  gray75: '#535355',  // button-secondary-hover
  gray80: '#464648',  // button-secondary
  gray100: '#131315', // text-primary

  // Red Scale
  red60: '#E72000',   // button-danger-primary
  red70: '#B32001',   // button-danger-secondary, button-danger-hover
  red80: '#801701',   // button-danger-active

  // White
  white: '#FFFFFF',
};

/**
 * FAM PrimeVue Preset
 *
 * Extends Lara theme with FAM-specific design tokens aligned to nr-theme.
 * Primary colors use BCGov blue scale instead of Lara's green.
 */
export const FamPrimeVuePreset = definePreset(Lara, {
  semantic: {
    // Keep semantic primary in sync with nr-theme to avoid Lara emerald defaults.
    primary: {
      50: '#E8F2FF',
      100: '#D2E6FF',
      200: '#A9CCFF',
      300: '#80B2FF',
      400: '#5798FF',
      500: NR_THEME_COLORS.blue60,
      600: NR_THEME_COLORS.blue65,
      700: NR_THEME_COLORS.blue70,
      800: NR_THEME_COLORS.blue80,
      900: '#003B73',
      950: '#00264D',
    },
    // Lara uses scheme-dependent tokens; override under colorScheme to ensure precedence.
    colorScheme: {
      light: {
        primary: {
          color: NR_THEME_COLORS.blue60,
          inverseColor: NR_THEME_COLORS.white,
          hoverColor: NR_THEME_COLORS.blue65,
          activeColor: NR_THEME_COLORS.blue80,
        },
      },
      dark: {
        primary: {
          color: NR_THEME_COLORS.blue60,
          inverseColor: NR_THEME_COLORS.white,
          hoverColor: NR_THEME_COLORS.blue65,
          activeColor: NR_THEME_COLORS.blue80,
        },
      },
    },
  },
  components: {
    button: {
      colorScheme: {
        light: {
          root: {
            primary: {
              background: NR_THEME_COLORS.blue60,
              hoverBackground: NR_THEME_COLORS.blue65,
              activeBackground: NR_THEME_COLORS.blue80,
              borderColor: NR_THEME_COLORS.blue60,
              hoverBorderColor: NR_THEME_COLORS.blue65,
              activeBorderColor: NR_THEME_COLORS.blue80,
              color: NR_THEME_COLORS.white,
              hoverColor: NR_THEME_COLORS.white,
              activeColor: NR_THEME_COLORS.white,
            },
            secondary: {
              background: NR_THEME_COLORS.gray80,
              hoverBackground: NR_THEME_COLORS.gray75,
              activeBackground: NR_THEME_COLORS.gray70,
              borderColor: NR_THEME_COLORS.gray80,
              hoverBorderColor: NR_THEME_COLORS.gray75,
              activeBorderColor: NR_THEME_COLORS.gray70,
              color: NR_THEME_COLORS.white,
              hoverColor: NR_THEME_COLORS.white,
              activeColor: NR_THEME_COLORS.white,
            },
          },
          outlined: {
            primary: {
              color: NR_THEME_COLORS.blue60,
              borderColor: NR_THEME_COLORS.blue60,
              hoverBackground: NR_THEME_COLORS.blue65,
              activeBackground: NR_THEME_COLORS.blue80,
            },
          },
        },
        dark: {
          root: {
            primary: {
              background: NR_THEME_COLORS.blue60,
              hoverBackground: NR_THEME_COLORS.blue65,
              activeBackground: NR_THEME_COLORS.blue80,
              borderColor: NR_THEME_COLORS.blue60,
              hoverBorderColor: NR_THEME_COLORS.blue65,
              activeBorderColor: NR_THEME_COLORS.blue80,
              color: NR_THEME_COLORS.white,
              hoverColor: NR_THEME_COLORS.white,
              activeColor: NR_THEME_COLORS.white,
            },
          },
          outlined: {
            primary: {
              color: NR_THEME_COLORS.blue60,
              borderColor: NR_THEME_COLORS.blue60,
              hoverBackground: NR_THEME_COLORS.blue65,
              activeBackground: NR_THEME_COLORS.blue80,
            },
          },
        },
      },
    },
  },
});

export default FamPrimeVuePreset;
