
"""
Module Chords
"""


__author__ = "https://github.com/ImproperDecoherence"


import itertools
import copy

from GUtils import GSignal, debugVariable

from .ToneIntervals import GToneInterval, normalizeIntervals, intervalSignature, nearSignatures
from .MusicalChar import GMusicalChar
from .Notes import noteToNoteValue, noteName, noteValuesToNoteNames, NoteNames, rebaseNoteValues


SCALE_DEGREES = {1: "Tonic", 2: "Supertonic", 3: "Mediant", 4: "Subdominant", 5: "Dominant", 6: "Submediant", 7: "Subtonic"}

class GChordModifier:

    def __init__(self, long_name: str, short_name: str, to_add: list[int], to_remove: list[int], cancels: list[int]) -> None:
        self.long_name = long_name
        self.short_name = short_name
        self.to_add = to_add
        self.to_remove = to_remove
        self.cancels = cancels

        
    def apply(self, root, source: list[int]) -> list[int]:        
        removing = [root + i for i in self.to_remove]
        adding   = [root + i for i in self.to_add]

        for r in removing:
            if r in source:
                source.remove(r)

        source.extend(adding)
        source.sort()

        return source
    

    def shortName(self):
        return self.short_name


    def longName(self):
        return self.long_name


    def appendShortName(self, input: str) -> str:
        return input + self.short_name
    

    def appendLongName(self, input: str) -> str:
        if (" major" in input) and ("major 7" not in input):
            input = input.replace(" major", "")

        return input + " " + self.long_name
    

    def cancelsModifiers(self):
        return self.cancels

    def __str__(self):
        return f"GChordModifier({self.self.short_name})"
    

    def __repr__(self):
        return self.__str__()


class GChordFlags:
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

class GDynamicChordTemplate:

    def __init__(self, long_name: str, short_name: str, intervals: list[int]) -> None:
        self.long_name = long_name
        self.short_name = short_name
        self.intervals = intervals

    def noteValues(self, root: int) -> list[int]:
        return [n + root for n in self.intervals]
    
    def shortName(self, root:int, style="flat") -> str:
        return noteName(root, style, show_octave=False) + self.short_name
    
    def longName(self, root: int, style="flat") -> str:
        if len(self.long_name) > 0:
            space = " "
        else:
            space = ""

        return noteName(root, style, show_octave=False) + space + self.long_name
    

class GChordType:
    MajorChord      = 1
    MinorChord      = 2
    DiminishedChord = 3
    AgumentedChord  = 4


CHORD_TYPES = {
    GChordType.MajorChord:      GDynamicChordTemplate("major",      "",                [GToneInterval.R, GToneInterval.M3, GToneInterval.P5]),
    GChordType.MinorChord:      GDynamicChordTemplate("minor",      "m",               [GToneInterval.R, GToneInterval.m3, GToneInterval.P5]),
    GChordType.DiminishedChord: GDynamicChordTemplate("diminished", GMusicalChar.Dim,  [GToneInterval.R, GToneInterval.m3, GToneInterval.dim5]),
    GChordType.AgumentedChord:  GDynamicChordTemplate("augmented",  "+",               [GToneInterval.R, GToneInterval.M3, GToneInterval.Aug5])}



