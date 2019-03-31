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

**Gotcha:** There is often a midi track for time signatures placed at track 0. This must be included in all solo mp3s,
otherwise you'll find that a 5 minute track might be over in 1 minute.

By default, track 0 of the midi is set to time sig, and tracks 1-4 are set to SATB respectively. These defaults are used with:

`$ ./midi-to-part-mp3s /Downloads/my-midi.mid`

To customize which tracks are assigned to track, run the command using the
options display with

`$./midi-to-part-mp3s --help`

The mp3 files will appear in the folder `$ ./output`

