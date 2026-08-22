---
title: "QualCoder: A Major Update for Qualitative Analysis"
date: 2026-08-XX
---

We are excited to present the latest version of QualCoder, a feature-rich update that transforms how you work with qualitative data. Whether you are a researcher, analyst, or data professional, this release introduces significant improvements in code hierarchy, AI integration, file management, and visualisation.

This version also marks an important evolution in data structure and analysis. Below is a detailed overview of the key new features.


## Optimised Language Support

To ensure the highest quality user experience, QualCoder now focuses on four main languages: English, German, French, and Spanish. These languages benefit from regular human reviews and frequent updates to ensure accurate and natural translations.

Additional languages remain available in the "Other Languages" folder, though they may not be as current or human-reviewed. If you would like to contribute translations for your language, please contact us.


## Structural Changes: More Organised Codes

### Improved Code Hierarchy

One of the major new features of this version is the ability to create sub-codes. Previously, QualCoder allowed you to structure your data in categories only. Now, you can also create hierarchies of codes, offering much finer granularity for organizing your analyses.


## Backups: Simpler and More Accessible

Project backups are now stored in the same folder as the project itself. Everything is grouped in one place, simplifying management and restoration of your work.


## AI Enhancements

The integration of artificial intelligence in QualCoder has been completely rethought. The AI chat is no longer just a conversational assistant; it has become an active collaborator that can interact with your data. Please note AI is optional within QualCoder.

We have implemented three access levels to secure data from accidental modifications and provide flexibility based on your needs and trust level:

| Access Level | Permissions | Use Case |
|--------------|-------------|----------|
| Read-only | Full access to the code tree, memos, codings, and empirical data through various search tools (text only). | Data analysis and exploration without risk of modification. |
| Sandboxed | Read + limited write access: ability to create new codes and codings, but cannot modify or delete existing ones. | Safe testing and experimentation. |
| Full access | All permissions, including modifying existing codes, codings, attributes, and cases. Destructive operations require explicit user confirmation. | Advanced work with human validation for critical actions. |


## Menus and Tabs: A Revised Interface

The QualCoder interface has been restructured to improve ergonomics and readability.

A new "Analysis" tab has been added, centralizing all data analysis functionalities. Menu items have been redistributed between "Analysis" and "Reports" for better logical organisation. The "Manage," "Coding," and "Reports" tabs now include detailed explanations of their respective roles, accessible via tooltips or embedded descriptions.


## Journals: Extended Export and Features

Journals (logs, memos, etc.) benefit from several improvements:

- Export to ODT format: your journals can now be exported in OpenDocument Text, a universal and editable format, opened with LibreOffice Writer, Microsoft Word or similar software.
- Conversion to coding file: right-click on a journal to convert it into a codable file within your QualCoder project.
- Direct URL opening: if your journal contains links (starting with http, https, or www), right-click on the URL to open it directly in your browser.


## File Management: Advanced Import and Manipulation

 A context menu offers Delete and Export options via right-click. In the filename column, pressing Delete removes the selected files.
 
### Survey Import

An "Import Survey" button now allows importing data from Excel (XLSX) or CSV files. Multiple row selection lets you choose several lines at once for importing as attributes or for qualitative processing.

### PDF Import with Highlights

You can now import annotated PDFs (with highlights) and automatically code the highlighted segments. Each highlight color is associated with a distinct code, created under a "PDF Highlights" category. Code colors are adapted to best match QualCoder's palette.

### LaTeX Import

LaTeX files can now be imported and converted to readable plain text. Note that complex presentations or files using commands like |input| or |include| may not import perfectly.


## Code Tree: More Intuitive and Powerful

The code tree, present in all coding screens, has been significantly improved:

- Sub-menus have been added for Modify (selected codes or categories), Filter, and Sort options.
- A visual filter indicator (filter icon) appears when the tree is filtered (for example, via "Show similar codes" or "Show codes by color").
- A code name text filter has been added below the tree.
- A "Move Category" option allows you to reorganise your tree.
- Drag-and-drop has been improved: you can now move an item to the top or bottom of the visible tree, and the tree will scroll automatically.
- A menu for the tree header allows choosing between automatic or manual column resizing.


## Text Coding: Advanced Customisation and Export

Text coding has been enriched with many features for a smoother and more flexible experience:

- Customise the font and size of your document's text.
- Resize code labels using resize handles.
- Toggle between different highlighting styles: marker, underline, or vertical stripes for codes.
- Export coded documents in ODF (OpenDocument Format), with color-coded highlights, associated comments, or as an analytical report.

Keyboard shortcuts have been added: e.g. C to add a new category. The text edit mode now includes a search bar for easier navigation.


## PDF Coding: A Revolutionised Experience

