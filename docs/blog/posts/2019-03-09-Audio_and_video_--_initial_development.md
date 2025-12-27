---
title: "Audio and video -- initial development"
date: 2019-03-09
author: ccbogel
category: Misc
---

Audio and video files can be imported into QualCoder in the following formats: wav, mp3, mov, mp4, ogg, wmv.

You do need to have the vlc media player installed. See their site for details: https://www.videolan.org/vlc/

Or you can download through the Windows Store. Alternatively, on linux you can add vlc using the terminal (or run the install script):

```
sudo apt install vlc qtwayland5
```

Audio and video segments can be coded. Currently, the only way to obtain reports on coded segments or delete coded segments is through the sql_dialog window. Further work will be implemented to improve these functions.

The audio or video is shown in its own dialog window and the controls, codes and transcript is shown in a separate dialog, as illustrated below.
