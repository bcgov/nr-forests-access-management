/**
 * PrimeVue Theme Preset Configuration for FAM
 *
 * This file centralizes PrimeVue v4 theme configuration using fam-custom-tokens.js generated
 * from source fam-custom-tokens.json (derived from external nr-theme design tokens).
 * Design token mapping ensures consistency with BCGov brand colors and visual standards.
 */

import Lara from '@primeuix/themes/lara';
import { definePreset } from '@primeuix/themes';
import {
  ComponentButtonDangerActive,
  ComponentButtonDangerBackground,
  ComponentButtonDangerHover,
  ComponentButtonPrimaryActive,
  ComponentButtonPrimaryBackground,
  ComponentButtonPrimaryHover,
  ComponentButtonSecondaryActive,
  ComponentButtonSecondaryBackground,
  ComponentButtonSecondaryHover,
  ComponentButtonTertiaryActive,
  ComponentButtonTertiaryBackground,
  ComponentButtonTertiaryHover,
  PrimitiveColorWhite,
  SemanticColorBorderInteractive,
  SemanticColorBorderSubtle,
  SemanticColorFocusDefault,
  SemanticColorIconPrimary,
  SemanticColorPrimary500,
  SemanticColorPrimary600,
  SemanticColorPrimary700,
  SemanticColorPrimary800,
  SemanticColorSurfaceLayer1,
  SemanticColorSurfaceLayerHover,
  SemanticColorSurfaceLayerSelected,
  SemanticColorTextOnColor,
  SemanticColorTextPrimary,
  SemanticColorTextSecondary,
} from '@/assets/generated/ts/fam-custom-tokens.js';

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
      500: SemanticColorPrimary500,
      600: SemanticColorPrimary600,
      700: SemanticColorPrimary700,
      800: SemanticColorPrimary800,
      900: '#003B73',
      950: '#00264D',
    },
    // Lara uses scheme-dependent tokens; override under colorScheme to ensure precedence.
    colorScheme: {
      light: {
        primary: {
          color: SemanticColorPrimary500,
          inverseColor: PrimitiveColorWhite,
          hoverColor: SemanticColorPrimary600,
          activeColor: SemanticColorPrimary800,
        },
      },
      dark: {
        primary: {
          color: SemanticColorPrimary500,
          inverseColor: PrimitiveColorWhite,
          hoverColor: SemanticColorPrimary600,
          activeColor: SemanticColorPrimary800,
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
              background: ComponentButtonPrimaryBackground,
              hoverBackground: ComponentButtonPrimaryHover,
              activeBackground: ComponentButtonPrimaryActive,
              borderColor: ComponentButtonPrimaryBackground,
              hoverBorderColor: ComponentButtonPrimaryHover,
              activeBorderColor: ComponentButtonPrimaryActive,
              color: SemanticColorTextOnColor,
              hoverColor: SemanticColorTextOnColor,
              activeColor: SemanticColorTextOnColor,
            },
            secondary: {
              background: ComponentButtonSecondaryBackground,
              hoverBackground: ComponentButtonSecondaryHover,
              activeBackground: ComponentButtonSecondaryActive,
              borderColor: ComponentButtonSecondaryBackground,
              hoverBorderColor: ComponentButtonSecondaryHover,
              activeBorderColor: ComponentButtonSecondaryActive,
              color: SemanticColorTextOnColor,
              hoverColor: SemanticColorTextOnColor,
              activeColor: SemanticColorTextOnColor,
            },
            danger: {
              background: ComponentButtonDangerBackground,
              hoverBackground: ComponentButtonDangerHover,
              activeBackground: ComponentButtonDangerActive,
              borderColor: ComponentButtonDangerBackground,
              hoverBorderColor: ComponentButtonDangerHover,
              activeBorderColor: ComponentButtonDangerActive,
              color: SemanticColorTextOnColor,
              hoverColor: SemanticColorTextOnColor,
              activeColor: SemanticColorTextOnColor,
            },
          },
          outlined: {
            primary: {
              color: ComponentButtonTertiaryBackground,
              borderColor: ComponentButtonTertiaryBackground,
              hoverBackground: ComponentButtonTertiaryHover,
              activeBackground: ComponentButtonTertiaryActive,
            },
            danger: {
              color: ComponentButtonDangerBackground,
              borderColor: ComponentButtonDangerBackground,
              hoverBackground: ComponentButtonDangerHover,
              activeBackground: ComponentButtonDangerActive,
            },
          },
        },
        dark: {
          root: {
            primary: {
              background: ComponentButtonPrimaryBackground,
              hoverBackground: ComponentButtonPrimaryHover,
              activeBackground: ComponentButtonPrimaryActive,
              borderColor: ComponentButtonPrimaryBackground,
              hoverBorderColor: ComponentButtonPrimaryHover,
              activeBorderColor: ComponentButtonPrimaryActive,
              color: SemanticColorTextOnColor,
              hoverColor: SemanticColorTextOnColor,
              activeColor: SemanticColorTextOnColor,
            },
            secondary: {
              background: ComponentButtonSecondaryBackground,
              hoverBackground: ComponentButtonSecondaryHover,
              activeBackground: ComponentButtonSecondaryActive,
              borderColor: ComponentButtonSecondaryBackground,
              hoverBorderColor: ComponentButtonSecondaryHover,
              activeBorderColor: ComponentButtonSecondaryActive,
              color: SemanticColorTextOnColor,
              hoverColor: SemanticColorTextOnColor,
              activeColor: SemanticColorTextOnColor,
            },
            danger: {
              background: ComponentButtonDangerBackground,
              hoverBackground: ComponentButtonDangerHover,
              activeBackground: ComponentButtonDangerActive,
              borderColor: ComponentButtonDangerBackground,
              hoverBorderColor: ComponentButtonDangerHover,
              activeBorderColor: ComponentButtonDangerActive,
              color: SemanticColorTextOnColor,
              hoverColor: SemanticColorTextOnColor,
              activeColor: SemanticColorTextOnColor,
            },
          },
          outlined: {
            primary: {
              color: ComponentButtonTertiaryBackground,
              borderColor: ComponentButtonTertiaryBackground,
              hoverBackground: ComponentButtonTertiaryHover,
              activeBackground: ComponentButtonTertiaryActive,
            },
            danger: {
              color: ComponentButtonDangerBackground,
              borderColor: ComponentButtonDangerBackground,
              hoverBackground: ComponentButtonDangerHover,
              activeBackground: ComponentButtonDangerActive,
            },
          },
        },
      },
    },
    select: {
      root: {
        background: SemanticColorSurfaceLayer1,
        filledBackground: SemanticColorSurfaceLayer1,
        filledHoverBackground: SemanticColorSurfaceLayer1,
        filledFocusBackground: SemanticColorSurfaceLayer1,
        borderColor: 'transparent',
        hoverBorderColor: 'transparent',
        focusBorderColor: 'transparent',
        color: SemanticColorTextPrimary,
        placeholderColor: SemanticColorTextSecondary,
      },
      dropdown: {
        color: SemanticColorIconPrimary,
      },
      overlay: {
        background: SemanticColorSurfaceLayer1,
        borderColor: SemanticColorBorderSubtle,
        color: SemanticColorTextPrimary,
      },
      option: {
        focusBackground: SemanticColorSurfaceLayerHover,
        selectedBackground: SemanticColorSurfaceLayerSelected,
        selectedFocusBackground: SemanticColorSurfaceLayerSelected,
        color: SemanticColorTextPrimary,
        selectedColor: SemanticColorTextPrimary,
        selectedFocusColor: SemanticColorTextPrimary,
        borderRadius: '0',
      },
    },
    input: {
      root: {
        background: SemanticColorSurfaceLayer1,
        filledBackground: SemanticColorSurfaceLayer1,
        filledHoverBackground: SemanticColorSurfaceLayer1,
        filledFocusBackground: SemanticColorSurfaceLayer1,
        borderColor: 'transparent',
        hoverBorderColor: 'transparent',
        focusBorderColor: 'transparent',
        color: SemanticColorTextPrimary,
        placeholderColor: SemanticColorTextSecondary,
        borderRadius: '0',
      },
    },
    checkbox: {
      root: {
        borderColor: SemanticColorIconPrimary,
        hoverBorderColor: SemanticColorIconPrimary,
        focusBorderColor: SemanticColorIconPrimary,
        checkedBackground: SemanticColorIconPrimary,
        checkedHoverBackground: SemanticColorIconPrimary,
        checkedBorderColor: SemanticColorIconPrimary,
        checkedHoverBorderColor: SemanticColorIconPrimary,
        checkedFocusBorderColor: SemanticColorIconPrimary,
        focusRing: {
          color: SemanticColorFocusDefault,
        },
      },
      icon: {
        checkedColor: SemanticColorTextOnColor,
      },
    },
    radiobutton: {
      root: {
        borderColor: SemanticColorIconPrimary,
        hoverBorderColor: SemanticColorIconPrimary,
        checkedBackground: SemanticColorIconPrimary,
        checkedHoverBackground: SemanticColorIconPrimary,
        checkedBorderColor: SemanticColorIconPrimary,
      },
      icon: {
        checkedColor: SemanticColorIconPrimary,
      },
    },
    card: {
      root: {
        background: SemanticColorSurfaceLayer1,
        color: SemanticColorTextPrimary,
      },
      subtitle: {
        color: SemanticColorTextSecondary,
      },
    },
    datatable: {
      root: {
        borderColor: SemanticColorBorderSubtle,
      },
      colorScheme: {
        light: {
          headerCell: {
            background: SemanticColorSurfaceLayerSelected,
            hoverBackground: SemanticColorSurfaceLayerSelected,
            selectedBackground: SemanticColorSurfaceLayerSelected,
            borderColor: SemanticColorBorderSubtle,
            color: SemanticColorTextPrimary,
          },
          row: {
            background: PrimitiveColorWhite,
            hoverBackground: SemanticColorSurfaceLayerHover,
            selectedBackground: SemanticColorSurfaceLayerSelected,
            stripedBackground: SemanticColorSurfaceLayer1,
            color: SemanticColorTextPrimary,
          },
          bodyCell: {
            borderColor: SemanticColorBorderSubtle,
            selectedBorderColor: SemanticColorBorderInteractive,
          },
        },
        dark: {
          headerCell: {
            background: SemanticColorSurfaceLayerSelected,
            hoverBackground: SemanticColorSurfaceLayerSelected,
            selectedBackground: SemanticColorSurfaceLayerSelected,
            borderColor: SemanticColorBorderSubtle,
            color: SemanticColorTextPrimary,
          },
          row: {
            background: PrimitiveColorWhite,
            hoverBackground: SemanticColorSurfaceLayerHover,
            selectedBackground: SemanticColorSurfaceLayerSelected,
            stripedBackground: SemanticColorSurfaceLayerSelected,
            color: SemanticColorTextPrimary,
          },
          bodyCell: {
            borderColor: SemanticColorBorderSubtle,
            selectedBorderColor: SemanticColorBorderInteractive,
          },
        },
      },
    },
    dialog: {
      root: {
        background: SemanticColorSurfaceLayer1,
        borderColor: SemanticColorBorderSubtle,
        color: SemanticColorTextPrimary,
      },
    },
  },
});

export default FamPrimeVuePreset;
