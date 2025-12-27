---
title: "QualCoder 3 0 Release"
date: 2022-05-20
author: ccbogel
category: Misc
---

Hello everyone,

I have released QualCoder 3.0 today. I have only tested on Ubuntu 20.04 and Windows 10.\
You must have VLC installed. Optionally, install ffmpeg for speech to text and waveform image creation. (ffmpeg tested on Ubuntu only).\
There is an exe for Windows 10 and an executable for Ubuntu 20.04.

The graphical framework have been updated from Qt5 to Qt6.

Other changes:

Manage files
------------

-   Rename database file name entry, function added.

Code text
---------

-   Fixed uncaught IndexError exception when editing text positions.
-   Fixed AttributeError updating Tooltips in merge_codes
-   Export coded text file to odt or html. Does not export the tooltips (future work to do).

Reports
-------

-   Added Charting function.
-   Pie, Bar, Sunburst, Heatmap and Treemap charts can be created and are displayed in the default web browser. Heatmaps are limited to 40 rows and 40 columns for nicer display and faster rendering.
-   Graph
    -   Added right-click menu options to show files and cases as text objects.
    -   Added right-click menu options to add extra free text objects and lines.
    -   zoom +/- function.
    -   Future work will be to save and load these user edited graphs within the database.

Special functions
-----------------

-   Added ability to merge another QualCoder project into the current project. Always make a back up of your project first, just in case there is a problem.

Errors fixed
------------

-   File deletion error -- SQL bindings mismatch -- fixed.
-   Uncaught IndexError exception when editing text positions from within code text -- fixed.
-   AttributeError updating Tooltips when merging codes- fixed.
-   Dark text on dark code colour in Code image fixed. Now shows white text. fixed.
