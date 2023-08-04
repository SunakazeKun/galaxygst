# galaxygst
![Ghost Luigi and Jibberjay Racers in Wild Glide Galaxy](https://raw.githubusercontent.com/SunakazeKun/galaxygst/master/SCREENSHOT.png)

**galaxygst** is a Python command-line tool to record object motion files (GST files) for [Ghost Luigis](https://www.mariowiki.com/Ghost_(Super_Mario_Galaxy_2)) and [Jibberjay Racers](https://www.mariowiki.com/Jibberjay) in **Super Mario Galaxy 2**. The tool reads relevant information from [Dolphin Emulator](https://dolphin-emu.org/)'s emulated game memory and automatically produces a GST file after recording stopped. The tool requires at least **Python 3.10**. It should also work with 3.11 and newer versions, but this hasn't been tested. Furthermore, it uses [py-dolphin-memory-engine](https://github.com/henriquegemignani/py-dolphin-memory-engine) to interact with Dolphin's game memory. In order to record object motion during gameplay, [Syati](https://github.com/SunakazeKun/Syati)'s *GstRecord* code is required to supply the information from the game to this tool.

It is available on PyPI, meaning that you can easily install it with pip:
```
pip install galaxygst
```

# Limitations
For Ghost Luigis, you should only record proper GST files for normal Power Stars. The game won't recognize GST files associated with Green Stars!

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
Before you can record GST files, you need to prepare a recorder object in your galaxy first. For example, ``GhostLuigiRecordHelper`` can be used to record GST files for Ghost Luigi. Once you have configured the helper object, you are ready to use the tool:

1. Launch the modded game in Dolphin and start this command-line tool like explained in previous sections.
2. While the game is running, pay attention to the tool's console output to verify that everything is running correctly.
3. Once you are in the desired galaxy, go to where you placed the recorder object. An A button icon will be displayed on the screen when you are close to it.
4. Once you press A, the recorder object will start. The player's controls will be disabled for one second before the recording starts.
5. If you desire to stop recording, press 2 on the first player's Wiimote.

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

## Synchronization Error
If the recording process terminates due to a synchronization error, you should try the following things before recording again:
- Close unnecessary programs and processes.
- Give the galaxygst process a higher priority.
- Reduce the emulation's execution speed (less than 100%).

If the error persists, try cutting down the emulator's execution speed even further.
