"""
This module provides services for generating chords from a seed chord and parameters.
"""

__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtCore import Qt, QAbstractListModel

from .ChordGenerators import GChordGenerator,  GMatchingChordsGenerator, GChordsOfScaleGenerator

from GUtils import GSignal, debugVariable
from GModels import GPianoModel, GPianoKeyState
from GMusicIntervals import GDynamicChord, GChordDatabase


class GChordFinder:
    """Provides an interface for handling a set of chord generators."""
    
    class SeedType:
        """Definition of different seed types."""
        NoSeed = 0
        Instrument = 1
        Chord = 2


    class _ChordListModel(QAbstractListModel):
        """Model for chords to be used by a QListView."""

        def __init__(self, chords: list[GDynamicChord]) -> None:
            super().__init__()
            self.chords = chords


        def data(self, index, role) -> GDynamicChord:
                if role == Qt.ItemDataRole.DisplayRole:
                    return self.chords[index.row()]
                

        def rowCount(self, index) -> int:
            return len(self.chords)


    def __init__(self, piano_model: GPianoModel):
        """
        Args:
            piano_model: The model to be used as seed for SeedType.Instrument.
        """
        self.piano_model = piano_model
        self.piano_model.keyStateChanged.connect(self._pianoKeyStateUpdated)

        self.found_chords: list[GDynamicChord] = []
        self.chord_list_model = GChordFinder._ChordListModel(self.found_chords)

        self.chord_database = GChordDatabase(number_mod_combinations=2)
        
        self.chord_generators = {g.name(): g for g in [GMatchingChordsGenerator(self.chord_database),
                                                       GChordsOfScaleGenerator()]}

        self.current_generator = self.chord_generators["Matching Chords"]
        for g in self.chord_generators.values():
            g.settingsChanged.connect(self._generatorSettingsUpdated)

        self.seed_chord: GDynamicChord = None
        self.seed_type = GChordFinder.SeedType.Instrument

        self.chordsUpdated = GSignal()


    def availableGenerators(self) -> list[GChordGenerator]:
        """Returns available chord generators."""
        return self.chord_generators.values()


    def currentSeedType(self) -> SeedType:
        """Returns the current seed type."""
        return self.seed_type


    def currentChords(self) -> list[GDynamicChord]:
        """Returns a list of generated chords."""
        return self.found_chords
    

    def currentNumberOfChords(self) -> int:
        """Returns number of generated chords."""
        return len(self.found_chords)


    def setCurrentGenerator(self, generator_name: str) -> None:
       """Sets the current chord generator."""
       self.current_generator = self.chord_generators[generator_name]
       self.updateChords()


    def currentGenerator(self) -> GChordGenerator:
        """Returns the current chord generator."""
        return self.current_generator


    def setSeedType(self, seed_type: SeedType):
        """Sets the current seed type."""
        self.seed_type = seed_type
        self.updateChords()


    def setSeedChord(self, chord: GDynamicChord):
        """Sets the chord to be used for seed type Chord."""
        self.seed_chord = chord
        if self.seed_type == GChordFinder.SeedType.Chord:
            self.updateChords()


    def updateChords(self):
        """Re-runs the current chord generator to replace the list of generated chords."""

        if self.seed_type == GChordFinder.SeedType.Chord:
            if self.seed_chord is not None:
                seed_interval = self.seed_chord.noteValues()
            else:
                seed_interval = []
        else:
            seed_interval = self.piano_model.selectedNoteValues()

        found_chords = self.currentGenerator().generateFromIntervals(seed_interval)
        debugVariable("found_chords")
        self.found_chords = found_chords
        self.chordsUpdated.emit(self)


    def _pianoKeyStateUpdated(self, key: GPianoKeyState):
        """Is called when selected instrument keys has changed."""
        if self.seed_type == GChordFinder.SeedType.Instrument:
            self.updateChords()    
    

    def _generatorSettingsUpdated(self, setting_name: str, setting_value):
        """Is called when the parameter settings of a generator had changed."""
        self.updateChords()

