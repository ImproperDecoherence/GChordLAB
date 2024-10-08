"""
Module defining a widget for coontrol of different chord generators..
"""

__author__ = "https://github.com/ImproperDecoherence"



from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QGroupBox, QSizePolicy, QComboBox, 
                             QPushButton, QApplication, QWidget, QRadioButton, QButtonGroup)
from PyQt6.QtGui import QEnterEvent, QWheelEvent
from PyQt6.QtCore import Qt, QSize

from GModels import GChordFinder, GChordGeneratorSetting, GPianoModel
from GUtils import debugVariable
from GMusicIntervals import GDynamicChord

from .ChordButton import GChordButton
from .ChordButtonPanel import GChordButtonLayout
from .ChordListWidget import GChordListWidget



class _SettingsPanel(QGroupBox):
    """A group box widget which is used to select one code generator parameter."""

    def __init__(self, setting: GChordGeneratorSetting, parent: QWidget=None) -> None:
        """
        Args:
            setting: The chord generator parameter to be controlled by this widget.
            parent: Parent widget.
        """
        super().__init__(setting.name, parent)
        self.setting = setting
        self.setToolTip(setting.toolTip)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setContentsMargins(0, 6, 0, 0)

        layout = QVBoxLayout()
        combo_box = QComboBox()
        combo_box.currentTextChanged.connect(self._valueChanged)
        self.setLayout(layout)
        layout.addWidget(combo_box)

        self.value_to_str = {value: value for value in setting.values}
        if not self.setting.hasStringValue():
            self.value_to_str = {value: str(value) for value in setting.values}
            combo_box.addItems(self.value_to_str.values())
        else:
            combo_box.addItems(setting.values)
        

    def _valueChanged(self, new_value: str) -> None:
        """This method is called when combo box for the parameter changes current value."""
        debugVariable("new_value")

        if not self.setting.hasStringValue():
            value = int(new_value)
        else:
            value = new_value

        self.setting.setValue(value)


