"""
Module ChordButtonPanel
"""

__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel, QVBoxLayout
from PyQt6.QtCore import QSize, Qt

from GModels import GPianoModel
from .ChordButton import GChordButton
from GMusicIntervals import GDynamicChord
from GUtils import GSignal, debugVariable


class GChordButtonLayout(QGridLayout):

    def __init__(self, no_of_rows: int, no_of_columns: int, 
                 accept_drops=True, edit_enabled=True, 
                 piano_model: GPianoModel = None,
                 parent: QWidget=None,
                 show_labels= False):
        
        super().__init__(parent)

        self.piano_model = piano_model        

        self.chordChanged = GSignal()
        self.chordFocusOn = GSignal()
        self.chordFocusOff = GSignal()
        self.chordSelected = GSignal()
        self.chordCtrlSelected = GSignal()

        self.chord_buttons = [GChordButton() for _ in range(no_of_rows * no_of_columns)]
        self.chord_labels = [QLabel() for _ in range(no_of_rows * no_of_columns)]

        for i, (chord_label, chord_button) in enumerate(zip(self.chord_labels, self.chord_buttons)):
            layout = QVBoxLayout()

            chord_label.setVisible(show_labels)
            chord_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
            layout.addWidget(chord_label)

            chord_button.buttonClicked.connect(self._chordButtonClicked)
            chord_button.buttonCtrlClicked.connect(self._chordButtonCtrlClicked)
            chord_button.enterButton.connect(self._enterChordButton)
            chord_button.leaveButton.connect(self._leaveChordButton)
            chord_button.chordChanged.connect(self._chordChanged)

            chord_button.setAcceptDrops(accept_drops)
            chord_button.enableEdit(edit_enabled)

            layout.addWidget(chord_button)

            self.addLayout(layout, i // no_of_columns, i % no_of_columns)                


    def sizeHint(self):
        button_size_hint = GChordButton().sizeHint()
        return QSize(self.columnCount() * button_size_hint.width() + 20, self.rowCount() * button_size_hint.height() + 20)


    def chordLabels(self):
        return self.chord_labels


    def chordButtons(self) -> list[GChordButton]:
        return self.chord_buttons


    def currentChords(self) -> list[GDynamicChord]:
        return [chord_button.chord for chord_button in self.chord_buttons if chord_button.chord is not None]


    def setChords(self, chord_list: list[GDynamicChord]):
        no_of_chords = len(chord_list)
        debugVariable("chord_list")

        for i, chord_button in enumerate(self.chord_buttons):
            if i < no_of_chords:
                 chord = chord_list[i]
                 debugVariable("chord")
                 chord_button.setChord(chord)
            else:
                chord_button.setChord(None)


    def _chordChanged(self, button: GChordButton):        
        self.chordChanged.emit(button.chord)


    def _enterChordButton(self, button: GChordButton):
        if (button.chord is not None) and (self.piano_model is not None):
            self.piano_model.setHighlightedNoteValues(button.chord.noteValues())

        self.chordFocusOn.emit(button.chord)


    def _leaveChordButton(self, button: GChordButton):        
        if (button.chord is not None) and (self.piano_model is not None):
            self.piano_model.setHighlightedNoteValues([])

        self.chordFocusOff.emit(button.chord)


    def _chordButtonClicked(self, button: GChordButton):
        if (button.chord is not None) and (self.piano_model is not None):
            self.piano_model.play(button.chord.noteValues())

        self.chordSelected.emit(button.chord)


    def _chordButtonCtrlClicked(self, button: GChordButton):
        if (button.chord is not None) and (self.piano_model is not None):
            self.piano_model.setSelectedNoteValues(button.chord.noteValues())

        self.chordCtrlSelected.emit(button.chord)



class GChordButtonPanel(QGroupBox):

    def __init__(self, title: str, no_of_rows: int, no_of_columns: int, 
                 accept_drops=True, edit_enabled=True, 
                 piano_model: GPianoModel = None,
                 parent: QWidget=None):
        
        super().__init__(title, parent)

        self.chord_button_layout = GChordButtonLayout(no_of_rows, no_of_columns, 
                                                      accept_drops, edit_enabled, 
                                                      piano_model, self)

        self.chordChanged = GSignal()
        self.chord_button_layout.chordChanged.connectSignal(self.chordChanged)

        self.chordFocusOn = GSignal()
        self.chord_button_layout.chordFocusOn.connectSignal(self.chordFocusOn)

        self.chordFocusOff = GSignal()
        self.chord_button_layout.chordFocusOff.connectSignal(self.chordFocusOff)

        self.chordSelected = GSignal()
        self.chord_button_layout.chordSelected.connectSignal(self.chordSelected)

        self.chordCtrlSelected = GSignal()
        self.chord_button_layout.chordCtrlSelected.connectSignal(self.chordCtrlSelected)
        
        self.setLayout(self.chord_button_layout)


    def chordButtons(self) -> list[GChordButton]:
        return self.chord_button_layout.chord_buttons()


    def chords(self) -> list[GDynamicChord]:
        return self.chord_button_layout.currentChords()


    def rowCount(self):
        return self.chord_button_layout.rowCount()


    def columnCount(self):
        return self.chord_button_layout.columnCount()


    def sizeHint(self):
        return self.chord_button_layout.sizeHint()        

