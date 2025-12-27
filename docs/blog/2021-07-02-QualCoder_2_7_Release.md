---
title: "QualCoder 2 7 Release"
date: 2021-07-02
author: ccbogel
category: Misc
---
The latest version of QualCoder has been released. <https://github.com/ccbogel/QualCoder/releases/tag/2.7>

Release 2.6 was removed as there was an error.

The wiki manual is current. <https://github.com/ccbogel/QualCoder/wiki> The pdf and odt manuals in the release folder do not show the latest functionality and so are outdated.

Fixed bugs:
-----------

Coding text: when searching for text and the 'all files' option is selected, an error occurs. (due to an upgrade in another functionality). Fixed.

Case deletion: This can affect the case attributes for multiple cases. Fixed.

Functionality:
--------------

Added dark mode. Activate in Settings.

Added search text function in Journals and in Manage Files > view audio/video file.\
Improved overly sensitive code extension and reduction keys in Code text (Shift or Alt + Left or Right arrow).

Added new auto-code function in Code text. This function uses start and end marks for autocoding. It includes all of the start mark and stops just before the end mark. The line ending character is '\n'.

Added an 'Important' function to coding. This flags coded text, AV, images as important codes. To use for obtaining exemplars. Added 'I' shortcut in code text code av text to mark important

Added a files filter when coding text, AV, images. This shows a filtered list of files, based on attribute values selected.

The codes tree -- can now merge one category into another category.

Improved importation of file variables from REFI-QDA Projects. Improved exportation of REFI-QDA Project file.

Added ctid unique autointeger column to the code_text database table.\
This also updates older QualCoder projects, when opened.

Can now edit coded text files while the text file contains coded/annotated/case-assigned text. **Avoid selecting text chunks and deleting or pasting text across selected text chunks which contain combinations of unmarked text sections and marked coded/annotated/case-assigned sections. As this will not update those assigned text segments correctly.** Press Ctrl+E when in the text area, to activate and exit this editing mode.

Reports:\
Added function to report on annotations in text files.\
Added function to add reporting memos: Options: None, Coded text memos, All memos.

Installation and running QualCoder:
-----------------------------------

### Windows:

Install VLC or from the Windows Store. Download and unzip the QualCoder-2.7.zip release.

The software does not have an exe for Windows. Download and install the Python programming language <https://www.python.org/downloads/windows/>. The minimum version that works for QualCoder is python 3.6. Download the file (at the bottom of the web site) "Windows installer (64-bit)" (or 32-bit if you have an older system) and install Python. IMPORTANT: in the first window of the installation mark the option "Add Python to PATH"

Install extra modules to Python. Type the letters "cmd" in the Windows Start searching engine, and click on the black software "cmd.exe" -- this is the command console for Windows. In the console paste, using the right-click context menu (ctrl+v does not work) the following:

py -m pip install pyqt5 lxml Pillow ebooklib ply chardet pdfminer.six openpyxl

Then click enter. Wait, until all modules are installed (the command phrase should be again visible: "C:\Users[Your Windows account name]> or similar).

Run QualCoder from cmd.exe Move to the QualCoder-2.7 folder. Then type py -m qualcoder

Or run by double-click. Open the QualCoder-2.7\qualcoder folder. Double-click the __main__.py file to run. You can make a shortcut to this file and keep the shortcut on the desktop.

### Linux:

Install these modules from the terminal:

sudo apt install python3-lxml python3-ply python3-six python3-pdfminer python3-chardet python3-qt5 python3-pillow

On some Linux versions you will need to install pip

sudo apt install python3-pip

sudo python3 -m pip install pdfminer.six openpyxl ebooklib

In the terminal, Go to the QualCoder-2.7 folder, then type:

sudo python3 setup.py install

To run. From the terminal type:

qualcoder

(Note: This release does not include a Debian install package.)
