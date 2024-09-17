# GChordLAB

## Background

Wondering why certain combinations of notes made me feel different things, I started to
study music theory on my own. After a while I got the idea that writing software which
make use of music theory could be a fun way to learn more about it - the result of that
decision is **GChordLAB**.

## The Current State of GChordLAB

GChordLAB is currently in alpha version.

GChordLAB has so far only been tested on Windows 10 which Python 3.12.3 and PyQt6 6.7.0.

## What's GChordLAB?

GChordLAB is program written in Python 3 and utilizes the [PyQt6](https://doc.qt.io/qtforpython-6/) 
framework for the GUI.

The current version of GChordLAB has the following features which are described in more detail further down:

- **Instrument** for playing notes and visualizing chords.
- **Scale** selector for finding notes and chord for different keys and scales.
- **Chord Editor** for chord creation.
- **Interval Circle** for visualizing the tone intervals of a chord.
- **Chord Cache** for storage of chords you have created.
- **Chord Finder** for chord generation by using a seed chord and parameter setting.s
- **Chord Player** for playing sequences of chords.

![GChordLAB overview](https://i.imgur.com/4gpqeF1.png)

### Instrument

The Instrument is a piano keyboard which keys you can click to play notes. You can CTRL + click the piano keys to select them - then they become red. Selected notes can be used as input to the Chord Finder.

You can change the sound of the notes and control the sound volume in the upper left corner of the Instrument. In the upper right corner you can change which octaves are used.

The Instrument also have a right click menu where you can clear all selections.

### Scale

In the Scale part of the GUI you can select a key and a scale and then click Play to see and hear the scale be played. When the Show checkbox is checked, and overlay on the Instrument shows the notes that belong to the scale.

Under the scale selection will the main chord of the scale be created. You can play these chords by clicking them and also drag'n'drop them to other parts of the GUI.

The following scales are currently supported:

- Lydian
- Natural major
- Mixolydian
- Dorian
- Natural minor
- Phrygian
- Locrian
- Harmonic minor

### Chord Editor

In the chord editor you can create a chord by performing the following steps:

1. Selecting a root note in the top left combobox.
2. Selecting chord type (major, minor, diminished or augmented) by selecting one of the buttons to the right of the root note selector.
3. Adding chord modifications by selecting one or more of the remaining (square) buttons.

The created chord appears in the bottom right corner of the Chord Editor. Drag the chord to the Chord Cache if you want to save it for later.

### Interval Circle

The Interval Circle is the main reason for me starting with this project. I wanted to see with my eyes how the chord intervals looked like for different types of chords.

The twelve chromatic notes that belongs to one octave are distributed around the circle like the hours of a clock. The current key (selected in the Scale section of the GUI) holds the 12 o' lock position.

When the mouse pointer hovers over a chord, the intervals of the notes of the chord will be drawn as lines in the circle. The following intervals are shown:

- m2/M7: minor 2nd (semitone) / Major 7th
- M2/m7: Major 2nd / minor 7th
- m3/M6: minor 3rd / Major 6th
- M3/m6: Major 3rd / minor 6th
- P4/P5: Perfect 4th / Perfect 5th
- dim5: diminished 5th / augmented 4th

### Chord Cache

The Chord Cache is a place for storing chords for later - drag'n'drop a chord to any free slot. If the slot is already occupied by a chord, the chord will be replaced.

Right-click on a chord to bring up its context menu; here you can clear the chord slot or cycle the chords inversion.

### Chord Finder

The Chord Finder is a tool for generating a set of chords from a seed chord and a set of adjustable parameters. To generate chords, perform the following actions:

1. Select which chord generator to use from the Generator combo box.
2. If the selected generator needs a seed chord, a selector for the Source for the seed chord appears under the Generator selection:
   - Instrument: the generator will use the selected notes at the piano keyboard as seed.
   - Seed: the generator will use the chord slot to the right as seed - drop any chord there.
3. If the generator needs parameters as input, they will appear in the bottom part of the Chord Finder. The heading of each parameter has a tool tip which explains its function - hover the mouse over it to see the tool tip.
4. The matching chord will now be show in the list to the right. Click them to visualize and play them and drag the chords to the Chord Cache to save them.

#### Chord Generator: Matching Chords

This generator takes a seed chord and a parameter called Distance. The generator will search for chords which differs with Distance number notes from the seed chord. For example:

The seed C+ with Distance 0 will generate: C+, E+, Ab+ which all contains same note intervals.

The seed C with Distance 1 will generate: C7, Cmaj7, Am7, etc.

#### Chord Generator: Chords of Scale

This generator takes no seed but has two parameters: Scale and Key. It will generate the triad chords which belongs to given scale and key. For example:

Scale: Natural Major and Key: C will generate: C, Dm, Em, F, G, Am, Bdim.

### Chord Player

The CHord Player is a simpe player of a sequence of chords - drag'n'drop chords to slots and press Play.


## Installing & Running GChordLAB

The following prerequisites must be fulfilled before GChordLab can be executed:

1. Install [Python 3](https://www.python.org/downloads/).
2. Install [PyQt6](https://www.pythonguis.com/pyqt6/).
3. Download the [GChordLAB repository](https://github.com/ImproperDecoherence/GChordLAB).
4. Install sound files for the Instrument - see below.
5. To run in Windows:
   1. Right-click on the shortcut GChordLAB and select Properties, and then change the "Start in" path to the path where you have downloaded the GChordLAB.
   2. Copy the shortcut to your desktop.
   3. Launch GChorLAB by double-click the GChordLAB on your desktop.

### Installing Sound Files for the Instrumnent

GChordLAB can run without installed sound files, but then it will not be able to play any chords.

To hear sound when using GChordLAB, sound profiles for the Instrument must be installed in the directory `gchordlab/res/` where `gchordlab/` is the folder where the GChordLAB repository is installed.

The `gchordlab/res/` should contain one sub-folder for each instrument sound profile. The name of the folder (with _ replaced with space) will be used as the name of Instrument in the GUI.

The sub-folders are supposed to contain wav-files where each wav-file is the sound of a single note. The naming covention is: `\<note name\>\<octave number>.wav`, where note names are written with "flat" notation, i.e. chromatic notes are written as `Db` and not `C#` There must be at least 3 octaves + 1 notes number files whith continious note names without gaps.

Example:

```
gchordlab/res/
    Grand_Piano/
        C1.wav
        Db1.wav
        D1.wav
        E1.wav
        Eb1.wav
        F1.wav
        Gb1.wav
        G1.wav
        Ab1.wav
        A1.wav
        Bb1.wav
        B1.wav
        C2.wav
        ...
        B2.wav
        C3.wav
```