Thanks to contributions from Lorenzo, PDF coding has been considerably improved. PDF presentation and manipulation now offer a smoother and more intuitive interface. You can code directly on the PDF page, whether it's text or image areas. AI-assisted text analysis can be applied directly from the PDF coding window.

A refactoring method has been added for existing QualCoder projects: text is re-extracted, and existing codings are remapped to the new extraction method. Codings that cannot be remapped are recorded in Journals as "lost codes" for your review.

PDF highlight export generates a copy of the original PDF with coded segments embedded as native highlight annotations (in each code's color, with the code name as annotation comment). This allows the coded document to be opened and reviewed in any standard PDF reader. An ODT report feature also enables exporting a coding report in OpenDocument Text format (ODT), listing coded segments with their codes (text and images).


## Image Coding: Easy Resizing

Coded areas on images can now be resized via a right-click context menu or using resize handles.


## Audio/Video Coding: Improved Bookmarks and Navigation

The bookmark feature allows you to restore the position in the media and text in the "Code A/V" and "View A/V" windows (from "Manage Files") after setting a bookmark. Keyboard shortcuts are available: B to create a bookmark, and Shift + B to go to a bookmark.


## Co-occurrence Report: Visualisation and Export

Proximity graphs allow you to visualise relationships between codes. You can also export your co-occurrence data in a format compatible with Gephi, a powerful network analysis tool.


## Graph: More Flexibility and Control

Graph offers more flexibility and control:

- Object manipulation has been improved, allowing you to move, resize, and organize nodes more easily.
- Export mind maps in a format compatible with draw.io for integration with other visualisation tools.
- Expand or collapse portions of the graph (categories) for a clearer view.
- A new dialog box allows adding coded segments to your graph.
- Multiple graph organization options are available, with layout choices: radial, vertical, or horizontal.
- Font and color customization offers more options to adapt your graph's appearance.
- A scrollable mini-map helps you navigate large graphs more easily.
- Choose from different node styles (box, oval, etc.).
- Use multi-selection to manipulate multiple elements at once.


## SQL Queries: Simplified Execution

SQL queries can now be executed more simply:

- Use the Ctrl + Enter shortcut to run your query.
- If you have selected part of your query, only that selected part will be executed.
- A menu option allows you to comment or uncomment selected text.


## Word Clouds and Filters

You can now choose stopword lists in multiple languages to refine your results. Text filters have been added to dropdown lists for files, cases, and categories. Right-click opens a menu with additional options.


## Code Reports: More Options and Flexibility

### Code Summary

A context menu allows you to display coded files associated with a code.

### Code Frequency

A context menu also allows you to display coded files associated with a code. You can enable or disable automatic column width resizing. Full code names (including their hierarchy) can also be displayed.


## Bug Fixes

This version includes numerous bug fixes to improve QualCoder's stability and reliability:

- A/V search by cases: fixed an issue where the "important" filter and ORDER BY clause were applied to the wrong SQL query, causing incorrect filtering results for audio/video media.
- Excel (XLSX) export: removed a duplicated column that incorrectly shifted the "a/v" value in case reports.
- "Only memos" filter: the strings "Only memos" and "Only coded memos" were not marked for translation, preventing the filter from working correctly in the Spanish version. This is now resolved for all languages.
- Matrix headers: fixed four issues that prevented correct display of code, file, and case memos in the matrix view (including a typo "alll," an extra comparison with "Case:", incorrect tuple validation, and a misplaced "All memo" literal).
- "Also all memos" option: now correctly displays the coded segment memo, a behavior previously missing despite the label's suggestion.
- Project merging: fixed an error that sometimes occurred when merging projects containing audio, video, or image files.


## New Features

### Category Hierarchy in Headers

The full hierarchical path is now displayed before the code name (for example: Root Category > Subcategory > ... > Code), making contextual reading of each segment easier.

### Co-occurring Codes

Below each coded segment memo, the set of overlapping codes within the same file is now listed in brackets, allowing quick identification of coding overlaps. This works for text, audio/video, and image data. You can view and export overlapping codes.

### New Category Sorting Option

A new sorting option has been added to the sort menu: "Category A-Z" and "Category Z-A," which organises results alphabetically according to the category hierarchy (with code name as a secondary criterion).


## In Summary

This QualCoder update represents a major leap forward for qualitative analysis. It offers better organization through code hierarchies, intelligent AI integration with secure permission levels, and more powerful file management tools (PDF, LaTeX, surveys). The interface has been improved for better ergonomics, with advanced visualisations (co-occurrence graphs, mind maps) and flexible exports (ODT, annotated PDFs, Gephi, draw.io). Numerous bug fixes have also been implemented for a more stable experience.


## Next Steps

We are already working on the next improvements for QualCoder. Your feedback is essential to help us prioritise future features. Please share your suggestions, bug reports, or ideas with us via [our support channel](https://github.com/ccbogel/QualCoder/issues).
