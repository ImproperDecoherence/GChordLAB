
"""
This module defines data, classes and functions used to handle different chords.
"""


__author__ = "https://github.com/ImproperDecoherence"


import itertools
import copy

from GUtils import GSignal, debugVariable

from .ToneIntervals import GToneInterval, normalizeIntervals, intervalSignature, nearSignatures
from .MusicalChar import GMusicalChar
from .Notes import noteToNoteValue, noteName, noteValuesToNoteNames, NoteNames, rebaseNoteValues


SCALE_DEGREES = {1: "Tonic", 2: "Supertonic", 3: "Mediant", 4: "Subdominant", 5: "Dominant", 6: "Submediant", 7: "Subtonic"}
"""Mapping between relative note position in a scale and the name of the scale degree name."""

class GChordModifier:
    """A GChordModifier can be applied to a GDynamicChord to alter its notes, e.g. to change a G chord to a G7 chord."""

    def __init__(self, long_name: str, short_name: str, to_add: list[int], to_remove: list[int], cancels: list[int]) -> None:
        """
        Args:
            long_name: The long name of the modifier, e.g. 'dominant 7'.
            short_name: The short name of the modifier, e.g. '7'.
            to_add: A list of relative intervals to be added to the chord, e.g. '[GToneInterval.m7]'.
            to_remove: A list of relative intervals to be removed from the chord.
            cancels: A list of relative intervals which represents a modifier which shall be cancelled by this modifier.            
        """

        self.long_name = long_name
        self.short_name = short_name
        self.to_add = to_add
        self.to_remove = to_remove
        self.cancels = cancels

        
    def apply(self, root, source: list[int]) -> list[int]:
        """Applies this modifier to a given input intervals and returns the result.
        
        All 'to_add' intervals are added and all 'to_remove' are removed from the 'source'.

        Args:
            root: The root note value to be used with 'source'.
            source: The input interval values; note value = root + source value.
        """
        removing = [root + i for i in self.to_remove]
        adding   = [root + i for i in self.to_add]

        for r in removing:
            if r in source:
                source.remove(r)

        source.extend(adding)
        source.sort()

        return source
    

    def shortName(self) -> str:
        """Returns the short name of the modifier, e.g. '7'."""
        return self.short_name


    def longName(self) -> str:
        """Returns the long name of the modifier, e.g. 'dominant 7'."""
        return self.long_name


    def appendShortName(self, input: str) -> str:
        """Returns the input string with the short name of the modifier appended."""
        return input + self.short_name
    

    def appendLongName(self, input: str) -> str:
        """Returns the input string with the long name of the modifier appended."""

        # Fix to avoid getting 'major major 7'
        if (" major" in input) and ("major 7" not in input):
            input = input.replace(" major", "")

        return input + " " + self.long_name
    

    def cancelsModifiers(self) -> list[int]:
        """Returns a list with the modifiers which shall be candelled by this modifier."""
        return self.cancels


    def __str__(self) -> str:
        """Enables print of GChordModifier."""
        return f"GChordModifier({self.self.short_name})"
    

    def __repr__(self) -> str:        
        """Enables print of GChordModifier."""
        return self.__str__()


class GChordFlags:
    """Flags which identifies different chord modifiers; can be added toghether with the binary | operator."""
    NoFlag       = 0b0000000000000000
    Dominant7    = 0b0000000000000001
    Major7       = 0b0000000000000010
    Dominant9    = 0b0000000000000100
    Dominant11   = 0b0000000000001000
    Dominant13   = 0b0000000000010000
    Add2         = 0b0000000000100000
    Add6         = 0b0000000001000000
    Add9         = 0b0000000010000000
    Flat5th      = 0b0000000100000000
    Suspended2nd = 0b0000001000000000
    Suspended4th = 0b0000010000000000


