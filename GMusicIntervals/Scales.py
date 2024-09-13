"""
Module Scales
"""


__author__ = "https://github.com/ImproperDecoherence"


from collections import deque
from itertools import accumulate

from GUtils import debugOn, debugVariable
from GMusicIntervals import (GDynamicChord, GToneInterval,
                             noteToNoteValue, noteName, noteValue, sortNoteNames, noteValuesToNoteNames, 
                             rebaseNoteValues, multiplyIntervals, transposeIntervals,
                             CHORD_TYPES)

class GScaleIntervals:
    NaturalMajor  = [GToneInterval.R, GToneInterval.M2, GToneInterval.M3, GToneInterval.P4, GToneInterval.P5, GToneInterval.M6, GToneInterval.M7, GToneInterval.O]
    HarmonicMinor = [GToneInterval.R, GToneInterval.M2, GToneInterval.m3, GToneInterval.P4, GToneInterval.P5, GToneInterval.m6, GToneInterval.M7, GToneInterval.O] 



class GScaleTemplate:
    def __init__(self, intervals, mode, name):
        self.intervals = intervals
        self.mode = mode
        self.name = name



SCALE_TEMPLATES = {"Lydian":         GScaleTemplate(intervals=GScaleIntervals.NaturalMajor,  mode=4, name="Lydian"),
                   "Natural Major":  GScaleTemplate(intervals=GScaleIntervals.NaturalMajor,  mode=1, name="Natural Major"),
                   "Mixolydian":     GScaleTemplate(intervals=GScaleIntervals.NaturalMajor,  mode=5, name="Mixolydian"),
                   "Dorian":         GScaleTemplate(intervals=GScaleIntervals.NaturalMajor,  mode=2, name="Dorian"),
                   "Natural minor":  GScaleTemplate(intervals=GScaleIntervals.NaturalMajor,  mode=6, name="Natural minor"),
                   "Phrygian":       GScaleTemplate(intervals=GScaleIntervals.NaturalMajor,  mode=3, name="Phrygian"),                                                         
                   "Locrian":        GScaleTemplate(intervals=GScaleIntervals.NaturalMajor,  mode=7, name="Locrian"),
                   "Harmonic minor": GScaleTemplate(intervals=GScaleIntervals.HarmonicMinor, mode=1, name="Harmonic minor"), 
                   }



class GScale:

    def __init__(self, root: int | str, scale_name: str):
        self.template = SCALE_TEMPLATES[scale_name]
        self.root = noteToNoteValue(root)


    def clone(self):
        return GScale(self.root, self.template.name)


    def scaleSteps(self) -> list[int]:
        steps = deque([b - a for a, b in zip(self.template.intervals[:-1], self.template.intervals[1:])])
        steps.rotate(1 - self.template.mode)
        return list(steps)


    def scaleIntervals(self) -> list[int]:
        return [0, *list(accumulate(self.scaleSteps()))]


    def noteValues(self, base_note_value: int = 0, octaves: int = 1) -> list[int]:

        if (base_note_value % GToneInterval.Octave) != 0:
            raise ValueError("base_note_value must be a C-note")
                
        return [base_note_value + self.root + interval for interval in self.scaleIntervals()[:-1]]


    def extendedNoteValues(self) -> list[int]:
        octave1 = self.noteValues()
        octave0 = [value - GToneInterval.Octave for value in octave1 if (value - GToneInterval.Octave) >= 0]
        octave2 = [value + GToneInterval.Octave for value in octave1]
        octave3 = [value + GToneInterval.Octave for value in octave2]
        return octave0 + octave1 + octave2 + octave3


    def rootNoteValue(self):
        return self.root


    def rootNoteName(self, style="flat") -> str:
        return noteName(self.root, style, show_octave=False)        


    def scaleName(self):
        return self.template.name


    def noteNames(self, style="flat") -> list[str]:
        return sortNoteNames(noteValuesToNoteNames(self.noteValues(), style, show_octave=True))
    

    def name(self, style="flat") -> str:
        return f"{self.rootNoteName(style)} {self.template.name}"


    def transpose(self, interval: int):
        self.root += interval


    def noteValueBelongsToScale(self, note_value: int) -> bool:
        normalized_note_value = note_value % GToneInterval.Octave
        normalized_scale_values = [note_value % GToneInterval.Octave for note_value in self.noteValues()]
        return normalized_note_value in normalized_scale_values


    def noteNameBelongsToScale(self, note_name) -> bool:        
        return self.noteValueBelongsToScale(noteValue(note_name))


    def numberOfNotesInScale(self):
        return len(self.template.intervals) - 1


    def relativeNoteName(self, note_value: int, base_value: int):
        normalized_scale_values = [value % GToneInterval.Octave for value in self.noteValues()]
        note_value_to_pos = {value: i + 1 for i, value in enumerate(normalized_scale_values)}

        normalized_note_value = note_value % GToneInterval.Octave
        if normalized_note_value in note_value_to_pos.keys():
            return str(note_value_to_pos[normalized_note_value])

        normalized_note_value = (note_value + 1) % GToneInterval.Octave
        if normalized_note_value in note_value_to_pos.keys():
            return "b" + str(note_value_to_pos[normalized_note_value])
        
        normalized_note_value = (note_value - 1) % GToneInterval.Octave
        if normalized_note_value in note_value_to_pos.keys():
            return "#" + str(note_value_to_pos[normalized_note_value])
        
        return ""


    def chordsOfScale(self, optimalInversion=False) -> list[GDynamicChord]:
        debugVariable("self")

        chords = []

        octave1 = self.noteValues()
        octave2 = [value + GToneInterval.Octave for value in octave1]
        scale_values = octave1 + octave2

        TONIC = 0
        MEDIANT = 2
        DOMINANT = 4

        for i, _ in enumerate(self.noteValues()):
            chord_note_values = [scale_values[TONIC + i], scale_values[MEDIANT + i], scale_values[DOMINANT + i]]
            chords.append(GDynamicChord.fromNoteValues(chord_note_values))

        return chords


    def setRoot(self, root):
        self.root = root


    def __str__(self):
        return self.name(style="flat") + " " + str(self.noteValues()) + " " + str(self.noteNames())
    

    def __repr__(self):
        return self.__str__()



def unitTest():
    pass
    

if __name__ == "__main__":
    unitTest()




