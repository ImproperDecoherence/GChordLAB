"""
This module defines different scales and function which operates on scales.
"""


__author__ = "https://github.com/ImproperDecoherence"


from collections import deque
from itertools import accumulate

from GUtils import debugOn, debugVariable
from GMusicIntervals import (GDynamicChord, GToneInterval,
                             noteToNoteValue, noteName, noteValue, sortNoteNames, noteValuesToNoteNames)

class GScaleIntervals:
    NaturalMajor  = [GToneInterval.R, GToneInterval.M2, GToneInterval.M3, GToneInterval.P4, GToneInterval.P5, GToneInterval.M6, GToneInterval.M7, GToneInterval.O]
    """Defines the intervals for the natural major scale."""

    HarmonicMinor = [GToneInterval.R, GToneInterval.M2, GToneInterval.m3, GToneInterval.P4, GToneInterval.P5, GToneInterval.m6, GToneInterval.M7, GToneInterval.O] 
    """Defines the intervals for the harmonic minor scale."""



class GScaleTemplate:
    """Scale templates defines tone intervals and a mode for that interval, e.g. Natural Major mode 2 (Dorian)."""

    def __init__(self, intervals: list[int], mode: int, name: str) -> None:
        """
        Args:
            intervals: A list of note itervals to be used for mode = 1.
            mode: An integer 1-7 defining the mode to be applied for the given 'intervals'.
            name: The name of the scale.
        """
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
"""A dictionary dict[scale name, scale template] which defines available scale templates."""



class GScale:
    """Represents a scale which is defined by its root note and its intervals, e.g. C Natural Major."""

    def __init__(self, root: int | str, scale_template_name: str):
        """
        Args:
            root: The root note name OR the root note value of the scale.
            scale_template_name: The name of the template which defines the intervals of the sclale (see SCALE_TEMPLATES)
        """
        self.template = SCALE_TEMPLATES[scale_template_name]
        self.root = noteToNoteValue(root)


    def scaleSteps(self) -> list[int]:
        """Returns a list with the distance (in semi tones) between the sequential intervals of the scale.
        
            The first value is the distance from the root note to next note, etc. until the last note
            of the scale.
        """
        steps = deque([b - a for a, b in zip(self.template.intervals[:-1], self.template.intervals[1:])])
        steps.rotate(1 - self.template.mode)
        return list(steps)


    def scaleIntervals(self) -> list[int]:
        """Returns the tone intervals of the scale relative the root note.
        
        I.e. the first value will always be zero.
        """
        return [0, *list(accumulate(self.scaleSteps()))]


    def noteValues(self, base_note_value: int = 0) -> list[int]:
        """Returns the note values (from one octave) of the scale.
        
        Args:
            base_note_value (optional): This must be a C-note value. The returned values of the scale
              will be greater than this C-note value but also as close as possible to this C-note value.
        
        Raises:
            ValueError if input conditions are not met.
        """
        if (base_note_value % GToneInterval.Octave) != 0:
            raise ValueError("base_note_value must be a C-note")
                
        return [base_note_value + self.root + interval for interval in self.scaleIntervals()[:-1]]


    def extendedNoteValues(self) -> list[int]:
        """Returns the note values of the scale from octaves 0 - 3."""
        octave1 = self.noteValues()
        octave0 = [value - GToneInterval.Octave for value in octave1 if (value - GToneInterval.Octave) >= 0]
        octave2 = [value + GToneInterval.Octave for value in octave1]
        octave3 = [value + GToneInterval.Octave for value in octave2]
        return octave0 + octave1 + octave2 + octave3


    def rootNoteValue(self):
        """Returns the root note value of the scale."""
        return self.root


    def rootNoteName(self, style="flat") -> str:
        """Returns the root note name of the scale.
        
        Args:
            style (optional): 'sharp' or 'flat'
        """
        return noteName(self.root, style, show_octave=False)        


    def scaleName(self):
        """Returns the name of the template of the scale, i.e. 'Dorian'."""
        return self.template.name


    def noteNames(self, style="flat") -> list[str]:
        """Returns a list of the note names of the scale."""
        return sortNoteNames(noteValuesToNoteNames(self.noteValues(), style, show_octave=True))
    

    def name(self, style="flat") -> str:
        """Returns the full name of the scale, including the name of the root note., i.e. 'C Natural Major'."""
        return f"{self.rootNoteName(style)} {self.template.name}"


    def noteValueBelongsToScale(self, note_value: int) -> bool:
        """Tests if a note value belongs to the scale."""

        normalized_note_value = note_value % GToneInterval.Octave
        normalized_scale_values = [note_value % GToneInterval.Octave for note_value in self.noteValues()]
        return normalized_note_value in normalized_scale_values


    def noteNameBelongsToScale(self, note_name) -> bool: 
        """Tests if a note name belongs to the scale."""
        return self.noteValueBelongsToScale(noteValue(note_name))


    def numberOfNotesInScale(self):
        """Returns the number of notes in the scale."""
        return len(self.template.intervals) - 1


    def relativeNoteName(self, note_value: int):
        """Returns the relative nota name of the scale for a given note value.
        
        The relative note name of the root note of the scale is '1', the next note in the scale
        has the relative note name '2', etc. Chromatic notes (not in scale) are named e.g.
        'b1' or '#5'.
        """
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


    def chordsOfScale(self) -> list[GDynamicChord]:
        """Returns the basic chords of the scale.
        
        The basic chords of the scale are the triad chords which can be constructed from
        the minor or major thirds of the scale.
        """
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


    def setRoot(self, root: int):
        """Changes the root note value of the scale."""
        self.root = root


    def __str__(self):
        """To enable print of scale."""
        return self.name(style="flat") + " " + str(self.noteValues()) + " " + str(self.noteNames())
    

    def __repr__(self):
        """To enable print of scale."""
        return self.__str__()



def unitTest():
    pass
    

if __name__ == "__main__":
    unitTest()




