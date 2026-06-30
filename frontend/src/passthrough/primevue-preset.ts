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
  ComponentDatatableHeaderBackground,
  ComponentNotificationErrorBackground,
  ComponentNotificationSuccessBackground,
  ComponentNotificationWarningBackground,
  PrimitiveColorWhite,
  SemanticColorBorderInteractive,
  SemanticColorBorderSubtle,
  SemanticColorFocusDefault,
  SemanticColorIconPrimary,
  SemanticColorPrimary50,
  SemanticColorPrimary100,
  SemanticColorPrimary200,
  SemanticColorPrimary300,
  SemanticColorPrimary400,
  SemanticColorPrimary500,
  SemanticColorPrimary600,
  SemanticColorPrimary700,
  SemanticColorPrimary800,
  SemanticColorPrimary900,
  SemanticColorPrimary950,
  SemanticColorSupportError,
  SemanticColorSupportSuccess,
  SemanticColorSupportWarning,
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
      50: SemanticColorPrimary50,
      100: SemanticColorPrimary100,
      200: SemanticColorPrimary200,
      300: SemanticColorPrimary300,
      400: SemanticColorPrimary400,
      500: SemanticColorPrimary500,
      600: SemanticColorPrimary600,
      700: SemanticColorPrimary700,
      800: SemanticColorPrimary800,
      900: SemanticColorPrimary900,
      950: SemanticColorPrimary950,
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
        background: PrimitiveColorWhite,
        color: SemanticColorTextPrimary,
        shadow: 'none',
      },
      subtitle: {
        color: SemanticColorTextSecondary,
      },
    },
    datatable: {
      root: {
        borderColor: SemanticColorBorderSubtle,
      },
      headerCell: {
        padding: '0.75rem',
      },
      bodyCell: {
        padding: '0.75rem',
      },
      colorScheme: {
        light: {
          headerCell: {
            background: ComponentDatatableHeaderBackground,
            hoverBackground: ComponentDatatableHeaderBackground,
            selectedBackground: ComponentDatatableHeaderBackground,
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
      },
    },
    dialog: {
      root: {
        background: SemanticColorSurfaceLayer1,
        borderColor: SemanticColorBorderSubtle,
        color: SemanticColorTextPrimary,
      },
    },
    message: {
      colorScheme: {
        light: {
          success: {
            background: ComponentNotificationSuccessBackground,
            borderColor: SemanticColorSupportSuccess,
            color: SemanticColorTextPrimary,
          },
          error: {
            background: ComponentNotificationErrorBackground,
            borderColor: SemanticColorSupportError,
            color: SemanticColorTextPrimary,
          },
          warn: {
            background: ComponentNotificationWarningBackground,
            borderColor: SemanticColorSupportWarning,
            color: SemanticColorTextPrimary,
          },
        },
      },
    },
  },
});

export default FamPrimeVuePreset;
