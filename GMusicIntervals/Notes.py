"""
This module defines the different notes and functions for handling notes.
"""

__author__ = "https://github.com/ImproperDecoherence"


import re
from string import digits

from GUtils import debugVariable
from .ToneIntervals import normalizeIntervals, GToneInterval


_NOTE_NAMES_TEMPLATE_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
"""Defintion of note names when using sharp (#) notation"""

_NOTE_NAMES_TEMPLATE_FLAT  = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
"""Defintion of note names when using flat (b) notation"""


def noteNameStyle(list_of_note_names: list[str]) -> str:
    """Returns the style (sharp/flat) used for given note names.
    
    If the style cannot be determined (no 'b' or '#' in anly of the note names),
    the default style 'sharp' is returned.

    Returns: 'sharp' or 'flat'
    """

    if any('b' in name for name in list_of_note_names):
        return "flat"
    else:
        return "sharp"


def noteName(note_value: int, style="flat", show_octave=True) -> str:
    """Returns the note name for a given note value.
    
    Args:
        note_value: The lowest note name 'C0' has note value 0; other notes have note values which represents
          their distance from 'C0' measured in number semi tones.
        style (optional): 'sharp' or 'flat'
        show_octave (optional): Indicates if the octave number shall be included in the note name.
    
    """

    match style:
        case "sharp":
            note_names_template = _NOTE_NAMES_TEMPLATE_SHARP
        case "flat":
            note_names_template = _NOTE_NAMES_TEMPLATE_FLAT
        case _:
            raise ValueError("Style must be 'sharp' or 'flat'")

    base_name_index = note_value % GToneInterval.Octave

    post_fix = ""
    if show_octave:
        post_fix = str(note_value // GToneInterval.Octave)
    
    return note_names_template[base_name_index] + post_fix


def noteValue(note_name: str) -> int:
    """Returns the note value for a given note name.
    
    Raises:
        ValueError if the input in not a valic note name.
    
    """

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

    return name_template.index(base_note_name) + octave * GToneInterval.Octave


def noteToNoteValue(note: str | int) -> int:
    """Translates a note value OR a note name to its note value.
    
    Raises:
        ValueError if the input cannot be decoded to a note value.
    """

    if isinstance(note, str):
        return noteValue(note)
    elif isinstance(note, int):
        return note
    else:
        raise ValueError("Parameter must be of type str or int")


def NoteNames(start_note: int | str, number_notes, style="flat", show_octave=True):
    """Generator for sequential note names in a given interval of notes.

    Args:
        start_note: Value or name of the first note.
        number_notes: The number of semi notes which will be generated.
        style (optional): 'sharp' or 'flat'
        show_octave (optional): Indicates if the octave number shall be included in the note name.

    Raises:
        ValueError if incorrect input.

    """

    startNoteValue = noteToNoteValue(start_note)
    for i in range(number_notes):
        yield noteName(i + startNoteValue, style, show_octave)


def listOfNoteNames(startNote: int | str, numberNotes, style="flat", show_octave=True):
    """Returns a list of sequential note names for a given interval of notes.

    Args:
        start_note: Value or name of the first note.
        number_notes: The number of semi notes which will be generated.
        style (optional): 'sharp' or 'flat'
        show_octave (optional): Indicates if the octave number shall be included in the note name.

    Raises:
        ValueError if incorrect input.

    """
    startNoteValue = noteToNoteValue(startNote)
    return [name for name in NoteNames(startNoteValue, numberNotes, style, show_octave)]



class _NoteNameDict:
    """Implements the interface of a dictory to mimic a dict[note value, note name] for all notes."""

    def __init__(self, style="flat"):
        self.style = style

    def __getitem__(self, note_value):
        return noteName(note_value)

    def index(self, note_name):
        return noteValue(note_name)


NOTE_NAMES_FLAT = _NoteNameDict("flat")
"""Represents a dictionary dict [note value, note name] for all note names with the style 'flat'."""

NOTE_NAMES_SHARP = _NoteNameDict("sharp")
"""Represents a dictionary dict [note value, note name] for all note names with the style 'sharp'."""


def sortNoteNames(list_of_note_names: list[str]) -> list[str]:
    """Sorts a list of note names according to its note values."""
    return sorted(list_of_note_names, key=lambda n: noteValue(n))
        

def noteValuesToNoteNames(note_values: list[int], style="flat", show_octave=False) -> list[str]:
    """Transforms a list of note values to the corresponding list of note names.
    
    Args:
        note_values: List of note values to be translated.
        style (optional): 'sharp' or 'flat'
        show_octave (optional): Indicates if the octave number shall be included in the note name.
    """

    return [noteName(note_value, style, show_octave) for note_value in note_values]


def noteNamesToNoteValues(note_names: list[str]) -> list[int]:
    """Translates a list of note names to a list of note values."""

    return [noteValue(note_name) for note_name in note_names]


def removeOctaveFromNoteName(note_name: str):
    """Strips any existing octave number from provided note name."""

    remove_digits = str.maketrans('', '', digits)
    return note_name.translate(remove_digits)


def isDiatonicNoteName(note_name: str) -> bool:
    """Returns True if the provided note name does not include any 'b' or '#'."""

    return ('b' not in note_name) and ('#' not in note_name)


def isDiatonicNoteValue(note_value: int) -> bool:
    """Returns True if the provided note value does not represent a note name which includes 'b' or '#'."""

    return isDiatonicNoteName(noteName(note_value))


def _rebaseNoteValues(note_values: list[int], base_value: int, current_base_value:int) -> list[int]:

    if len(note_values) > 0:
        zero_based_note_values = [value - current_base_value for value in note_values]
        return [value + base_value for value in zero_based_note_values]
    else:
        return []


def _baseValue(note_values: list[int] | list[list[int]]) -> int:
    """Finds the C-note base value for given note values.
    
    The C-note base is the C-note which is closest to to the given note values but 
    also has a lower value than all given note values.
    """

    if isinstance(note_values[0], int):
        min_value = min(note_values)
    
    if isinstance(note_values[0], list):
        min_value = min([min(value_list) for value_list in note_values if any(value_list)])
    
    return (min_value // GToneInterval.Octave) * GToneInterval.Octave


def rebaseNoteValues(note_values: list[int] | list[list[int]], base_value: int) -> list[int] | list[list[int]]:
    """Transposes the provided note values N octaves be just above the given C-note.
    
    Args:
        note_values: A list of note values OR a list of lists of note values.
        base_value: A C-note value which represents the octave to which the notes shall be transposed.
          The new note values will be above the given C-note and also as close as possible to the 
          given C-note.

    Returns:
        A list on the same format as the input with transposed note values.
    
    """
    
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
    
    for i in range(6 * GToneInterval.Octave):
        note_name = noteName(i, "flat", show_octave=True)
        note_value = noteValue(note_name)
        print (note_value, note_name)