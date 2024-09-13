
"""
Module ChordGenerators
"""


__author__ = "https://github.com/ImproperDecoherence"


from GMusicIntervals import GDynamicChord, GChordDatabase, GScale, SCALE_TEMPLATES, listOfNoteNames
from GUtils import GSignal


class GChordGeneratorSetting:

    def __init__(self, name: str, init_value, values: list) -> None:
        self.name = name
        self.currentValue = init_value
        self.values = values
        self.toolTip = ""

        self.valueChanged = GSignal()        
    

    def setToolTip(self, tool_tip: str):
        self.toolTip = tool_tip


    def hasStringValue(self) -> bool:
        return (len(self.values) > 0) and (isinstance(self.values[0], str))


    def setValue(self, value):
        old_value = self.currentValue
        self.currentValue = value

        if old_value != self.currentValue:
            self.valueChanged.emit(self.name, self.currentValue)



class GChordGenerator:

    def __init__(self, name: str, need_source: bool = True) -> None:
        self.generator_name = name
        self.need_source = need_source
        self.generator_settings: dir[str, GChordGeneratorSetting] = {}
        self.settingsChanged = GSignal()


    def name(self) -> str:
        return self.generator_name


    def needSource(self) -> bool:
        return self.need_source


    def generateFromIntervals(self, intervals: list[int]) -> list[GDynamicChord]:
        return []
    

    def generateFromChord(self, chord: GDynamicChord) -> list[GDynamicChord]:
        return []
    

    def addSetting(self, setting: GChordGeneratorSetting):        
        self.generator_settings[setting.name] = setting    


    def settings(self) -> list[GChordGeneratorSetting]:
        return self.generator_settings.values()



class GMatchingChordsGenerator(GChordGenerator):

    def __init__(self, db: GChordDatabase) -> None:
        super().__init__("Matching Chords", need_source=True)

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

    def __init__(self) -> None:
        super().__init__("Chords of Scale", need_source=False)

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