class GChordFinderWidget(QGroupBox):
    """A widget with chord generator selector, parameter settings and a list view to show the results."""

    def __init__(self, chord_finder: GChordFinder, piano_model: GPianoModel = None, parent: QWidget=None) -> None:
        """
        Args:
            chord_finder: The model which holds the states of the chord generators.
            piano_model: The model to which selected chord can be applied.
            parent: Parent widget.
        """
        super().__init__("Chord Finder", parent)

        self.chord_finder = chord_finder
        self.chord_finder.chordsUpdated.connect(self._chordsUpdated)
        
        self.piano_model = piano_model

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        main_layout = QHBoxLayout(self)        
        main_layout.setContentsMargins(5, 0, 5, 5)

        settings_and_generator_widget = QWidget()
        settings_and_generator_widget.setContentsMargins(0, 0, 0, 0)
        settings_and_generator_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setting_and_generator_layout = QVBoxLayout()
        settings_and_generator_widget.setLayout(self.setting_and_generator_layout)
        settings_and_generator_widget.setMinimumHeight(80)
        main_layout.addWidget(settings_and_generator_widget)
        main_layout.setAlignment(settings_and_generator_widget, Qt.AlignmentFlag.AlignTop)
    

        generator_box = QGroupBox("Generator")
        generator_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        generator_box.setContentsMargins(0, 6, 0, 0)
        generator_layout = QHBoxLayout()
        generator_combo_box = QComboBox()
        generator_names = [generator.name() for generator in self.chord_finder.availableGenerators()]
        generator_combo_box.addItems(generator_names)
        generator_layout.addWidget(generator_combo_box)
        generator_box.setLayout(generator_layout)
        generator_combo_box.currentTextChanged.connect(self._currentGeneratorChanged)
        self.setting_and_generator_layout.addWidget(generator_box)

        self.source_box = QGroupBox("Source")
        self.source_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.source_box.setContentsMargins(0, 6, 0, 0)
        source_layout = QHBoxLayout()

        source_button_names = {GChordFinder.SeedType.Instrument: "Instrument", GChordFinder.SeedType.Chord: "Seed"}

        self.source_button_group = QButtonGroup()
        self.source_button_group.setExclusive(True)

        source_instrument_button = QRadioButton(source_button_names[GChordFinder.SeedType.Instrument])
        source_layout.addWidget(source_instrument_button)
        self.source_button_group.addButton(source_instrument_button)
        self.source_button_group.setId(source_instrument_button, GChordFinder.SeedType.Instrument)

        source_seed_button = QRadioButton(source_button_names[GChordFinder.SeedType.Chord])
        source_layout.addWidget(source_seed_button)
        self.source_button_group.addButton(source_seed_button)
        self.source_button_group.setId(source_seed_button, GChordFinder.SeedType.Chord)

        self.source_button_group.button(self.chord_finder.currentSeedType()).setChecked(True)
        self.source_button_group.buttonToggled.connect(self._sourceToggled)

        self.source_box.setLayout(source_layout)
        self.setting_and_generator_layout.addWidget(self.source_box)

        seed_chord_button = GChordButton()
        seed_chord_button.setAcceptDrops(True)
        seed_chord_button.chordChanged.connect(self._seedChordChanged)
        source_layout.addWidget(seed_chord_button)
        source_layout.setAlignment(seed_chord_button, Qt.AlignmentFlag.AlignTop)


        self.chord_list = GChordListWidget(self.chord_finder)
        self.chord_list.selectedChordChanged.connect(self._selectedChordChanged)
        main_layout.addWidget(self.chord_list)

        self.setLayout(main_layout)

        self.setting_panels: list[_SettingsPanel] = []
        self._updateSettingsPanel()


    def sizeHint(self) -> QSize:
        """Returns the preferred size of the widget."""
        return QSize(300, 300)


    def enterEvent(self, event: QEnterEvent) -> None:
        """This method is called by the framework when the mouse pointer enters the widget."""
        super().enterEvent(event)
        self._updateHighlightedChord()        
        

    def leaveEvent(self, event: QEnterEvent) -> None:
        """This method is called by the framework when the mouse pointer leaves the widget."""
        super().leaveEvent(event)
        
        if self.piano_model is not None:
            self.piano_model.setHighlightedNoteValues([])
            

    def _currentGeneratorChanged(self, generator_name: str) -> None:
        """This method is called when the current item in the combo box for gernerator selection is changed."""
        self.chord_finder.setCurrentGenerator(generator_name)
        self._updateSettingsPanel()


    def _sourceToggled(self, button: QRadioButton, checked: bool) -> None:
        """This method is called when the seed source selection is changed."""
        id = self.source_button_group.id(button)
        if checked:
            self.chord_finder.setSeedType(id)


    def _seedChordChanged(self, chord_button: GChordButton) -> None:
        """This method is called when the seed chord is changed."""
        self.chord_finder.setSeedChord(chord_button.chord)
        

    def _chordsUpdated(self, finder: GChordFinder) -> None:
        """This method is called when the chords found by the chord finder are updated."""
        pass        


    def _updateHighlightedChord(self) -> None:
        """Highlights the selected chord in the chord list in the piano model."""
        highlighted_note_values = []
        current_cord = self.chord_list.currentChord()

        if current_cord is not None:
            highlighted_note_values = current_cord.noteValues()            

        if self.piano_model is not None:
            self.piano_model.setHighlightedNoteValues(highlighted_note_values)


    def _updateSettingsPanel(self) -> None:
        """Reconstructs the parameter settings panel based in available parameters for the current generator."""

        for setting_panel in self.setting_panels:
            self.setting_and_generator_layout.removeWidget(setting_panel)

        current_generator = self.chord_finder.currentGenerator()

        self.source_box.setVisible(current_generator.needSeed())

        self.setting_panels = [_SettingsPanel(setting) for setting in current_generator.settings()]

        for setting_panel in self.setting_panels:
            self.setting_and_generator_layout.addWidget(setting_panel)


    def _selectedChordChanged(self, current_chord: GDynamicChord) -> None:
        """This method is called when the selected chord in the list of found chords is changed."""
        self._updateHighlightedChord()
        self.piano_model.play(current_chord.noteValues())




def unitTest():
    pass


if __name__ == "__main__":
    unitTest()