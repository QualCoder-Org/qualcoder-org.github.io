---
title: "QualCoder 2 9 release"
date: 2022-01-25
author: ccbogel
category: Misc
---

The 2.9 version is now available through <https://github.com/ccbogel/QualCoder/releases/tag/2.9>

There is also a Windows 10 exe in the release.

Details of changes are listed below:

Manage files
------------

New audio/video file.\
Option to use an online speech to text service if there is no transcription text present.\
This requires ffmpeg software to be installed.\
Fixed a time stamp error when inserting a time stamp on a transcription.

Manage bad links to files
-------------------------

Added an automated search that looks through the user's home directory for up to 2 matching file names. This intended to speed up finding the link to files where the link is currently pointing to nothing.

Coding text
-----------

Added right-hand side side panel that shows three different information options:

-   Current code with code rule and examples of its use.
-   Current journal (most recent date) for reading and editing
-   Project memo for reading and editing
-   Underline applied to overlapping codes, for identification of overlaps
-   Added button to enter and exit the edit text mode
-   Added Ctrl + Z to restore the last coding that was unmarked.

Coding images
-------------

-   Added Ctrl + Z to restore the last coding that was unmarked.
-   Add menu option to resize and reposition a coded area.

Coding Audio Video
------------------

-   Added Ctrl + Z to restore the last coding that was unmarked.

Reports codes
-------------

Added statistics summary via check box\
Added options to the matrix. So can have codes/categories by file or by case.\
Added coding in context checkbox for text codings. This shows the surrounding 250 characters of text to help put the coded section in context in the report. The coded text is shown in bold.

View Graph
----------

-   Added button to save graph as a png image.

Special functions
-----------------

Dynamic text file replacement.\
For example, useful for updating a text file of a list of blog posts.\
The function works by looking for identical text segments in the replacement file to match the previous codings and annotations. If the replacement file contains multiple matches, then only the first match is used. So there is potential for inaccuracy. Tries to match any case assignment also. Again may potentially be inaccurate.

Settings
--------

The number of project backups can be selected by he user.\
Changed how to selected another coder name and how to enter a new coder name.
