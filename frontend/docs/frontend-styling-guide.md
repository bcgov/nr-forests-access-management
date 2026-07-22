# Frontend Theming Guide

This guide covers FAM's design token system, PrimeVue v4 theming approach, and the workflows developers follow when customizing or updating styles.

---

## Table of Contents

1. [Why nr-theme Lives in fam-custom-tokens.json](#1-why-nr-theme-lives-in-fam-custom-tokenjson)
2. [Generating fam-custom-tokens.css and fam-custom-tokens.js](#2-generating-fam-custom-tokenscss-and-fam-custom-tokensjs)
3. [Typography System](#3-typography-system)
4. [PrimeVue v4: Preset and PassThrough](#4-primevue-v4-preset-and-passthrough)
5. [FAM Customization Scenarios](#5-fam-customization-scenarios)
6. [Updating the Source of Truth](#6-updating-the-source-of-truth)

---

## 1. Why nr-theme Lives in fam-custom-tokens.json

### Background

The BC Government Natural Resources sector mandates visual consistency through **`@bcgov-nr/nr-theme`** — an NPM package that publishes the BCGov design system as SCSS tokens and variables (e.g., colour palettes, typography scales). FAM consumes this package but cannot use it directly inside PrimeVue's preset API, which expects plain JavaScript values, not SCSS variables.

### The Bridge Layer

`frontend/src/assets/tokens/fam-custom-tokens.json` is the **single source of truth** that bridges `nr-theme` and PrimeVue. It encodes the BCGov brand colours (which originate from `nr-theme`) alongside FAM-specific overrides into a portable, tool-agnostic JSON structure understood by [Style Dictionary](https://styledictionary.style/).

**Why JSON and not SCSS?**

| Concern | SCSS (`nr-theme` native) | JSON (`fam-custom-tokens.json`) |
|---|---|---|
| Readable by PrimeVue preset (JS) | No | Yes — compiled to `.js` exports |
| Readable by browser (CSS variables) | No | Yes — compiled to `.css` custom properties |
| Type-safe in TypeScript | No | Yes — named exports with literal values |
| Single definition of each token | No — SCSS and JS would diverge | Yes — one JSON drives all outputs |

### Token Architecture

The JSON is structured in four layers, following atomic design token conventions:

```
primitive   →  Raw colour values (hex, rgba)
semantic    →  Intent-based aliases (primary, error, border, focus…)
component   →  Component-specific roles (button.primary.hover, notification.error.background…)
typography  →  Font size, line-height, letter-spacing
```

References inside the JSON use the `{path.to.token}` syntax:

```json
"semantic": {
  "color": {
    "primary": {
      "500": { "value": "{primitive.color.blue.60}" }
    }
  }
}
```

Style Dictionary resolves these references at build time, so changing `primitive.color.blue.60` propagates automatically to every semantic and component token that references it.

### Why nr-theme colours are re-declared rather than imported

`nr-theme` v1.8.9 ships only as SCSS. There is no JSON or JS export from the package. The hex values in `fam-custom-tokens.json` (e.g., `#0073E6` for BCGov Blue 60) are **manually aligned** with the values in `nr-theme`'s SCSS light theme. This is a deliberate trade-off: it gives FAM full control over which tokens enter the PrimeVue layer while keeping the SCSS-side (non-PrimeVue styles, `styles.scss`) sourcing colours directly from the `nr-theme` package.

> **Note:** `@bcgov-nr/nr-theme` is locked to `~1.8.9` in `package.json`. Version 1.9+ introduces BC Sans 2.0, which has not yet been evaluated for FAM. When upgrading, cross-check the colour values in the new `nr-theme` release against the `primitive` section of `fam-custom-tokens.json`.

---

## 2. Generating fam-custom-tokens.css and fam-custom-tokens.js

### What gets generated

| Output file | Location | Consumer |
|---|---|---|
| `fam-custom-tokens.css` | `src/assets/generated/css/` | SCSS (`styles.scss` imports it into `:root`), PassThrough SCSS files via `var(--…)` |
| `fam-custom-tokens.js` | `src/assets/generated/ts/` | PrimeVue preset (`primevue-preset.ts`) — named JS imports |

Both files are **committed to the repository** as build artefacts so the project builds without requiring a separate token-generation step in CI.

### Tool: Style Dictionary

[Style Dictionary](https://styledictionary.style/) (`^5.4.4`) reads `fam-custom-tokens.json` and applies platform-specific transforms to produce the outputs above. Its configuration lives in `frontend/style-dictionary.config.json`:

```json
{
  "source": ["src/assets/tokens/fam-custom-tokens.json"],
  "platforms": {
    "css": {
      "transformGroup": "css",
      "buildPath": "src/assets/generated/css/",
      "files": [{ "destination": "fam-custom-tokens.css", "format": "css/variables" }]
    },
    "js": {
      "transformGroup": "js",
      "buildPath": "src/assets/generated/ts/",
      "files": [{ "destination": "fam-custom-tokens.js", "format": "javascript/es6" }]
    }
  }
}
```

### Running the generator

```bash
cd frontend
npm run build:tokens
```

This single script regenerates both files. It must be re-run any time `fam-custom-tokens.json` changes (see [§5 Updating the Source of Truth](#5-updating-the-source-of-truth)).

### How the outputs are consumed

**CSS (`fam-custom-tokens.css`)**

Imported in `src/assets/styles/styles.scss`, which adds all tokens to `:root` as CSS custom properties:

```scss
@import "@/assets/generated/css/fam-custom-tokens.css";
```

PassThrough SCSS files then reference these custom properties directly:

```scss
.p-button.fam-button {
  font-size: var(--typography-body-compact-01-font-size);
  box-shadow: 0 0 0 0.125rem var(--semantic-color-focus-default) inset;
}
```

Token names are derived from the JSON path, kebab-cased and prefixed with `--`. For example:
- `primitive.color.blue.60` → `--primitive-color-blue-60`
- `semantic.color.focus.default` → `--semantic-color-focus-default`
- `typography.body-compact-01.fontSize` → `--typography-body-compact-01-font-size`

**JS (`fam-custom-tokens.js`)**

Exports named ES6 constants, PascalCase from the JSON path. Imported in `primevue-preset.ts`:

```ts
import {
  ComponentButtonPrimaryBackground,   // "#0073E6"
  SemanticColorFocusDefault,           // "#0073E6"
  SemanticColorSurfaceLayer1,          // "#F3F3F5"
} from '@/assets/generated/ts/fam-custom-tokens.js';
```

These literal values are passed directly into PrimeVue's `definePreset()` call, where PrimeVue v4 resolves them into its internal CSS variable system.

---

## 3. Typography System

FAM uses two complementary mechanisms to apply consistent typography. Understanding both prevents confusion when you encounter the same type scale names in different parts of the codebase.

### 3.1 Carbon type scale (compile-time SCSS mixins)

FAM uses **`@carbon/type`** as a compile-time Sass utility for applying IBM Carbon's named type styles. This is purely a typography utility — no Carbon UI components are used in FAM.

In `.vue` component `<style>` blocks and in `src/assets/styles/styles.scss`, you will see:

```scss
@use "@carbon/type" as type;

.my-element {
    @include type.type-style("body-compact-01");
}
```

Sass expands this at build time into plain CSS properties:

```css
.my-element {
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.28572;
    letter-spacing: 0.16px;
}
```

There is no runtime overhead — the mixin is fully resolved during the Vite build. The named type styles used in FAM are defined by Carbon's type scale specification and are not FAM-specific:

| Style name | Rough purpose |
|---|---|
| `label-01` | Small labels, captions (~12px) |
| `body-01` | Regular body text (~14px, generous line-height) |
| `body-compact-01` | Regular body text, tighter line-height |
| `heading-compact-01` | Small bold heading |
| `heading-01` | Small heading |
| `heading-03` | Medium heading |
| `heading-05` | Large heading |

### 3.2 Typography tokens in fam-custom-tokens.json (runtime CSS variables)

`fam-custom-tokens.json` includes a `typography` section that mirrors a subset of the Carbon type scale values:

```json
"typography": {
    "body-compact-01": {
        "fontSize": { "value": "14px" },
        "lineHeight": { "value": "1.28572" },
        "letterSpacing": { "value": "0.16px" }
    },
    "label-01": {
        "fontSize": { "value": "12px" },
        "lineHeight": { "value": "16px" }
    },
    "heading-03": {
        "fontSize": { "value": "20px" },
        "lineHeight": { "value": "28px" }
    }
}
```

Style Dictionary compiles these into CSS custom properties (e.g. `--typography-body-compact-01-font-size: 14px`), which are used exclusively in the **PrimeVue PassThrough SCSS files**:

```scss
// src/passthrough/button/buttonPassThrough.scss
.p-button.fam-button {
    font-size: var(--typography-body-compact-01-font-size);
    letter-spacing: var(--typography-body-compact-01-letter-spacing);
}
```

The PassThrough files cannot use the `@carbon/type` SCSS mixin because they style PrimeVue's internal DOM structure via CSS class injection — CSS custom properties are the only viable mechanism there.

### 3.3 Why both exist

| Mechanism | Where used | How it works |
|---|---|---|
| `@include type.type-style(...)` | Vue component `<style>` blocks, `styles.scss` | Sass mixin, expanded at build time into static CSS |
| `var(--typography-*)` | PrimeVue PassThrough SCSS files | CSS custom property, resolved at runtime from `fam-custom-tokens.css` |

The two mechanisms do not conflict — they deliver the same values through different paths dictated by the context each mechanism is used in.

### 3.4 Guidance for new development

- For styling **custom (non-PrimeVue) components**, use `@include type.type-style(...)` with `@use "@carbon/type" as type` in the component's `<style>` block.
- For styling **PrimeVue component internals** via PassThrough SCSS, use `var(--typography-*)` CSS custom properties.
- If you need a type style in PassThrough SCSS that is not yet in `fam-custom-tokens.json`, add it to the `typography` section using the same Carbon name and values, then run `npm run build:tokens` to regenerate the CSS variables.
- Never hardcode `font-size`, `line-height`, or `letter-spacing` values directly — always trace back to either a Carbon type style name or a `--typography-*` token to keep both systems aligned.

---

## 4. PrimeVue v4: Preset and PassThrough

> Official documentation: https://primevue.org/theming/styled/ and https://primevue.org/passthrough/

### Two separate styling mechanisms

PrimeVue v4 gives developers two distinct, complementary hooks:

| Hook | What it controls | Where it lives in FAM |
|---|---|---|
| **Preset** | Colors, surfaces, focus rings — any property that PrimeVue exposes in its theme token API | `src/passthrough/primevue-preset.ts` |
| **PassThrough (PT)** | Structure: CSS classes injected on each DOM element of a component, enabling custom SCSS selectors | `src/passthrough/<component>/` |

**Rule of thumb:** use the **preset** for colour and visual-state tokens; use **PassThrough + SCSS** for layout, spacing, typography, and anything not in PrimeVue's theme token API.

### 3.1 Preset

A preset is created with `definePreset(BaseTheme, overrides)` from `@primeuix/themes`. FAM extends the **Lara** base theme:

```ts
import Lara from '@primeuix/themes/lara';
import { definePreset } from '@primeuix/themes';

export const FamPrimeVuePreset = definePreset(Lara, {
  semantic: {
    primary: {
      500: SemanticColorPrimary500,  // BCGov Blue 60 — replaces Lara's emerald
      600: SemanticColorPrimary600,
      // …
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
            },
          },
        },
      },
    },
  },
});
```

The preset is registered globally in `src/main.ts`:

```ts
app.use(PrimeVue, {
  theme: { preset: FamPrimeVuePreset },
  pt: { /* see below */ },
});
```

**Best practice:** only override tokens that genuinely need to differ from Lara. Avoid duplicating Lara's `colorScheme` blocks for light and dark if FAM is light-only — identical blocks are dead weight. Reference component theme token paths from the [PrimeVue theming docs](https://primevue.org/theming/styled/).

### 3.2 PassThrough (PT)

PT is a configuration object keyed by the component's internal slot names (e.g., `root`, `label`, `overlay`). Each entry can carry a `class`, `style`, or any HTML attribute to inject onto that DOM element.

FAM uses PT solely to inject CSS class names, keeping the logic in TypeScript thin and the styling in SCSS:

```ts
// src/passthrough/button/buttonPassThrough.ts
export const BUTTON_PASS_THROUGH = {
  root: { class: 'fam-button' },
};
```

```scss
// src/passthrough/button/buttonPassThrough.scss
.p-button.fam-button {
  font-size: var(--typography-body-compact-01-font-size);
  padding: 0.375rem 1rem;
  border-radius: 0.25rem;
}
```

The `.p-button` prefix is the PrimeVue-generated base class — always use `p-<component>.fam-<component>` selectors (not just `.fam-<component>`) to respect specificity without needing `!important`.

#### Global vs per-component PT registration

**Global PT** (registered in `main.ts`) applies to every instance of that component automatically:

```ts
app.use(PrimeVue, {
  pt: {
    button: BUTTON_PASS_THROUGH,
    inputtext: INPUT_PASS_THROUGH,
    dialog: DIALOG_PASS_THROUGH,
    radiobutton: RADIO_BUTTON_PASS_THROUGH,
    message: MESSAGE_PASS_THROUGH,
  },
});
```

**Per-component PT** (applied via the `:pt` prop) is used when a component needs context-specific overrides not appropriate globally — FAM currently applies Select and DataTable this way:

```vue
<Select :pt="SELECT_PASS_THROUGH" />
<DataTable :pt="TABLE_DATATABLE_PT" />
```

**Best practice:** prefer global registration for shared components (buttons, inputs, dialogs). Reserve `:pt` props for components whose structure genuinely varies between usage contexts.

### 3.3 Component slot names

PrimeVue documents each component's PT slots on its component page (e.g., https://primevue.org/button/#pt). Check the "PassThrough" tab to see all available slot names before writing a PT config.

---

## 5. FAM Customization Scenarios

### Scenario A — Change a colour that PrimeVue controls (preset token)

**Example:** change the primary button hover colour.

1. Update the value in `fam-custom-tokens.json`:
   ```json
   "component": {
     "button": {
       "primary": {
         "hover": { "value": "{primitive.color.blue.70}" }
       }
     }
   }
   ```
2. Run `npm run build:tokens` to regenerate `fam-custom-tokens.css` and `fam-custom-tokens.js`.
3. The new JS constant (`ComponentButtonPrimaryHover`) is picked up by `primevue-preset.ts` automatically — no preset edits needed.

### Scenario B — Change a layout/spacing/typography property (PassThrough SCSS)

**Example:** increase button padding.

1. Open `src/passthrough/button/buttonPassThrough.scss`.
2. Update the relevant rule using CSS custom properties from `fam-custom-tokens.css` where possible:
   ```scss
   .p-button.fam-button {
     padding: 0.5rem 1.25rem;
   }
   ```
3. No token rebuild required.

### Scenario C — Style a PrimeVue component that has no PT configured yet

1. Look up the component's PT slot names on the [PrimeVue docs](https://primevue.org/) component page ("PassThrough" tab).
2. Create `src/passthrough/<component>/<component>PassThrough.ts` and a matching `.scss` file.
3. Export the PT object from the `.ts` file.
4. Import the `.scss` file in `src/assets/styles/main.scss` (or the component's own `<style>` block if it is isolated).
5. Register globally in `main.ts` (`pt: { <componentKey>: MY_PASS_THROUGH }`) or apply via `:pt` prop.

### Scenario D — Style a non-PrimeVue element (plain HTML, custom component)

Use CSS custom properties from `fam-custom-tokens.css` directly in SCSS:

```scss
.my-section-header {
  color: var(--semantic-color-text-primary);
  border-bottom: 1px solid var(--semantic-color-border-subtle);
  font-size: var(--typography-heading-03-font-size);
}
```

Never hardcode hex values in component SCSS. Always trace back to the token.

### Scenario E — FAM needs a colour not in the current token set

1. Determine whether the colour belongs to BCGov brand (`primitive`) or is FAM-specific (`semantic`/`component`).
2. Add the token at the correct layer in `fam-custom-tokens.json`.
3. Run `npm run build:tokens`.
4. Reference the generated CSS variable or JS constant in the appropriate file.

Do not invent hex literals in SCSS without first adding a token — this breaks the single-source-of-truth contract.

---

## 6. Updating the Source of Truth

The source of truth for FAM's design tokens is `frontend/src/assets/tokens/fam-custom-tokens.json`. The generated files (`fam-custom-tokens.css`, `fam-custom-tokens.js`) are derived artefacts — they must be regenerated and committed whenever the JSON changes.

### When nr-theme releases a new version

1. Check the `nr-theme` changelog for colour changes.
2. Update the locked version in `frontend/package.json` (`@bcgov-nr/nr-theme`).
3. Run `npm install` to fetch the new package.
4. Cross-check the new SCSS colour values in `node_modules/@bcgov-nr/nr-theme/design-tokens/` against the `primitive.color.*` entries in `fam-custom-tokens.json`.
5. Update any differing hex values in `fam-custom-tokens.json`.
6. Run `npm run build:tokens` to regenerate both output files.
7. Visually test in the running app (`npm run dev`) — focus on buttons, form inputs, focus rings, and notifications.
8. Commit `fam-custom-tokens.json`, `fam-custom-tokens.css`, and `fam-custom-tokens.js` together in the same PR.

> **Tip:** Before upgrading `nr-theme` past `~1.9`, evaluate whether BC Sans 2.0 font changes are acceptable for all FAM screens — typography metrics may shift.

### When a FAM-specific design decision changes

1. Edit `fam-custom-tokens.json` at the appropriate layer (`semantic` for intent aliases, `component` for specific component roles, `typography` for font metrics).
2. Run `npm run build:tokens`.
3. Verify the SCSS side (PassThrough files) — if the token was only used via the JS import in the preset, no SCSS changes are needed; if it was also used as a CSS variable in PassThrough SCSS, verify those rules still read correctly.
4. Commit all three files: `fam-custom-tokens.json`, `fam-custom-tokens.css`, `fam-custom-tokens.js`.

### Checklist before committing token changes

- [ ] `fam-custom-tokens.json` — the edit was made here, not in the generated files
- [ ] `npm run build:tokens` ran successfully with no errors
- [ ] `fam-custom-tokens.css` reflects the expected CSS variable changes
- [ ] `fam-custom-tokens.js` reflects the expected JS constant changes
- [ ] `npm run build` passes (TypeScript, Vite)
- [ ] Visual check in `npm run dev` on at least one affected component
- [ ] All three files are staged in the same commit

### File ownership quick reference

| File | Edit? | Commit? | Notes |
|---|---|---|---|
| `src/assets/tokens/fam-custom-tokens.json` | Yes — this is the source | Yes | Only file you hand-edit |
| `src/assets/generated/css/fam-custom-tokens.css` | Never directly | Yes | Auto-generated; commit the output |
| `src/assets/generated/ts/fam-custom-tokens.js` | Never directly | Yes | Auto-generated; commit the output |
| `frontend/style-dictionary.config.json` | Only if generator config changes | Yes | Rarely touched |
| `src/passthrough/primevue-preset.ts` | Yes — add/remove preset overrides | Yes | Import new JS constants here |
| `src/passthrough/<component>/*.scss` | Yes — layout/structure rules | Yes | Reference CSS variables here |
