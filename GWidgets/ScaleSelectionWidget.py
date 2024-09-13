"""
Module ScaleSelectionWidget
"""

__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import (QGroupBox, QSizePolicy, QHBoxLayout, QComboBox, QApplication,
                             QWidget, QCheckBox, QPushButton, QVBoxLayout, QLabel, QGridLayout)

from .WidgetUtils import checkStateToBool
from .ChordButtonPanel import GChordButtonLayout

from GMusicIntervals import GMusicalChar, SCALE_DEGREES
from GModels import GKeyScaleModel, GPlayer, GPianoModel
from GUtils import integerToRoman



class GScaleSelectionWidget(QGroupBox):

    def __init__(self, scale_model: GKeyScaleModel, piano_model: GPianoModel, parent: QWidget=None):
        super().__init__("Scale", parent)

        self.scale_model = scale_model
        self.piano_model = piano_model

        NUMBER_OF_CHORD_COLUMNS = 7
        NUMBER_OF_CHORD_ROWS = 1

        main_layout = QVBoxLayout()

        scale_selection_layout = QHBoxLayout()

        self.key_combo_box = QComboBox()
        self.key_combo_box.setModel(self.scale_model.key_model)
        self.key_combo_box.currentTextChanged.connect(self.scale_model.currentKeyChanged)
        self.scale_model.currentKeyUpdated.connect(self._currentKeyModelUpated)
        scale_selection_layout.addWidget(self.key_combo_box)

        self.scale_combo_box = QComboBox()
        self.scale_combo_box.setModel(scale_model.scale_model)
        self.scale_combo_box.currentTextChanged.connect(self.scale_model.currentScaleChanged)
        self.scale_model.currentScaleUpdated.connect(self._currentScaleModelUpdated)
        scale_selection_layout.addWidget(self.scale_combo_box)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self._playScale)
        play_metrics = QFontMetrics(self.play_button.font()).boundingRect(self.play_button.text())
        self.play_button.setFixedWidth(play_metrics.width() + 10)
        scale_selection_layout.addWidget(self.play_button)

        scale_selection_layout.addStretch(1)

        self.show_scale_check_box = QCheckBox("Show")
        self.show_scale_check_box.setChecked(self.scale_model.showScale())
        self.show_scale_check_box.checkStateChanged.connect(self._showScaleUpdated)
        scale_selection_layout.addWidget(self.show_scale_check_box)

        main_layout.addLayout(scale_selection_layout)

        self.chord_panel = GChordButtonLayout(NUMBER_OF_CHORD_ROWS, NUMBER_OF_CHORD_COLUMNS,
                                            accept_drops=False, edit_enabled=False,
                                            piano_model=piano_model, show_labels=True)
        for button in self.chord_panel.chordButtons():
            button.setFixedWidth(40)

        for i, label in enumerate(self.chord_panel.chordLabels()):
            scale_degree = i + 1
            label.setText(integerToRoman(scale_degree))
            label.setToolTip(SCALE_DEGREES[scale_degree])

        main_layout.addLayout(self.chord_panel)

        self.setLayout(main_layout)

        self.scale_model.modelUpdated.connect(self._modelUpdated)
        self.piano_model.playEnded.connect(self._playEnded)

        self.scale_combo_box.setCurrentText("Natural Major")

        self._updateChords()


    def sizeHint(self):
        return QSize(100, 100)


    def _updateChords(self):
        applicable_chords = enumerate(self.scale_model.currentScale().chordsOfScale())        
        chord_buttons = self.chord_panel.chordButtons()
        chord_labels = self.chord_panel.chordLabels()

        for i, chord in applicable_chords:
            chord_buttons[i].setChord(chord)
            scale_degree = i + 1
            
            match chord.template.long_name:
                case "major":
                    case = "upper"
                    postfix = ""
                    
                case "minor":
                    case = "lower"
                    postfix = ""
                    
                case "diminished":
                    case = "lower"
                    postfix = GMusicalChar.Dim

                case "augmented":
                    case = "lower"
                    postfix = "+"

            chord_labels[i].setText(integerToRoman(scale_degree, case) + postfix)


    def _modelUpdated(self, model:GKeyScaleModel):
        self._updateChords()


    def _playEnded(self):
        self.play_button.setDisabled(False)


    def _playScale(self):
        self.play_button.setDisabled(True)

        scale = self.scale_model.currentScale()
        notes_to_play = scale.extendedNoteValues()[:(scale.numberOfNotesInScale() + 1)]
        appegio_to_play = [[note_name] for note_name in notes_to_play]
        self.piano_model.play(appegio_to_play, rebase=True, arpeggio_period=250, arpeggio=GPlayer.ArpeggioType.ForwardBackward)


    def _showScaleUpdated(self, state: Qt.CheckState):
        self.scale_model.setShowScale(checkStateToBool(state))


    def _currentKeyModelUpated(self, key_index):        
        self.key_combo_box.setCurrentIndex(key_index)


    def _currentScaleModelUpdated(self, scale_index):        
        self.scale_combo_box.setCurrentIndex(scale_index)



def unitTest():

    app = QApplication([])

    scale_model = GKeyScaleModel()
    scale_selection_box = GScaleSelectionWidget(scale_model)

    scale_selection_box.show()
    app.exec()



if __name__ == "__main__":
    unitTest()