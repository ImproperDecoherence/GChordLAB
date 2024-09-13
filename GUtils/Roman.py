"""
Module for converting integers to roman numerals.
"""


__author__ = "https://github.com/ImproperDecoherence"


_ROMAN_NUMERALS = {1: "I", 4: "IV", 5: "V", 9: "IX", 
                   10: "X", 40: "XL", 50: "L", 90: "XC", 
                   100: "C", 400: "CD", 500: "D", 900: "XC",
                   1000: "M"}


def integerToRoman(integer: int, case="upper") -> str:
    """Converts an integer to corresponding roman numeral.
    
    Args:
        integer: Positive integer to be converted.
        case (optional): 'upper' or 'lower'; defines if the
          roman numerals shall be uppercase or lowercase.
    
    """

    roman = str()

    for base in reversed(_ROMAN_NUMERALS.keys()):
        div = integer // base
        integer = integer % base
        roman = roman + (_ROMAN_NUMERALS[base] * div)

    if case == "upper":
        return roman
    else:
        return roman.lower()



def unitTest():

    test_integers = range(2000)

    for integer in test_integers:
        print(integer, integerToRoman(integer))
        print(integer, integerToRoman(integer, "lower"))



if __name__ == "__main__":
    unitTest()
