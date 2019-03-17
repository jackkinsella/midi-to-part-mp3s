# SATB

This program splits takes a midi file that contains every part of a choral work (i.e. SATB) and generates practice MP3 tracks for each voice.

# Installation

* git clone `TODO`

## Dependencies
* python3
* [TiMidity++](https://wiki.archlinux.org/index.php/timidity) - MIDI-to-WAVE converter and player. Install on macos with `$ brew
    install timidity`
* [Lame](http://lame.sourceforge.net/) - create mp3 files. Install on macos with `$ brew install lame`
* [mido](https://mido.readthedocs.io/en/latest/)  - midi objects for python. Install with `pip3 install mido`

# Usage

`$ midi-to-part-mp3s /Downloads/my-midi.mid`

The files will appear in the folder `$ ./output`
