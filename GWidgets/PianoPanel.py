"""
Module GPianoWidget
"""

__author__ = "https://github.com/ImproperDecoherence"


from GModels import GPianoModel, GPlayer
from GMusicIntervals import isDiatonicNoteName, noteValue, noteName

from .WidgetUtils import checkStateToBool, boolToCheckState
from .PianoWidget import GPianoWidget

from PyQt6.QtWidgets import (QApplication, QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel,
                             QSizePolicy, QComboBox, QCheckBox, QLabel, QSlider, QSpinBox)
                             
from PyQt6.QtCore import Qt


class GPianoPanel(QGroupBox):

    def __init__(self, title: str, piano_model: GPianoModel, parent=None):
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


    def _availableFirstNotes(self):
        available_notes = self.player.supportedNoteNames()
        number_keys = self.piano_model.numberOfPianoKeys()

        return [note for note in available_notes[:-number_keys] if (isDiatonicNoteName(note) and (('C' in note) or ('F' in  note)))]


    def _keyLayoutChanged(self, piano_model: GPianoModel):
        self.base_note_indicator.setText(noteName(piano_model.firstNoteValue()))
    

    def _firstKeyNoteChanged(self, note_name):
        if len(note_name) > 0:
            self.piano_model.setFirstNoteValue(noteValue(note_name))


    def _chordGravityChanged(self, note_name):
        pass


    def _currentInstrumentChanged(self, instrument_name):
        self.player.setInstrument(instrument_name)


    def _playerInstrumentChanged(self, instrument: GPlayer.Instrument):
        self.first_key_combo_box.clear()
        self.first_key_combo_box.addItems(self._availableFirstNotes())
        self.first_key_combo_box.setCurrentText(noteName(self.piano_model.supportedNoteValues()[0]))


    def _muteChanged(self, state: Qt.CheckState):
        self.player.mute(checkStateToBool(state))


    def _volumeChanged(self, value: int):
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