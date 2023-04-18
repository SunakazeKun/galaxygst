# galaxygst
![Ghost Luigi and Jibberjay Racers in Wild Glide Galaxy](https://raw.githubusercontent.com/SunakazeKun/galaxygst/master/SCREENSHOT.png)

**galaxygst** is a Python command-line tool to record object motion files (GST files) for [Ghost Luigis](https://www.mariowiki.com/Ghost_(Super_Mario_Galaxy_2)) and [Jibberjay Racers](https://www.mariowiki.com/Jibberjay) in **Super Mario Galaxy 2**. The tool reads relevant information from [Dolphin Emulator](https://dolphin-emu.org/)'s emulated game memory and automatically produces a GST file after recording stopped. The tool requires at least **Python 3.10**. It should also work with 3.11 and newer versions, but this hasn't been tested. Furthermore, it uses [py-dolphin-memory-engine](https://github.com/henriquegemignani/py-dolphin-memory-engine) to interact with Dolphin's game memory. In order to record object motion during gameplay, [Syati](https://github.com/SunakazeKun/Syati)'s *GstRecord* code is required to supply the information from the game to this tool.

It is available on PyPI, meaning that you can easily install it with pip:
```
pip install galaxygst
```

# Usage
In this section, it is assumed that the game you want to record object motion in already uses Syati's *GstRecord* code. The general usage is this:
```
usage: galaxygst [-h] [-address [ADDRESS]] output_folder_path

Record GST object motion in SMG2 from Dolphin memory.

positional arguments:
  output_folder_path  folder to save GST files to

options:
  -h, --help          show this help message and exit
  -address [ADDRESS]  address from which the tool retrieves GstRecordInfo*
```

The ``-address`` option is not required, as the tool assumes ``GstRecordInfo*`` is supplied at ``0x80003FF8`` by default.

# Recording
**TODO**

The tool keeps you informed about its current state, and it should inform you when something goes wrong. Here's an example from one of my tests:
```
Waiting for Dolphin...
Hooked to Dolphin, game ID is SB4P!
Searching for GstRecorderInfo* at 0x80003FF8...
Waiting for GstRecordHelper...
Started recording for GhostAttackGhost in RedBlueExGalaxy Star 1!
Stopped recording!
Dumped 619 ghost frames (approx. 10 seconds) to '.\RedBlueExGalaxy\GhostAttackGhostData01.gst'.
```

After recording, you can build a Ghost.arc containing the GST file. However, this is beyond the scope of this tool. In final releases of your levels, you don't want players to interact with GstRecordHelper objects, so make sure to remove them once they are not needed anymore.