class GDynamicChord:

    def __init__(self, root: int | str, template: GDynamicChordTemplate, flags: int | list[int] = GChordFlags.NoFlag) -> None:
        self.root = noteToNoteValue(root)
        self.template = template
        self.inversion = 0
        self.flags: list[int] = []
        self.chordChanged = GSignal()
        self.setFlags(flags)


    def clone(self) -> 'GDynamicChord':
        return copy.copy(self)


    @staticmethod
    def fromNoteValues(note_values: list[str]) -> 'GDynamicChord':
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


    def rootNoteValue(self):
        return self.root


    def rootNoteName(self, style="flat", show_octave=False) -> str:
        return noteName(self.root, style, show_octave)
    

    def noteValues(self) -> list[int]:
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


    def numberOfNotes(self):
        return len(self.noteValues())
    

    def normalizedNoteValues(self) -> set[int]:
        return normalizeIntervals(self.noteValues())
    

    def signature(self) -> int:        
        return intervalSignature(self.noteValues())


    def noteNames(self, style="flat", show_octave=True) -> list[str]:
        return noteValuesToNoteNames(self.noteValues(), style, show_octave)


    def transpose(self, interval: int):
        self.root += interval


    def setInversion(self, steps: int):
        self.inversion = steps % len(self.noteValues())


    def cycleInversion(self):
        self.inversion = (self.inversion + 1) % len(self.noteValues())


    def invertTowards(self, target: 'GDynamicChord'):                        
        distanceToInversion = {}
        clone = self.clone()

        for i in range(self.numberOfNotes()):
            clone.setInversion(i)
            distanceToInversion[abs(target.centerOfGravity - clone.centerOfGravity)] = i

        self.setInversion(distanceToInversion[min(distanceToInversion.keys())])


    def setRoot(self, root: int | str):
        old_root = self.root
        self.root = noteToNoteValue(root)
        if self.root != old_root:
            self.chordChanged.emit(self)

    
    def setFlags(self, flags: int | list[int]):
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
        return self.template.shortName(self.root, style)


    def shortModName(self, style="flat") -> str:
        name = ""
        for flag in self.flags:
            name = CHORD_MODIFIERS[flag].appendShortName(name)

        base_note_value = self.noteValues()[0]
        if base_note_value != self.rootNoteValue():
            name = name + "/" + noteName(base_note_value, style, show_octave=False)

        return name


    def longName(self, style="flat") -> str:
        name = self.template.longName(self.root, style)
        for flag in self.flags:
            name = CHORD_MODIFIERS[flag].appendLongName(name)

        return name
    

    def shortName(self, style="flat") -> str:
        return self.shortTypeName(style) + self.shortModName()        


    def match(self, intervals: set[int]) -> bool:
        normalized_interval = {v % GToneInterval.Octave for v in intervals}
        return normalized_interval == self.normalizedNoteValues()


    def contains(self, intervals: set[int]) -> bool:
        normalized_interval = {v % GToneInterval.Octave for v in intervals}
        return normalized_interval.issubset(self.normalizedNoteValues())


    @property
    def centerOfGravity(self):
        return sum(self.noteValues()) / self.numberOfNotes()


    def __eq__(self, other):

        if isinstance(other, GDynamicChord):
            return self.signature() == other.signature()
        
        if isinstance(other, list):
            if len(other) > 0:
                if isinstance(other[0], int):
                    return self.signature() == intervalSignature(other)
                
        raise ValueError("Invalid type!")
        

    def __ne__(self, other):
        return not self.__eq__(other)


    def __str__(self):
        return f"GDynamicChord({self.longName()} | {self.shortName()})"
    

    def __repr__(self):
        return self.__str__()



class GChordDatabase:

    def __init__(self, number_mod_combinations = 2):
        
        self._chord_database: dict[int, list[GDynamicChord]] = dict()        

        print(f"Creating chord data base ...")

        for root in NoteNames(0, GToneInterval.Octave, style="flat", show_octave=False):
            for type in CHORD_TYPES.values():
                all_flags = [GChordFlags.NoFlag, *CHORD_MODIFIERS.keys()]
                flag_combinations = [list(t) for t in itertools.combinations(all_flags, number_mod_combinations)]                

                self._addChord(GDynamicChord(root, type, GChordFlags.NoFlag))

                for flags in flag_combinations:
                    self._addChord(GDynamicChord(root, type, flags))
                    
        print(f"{self._size()} chords added to chord datbase with {len(self._chord_database)} unique signaturres.")   


    def _addChord(self, chord: GDynamicChord):
        signature = chord.signature()

        if signature in self._chord_database:
            chords_with_signature = self._chord_database[signature]
            if chord.shortName() not in [c.shortName() for c in chords_with_signature]:
                self._chord_database[signature].append(chord)
        else:
            self._chord_database[signature] = [chord]


    def _size(self) -> int:
        count = 0
        for chords in self._chord_database.values():
            count += len(chords)
        return count


    def matchIntervals(self, intervals: list[int], distance: int = 0) -> list[GDynamicChord]:

        chords: list[GDynamicChord] = []
        input_signature = intervalSignature(intervals)        
        signatures_to_seach_for = nearSignatures(input_signature, distance)
        
        signatures_to_seach_for_print = ["{:012b}".format(s) for s in signatures_to_seach_for]

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
    