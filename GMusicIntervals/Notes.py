"""
Module NoteNames
"""

__author__ = "https://github.com/ImproperDecoherence"


import re
from string import digits

from GUtils import debugVariable
from .ToneIntervals import normalizeIntervals, GToneInterval

_NOTE_NAMES_TEMPLATE_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_NOTE_NAMES_TEMPLATE_FLAT  = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
_OCTAVE_SIZE = len(_NOTE_NAMES_TEMPLATE_FLAT)


def noteNameStyle(list_of_note_names: list[str]) -> str:
    if any('b' in name for name in list_of_note_names):
        return "flat"
    else:
        return "sharp"


def noteName(note_value: int, style="flat", show_octave=True) -> str:

    match style:
        case "sharp":
            note_names_template = _NOTE_NAMES_TEMPLATE_SHARP
        case "flat":
            note_names_template = _NOTE_NAMES_TEMPLATE_FLAT
        case _:
            raise ValueError("Style must be 'sharp' or 'flat'")

    base_name_index = note_value % _OCTAVE_SIZE

    post_fix = ""
    if show_octave:
        post_fix = str(note_value // _OCTAVE_SIZE)
    
    return note_names_template[base_name_index] + post_fix


def noteValue(note_name: str) -> int:
    style = noteNameStyle([note_name])

    match style:
        case "sharp":
            name_template = _NOTE_NAMES_TEMPLATE_SHARP
        case "flat":
            name_template = _NOTE_NAMES_TEMPLATE_FLAT
        case _:
            raise ValueError("Style must be 'sharp' or 'flat'")

    pattern = re.compile('(\D+)(\d*)')
    match = pattern.search(note_name)
    base_note_name = match.group(1)
    octave_str = match.group(2)
        
    try:
        octave = int(octave_str)
    except:
        octave = 0

    return name_template.index(base_note_name) + octave * _OCTAVE_SIZE


def noteToNoteValue(note: str | int) -> int:
    if isinstance(note, str):
        return noteValue(note)
    elif isinstance(note, int):
        return note
    else:
        raise ValueError("Parameter must be of type str or int")


def NoteNames(startNote: int | str, numberNotes, style="flat", show_octave=True):
    startNoteValue = noteToNoteValue(startNote)
    for i in range(numberNotes):
        yield noteName(i + startNoteValue, style, show_octave)


def listOfNoteNames(startNote: int | str, numberNotes, style="flat", show_octave=True):
    startNoteValue = noteToNoteValue(startNote)
    return [name for name in NoteNames(startNoteValue, numberNotes, style, show_octave)]



class NoteNameList:

    def __init__(self, style="flat"):
        self.style = style

    def __getitem__(self, note_value):
        return noteName(note_value)

    def index(self, note_name):
        return noteValue(note_name)


NOTE_NAMES_FLAT = NoteNameList("flat")
NOTE_NAMES_SHARP = NoteNameList("sharp")


def sortNoteNames(list_of_note_names: list[str]) -> list[str]:
    return sorted(list_of_note_names, key=lambda n: noteValue(n))
        

def noteValuesToNoteNames(note_values: list[int], style="flat", show_octave=False) -> list[str]:
    return [noteName(note_value, style, show_octave) for note_value in note_values]


def noteNamesToNoteValues(note_names: list[str]) -> list[int]:
    return [noteValue(note_name) for note_name in note_names]


def removeOctaveFromNoteName(note_name: str):
    remove_digits = str.maketrans('', '', digits)
    return note_name.translate(remove_digits)


def isDiatonicNoteValue(note_value: int) -> bool:
    return isDiatonicNoteName(noteName(note_value))


def isDiatonicNoteName(note_name: str) -> bool:
    return ('b' not in note_name) and ('#' not in note_name)


def fitNoteNamesToInterval(note_names_to_be_fitted: list[str], inteval_note_names: list[str]) -> list[str]:
        style = noteNameStyle(note_names_to_be_fitted)
        
        interval_note_values = noteNamesToNoteValues(inteval_note_names)
        interval_note_values_set = set(interval_note_values)
        note_values_to_be_fitted = normalizeIntervals(noteNamesToNoteValues(note_names_to_be_fitted))        

        while (not (set(note_values_to_be_fitted) <= interval_note_values_set) and 
               ((note_values_to_be_fitted[-1] + GToneInterval.Octave) <= interval_note_values[-1])):
            note_values_to_be_fitted = [value + GToneInterval.Octave for value in note_values_to_be_fitted]

        return noteValuesToNoteNames(note_values_to_be_fitted, style, show_octave=True)


def _rebaseNoteValues(note_values: list[int], base_value: int, current_base_value:int) -> list[int]:

    if len(note_values) > 0:
        zero_based_note_values = [value - current_base_value for value in note_values]
        return [value + base_value for value in zero_based_note_values]
    else:
        return []


def _baseValue(note_values: list[int] | list[list[int]]) -> int:

    if isinstance(note_values[0], int):
        min_value = min(note_values)
    
    if isinstance(note_values[0], list):
        min_value = min([min(value_list) for value_list in note_values if any(value_list)])
    
    return (min_value // GToneInterval.Octave) * GToneInterval.Octave


def rebaseNoteValues(note_values: list[int] | list[list[int]], base_value: int) -> list[int]:
    
    if len(note_values) == 0:
        return []

    if base_value % GToneInterval.Octave != 0:
        raise ValueError("base_value must be a C note!")

    if isinstance(note_values[0], int):
        current_base = _baseValue(note_values)
        return _rebaseNoteValues(note_values, base_value, current_base)
    
    if isinstance(note_values[0], list):
        current_base = _baseValue(note_values)
        note_value_list = list()

        for n in note_values:
            note_value_list.append(_rebaseNoteValues(n, base_value, current_base))

        return note_value_list
    
    return []



if __name__ == "__main__":
    
    for i in range(6 * _OCTAVE_SIZE):
        note_name = noteName(i, "flat", show_octave=True)
        note_value = noteValue(note_name)
        print (note_value, note_name)