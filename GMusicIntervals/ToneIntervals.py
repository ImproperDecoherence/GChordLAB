"""
This module defines basic tone intervals and some functions which can operate on them.
"""

__author__ = "https://github.com/ImproperDecoherence"


import itertools
import collections


class GToneInterval:
    """Defines names and values for different note intervals."""
    # Interval definitions
    PerfectUnison =  0
    Root          =  0
    Tonic         =  0
    SemiTone      =  1
    Tone          =  2 * SemiTone
    minor2nd      =  1 * SemiTone
    Major2nd      =  2 * SemiTone
    minor3rd      =  3 * SemiTone
    Major3rd      =  4 * SemiTone
    Perfect4th    =  5 * SemiTone
    Diminished5th =  6 * SemiTone
    Augmented4th  =  6 * SemiTone
    TriTone       =  6 * SemiTone
    Perferct5th   =  7 * SemiTone
    Augmented5th  =  8 * SemiTone
    minor6th      =  8 * SemiTone
    Major6th      =  9 * SemiTone
    minor7th      = 10 * SemiTone
    Major7th      = 11 * SemiTone
    PerfectOctave = 12 * SemiTone
    minor9th      = 13 * SemiTone
    Major9th      = 14 * SemiTone
    Perfect11th   = 17 * SemiTone
    Major13th     = 21 * SemiTone
    Octave        = PerfectOctave

    # Abbreviations
    P1 = PerfectUnison
    R  = Root
    m2 = minor2nd
    M2 = Major2nd
    m3 = minor3rd
    M3 = Major3rd
    P4 = Perfect4th
    dim5 = Diminished5th
    Aug4 = Augmented4th
    T = TriTone    
    P5 = Perferct5th    
    Aug5 = Augmented5th
    m6 = minor6th    
    M6 = Major6th
    m7 = minor7th
    M7 = Major7th
    P8 = PerfectOctave
    m9 = minor9th
    M9 = Major9th
    P11 = Perfect11th
    M13 = Major13th
    O = Octave

INTERVAL_SHORT_NAMES = {GToneInterval.R:    "R", 
                        GToneInterval.m2:   "m2",
                        GToneInterval.M2:   "M2",
                        GToneInterval.m3:   "m3",
                        GToneInterval.M3:   "M3",
                        GToneInterval.P4:   "P4",
                        GToneInterval.dim5: "dim5",
                        GToneInterval.P5:   "P5",
                        GToneInterval.m6:   "m6",
                        GToneInterval.M6:   "M6",
                        GToneInterval.m7:   "m7",
                        GToneInterval.M7:   "M7",
                        GToneInterval.O:    "O",
                        GToneInterval.m9:   "m9",
                        GToneInterval.M9:   "M9",
                        GToneInterval.P11:  "P11",
                        GToneInterval.M13:  "M13"
                        }
"""Directory defining translation from interval values to strings that represents the abbreviation of the intervals."""


def normalizeIntervals(intervals: list[int]) -> list[int]:
    """Normalizes a list of note intervals to be in the range Root (0) to Major7th (11)."""
    normalized_set = {v % GToneInterval.Octave for v in intervals}
    return list(normalized_set)


def transposeIntervals(intervals: list[int], steps: int) -> list[int]:
    """Transposes the given interval values a number of semi tone steps"""
    return [value + steps for value in intervals if (value + steps) >= 0]


def multiplyIntervals(intervals: list[int], number_of_octaves: int) -> list[int]:
    """Transposes the given interval a number of full octaves (12 semi tones)."""
    result = list()

    for i in range(number_of_octaves):
        offset = i * GToneInterval.Octave
        result.extend([value + offset for value in intervals])
    return result


def intervalSignature(interval: list[int]) -> int:
    """Translates a list of tone intervals to an interger number which is unique for the normalized interval.

    Each bit in the signature represents a note in the normalized (see normalizeIntervals) interval:
        0: note not present
        1: note present
    
    Returns:
        A normalzed interval signature number between 0 and 4095 (2^12 - 1).
    """
    signature = 0
    mask = 1
    
    for value in normalizeIntervals(interval):        
        signature = signature | (mask << value)
        
    return signature


def nearSignatures(signature: int, distance: int) -> list[int]:
    """Finds normalized interval signatures which are close to a given signature
    
    Args:
        signature: The target signature (see intervalSignature).
        distance: The function will return signatures which are at this distance from the target signature.
          The distance is defined as number of notes which differs from the target signature.
    
    """
    near_signatures = []

    if distance < 0:
        raise ValueError("Distance must be positive or zero!")

    if distance == 0:
        return [signature]
    
    bits_to_toggle = [list(t) for t in itertools.combinations(range(GToneInterval.Octave), distance)]

    for bits in bits_to_toggle:
        mask = 0
        for bit in bits:                
            mask = mask | (1 << bit)

        near_signatures.append(signature ^ mask) # xor toggles the bits in the mask

    return near_signatures



def unitTest():
    
    signature = 0xFFF
    near_signatures = nearSignatures(signature, 2)

    print(f"signature = {signature:03b}")
    print(f"near signatures = ")
    for s in near_signatures:
        print(f"{s:03b}")

    duplicates = [value for value, count in collections.Counter(near_signatures).items() if count > 1]
    print(f"duplicates: {duplicates}")



if __name__ == "__main__":
    unitTest()