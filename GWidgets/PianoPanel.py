"""
Module defining a group box widget which contains a piano keyboard and instrument settings.
"""

__author__ = "https://github.com/ImproperDecoherence"


from GModels import GPianoModel, GPlayer
from GMusicIntervals import isDiatonicNoteName, noteValue, noteName

from .WidgetUtils import checkStateToBool, boolToCheckState
from .PianoWidget import GPianoWidget

from PyQt6.QtWidgets import (QApplication, QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel,
                             QSizePolicy, QComboBox, QCheckBox, QLabel, QSlider)
                             
from PyQt6.QtCore import Qt


class GPianoPanel(QGroupBox):
    """Group box containing a piano keybord and instrument settings."""

    def __init__(self, title: str, piano_model: GPianoModel, parent=None) -> None:
        """
        Args:
            piano_model: Piano model used to hold keybord state and to play notes.
        """
        super().__init__(title)
        self.player = piano_model.player
        self.piano_model = piano_model

        main_layout = QVBoxLayout()

        control_layout = QHBoxLayout()

        control_widget = QWidget()
        control_widget.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

        instrument_combo_box = QComboBox()
        instrument_combo_box.addItems(self.player.availableIstrumentNames())
        instrument_combo_box.currentTextChanged.connect(self._currentInstrumentChanged)
        instrument_combo_box.setCurrentText(self.player.currentInstrumentName())
        instrument_combo_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        control_layout.addWidget(instrument_combo_box)

        mute_checkbox = QCheckBox("Mute")
        mute_checkbox.setCheckState(boolToCheckState(self.player.isMuted()))
        mute_checkbox.checkStateChanged.connect(self._muteChanged)
        control_layout.addWidget(mute_checkbox) 

        volume_label = QLabel("Volume:")
        control_layout.addWidget(volume_label)

        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setMinimum(0)
        volume_slider.setMaximum(100)
        volume_slider.setSingleStep(5)
        volume_slider.setPageStep(20)
        volume_slider.setTickInterval(10)
        volume_slider.setValue(int(self.player.volume() * 100))
        volume_slider.valueChanged.connect(self._volumeChanged)
        volume_slider.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        control_layout.addWidget(volume_slider)

        self.volume_indicator = QLabel(str(volume_slider.value()))        
        control_layout.addWidget(self.volume_indicator)

        control_layout.addStretch(2)

        first_key_label = QLabel("Lowest Note:")
        control_layout.addWidget(first_key_label)

        self.first_key_combo_box = QComboBox()
        self.first_key_combo_box.addItems(self._availableFirstNotes())
        self.first_key_combo_box.currentTextChanged.connect(self._firstKeyNoteChanged)
        self.first_key_combo_box.setCurrentText(noteName(self.piano_model.supportedNoteValues()[0]))
        control_layout.addWidget(self.first_key_combo_box)

        base_note_label = QLabel("Base Note:")
        control_layout.addWidget(base_note_label)
        self.base_note_indicator = QLabel(noteName(self.piano_model.firstNoteValue()))
        control_layout.addWidget(self.base_note_indicator)        
        
        control_widget.setLayout(control_layout)
        main_layout.addWidget(control_widget)

        piano_widget = GPianoWidget(piano_model)
        main_layout.addWidget(piano_widget)

        self.setLayout(main_layout)    

        self.piano_model.keyLayoutChanged.connect(self._keyLayoutChanged)
        self.player.instrumentChanged.connect(self._playerInstrumentChanged)


    def _availableFirstNotes(self) -> list[str]:
        """Returns note names which are available to use as the lowest note for the piano keyboard."""
        available_note_names = self.player.supportedNoteNames()
        number_keys = self.piano_model.numberOfPianoKeys()

        return [note for note in available_note_names[:-number_keys] if (isDiatonicNoteName(note) and (('C' in note) or ('F' in  note)))]


    def _keyLayoutChanged(self, piano_model: GPianoModel):
        """Updates the first note indicator when the layput of the piano keyboard is changed."""
        self.base_note_indicator.setText(noteName(piano_model.firstNoteValue()))
    

    def _firstKeyNoteChanged(self, note_name):
        """This method is called when the current item in the combo box for selection of the lowest note is changed."""
        if len(note_name) > 0:
            self.piano_model.setFirstNoteValue(noteValue(note_name))


    def _currentInstrumentChanged(self, instrument_name):
        """This method is called when the current item in the combo box for selection of instrument is changed."""
        self.player.setInstrument(instrument_name)
        self.piano_model.setFirstNoteValue(noteValue("C2"))


    def _playerInstrumentChanged(self, instrument: GPlayer.Instrument):
        """This method is called when the sound player signals that the instrument has been changed."""
        self.first_key_combo_box.clear()
        self.first_key_combo_box.addItems(self._availableFirstNotes())
        self.first_key_combo_box.setCurrentText(noteName(self.piano_model.supportedNoteValues()[0]))


    def _muteChanged(self, state: Qt.CheckState):
        """This method is called when the check box for muting the sound is updated."""
        self.player.mute(checkStateToBool(state))


    def _volumeChanged(self, value: int):
        """This method is called when the slider for sound vlume is updated."""
        self.player.setVolume(value / 100.0)
        self.volume_indicator.setText(str(int(self.player.volume() * 100)))



def unitTest():

    app = QApplication([])
    piano_model = GPianoModel(number_of_octaves=3)
    piano_widget = GPianoWidget(piano_model)
    piano_widget.resize(1500, 400)
    piano_widget.show()
    app.exec()



if __name__ == "__main__":
    unitTest()