CHORD_MODIFIERS = {
    GChordFlags.Dominant7:    GChordModifier("dominant 7",    "7",    
                                             to_add=[GToneInterval.m7], 
                                             to_remove=[],
                                             cancels=[]),

    GChordFlags.Major7:       GChordModifier("major 7",       "maj7", 
                                             to_add=[GToneInterval.M7], 
                                             to_remove=[],
                                             cancels=[]),

    GChordFlags.Dominant9:    GChordModifier("dominant 9",    "9",    
                                             to_add=[GToneInterval.m7, GToneInterval.M9], 
                                             to_remove=[], 
                                             cancels=[GChordFlags.Dominant7]),

    GChordFlags.Dominant11:   GChordModifier("dominant 11",   "11",   
                                             to_add=[GToneInterval.m7, GToneInterval.M9, GToneInterval.P11], 
                                             to_remove=[], 
                                             cancels=[GChordFlags.Dominant7, GChordFlags.Dominant9]),

    GChordFlags.Dominant13:   GChordModifier("dominant 13",   "13",   
                                             to_add=[GToneInterval.m7, GToneInterval.M9, GToneInterval.P11, GToneInterval.M13], 
                                             to_remove=[],
                                             cancels=[GChordFlags.Dominant7, GChordFlags.Dominant9, GChordFlags.Dominant11]),

    GChordFlags.Suspended2nd: GChordModifier("suspended 2nd", "sus2", 
                                             to_add=[GToneInterval.M2], 
                                             to_remove=[GToneInterval.m3, GToneInterval.M3],
                                             cancels=[]),

    GChordFlags.Suspended4th: GChordModifier("suspended 4th", "sus4", 
                                             to_add=[GToneInterval.P4], 
                                             to_remove=[GToneInterval.m3, GToneInterval.M3],
                                             cancels=[]),

    GChordFlags.Add2:         GChordModifier("add 2",         "+2", 
                                             to_add=[GToneInterval.M2], 
                                             to_remove=[],
                                             cancels=[]),

    GChordFlags.Add6:         GChordModifier("add 6",         "+6",    
                                             to_add=[GToneInterval.M6], 
                                             to_remove=[],
                                             cancels=[]),

    GChordFlags.Add9:         GChordModifier("add 9",         "+9", 
                                             to_add=[GToneInterval.M9], 
                                             to_remove=[],
                                             cancels=[]),

    GChordFlags.Flat5th:      GChordModifier("flath 5th",     "b5",   
                                             to_add=[GToneInterval.dim5], 
                                             to_remove=[GToneInterval.P5],
                                             cancels=[]),
    }
"""Defines dictionary dict[GChordFlag, GChordModifier] with available chord modifiers."""


class GDynamicChordTemplate:
    """A template for different triad chord types, e.g. major, minor etc."""

    def __init__(self, long_name: str, short_name: str, intervals: list[int]) -> None:
        """
        Args:
            long_name: The long name of the chord type, e.g. 'minor'.
            short_name: The short name of the chord type, e.g. 'm'.
            intervals: A list of relative interval values which defines the chord type.
        """
        self.long_name = long_name
        self.short_name = short_name
        self.intervals = intervals


    def noteValues(self, root: int) -> list[int]:
        """Returs the note values of the chord.
        
        Args:
            root: The root note value of the chord.
        """
        return [n + root for n in self.intervals]
    

    def shortName(self, root:int, style="flat") -> str:
        """Returns the short name of the chord, e.g. 'Cm'."""

        return noteName(root, style, show_octave=False) + self.short_name
    

    def longName(self, root: int, style="flat") -> str:
        """Returns the long name of the chord, e.g. 'C minor'."""

        if len(self.long_name) > 0:
            space = " "
        else:
            space = ""

        return noteName(root, style, show_octave=False) + space + self.long_name
    

class GChordType:
    """Definition of values representing the different types of triad chords."""
    MajorChord      = 1
    MinorChord      = 2
    DiminishedChord = 3
    AgumentedChord  = 4


CHORD_TYPES = {
    GChordType.MajorChord:      GDynamicChordTemplate("major",      "",                [GToneInterval.R, GToneInterval.M3, GToneInterval.P5]),
    GChordType.MinorChord:      GDynamicChordTemplate("minor",      "m",               [GToneInterval.R, GToneInterval.m3, GToneInterval.P5]),
    GChordType.DiminishedChord: GDynamicChordTemplate("diminished", GMusicalChar.Dim,  [GToneInterval.R, GToneInterval.m3, GToneInterval.dim5]),
    GChordType.AgumentedChord:  GDynamicChordTemplate("augmented",  "+",               [GToneInterval.R, GToneInterval.M3, GToneInterval.Aug5])}
