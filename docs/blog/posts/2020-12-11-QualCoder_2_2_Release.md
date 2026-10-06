---
title: "QualCoder 2 2 Release"
date: 2020-12-11
author: ccbogel
category: Misc
---

The latest release of QualCoder is available from:

<https://github.com/ccbogel/QualCoder/releases/tag/2.2>

The changes are:

-   Improved UI features,with the use of icons and files selector list.
-   Improved imports and exports of REFI-QDA projects. Still an experimental function.
-   An option to link to files rather than store them internally in the project folder.
-   No longer store files larger than 2 Gbytes internally in the project folder for REFI-QDA compatibility.
-   Coded text memo functionality added.
-   Additional text auto-coding options for sentences (in one file or across all text files).
-   Auto-coding undo option.
-   Select multiple files for deletion function.
-   Italian language added.
-   Greek language added (translation requires revision).
-   Added warning when entering text into numeric case attribute.
-   Fixed error, new case attributes were always assigned to numeric type.

Revision of Japanese and Spanish translations is also required.

REFI-QDA:

REFI-QDA project export and import has improved. However, further testing of absolute and relative file links needs to be undertaken. In audio and video transcripts, the transcript codings and syncpoints require further testing. For REF-QDA project import, variables are stored as text so: boolean, date, integer and floating point. Although some of these are cast as numeric during operations. QualCoder does not import sets or graphs as it does not have this functionality.

With the newer iconified toolbars, the icons have not been tested on Mac OS.
