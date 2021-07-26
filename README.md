# Midi to Part MP3s

This program splits takes a midi file that contains every part of a choral work (e.g. SATB) and generates practice MP3
tracks for each voice.

E.g. running

```bash
./bin/midi-to-part-mp3s -f ~/Downloads/full_song.mid -tsf 0.7 -s 1 -s2 2 -a 3 -t 4 -b 5
```

Would split the midi file into 5 tracks (including soprano 1 and 2) and scale the tempo by 70%.

The mp3 files will appear in the folder `./output`.

## Detailed Use

```bash
midi-to-part-mp3s: : the following arguments are required: -f/--file-path

optional arguments: [-h] [-a ALTO] [-a2 ALTO2] [-s SOPRANO] [-s2 SOPRANO2] [-b BASS] [-b2 BASS2] [-t TENOR] [-t2 TENOR2]
                         [-in INSTRUMENT] [-tsf TEMPO_SCALING_FACTOR] [-av ACCOMPANIMENT_VOLUME_RATIO] [-iv INSTRUMENTAL_VOLUME]
                         [-i INSTRUMENTAL_ACCOMPANIMENT [INSTRUMENTAL_ACCOMPANIMENT ...]] -f FILE_PATH
                         [-rif [RETAIN_INTERMEDIATE_FILES]] [-gat [GENERATE_ACCOMPANIMENT_TRACKS]] [-gabot]
                         [-o OUTPUT_DIRECTORY] [-sf SOUNDFONT_PATH] [-c COMPRESS_DYNAMIC_RANGE] [-v] [-la]

```

See the `cli.py` file for details.

## Installation

Clone this repo, then:

```bash
brew install fluidsynth lame sox # Assuming mac
python -m venv venv
source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

Next add a general soundfont. This must be placed within './soundfonts'. The program assumes you have [Timbres of Heaven](https://drive.google.com/uc?id=0B2NEzl-56UFHd054VnJETzJOZjg&export=download) downloaded to that folder and named `timbres-of-heaven.sf2`. If you download an `.sfark` file, you can [go here to convert it](https://cloudconvert.com/sfark-to-sf2) to ".sf2".

## Dependencies

* python3, version 3.6 or greater
* [Fluidsynth](http://www.fluidsynth.org/) - MIDI-to-WAVE converter and player.
* [Lame](http://lame.sourceforge.net/) - create mp3 files.
* [SoX](http://sox.sourceforge.net/) - mix audio files.
* [mido](https://mido.readthedocs.io/en/latest/)  - midi objects for python.
* [musescore](https://musescore.org/en/handbook/install-linux) - music toolkit used to convert MusicXML to midi.

## Usage

**Gotcha:** There is often a midi track for time signatures called a tempo map placed at track 0. This must be included in all solo mp3s, otherwise you'll find that a 5 minute track might be over in 1 minute.

By default, track 0 of the midi is set to time signatures, and tracks 1-4 are set to SATB respectively. These defaults are used with:

## Development

If you're having issues, run the command with the flags `-v` (`--verbose`) and `-la` (`--log-all-midi-messages`) and redirect the output to `debug.log`

Afterwards use command line tools to debug the messages

```bash
rg velocity debug.log | rg note_on | awk '{print $4}' | uniq
```

### Static type checker

First install [mypy](http://mypy-lang.org/) `$ pip3 install mypy`.  Now run `$ mypy midi-to-part-mp3s`. Or better yet, integrate `mypy` to your editor for inline type warnings.

### Code formatting

First install [autopep8](https://pypi.org/project/autopep8/) `$ pip3 install autopep8`. Now run `$ autopep8 <filename>`. Best include `autopep8` in your editor to format the code on save automatically.

## Tests

```bash
(venv) $ python -m unittest discover -s tests/ -p 'test*.py'
```

### Available fixtures

* tests/fixtures/Schumann-op67-4.mid – already includes a separate tempo map. Happy case.
* tests/fixtures/Schubert-872-sanctus.mid – does not have a separate tempo map, therefore exercises our internal midi rewrite features
* tests/fixtures/Brahms-Da-unten-im-Tale.mid - Another SATB example for general testing
* tests/fixtures/Abendlied-Rheinberger.xml - MusicXML example to test conversion and SSAATTBB track generation
* tests/fixtures/chillingham.mid - Example that uses channel instead of tracks to split up different voices
* tests/fixtures/an_den_mond.midi - Example that has all the same CC=11 to scale
  volumen instead
* tests/fixtures/Ws-mend-595.midi - MusicXML example where the tempo info was lost with some conversion kits. File should be 1:47 (not 40 seconds as it were initially)

## License

This and all derivative code can be used freely for non-commercial purposes.
