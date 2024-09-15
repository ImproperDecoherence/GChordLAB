"""
Module definings layouts and panels for GChordButtons.
"""

__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel, QVBoxLayout
from PyQt6.QtCore import QSize, Qt

from GModels import GPianoModel
from .ChordButton import GChordButton
from GMusicIntervals import GDynamicChord
from GUtils import GSignal, debugVariable


class GChordButtonLayout(QGridLayout):
    """Grid layout for GChordButtons."""

    def __init__(self, no_of_rows: int, no_of_columns: int, 
                 accept_drops: bool=True, edit_enabled: bool=True, 
                 piano_model: GPianoModel=None,
                 parent: QWidget=None,
                 show_labels: bool=False) -> None:
        """
        Args:
            no_of_rows: Number of grid layout rows.
            no_of_columns: Number of grid layout columns.
            accept_drops (optional): Enables buttons in the layout to acceps drops.
            edit_enabled (optional): Enables buttons in the layout to be edited.
            piano_model (optional): Piano model used to play and visualize chords.
            parent (optional): Parent widget.
            show_labels (optional): Enables a text label above each button.
        """
        
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


    def sizeHint(self) -> QSize:
        """Returns the preferred size of the widget."""
        button_size_hint = GChordButton().sizeHint()
        return QSize(self.columnCount() * button_size_hint.width() + 20, self.rowCount() * button_size_hint.height() + 20)


    def chordLabels(self) -> list[QLabel]:
        """Returns the lables of all chord buttons."""
        return self.chord_labels


    def chordButtons(self) -> list[GChordButton]:
        """Returns all chord buttons."""
        return self.chord_buttons


    def currentChords(self) -> list[GDynamicChord]:
        """Returns the current chord of all chord buttons."""
        return [chord_button.chord for chord_button in self.chord_buttons if chord_button.chord is not None]


    def setChords(self, chord_list: list[GDynamicChord]):
        """Sets the current chord of the chord buttons, from top left to bottom right.
        
        Remaining chord buttons are reset to not contain any chord.
        """

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
        """This method is called when a chord is changed in any of the chord buttons."""
        self.chordChanged.emit(button.chord)


    def _enterChordButton(self, button: GChordButton):
        """This method is called when a the mouse enters any of the chord buttons."""

        if (button.chord is not None) and (self.piano_model is not None):
            self.piano_model.setHighlightedNoteValues(button.chord.noteValues())

        self.chordFocusOn.emit(button.chord)


    def _leaveChordButton(self, button: GChordButton):
        """This method is called when a the mouse leaves any of the chord buttons."""

        if (button.chord is not None) and (self.piano_model is not None):
            self.piano_model.setHighlightedNoteValues([])

        self.chordFocusOff.emit(button.chord)


    def _chordButtonClicked(self, button: GChordButton):
        """This method is called when any of the chord buttons is clicked."""

        if (button.chord is not None) and (self.piano_model is not None):
            self.piano_model.play(button.chord.noteValues())

        self.chordSelected.emit(button.chord)


    def _chordButtonCtrlClicked(self, button: GChordButton):
        """This method is called when any of the chord buttons is ctrl-clicked."""

        if (button.chord is not None) and (self.piano_model is not None):
            self.piano_model.setSelectedNoteValues(button.chord.noteValues())

        self.chordCtrlSelected.emit(button.chord)



class GChordButtonPanel(QGroupBox):
    """A group box which contains a GChordButtonLayout."""

    def __init__(self, title: str, no_of_rows: int, no_of_columns: int, 
                 accept_drops:bool =True, edit_enabled: bool=True, 
                 piano_model: GPianoModel = None,
                 parent: QWidget=None) -> None:
        """
        Args:
            title: The title of the group box.
            no_of_rows: Number of grid layout rows.
            no_of_columns: Number of grid layout columns.
            accept_drops (optional): Enables buttons in the layout to acceps drops.
            edit_enabled (optional): Enables buttons in the layout to be edited.
            piano_model (optional): Piano model used to play and visualize chords.
            parent (optional): Parent widget.
        """
        
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
        """Returns all chord buttons."""
        return self.chord_button_layout.chord_buttons()


    def chords(self) -> list[GDynamicChord]:
        """Returns the current chord of all chord buttons."""
        return self.chord_button_layout.currentChords()


    def rowCount(self):
        """Returns the number of chord button rows."""
        return self.chord_button_layout.rowCount()


    def columnCount(self):
        """Returns the number of chord button columns."""
        return self.chord_button_layout.columnCount()


    def sizeHint(self):
        """Returns the preferred size of the widget."""
        return self.chord_button_layout.sizeHint()        

