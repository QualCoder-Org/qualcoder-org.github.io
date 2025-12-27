---
title: "Launcher for Linux"
date: 2024-11-12
author: ccbogel
category: Misc
---

Thanks to Carlos Lira for this post on his blog. This is how to make a launcher for QualCoder on Linux. The Ubuntu executable is available through the Releases pages of QualCoder. If you use a different version of Linux, or want to run for source code instead. Please read the full blog below. I have copied an excerpt only

<https://aldats.dev/blog/launch-qualcoder-without-terminal>

### Creating the QualCoder Script

1.  Create a file named `qualcoder` in your preferred text editor.
2.  Copy the Bash script below and paste it into the `qualcoder` file.

    `#!/bin/bash`\
    `\
    QUALCODER_DIRECTORY="/home/aldats/Documents/qualcoder"`\
    `\
    source $QUALCODER_DIRECTORY/qualcoder/bin/activate\
    $QUALCODER_DIRECTORY/qualcoder/bin/qualcoder &`

3.  Replace the value for `QUALCODER_DIRECTORY` on line 3 with the full path to your QualCoder installation.
4.  Mark the file `qualcoder` as executable. This can be done with the command `chmod +x qualcoder`.
5.  Enter the command `./qualcoder`. QualCoder should launch.

### Moving the QualCoder Script to a `PATH` Directory

1.  In a terminal, enter the command `echo $PATH`. This prints the value of your `PATH` variable.
2.  Observe output similar to below. Paths are separated by a colon (`:`).\
    `/home/aldats/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/sbin:/bin`
3.  Pick one of the paths in your `PATH` output. I picked `/home/aldats/.local/bin`.
4.  Move your `qualcoder` script to the directory at the path you picked.
5.  Open a new terminal.
6.  In the new terminal, enter the command `qualcoder`. QualCoder should launch.

Second: Run QualCoder From a Launcher
-------------------------------------

On Linux, launchers generate a list of launchable programs by looking for special *desktop* files in directories like `/usr/share/applications/` and `~/.local/share/applications/`. If you make a desktop file for QualCoder in one of these directories, you can run QualCoder with a launcher.

1.  Create a file named `qualcoder.desktop` in your preferred text editor.
2.  Copy the below text and paste it into `qualcoder.desktop`.\
    `[Desktop Entry]`\
    `Name=QualCoder`\
    `Exec=qualcoder`\
    `Type=Application`\
    `StartupWMCClass=qualcoder`
3.  Move your `qualcoder.desktop` file to a directory your launcher will find desktop files in, like `/usr/share/applications/` or `~/.local/share/applications/`.
4.  In your launcher, look up "QualCoder" and launch.
