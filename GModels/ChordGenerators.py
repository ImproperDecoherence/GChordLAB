
"""
This module defines functions for generating different sets of chords.
"""


__author__ = "https://github.com/ImproperDecoherence"


from GMusicIntervals import GDynamicChord, GChordDatabase, GScale, SCALE_TEMPLATES, listOfNoteNames
from GUtils import GSignal


class GChordGeneratorSetting:
    """Represents a parameter which can be set for a chord generator.
    
    The parameter can be an integer or an string.
    """

    def __init__(self, name: str, init_value: int | str, values: list[int | str]) -> None:
        """
        Args:
            name: The name of the parameter.
            init_value: The initial current value of the parameter.
            values: Possible values.
        """
        self.name = name
        self.currentValue = init_value        
        self.toolTip = ""

        self.values = values
        """Possible parameter values."""

        self.valueChanged = GSignal()        
    

    def setToolTip(self, tool_tip: str):
        """Sets the tooltip text for the parameter."""
        self.toolTip = tool_tip


    def hasStringValue(self) -> bool:
        """Tests if the parameter is a string."""
        return (len(self.values) > 0) and (isinstance(self.values[0], str))


    def setValue(self, value):
        """Sets the current value of the parameter."""
        old_value = self.currentValue
        self.currentValue = value

        if old_value != self.currentValue:
            self.valueChanged.emit(self.name, self.currentValue)



class GChordGenerator:
    """Base class for all chord generators."""

    def __init__(self, name: str, need_seed: bool = True) -> None:
        """
        Args:
            name: Name of the generator.
            need_seed: Indecates if the generator needs a chord as a seed.
        """
        self.generator_name = name
        self.need_seed = need_seed
        self.generator_settings: dir[str, GChordGeneratorSetting] = {}
        self.settingsChanged = GSignal()


    def name(self) -> str:
        """Returns tha name of the generator."""
        return self.generator_name


    def needSeed(self) -> bool:
        """Tests if the generator needs a chord as seed."""
        return self.need_seed


    def generateFromIntervals(self, intervals: list[int]) -> list[GDynamicChord]:
        """Returns a list of chords which matches the seed and parameter values of the generator."""
        return []  # Default implementaion
        

    def addSetting(self, setting: GChordGeneratorSetting):
        """Adds a parameter setting to the generator."""
        self.generator_settings[setting.name] = setting    


    def settings(self) -> list[GChordGeneratorSetting]:
        """Returns the parameter settings for the generator."""
        return self.generator_settings.values()



class GMatchingChordsGenerator(GChordGenerator):
    """Generates chords which have a certain Distance to a seed chord.

    The Distance is the number of notes which shall differ to make a match, e.g.
    distance = 0 returns exact matches, distance = 1 returns chords which
    differs with one note, etc.
    """

    def __init__(self, db: GChordDatabase) -> None:
        """
        Args:
            db: Reference to the chord database from which matches shall be found.
        """

        super().__init__("Matching Chords", need_seed=True)

        self.db = db

        distance_setting = GChordGeneratorSetting("Distance", 0, range(0, 3))
        distance_setting.setToolTip("0 = exact match, 1 = one note different, etc.")
        distance_setting.valueChanged.connectSignal(self.settingsChanged)
        self.addSetting(distance_setting)


    def name(self) -> str:        
        return self.generator_name


    def generateFromIntervals(self, intervals: list[int]) -> list[GDynamicChord]:
        distance: int = self.generator_settings["Distance"].currentValue
        return self.db.matchIntervals(intervals, distance)
    

class GChordsOfScaleGenerator(GChordGenerator):
    """Generates the basic chords for a given Key and Scale.
        
    The basic chords of the scale are the triad chords which can be constructed from
    the minor or major thirds of the scale. This generator takes no seed.
    """

    def __init__(self) -> None:
        super().__init__("Chords of Scale", need_seed=False)

        scale_setting = GChordGeneratorSetting("Scale", "Natural Major", list(SCALE_TEMPLATES.keys()))
        scale_setting.setToolTip("The scale to which the chords shall belong")
        scale_setting.valueChanged.connectSignal(self.settingsChanged)
        self.addSetting(scale_setting)

        key_setting = GChordGeneratorSetting("Key", "C", listOfNoteNames("C", 12, style="flat", show_octave=False))
        key_setting.setToolTip("The scale to which the chords shall belong")
        key_setting.valueChanged.connectSignal(self.settingsChanged)
        self.addSetting(key_setting)


    def name(self) -> str:
        return self.generator_name


    def generateFromIntervals(self, intervals: list[int]) -> list[GDynamicChord]:
        scale = GScale(self.generator_settings["Key"].currentValue, self.generator_settings["Scale"].currentValue)
        return scale.chordsOfScale()



