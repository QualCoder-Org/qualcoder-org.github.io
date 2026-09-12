# Enhance UI
It's possible to enhance UI with PyQt6.

Key takeaways:
- vertical tabs on the left
- revamped home screen, with suggested actions
- cleanup/simplification of style files (to suit system requirements) : use system font, delete herited theme (original/dark/orange/yellow/green/blue/purple/rainbow)
- The idea: transform the window into a dockable workspace featuring a central area (the document currently being coded) surrounded by docks. Everything is visible, everything can be docked or undocked, and the layout is saved.
  
<img width="1615" height="912" alt="image" src="https://github.com/user-attachments/assets/8fd6d8a7-e8c4-4178-91d7-f9d801104e3b" />


Idea of themes for pyqt6
https://dev.to/hi3ris/creer-des-interfaces-python-modernes-et-fluides-avec-pyqt6-b5m
https://github.com/Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6

this text it's "brainstorming" with AI. I "vibecode" for have idea of UI.

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

# Bolder Ideas (still PyQt6)

The first PR modernized the styling. For a real leap in impression, you need to move the UI structure, not just the colors.

## 1. From Tab Bar to Lateral Navigation (Sidebar)

Today: a horizontal 5-tab QTabWidget at the top — the archetype of "2000s toolbox software." Modern apps (VS Code, Notion, Linear) use an icon rail on the left:
- Replace the horizontal QTabWidget with `setTabPosition(QTabWidget.West)` + icon-only tabs (already available via qtawesome) + tooltips, label appearing only on hover or in wide mode.
- A very cheap change (one line of QSS + `setTabPosition`) that instantly transforms the app's silhouette. Gains vertical space for content and reads like a 2024 app.

## 2. Home Screen / "Home" Page

Instead of landing on the action log, show a home page with:
- Clickable cards (Open recent project, New project, Help)
- Current project status (name, file count, code count, last activity)
- Shortcuts to sections. Built with a QFrame + grid layout of qtawesome icons. Delivers the "first impression" that makes all the difference.

## 3. Contextual Inspector Panel (macOS / Inspector style)

Many dialogs (code_text, code_pdf, code_av) are large fixed 2-or-3-panel QSplitters. Adopt a retractable right side panel that changes with the selection: code properties, segment memo, coder comparison. A QStackedWidget driven by context. Reduces visual overload.

## 4. Icon Toolbars Instead of Text Menus

The QMenuBar is overloaded (11 menus in ui_main.ui). Extract the most frequent actions into an icon QToolBar (qtawesome icons + tooltips) at the top of the content area, and keep only rare actions in the menubar. QMenus remain accessible, but the visual bar gives a "pro app" feel.

## 5. Subtle Animations and Transitions

- QPropertyAnimation on retractable panels (AI sidebar, inspector) for a slide instead of a jarring appearance.
- QGraphicsOpacityEffect on tab change (fade). Negligible cost, strong perceived effect.

## 6. "Comfort" Density by Default + Global Zoom

Offer an interface scale (small/comfort/large) that adjusts all metrics (padding, tree row height, icon size), not just the font. The user keeps control, but the default becomes airy rather than dense.

## 7. Consistent, Color-Coded Icon System

qtawesome is already wired. Currently icons use `highlight_color()`. Would benefit from a semantic icon set (codes = label, files = document, AI = robot) with a touch of color per category — gives immediate readability to the code tree and lists.

## 8. Redesign the Code Tree

`code_tree.py` (74k lines) is central. Move from a basic QTreeWidget to:
- Clearer indentation and subtle guide lines (already partially in the QSS)
- Frequency badges on each node (GitHub style)
- Code color as a chip left of the label
- Drag handle for reordering. It's the most-viewed element; modernizing it pays the most.

## 9. "Focus" Mode for Coding

When coding text, hide sidebar/menubar and keep only the document + code palette as a lateral overlay. QMainWindow allows dynamically hiding dock areas. Delivers a "distraction-free" experience highly valued in qualitative analysis.

## 10. (Most Ambitious) Dockable Layout Overhaul

Transform the main window into a QMainWindow with QDockWidgets for codes/files/inspector, letting the user rearrange and detach panels. This is the VS Code / Qt Creator model. More costly, but radically transforms perception and flexibility.

