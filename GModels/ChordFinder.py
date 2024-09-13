"""
Module ChordFinder
"""

__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtCore import Qt, QAbstractListModel

from .ChordGenerators import GChordGenerator,  GMatchingChordsGenerator, GChordsOfScaleGenerator

from GUtils import GSignal, debugVariable
from GModels import GPianoModel, GPianoKeyState
from GMusicIntervals import GDynamicChord, GChordDatabase


class GChordFinder:
    
    class SourceType:
        NoSource = 0
        Instrument = 1
        Seed = 2

    class _ChordListModel(QAbstractListModel):

        def __init__(self, chords: list[GDynamicChord]):
            super().__init__()
            self.chords = chords

        def data(self, index, role):            
                if role == Qt.ItemDataRole.DisplayRole:
                    return self.chords[index.row()]
                
        def rowCount(self, index):
            return len(self.chords)


    def __init__(self, piano_model: GPianoModel):        
        self.piano_model = piano_model
        self.piano_model.keyStateChanged.connect(self.pianoKeyStateUpdated)

        self.found_chords: list[GDynamicChord] = []
        self.chord_list_model = GChordFinder._ChordListModel(self.found_chords)

        self.chord_database = GChordDatabase(number_mod_combinations=2)
        
        self.chord_generators = {g.name(): g for g in [GMatchingChordsGenerator(self.chord_database),
                                                     GChordsOfScaleGenerator()]}
        
        print(self.chord_generators)

        self.current_generator = self.chord_generators["Matching Chords"]
        for g in self.chord_generators.values():
            g.settingsChanged.connect(self._generatorSettingsUpdated)

        self.seed_chord: GDynamicChord = None
        self.source = GChordFinder.SourceType.Instrument

        self.chordsUpdated = GSignal()


    def availableGenerators(self) -> list[GChordGenerator]:
        return self.chord_generators.values()


    def currentSource(self) -> SourceType:
        return self.source


    def currentChords(self) -> list[GDynamicChord]:
        return self.found_chords
    

    def currentNumberOfChords(self) -> int:
        return len(self.found_chords)


    def setCurrentGenerator(self, generator_name: str):
       self.current_generator = self.chord_generators[generator_name]
       self.updateChords()


    def currentGenerator(self) -> GChordGenerator:
        return self.current_generator


    def pianoKeyStateUpdated(self, key: GPianoKeyState):
        if self.source == GChordFinder.SourceType.Instrument:
            self.updateChords()    


    def setSource(self, source: SourceType):
        self.source = source
        self.updateChords()


    def setSeedChord(self, chord: GDynamicChord):
        self.seed_chord = chord
        if self.source == GChordFinder.SourceType.Seed:
            self.updateChords()


    def updateChords(self):

        if self.source == GChordFinder.SourceType.Seed:
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

    
    def _generatorSettingsUpdated(self, setting_name: str, setting_value):
        self.updateChords()

