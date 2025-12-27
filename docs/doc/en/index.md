# Documentation
Welcome to the QualCoder wiki!

The wiki covers instructions to install and use the QualCoder qualitative data analysis software. THe information here refers to the most recent version of QualCoder.

## What is QualCoder?
QualCoder is free, open source software for qualitative data analysis. 
With QualCoder you can code text, images, audio and video, write journal notes and memos. You can categorise codes into a tree-like hierarchical categorisation scheme. Coding for audio and video requires the VLC media player.
Coder comparison reports can be generated for text coding using the Cohen’s Kappa statistic. A graph displaying codes and categories can be generated to visualise the coding hierarchy. Most reports can be exported as html, open document text (ODT) or as plain text files.

Since version 3.6, QualCoder includes a set of AI-assisted features that utilize GPT-4 or other Large Language Models to help explore, analyze, and interact with data in innovative ways. Familiarize yourself with new data by [exploring broad topics or concepts](https://github.com/ccbogel/QualCoder/wiki/5.1.-AI-chat-based-analysis#topic-analysis-chat) in an interactive chat with the AI. Dive deeper into specific aspects with [AI-assisted coding](https://github.com/ccbogel/QualCoder/wiki/4.3.-AI-Assisted-Coding) and [text analysis](https://github.com/ccbogel/QualCoder/wiki/5.1.-AI-chat-based-analysis#text-analysis-chat). And if you reach the point where you must synthesize and consolidate your results, [discuss them in a code chat](https://github.com/ccbogel/QualCoder/wiki/5.1.-AI-chat-based-analysis#code-analysis-chat) with the AI.

QualCoder is designed to be used as client-based software to be used by one person at a time. (A second coder can use the same project on the same computer, or the project folder can be transferred to the second coder's computer). QualCoder is not designed to be multi-accessed at the same time. Accessing the project in a cloud location is not recommended, it may corrupt the database if a database connection is lost during any database updating processes. 

QualCoder is written by an Australian developer in python 3 using Qt for the graphical interface. A Sqlite database is used to store the coding data. There is also a Wordpress site for QualCoder at https://qualcoder.wordpress.com/.

##  Why use QualCoder?
**Qualcoder is free of charge.** Many qualitative analysis software requiring expensive one-time fees or monthly subscriptions. Not everyone can afford expensive fees.

**QualCoder is easy to use.** It has all you need to perform qualitative analysis without the complicated interfaces of some alternatives.

**QualCoder works offline.** Internet is not always available and QualCoder does not require internet to work.

**QualCoder is not tied to a computer.** If you change workplace you do not have to worry about being tied to your former workplace’s license or to buy a new license. QualCoder license allows you to use the software regardless of where you work or on what computer it is installed on.

**QualCoder is multi-platform.** It runs on Linux, Windows and Mac, this means that you do not have to worry if you change operating systems, and it also means you can collaborate with colleagues on different platforms.

**QualCoder uses AI transparently.** Unlike most commercial QDA packages, QualCoder allows you to see and even modify the underlying prompts of its AI features. You can also choose between different AI models or integrate your own. This gives methodological control back to us as researchers and makes QualCoder an ideal platform to experiment with new forms of AI-assisted qualitative data analysis. And yes—you can also disable the AI features completely if you choose not to use them.

**QualCoder relies on the community.** If you find a bug or have a feature request or feedback, write it on QualCoder’s page on github https://github.com/ccbogel/QualCoder.

**QualCoder is always improving.** QualCoder is actively developed meaning that newer versions are released with functionality improvements and error fixes.

**QualCoder supports open standards.** QualCoder aims to support the REFI-QDA Standard, see https://www.qdasoftware.org/ You may exchange codebooks and projects with your colleagues even if they do not use QualCoder, as long as the software they use supports the REFI-QDA Standard. It means that you do not risk your data being unavailable. The REFI-QDA Project export/import is still somewhat experimental and not guaranteed to work.

**QualCoder can be modified.** You can modify and adapt QualCoder to your needs, or if you do not how you ask someone to do it for you, as long as you release your changes to everyone. This also means you can copy the software and give it to your colleagues or students free of charge. It is released from 3.6 and up under the LGPL v3 license.

**QualCoder is a software option to support open science. [UNESCO recommendations on open science](https://www.unesco.org/en/open-science?hub=686)

## Wiki in other languages

[Wiki in Français](https://qualcoder-fr.frama.io/)

## Collaboration on a Qualcoder project

[Page on how to work as a team with QualCoder](https://github.com/ccbogel/QualCoder/wiki/2.4.-Working-in-a-Team)


**If you use and like QualCoder please support the development.**

<a href="https://www.buymeacoffee.com/ccbogelB" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

_5.3_

# Setup
## QualCoder Installation and running instructions

### INSTALLATION 

For the manual installations (using the command line or terminal) I mention a specific release version, for example version 3.6. Please check on the [releases page](https://github.com/ccbogel/QualCoder/releases) for the most current version, as it may be newer. 

#### Prerequisites
VLC is optional, but you will need it installed if you need to do any audio/video coding. Optionally, install ffmpeg for speech to text and waveform display, see https://phoenixnap.com/kb/ffmpeg-windows..

#### Windows

See [https://github.com/ccbogel/QualCoder/releases/3.7](https://github.com/ccbogel/QualCoder/releases/3.7)

You have two options for executables, created on Windows 11, and may work on Windows 10:

- There is a Windows installer on the release page called: **QualCoder.Win.3.7.exe**

- There is a standalone, non-installable exe folder called: **QualCoder.Win.3.7.Portable.zip** Download and unzip. It is in a folder alongside an internal folder. These both must be together or the exe will not run. Double-click the QualCoder exe to run, it takes up to 20 seconds to start. 

Standalone, portable version: <img width="100" height="60" alt="QualCoder portable" src="https://github.com/user-attachments/assets/6be1de98-8b47-4d57-b4b5-c34375e44959" />

On first use of the exe, Windows may ask you to allow to run QualCoder. This is because it is from an unknown publisher. It costs a lot of money to get a trusted publisher certificate - so that will not be possible for the foreseeable future. If you are uncomfortable with these warnings install from the source as detailed next.

Alternatively, install from source code:

Download the source code. Read and apply the section for Windows source code usage in the **Readme.md** file.
Remove the back ticks that surround the command line instructions ` as these are used for display only.

#### MacOS

**Install from App bundles:**

Make sure you have installed any MAC OS updates before starting the installation. Go to the System Settings app on your Mac. Click General in the sidebar (you may need to scroll down), then click Software Update.

Install QualCoder:  Double-click the downloaded dmg-file. Drag QualCoder into the link to your applications.

Start QualCoder from your Launchpad or by double-clicking the app within your applications folder.
We are currently not able to sign the app bundles, so when you first try to run the program, you may get a pop-up warning that QualCoder is from an unregistered developer or "QualCoder can't be opened because Apple cannot check it for malicious software." Depending on your processor, you may see one of these:

If you see "Show in Finder" or OK.  Click Ok.

If you see "Done" or "Move to trash. Click "Done.

Next, go to Settings and select Privacy and Security.  Scroll down until you see a message stating QualCoder was prevented from starting. Click on "open anyway". You may be prompted to enter your password and may need to click "Open" again.  After entering your password, just wait for the program to open up. It may take several seconds.

From now on, QualCoder should start without issues.

**Install from source code:**

Download the source code. Read and apply the section for masOC source code usage in the **Readme.md** file.
Remove the back ticks that surround the command line instructions ` as these are used for display only.


#### Debian/Ubuntu Linux

There is an executable file in the releases page for Ubuntu 24.04 for the 3.6 release. Download and double click to run.

Alternatively, run QualCoder from the source code:

Download the source code. Read and apply the section for Ubuntu source code usage in the **Readme.md** file.
Remove the back ticks that surround the command line instructions ` as these are used for display only.

#### Fedora 43

These instructions are tested with QualCoder 3.7 on Fedora 43 with Python 3.12.12.

Install dependencies:

`sudo dnf install python3.12`

Set up QualCoder:

`cd ~/qualcoder  # replace with appropriate location on your machine`

`python3.12 -m venv env`

`source env/bin/activate`

`python3.12 -m ensurepip`

`python3.12 -m pip install --upgrade pip`

`mkdir tmp`

`TMPDIR=./tmp python3.12 -m pip install -r requirements.txt`

`deactivate`

Usage:

`cd ~/qualcoder  # replace with appropriate location on your machine`

`source env/bin/activate`

`cd src`

`python3.12 -m qualcoder`

#### Fedora 42 

These instructions download the current source code directly from GitHub. Note: Fedora uses Wayland which may not work well with the Qt graphical interface. It is suggested you also install Xwayland.

Download the source code. Read and apply the section for Fedora source code usage in the **Readme.md** file.
Remove the back ticks that surround the command line instructions ` as these are used for display only.

There may be problems with QualCoder working with audio / video in Fedora.

#### Arch/Manjaro Linux

Download the source code. Read and apply the section for Arch source code usage in the **Readme.md** file.
Remove the back ticks that surround the command line instructions ` as these are used for display only.



