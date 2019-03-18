# SATB

This program splits takes a midi file that contains every part of a choral work (i.e. SATB) and generates practice MP3 tracks for each voice.

# Installation

* git clone `TODO`

## Dependencies
* python3
* [Fluidsynth](http://www.fluidsynth.org/) - MIDI-to-WAVE converter and player. Install on macos with `$ brew
    install timidity`
* [Lame](http://lame.sourceforge.net/) - create mp3 files. Install on macos with `$ brew install lame`
* [SoX](http://sox.sourceforge.net/) - mix audio files. Install on macos with `$brew install sox`. Also
    require python interface, installed with `pip3 install sox`
* [mido](https://mido.readthedocs.io/en/latest/)  - midi objects for python. Install with `pip3 install mido`

# Usage

`$ ./midi-to-part-mp3s /Downloads/my-midi.mid`

The files will appear in the folder `$ ./output`