"""Dictionary dict[GChordType, GDynamicChordTemplate] which defines templates for avaliable triad chord types."""



class GDynamicChord:
    """Represents a chord which can be modified by applying GChordModifiers."""

    def __init__(self, root: int | str, template: GDynamicChordTemplate, flags: int | list[int] = GChordFlags.NoFlag) -> None:
        """
        Args:
            root: Root note value OR root note name of the chord.
            template: The GDynamicChordTemplate which defines the type of the chord.
            flags (optional): A list of GChordFlags which each represents a chord modifier to be applyed, OR
              an integer with accumulated GChordFlags, e.g. 'GChordFlags.Dominant7 | GChordFlags.Add9'.
        """
        self.root = noteToNoteValue(root)
        self.template = template        
        self.flags: list[int] = []
        
        self.inversion = 0 
        """Represents how many inversion steps have been applied to the chord. Inversion is modulo number of notes in the chord.
        """

        self.chordChanged = GSignal()
        """Signal which is emitted with parameter GDynamicChord when the state of the chord is changed."""

        self.setFlags(flags)


    def clone(self) -> 'GDynamicChord':
        """Returns a deep copy of the chord."""

        return copy.copy(self)


    @staticmethod
    def fromNoteValues(note_values: list[str]) -> 'GDynamicChord':
        """Creates and returns a GDynamicChord based on the provided note values.
        
        Currently this method only returns one of the basic chord types, i.e.
        major, minor, diminished or augmented.

        Args:
            note_values: At least three note values.

        Returns:
            A GDynamicChord or None.

        Raises:
            ValueError if the chord cannot be created from provided notes.
        """
        debugVariable("note_values")

        if len(note_values) < 3:
            raise ValueError("At least 3 notes!")
        
        rebased_note_values = rebaseNoteValues(note_values, 0)
        debugVariable("rebased_note_values")
        tonic = rebased_note_values[0]
        
        note_intervals = {value - tonic for value in rebased_note_values}
        debugVariable("note_intervals")

        chord = None

        for chord_type in CHORD_TYPES.keys():
            if set(CHORD_TYPES[chord_type].intervals) <= note_intervals:
                chord = GDynamicChord(tonic, CHORD_TYPES[chord_type])

        return chord


    def rootNoteValue(self) -> int:
        """Returns the root note value of the chord."""
        return self.root


    def rootNoteName(self, style="flat", show_octave=False) -> str:
        """Returns the root note name of the chord."""
        return noteName(self.root, style, show_octave)
    

    def noteValues(self) -> list[int]:
        """Returns the note values of the chord.
        
        The root note will be in octave 0.
        Selected inversion will be applied (see setInversion).
        """
        values = self.template.noteValues(self.root)

        # apply modifiers
        for flag in self.flags:            
            values = CHORD_MODIFIERS[flag].apply(self.root, values)

        # apply inversion
        for _ in range(self.inversion):
            values = [values[-1] - GToneInterval.Octave] + values[:-1]
            if values[0] < 0:
                values = [i + GToneInterval.Octave for i in values]

        return values


    def numberOfNotes(self) -> int:
        """Returns the number of notes of the chord."""
        return len(self.noteValues())
    

    def normalizedNoteValues(self) -> set[int]:
        """Returns the normalized note values of the chord.
        
        A normalized chord will have all note values within octave 0.
        """
        return normalizeIntervals(self.noteValues())
    

    def signature(self) -> int:
        """Returns an integer which represents an unique signature of the normalized notes of the chord."""
        return intervalSignature(self.noteValues())


    def noteNames(self, style="flat", show_octave=True) -> list[str]:
        """Returns the names of the notes of the chord.
        
        Args:
            style (optional): 'sharp' or 'flat'.
            show_octave (optional): Indicates if the octave numbers shall be a part of the name.
        """
        return noteValuesToNoteNames(self.noteValues(), style, show_octave)


    def setInversion(self, steps: int):
        """Sets the inversion of the chord.

        When a chord is inverted, the root note will no longer be the lowest note of the chord.
        For each inversion step, another of the notes of the chord will be the lowest note
        of the chord.
        
        Args:
            steps: The number of inversion steps. Inversion steps are modulo N, where N is
              the number of notes of the chord, i.e. inversion N + 1 = inversion 0.            
        """
        self.inversion = steps % len(self.noteValues())


    def cycleInversion(self):
        """Increases the inversion by one, module number of notes of the chord."""
        self.inversion = (self.inversion + 1) % len(self.noteValues())    


    def setRoot(self, root: int | str):
        """Sets the root note of the chord.
        
        Args:
            root: Note value OR note name.

        Emits:
            chordChanged if the root note was changed.
        """
        old_root = self.root
        self.root = noteToNoteValue(root)

        if self.root != old_root:
            self.chordChanged.emit(self)

    
    def setFlags(self, flags: int | list[int]):
        """Sets the modifications which shall be applied to the chord.
        
        Args:
            flags: A list of GChordFlags which each represents a chord modifier to be applyed, OR
              an integer with accumulated GChordFlags, e.g. 'GChordFlags.Dominant7 | GChordFlags.Add9'.

        Emits:
            chordChanged if the modifiers of the chord is changed.
        """
        old_flags = list(self.flags)
        temp_flags = []

        if type(flags) is list:
            if GChordFlags.NoFlag in flags:
                flags.remove(GChordFlags.NoFlag)
            temp_flags = flags

        elif flags != GChordFlags.NoFlag:            
            temp_flags = [flag for flag in CHORD_MODIFIERS.keys() if (flags & flag)]

        self.flags = list(temp_flags)

        for flag in temp_flags:
            for flag_to_be_canceled in CHORD_MODIFIERS[flag].cancelsModifiers():
                if flag_to_be_canceled in self.flags:
                    self.flags.remove(flag_to_be_canceled)

        if self.flags != old_flags:
            self.chordChanged.emit(self)


    def shortTypeName(self, style="flat") -> str:
        """Returns the short name of the chord without modifiers, i.e. 'C#m' for 'minor'."""
        return self.template.shortName(self.root, style)


    def shortModName(self, style="flat") -> str:
        """Returns the combined short name of the modifiers and inversion, without the root note name and the chord type, e.g. '7add9/G'."""
        name = ""

        for flag in self.flags:
            name = CHORD_MODIFIERS[flag].appendShortName(name)

        base_note_value = self.noteValues()[0]
        if base_note_value != self.rootNoteValue():
            name = name + "/" + noteName(base_note_value, style, show_octave=False)

        return name


    def longName(self, style="flat") -> str:
        """Returns the full long name of the chord including modifiers."""
        name = self.template.longName(self.root, style)

        for flag in self.flags:
            name = CHORD_MODIFIERS[flag].appendLongName(name)

        return name
    

    def shortName(self, style="flat") -> str:
        """Returns the full short name of the chord including modifiers and inversion."""
        return self.shortTypeName(style) + self.shortModName()        


    def match(self, intervals: set[int]) -> bool:
        """Tests if the normalized input intervals are equal to the normalized intervals of the chord."""
        normalized_interval = {v % GToneInterval.Octave for v in intervals}
        return normalized_interval == self.normalizedNoteValues()


    def contains(self, intervals: set[int]) -> bool:
        """Tests if the normalized input intervals is a subset of the normalized intervals of the chord."""
        normalized_interval = {v % GToneInterval.Octave for v in intervals}
        return normalized_interval.issubset(self.normalizedNoteValues())


    @property
    def centerOfGravity(self) -> float:
        """Returns the average note value of the note values of the chord."""
        return sum(self.noteValues()) / self.numberOfNotes()


    def __eq__(self, other):
        """Compare operator for GDynamicChord."""

        if isinstance(other, GDynamicChord):
            return self.signature() == other.signature()
        
        if isinstance(other, list):
            if len(other) > 0:
                if isinstance(other[0], int):
                    return self.signature() == intervalSignature(other)
                
        raise ValueError("Invalid type!")
        

    def __ne__(self, other):
        """Compare operator for GDynamicChord."""
        return not self.__eq__(other)


    def __str__(self):
        """Enables print of GDynamicChord."""
        return f"GDynamicChord({self.longName()} | {self.shortName()})"
    

    def __repr__(self):
        """Enables print of GDynamicChord."""
        return self.__str__()



