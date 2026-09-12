# Enhance UI
It's possible to enhance UI with PyQt6.

Remove "old theme" to QC, keep Fusion.

Adapt with dark or light color system (QGuiApplication.styleHints().colorScheme())

# QualCoder UI Modernization — Summary

## Current State

QualCoder (PyQt6) already has a solid foundation for modernization:
- Forced Fusion style for consistent cross-platform rendering
- An existing QSS theme system (native, dark, original, blue, green, orange, purple, yellow, rainbow)
- qtawesome icons already wired (FontAwesome/Material)
- Noto Sans font installed and loaded

## What Makes It Look Dated

- Hardcoded QSS as Python strings (beige/gray colors, fixed 12px sizes)
- No system light/dark mode following — users must pick manually
- Minimal padding and 2px border-radius — a "2000s spreadsheet" feel
- Each theme duplicates ~40 QSS rules → hard to maintain, inconsistencies between themes
- Icons present but underused (toolbars, menus)

## Recommendations (all PyQt6-compatible)

1. **Follow system light/dark mode** (highest impact): use `QGuiApplication.styleHints().colorScheme()` (Qt 6.5+) to auto-switch. Add a `stylesheet: auto | light | dark | native` setting with `auto` as default.

2. **Externalize QSS into `.qss` files + color variables**: move styles to `themes/dark.qss`, `light.qss`. Qt lacks native CSS variables, so substitute them in Python at load time (e.g. `--bg`, `--accent`, `--text`). Reduces duplication and makes tweaks trivial.

3. **Adopt a spacing grid and unified accent**: standardized 8px padding, 6px border-radius instead of 2px; a single accent color (#f89407) applied consistently to focus, tab selection, headers — replacing the current mixed red/orange/blue. Subtler 1px borders (#d0d0d0 light / #3a3a3a dark).

4. **Modernize specific controls**:
   - QTabBar: flat tabs with accent underline
   - QTreeView: taller rows, clearer indentation, subtle hover
   - QTableWidget: accent border only on focus, optional zebra striping
   - QSplitter: wider, more discreet handles; remove aggressive red hover
   - QMenu: drop the inconsistent blue background, use transparent accent

5. **Information density & toolbar**: group actions in a QToolBar with qtawesome icons + tooltips; add icons to QMenu items; enrich a QStatusBar (current project, code count) to make the app feel alive.

6. **Typography**: replace the fixed 12px base with a scale (small/normal/large) tied to existing font-size settings, applied via a single `* { font-size: ... }` rule instead of the current 5 fragile `.replace()` calls.

7. **Visual testing without breaking existing themes**: keep current themes as fallback for backward compatibility; add modern `auto` + `light` + `dark` as new defaults without removing legacy ones (original, rainbow, etc.).

8. **(Optional, ambitious) Responsive layout**: use QSplitter with persistent proportions and a "Home" tab with start icons (Open project, New, Help) for a modern first impression.
