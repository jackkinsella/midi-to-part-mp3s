# Midi to Part MP3s

This program splits takes a midi file that contains every part of a choral work (i.e. SATB) and generates practice MP3 tracks for each voice.

# Installation

* `git clone https://github.com/jackkinsella/midi-to-part-mp3s`

## Dependencies
* python3
* [Fluidsynth](http://www.fluidsynth.org/) - MIDI-to-WAVE converter and player. Install on macos with `$ brew
    install timidity`
* [Lame](http://lame.sourceforge.net/) - create mp3 files. Install on macos with `$ brew install lame`
* [SoX](http://sox.sourceforge.net/) - mix audio files. Install on macos with `$ brew install sox`. Also
    require python interface, installed with `$ pip3 install sox`
* [mido](https://mido.readthedocs.io/en/latest/)  - midi objects for python. Install with `$ pip3 install mido`
* [music21](https://web.mit.edu/music21/) - music toolkit used to convert MusicXML to midi. Install with `$ pip3 install music21`
* A general soundfont. This must be placed within './soundfonts'. The program assumes you have [Timbres of Heaven](https://drive.google.com/uc?id=0B2NEzl-56UFHd054VnJETzJOZjg&export=download) downloaded to that folder and named `timbres-of-heaven.sf2`. If you download an `.sfark` file, you can [go here to convert it](https://cloudconvert.com/sfark-to-sf2) to ".sf2"

# Usage

**Gotcha:** There is often a midi track for time signatures placed at track 0. This must be included in all solo mp3s,
otherwise you'll find that a 5 minute track might be over in 1 minute.
## Quick start

By default, track 0 of the midi is set to time signatures, and tracks 1-4 are set to SATB respectively. These defaults are used with:

`$ pip3 install -r requirements.txt`
`$ ./midi-to-part-mp3s /Downloads/my-midi.mid`

The mp3 files will appear in the folder `$ ./output`.

## Detailed

To customize which input tracks are assigned to which voices and certain volume ratios.

```bash
usage: midi-to-part-mp3s [-h]
                         [-csts COMMON_SOLO_TRACKS [COMMON_SOLO_TRACKS ...]]
                         [-s SOPRANO] [-a ALT] [-t TENOR] [-b BASS]
                         [-iv INSTRUMENTAL_VOLUME]
                         [-i INSTRUMENTAL_ACCOMPANIMENT [INSTRUMENTAL_ACCOMPANIMENT ...]]
                         midifile_path

positional arguments:
  midifile_path

optional arguments:
  -h, --help            show this help message and exit
  -csts COMMON_SOLO_TRACKS [COMMON_SOLO_TRACKS ...], --common-solo-tracks COMMON_SOLO_TRACKS [COMMON_SOLO_TRACKS ...]
                        midi tracks that must appear in all solo mp3s e.g.
                        because they contain time signature changes
  -s SOPRANO, --soprano SOPRANO
  -a ALT, --alt ALT
  -t TENOR, --tenor TENOR
  -b BASS, --bass BASS
  -iv INSTRUMENTAL_VOLUME, --instrumental-volume INSTRUMENTAL_VOLUME
                        configure instrumental volume
  -i INSTRUMENTAL_ACCOMPANIMENT [INSTRUMENTAL_ACCOMPANIMENT ...], --instrumental-accompaniment INSTRUMENTAL_ACCOMPANIMENT [INSTRUMENTAL_ACCOMPANIMENT ...]
                        midi tracks that appear in all accompaniment mp3s e.g.
                        piano or orchestra

```

