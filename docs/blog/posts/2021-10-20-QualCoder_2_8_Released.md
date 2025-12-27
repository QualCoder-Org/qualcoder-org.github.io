---
title: "QualCoder 2 8 Released"
date: 2021-10-20
author: ccbogel
category: Misc
---

Hello,

I am pleased to announce a new release of QualCoder, version 2.8. This release includes a Windows 10 exe.

This release contains bug fixes and additional functionality.

The release is available from: <https://github.com/ccbogel/QualCoder/releases/tag/2.8>

The main new functions are:

### Code by case.

You can select a case and code the files or text file portions assigned to that case. There is some reduced functionality compared to the existing Code Text and Code AV functions:

-   in text files: no auto-coding -- due to risk of auto coding non-case assigned text portions.
-   in A/V files only duration segments can be coded, the associated text file is not shown -- due to file conflicts in how the data structure works in Code by Case.

The code by case function will be useful when importing a survey and one or more of the survey columns is designated 'qualitative'. The qualitative data are converted into a single text entry on import. Sections of this text are assigned to the relevant case (relevant survey row) and can then be coded for each case (survey row entry).

SQL statements
--------------

You can save SQL statements for later use. SQL statements can be deleted via right-click menu option.

With regards Colin