class GChordDatabase:
    """An instance of this class is a database with chords of all types, all normalized root notes and 
    combinations of chord modifications.    
    """

    def __init__(self, number_mod_combinations = 2) -> None:
        """
        Args:
            number_mod_combinations (optional): An integer which defines the number of combinations of
              chord modifications will be applied when the database is created.
        """
        
        self._chord_database: dict[int, list[GDynamicChord]] = dict()
        """The chord database is a directory with the chord signature as key value. Since different
        chords can have the same signature, each database entry may contain several chords.
        """

        print(f"Creating chord database ...")

        for root in NoteNames(0, GToneInterval.Octave, style="flat", show_octave=False):
            for type in CHORD_TYPES.values():
                all_flags = [GChordFlags.NoFlag, *CHORD_MODIFIERS.keys()]
                flag_combinations = [list(t) for t in itertools.combinations(all_flags, number_mod_combinations)]                

                self._addChord(GDynamicChord(root, type, GChordFlags.NoFlag))

                for flags in flag_combinations:
                    self._addChord(GDynamicChord(root, type, flags))
                    
        print(f"{self._size()} chords added to chord datbase with {len(self._chord_database)} unique signaturres.")   


    def _addChord(self, chord: GDynamicChord) -> None:
        """Adds a chord to the database."""
        signature = chord.signature()

        if signature in self._chord_database:
            chords_with_signature = self._chord_database[signature]
            if chord.shortName() not in [c.shortName() for c in chords_with_signature]:
                self._chord_database[signature].append(chord)
        else:
            self._chord_database[signature] = [chord]


    def _size(self) -> int:
        """Returns the number of chords in the database."""
        count = 0

        for chords in self._chord_database.values():
            count += len(chords)
        return count


    def matchIntervals(self, intervals: list[int], distance: int = 0) -> list[GDynamicChord]:
        """Returns chords found in the database which matches the input intervals.
        
        Args:
            intervals: The input interval is normalized and it is compared with the
              normalized intervals of the chords in the database.
            distance: The number of notes which shall differ to make a match, e.g.
              distance = 0 returns exact matches, distance = 1 returns chords which
              differs with one note.
        """
        chords: list[GDynamicChord] = []
        input_signature = intervalSignature(intervals)        
        signatures_to_seach_for = nearSignatures(input_signature, distance)        

        debugVariable("input_signature")
        debugVariable("signatures_to_seach_for")

        for signature in signatures_to_seach_for:
            if signature in self._chord_database:
                chords.extend(self._chord_database[signature])

        debugVariable("chords")

        return chords




def unitTest():

    chords = [GDynamicChord("C", CHORD_TYPES[GChordType.MajorChord]),
              GDynamicChord("C", CHORD_TYPES[GChordType.MinorChord]),
              GDynamicChord("C", CHORD_TYPES[GChordType.MinorChord], GChordFlags.Add2 | GChordFlags.Add9),
              GDynamicChord("E", CHORD_TYPES[GChordType.AgumentedChord], GChordFlags.Suspended2nd | GChordFlags.Add2 ),
              GDynamicChord("E", CHORD_TYPES[GChordType.AgumentedChord], GChordFlags.Suspended2nd | GChordFlags.Add9 )
              ]


    for c in chords:
        print(c, intervalSignature(c.noteValues()))

    # for root in NoteNames(0, GToneInterval.Octave, style="sharp", show_octave=False):
    #     for type in CHORD_TYPES.values():
    #         for flag in [GChordFlags.NoFlag, *CHORD_MODIFIERS.keys()]:
    #             flag = flag | GChordFlags.Dominant7
    #             chord = GDynamicChord(root, type, flag)
    #             print(chord, chord.noteNames(), chord.signature(), chord.centerOfGravity)



if __name__ == "__main__":
    unitTest()
    