Let me quickly verify a couple of technical facts so the wiki page is accurate (QGIS specifics and QualCoder's actual structure).
Confirmed: no `QDockWidget`/`saveState`/`statusBar` usage today; the main window is a splitter + QTabWidget + a hand-built sidebar. Here is the synthesis for the wiki.

---

# UI Modernization: Analysis and Roadmap

## Why QualCoder's UI feels dated (despite using Qt)

QualCoder runs on PyQt6, the same toolkit as QGIS, Krita, FreeCAD, and Qt Creator — all of which look modern and professional. The framework is not the limit. The difference is **architecture and styling discipline**, not the toolkit.

### 1. Dialog-driven workflow instead of a unified workspace
QualCoder's `MainWindow` (`src/qualcoder/__main__.py`, `class MainWindow(QtWidgets.QMainWindow)`) is a `QMainWindow` only in name. Its real structure is a horizontal `QSplitter` containing:
- a `QTabWidget` with 5 tabs (Action Log, Manage, Coding, Reports, AI Agent), where **each tab holds only a placeholder `QTextBrowser`**;
- a hand-built `sidebar` widget on the right.

The actual work happens in **separate dialogs** launched on demand: `DialogCodeText`, `DialogCodeAV`, `DialogCodePdf`, `DialogManageFiles`, `DialogReportCodes`, `DialogCases`, `DialogJournals` (all in `src/qualcoder/`). These are `QDialog`/`QWidget` instances that get embedded into a tab via a `tab_layout_helper()` call, but they were designed as standalone dialogs with their own internal splitters (code tree | text | segments).

**Effect:** the user opens a box, works, closes it, opens another. There is no persistent context. This is the single biggest reason the app feels old — it is the workflow model of early-2000s software, not a modern workspace.

### 2. No use of QMainWindow's native facilities
- **No `QDockWidget`s** — panels cannot be moved, undocked, or rearranged.
- **No saved layout** — `saveState()` / `restoreState()` are never called; the dockable layout cannot persist.
- **No status bar usage** — `QMainWindow.statusBar()` is not exploited for project info, current code/file, or a locator.
- **No locator/command palette** — there is no quick way to find a code, open a file, or run an action by typing.

### 3. Heavy custom QSS overrides native styling
`App.merge_settings_with_default_stylesheet()` (`src/qualcoder/app.py`) returns ~230 lines of hardcoded QSS that override almost every widget (borders, padding, radius, tabs, splitters, scrollbars). This makes the app look unlike the rest of the OS and unlike other Qt apps. Modern Qt apps (QGIS included) use the native style + palette and adapt icons, rather than redrawing every control.

### 4. Bundled font forced app-wide
`Noto Sans` is installed and loaded as the application font (`install_noto_sans()` + `addApplicationFont`), regardless of platform. The system font (SF on macOS, Segoe UI on Windows, the GTK font on Linux) is ignored, so the typography does not match the OS.

### 5. No system light/dark following
There is no connection to `QGuiApplication.styleHints().colorSchemeChanged`; dark-mode detection is scattered as `== 'dark'` / `in ('dark', 'rainbow')` checks across `cases.py`, `helpers.py`, `report_sql.py`, `code_pdf.py`, `code_av.py`, `code_text.py`, `code_organiser.py`, `ai_chat.py`, and the waveform code.

---

## What makes QGIS feel modern (with the same Qt)

QGIS achieves a professional, modern feel without leaving Qt by leaning on standard Qt architecture patterns:

| Pattern | QGIS | Why it reads as modern |
|---|---|---|
| Dockable workspace | `QMainWindow` + `QDockWidget`s; Panels and Toolbars toggle on/off from View menu / right-click; drag to rearrange; layout saved via `saveState`/`restoreState` | Persistent, customizable, multi-monitor friendly |
| Single central canvas | The map canvas is the focus; all panels serve it | One clear "stage" the eye locks onto |
| Status bar | Scale, CRS, coordinates, progress | Always-on context, no dialogs needed |
| Locator bar | A search field in the status bar that finds layers, features, algorithms, options and runs them | Command-palette UX (like VS Code/Sublime) — instantly feels pro |
| Toolbars | Dockable, contextual, hideable | Quick access without menu diving |
| Native style + SVG icon theme (light/dark) | Uses the platform style; icons ship as SVG with light/dark variants | Looks like the OS, not a custom skin |

**The lesson:** QGIS's modernity comes from the **dockable architecture + central canvas + status/locator bar**, not from decoration. The QSS just follows. Redecorating controls (rounded corners, accent colors) improves aesthetics but does not change the workflow experience.

---

## Two parallel experimental branches

Two approaches have been prototyped to validate directions:

### Branch `vibe/ui-modernization-704837` (PR #8) — Theme refresh
A custom theme system: QSS files in `src/qualcoder/themes/` rendered via `{{placeholder}}` substitution, `auto`/`light`/`dark` modes following the system color scheme, a unified accent, an icon sidebar (West tab position), a startup home panel, and color chips + frequency badges on the code tree.
- **Verdict:** makes the controls look cleaner, but does **not** change the dialog-driven workflow. Aesthetic only.

### Branch `vibe/os-native-704837` (PR #9) — OS integration
A new `system` theme (default) that delegates drawing to the native Qt/OS style and palette: no custom QSS, the system font is used (Noto Sans kept as fallback), live light/dark following via `colorSchemeChanged`, and centralized `is_dark_theme()` / `resolved_stylesheet()` helpers routing all scattered dark-mode checks.
- **Verdict:** the app matches the OS, but the architecture remains dialog-driven. Integration without restructuring.

Both are valuable but **neither touches the root cause**: the dialog-per-function workflow.

---

## Recommended direction: a dockable workspace (the QGIS pattern)

Transform `MainWindow` from a "splitter + tabs of placeholder browsers" into a real dockable workspace with a single central canvas. This is the change that actually modernizes the experience.

### Proposed structure

| Region | Widget | Content |
|---|---|---|
| **Center** | `QStackedWidget` (set via `setCentralWidget`) | The document being coded: `QTextEdit` for text, the PDF view, the image view, or the AV player + waveform. This is the "map canvas" equivalent. |
| **Left docks** | `QDockWidget`s | **Documents** (from `DialogManageFiles`), **Codes** (the shared code tree), **Cases**, **Journals/Memos** — tabbed together or stacked |
| **Bottom dock** | `QDockWidget` | **Retrieved Segments** / query results (like MAXQDA's fourth window) |
| **Right dock** | `QDockWidget` (optional) | **Inspector** — context info on the selected code/document |
| **Status bar** | `QMainWindow.statusBar()` | Project name + path (left), current file/code/segment count (center), theme toggle, language, help (right) |
| **Locator** | `QLineEdit` in/above the status bar | Find a code, open a file, run a menu action — by typing |

### What each current dialog becomes

| Current dialog | Becomes |
|---|---|
| `DialogManageFiles` | **Documents** dock (left) — double-click opens a file in the central canvas |
| Code tree (inside `DialogCodeText`) | **Codes** dock (left), always visible during coding |
| `DialogCases` | **Cases** dock (left, tabbed with Documents) |
| `DialogJournals` | **Journals/Memos** dock (left) |
| `DialogCodeText` / `DialogCodeAV` / `DialogCodePdf` | Editing surface moves into the **central canvas**; their internal splitters are dissolved into docks |
| `DialogReportCodes` and variants | **Analysis** dock (right or bottom), results shown beside the document |
| Retrieved segments / query results | **Retrieved Segments** dock (bottom) |

### Technical implications

1. **`src/qualcoder/GUI/ui_main.py`**: replace the `splitter + QTabWidget` with `setCentralWidget(QStackedWidget)` and `addDockWidget()` for each panel. Layout persists via `saveState()` / `restoreState()` (native Qt).
2. **`src/qualcoder/code_tree.py`**: `CodeTreeController` already operates on a host-owned `QTreeWidget`. Moving that tree into a dock (instead of a dialog) is mostly a parenting change — the controller logic stays.
3. **`DialogCodeText` / `DialogCodeAV` / `DialogCodePdf`**: the heaviest work. Their `.ui` files (`ui_dialog_code_text.py`, etc.) are designed as dialogs with an internal splitter (tree | text | segments). The internal splitter must be broken apart: the tree goes to a dock, the editing surface goes to the central canvas, the segment list goes to a bottom dock. This is the largest refactor item.
4. **`tab_layout_helper()`** is replaced by `addDockWidget()`.
5. **Locator**: a `QLineEdit` in the status bar backed by a model indexing codes, files, and menu actions.

### Incremental rollout (do not rewrite everything at once)

The dockable workspace can be built incrementally without breaking existing dialogs:

1. **Status bar + locator** (small effort, large perceived impact) — do this first.
2. **Permanent Codes dock**: extract the code tree from the coding dialog into a shared left dock. Existing dialogs keep working but read the selected code from the shared dock.
3. **Documents dock**: `manage_files` becomes a dockable browser; double-click opens a file in the canvas.
4. **Central canvas**: introduce the `QStackedWidget` that shows text/PDF/image/AV according to the open file.
5. **Retrieved Segments dock** at the bottom.
6. **Saved layout**: wire `saveState()` / `restoreState()`.

Steps 1 + 2 alone (status bar + permanent codes dock) deliver roughly 70% of the "QGIS feel" without touching the existing coding dialogs. The full canvas migration (steps 3–4) is the larger, riskier work and can follow.

---

## Summary

- QualCoder feels old **because of the dialog-driven workflow and the heavy QSS skin**, not because of Qt.
- QGIS feels modern **because of a dockable workspace + central canvas + status/locator bar**, using native styling.
- Two theme experiments (PR #8: custom theme; PR #9: OS-native) improve look and OS fit but leave the workflow unchanged.
- The high-impact, aligns-with-competitors direction is a **dockable `QMainWindow` workspace with a central document canvas**, built incrementally starting with the status bar + a permanent codes dock.

This is a design/architecture discussion item, not a committed plan.
Here is the synthesis, ready to paste into the developer wiki.

---

# UI Modernization: Direction and Rationale

## Context

QualCoder is sometimes described as having a dated interface, despite being built on PyQt6, the same toolkit as modern applications like QGIS, Krita, FreeCAD, and Qt Creator. This page explains **why** the perception exists and proposes a concrete direction for modernizing the UI while staying fully on PyQt.

## Why PyQt is not the problem

QGIS is the clearest proof that Qt can produce a modern, professional-feeling UI. QGIS achieves its look through **architecture**, not decoration:

- A `QMainWindow` with **dockable panels** (`QDockWidget`) that can be moved, undocked to a second monitor, hidden, and re-arranged. The layout is saved and restored with native `saveState()`/`restoreState()`.
- A single **central canvas** (the map) that everything else serves.
- A **status bar** with contextual information (scale, CRS, coordinates) and a **locator bar** — a search field that finds and runs any layer, algorithm, or option. This is equivalent to a command palette (VS Code / Sublime) and is a strong signal of a modern app.
- **Dockable toolbars**, toggleable by right-click on the menu bar.
- It relies on the **native Qt style and palette** rather than overriding every widget with custom QSS; it adapts its SVG icon set to light/dark.

The dated feel of QualCoder is therefore **not a Qt limitation** — it is an **application-architecture** difference.

## What makes QualCoder feel dated today

The main window is already a `QMainWindow` containing a horizontal `QSplitter` with a `QTabWidget` (Action Log / Manage / Coding / Reports / AI Agent) on the left and a `sidebar` on the right. Each tab only holds a placeholder `QTextBrowser`.

The actual work happens in **separate dialogs** launched from these tabs and embedded via `tab_layout_helper`:

| Dialog | Current role |
|---|---|
| `DialogCodeText` | Code text documents |
| `DialogCodeAV` | Code audio/video |
| `DialogCodePdf` | Code PDF documents |
| `DialogManageFiles` | Import/manage documents |
| `DialogReportCodes` and variants | Analysis reports |
| `DialogCases`, `DialogJournals` | Cases and journals |

Because each function is a self-contained dialog with its own internal splitter (code tree | document | segments), the user spends the session opening and closing boxes rather than working in one unified workspace. This modal-dialog pattern is the primary source of the "dated" impression. Secondary causes: no status bar usage, no command/locator bar, hardcoded QSS that overrides the native look, and a forced bundled font (`Noto Sans`).

## The target: a dockable workspace (the QGIS / MAXQDA / ATLAS.ti model)

Move from "a window with tabs that launch dialogs" to **a single dockable workspace centered on the document being coded**.

### 1. Central canvas (`QStackedWidget`)
A single central area that shows the currently open document, switching by type:
- text → `QTextEdit` coder
- PDF → PDF view
- image → image view
- audio/video → player + waveform

This is the equivalent of the QGIS map canvas: everything else exists to serve it.

### 2. Panels become `QDockWidget`

| Current dialog | Becomes a dock (suggested position) |
|---|---|
| `DialogManageFiles` | **Documents** — left dock (file browser; double-click opens in canvas) |
| Code tree (`treeWidget` in `DialogCodeText`) | **Codes** — left/bottom dock, persistent during coding |
| `DialogCases` | **Cases** — left dock (tabbed with Documents) |
| `DialogJournals` | **Journals / Memos** — left dock |
| Retrieved segments / query results | **Retrieved Segments** — bottom dock (like MAXQDA) |
| `DialogReportCodes` and variants | **Analysis** — right or bottom dock, visible alongside the document |
| `DialogCodeAV` player | stays in the central canvas when the file is audio/video |

Layout saved/restored with native `QMainWindow.saveState()` / `restoreState()`.

### 3. Status bar (already available on `QMainWindow`, just unused)
- left: project name + path (like MAXQDA)
- center: current file / current code / number of coded segments
- right: theme toggle (light/dark), language, help

### 4. Locator bar / command palette
A search field integrated into the status bar (or just above it) that:
- finds a code by name → selects it in the Codes dock
- finds a file → opens it in the canvas
- launches a menu action (new project, import, settings…)
- finds a coded segment

This is the single highest "modern feel" payoff for the least effort.

### 5. Dockable contextual toolbars
A toolbar whose icons change depending on what is in the canvas (text coding vs AV vs image). Dockable, toggleable by right-click on the menu bar.

### 6. "Manage" becomes a real panel, not an isolated tab
Import, attributes, links, references → a left "Manage" dock rather than a tab the user leaves and returns to.

## Technical impact

1. **`GUI/ui_main.py`**: replace the `splitter + QTabWidget` with `addDockWidget()` around `setCentralWidget(QStackedWidget)`. Dock state saved via `saveState()` / `restoreState()` (native Qt).
2. **`code_tree.py`**: `CodeTreeController` already operates on a host-provided `QTreeWidget`. Move that widget into a shared dock instead of a dialog.
3. **`DialogCodeText` / `DialogCodeAV` / `DialogCodePdf`**: the heaviest work. Their `.ui` files are built as dialogs with an internal splitter (tree | document | segments). The splitter needs to be split into docks, leaving only the editing area in the central canvas.
4. **`tab_layout_helper`** is replaced by `addDockWidget`.
5. **Locator**: a `QLineEdit` in the status bar + a model indexing codes, files, and actions.

## Recommended incremental path (no big-bang rewrite)

1. **Status bar + locator bar** — small effort, large perceived effect. Do this first.
2. **Persistent Codes dock** — extract the code tree from the coding dialog into a shared left dock. Existing dialogs keep working but read the code selected in the shared dock.
3. **Documents dock** — turn `DialogManageFiles` into a dockable browser; double-click opens a file in the canvas.
4. **Central canvas** — `QStackedWidget` showing text/PDF/image/AV by file type.
5. **Retrieved Segments** bottom dock.
6. **Saved layout** (`saveState` / `restoreState`).

Steps 1 + 2 alone deliver roughly 70% of the "QGIS feel" without touching the existing dialogs.

## Companion work (already in progress on feature branches)

- **OS-integrated theme** (`system` mode): delegate drawing to the native Qt/OS style and palette, follow the system light/dark scheme live, use the system font by default. This is the QGIS approach to theming and removes the custom-QSS "dated" look at the same time as the dockable work removes the "modal-dialog" feel.
- Both directions are complementary: the dockable workspace fixes the **structure**, the OS-native theme fixes the **look**.

## Key takeaway

> A modern feel is mostly an **architecture** change (dockable workspace + central canvas + locator/status bar), not a **decoration** change. QGIS proves that PyQt can look modern; the difference is that QGIS is a `QMainWindow` with docks around a central canvas, while QualCoder currently launches functions as separate dialogs.

