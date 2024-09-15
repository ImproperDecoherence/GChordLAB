"""
Module defining a widget for editing chords.
"""

__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtWidgets import QSizePolicy, QGridLayout, QComboBox, QButtonGroup, QPushButton, QGroupBox
from PyQt6.QtGui import QEnterEvent, QWheelEvent
from PyQt6.QtCore import QSize

from GModels import GPianoModel, GKeyScaleModel
from .ChordButton import GChordButton
from GMusicIntervals import (GDynamicChord, GDynamicChordTemplate, GScale, GToneInterval,
                             CHORD_TYPES, CHORD_MODIFIERS, listOfNoteNames)



class GChordEditPanel(QGroupBox):
    """A widget for editing chords."""

    def __init__(self, title: str, no_of_columns: int,                  
                 piano_model: GPianoModel = None, 
                 scale_model: GKeyScaleModel = None,
                 parent=None) -> None:
        """
        Args:
            title: The title of the widget's group box.
            no_of_columns: The number of columns to be used for the chord modifier buttons.
            piano_model: The piano model to be used for visalizing and playing the chord.
            scale_model: The scale model providing current key.
            parent (optional): Parent widget.
        """
        
        super().__init__(title, parent)

        self.piano_model = piano_model        
        self.scale_model = scale_model        

        self.grid_layout = QGridLayout()

        self.root_combo_box = QComboBox()
        self.root_combo_box.addItems(listOfNoteNames(0, GToneInterval.Octave, style="flat", show_octave=False))
        self.root_combo_box.currentTextChanged.connect(self._rootChanged)
        self.root_combo_box.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.grid_layout.addWidget(self.root_combo_box, 0, 0)

        self.chord_type_button_group = QButtonGroup()
        self.chord_type_button_group.setExclusive(True)
        self.chord_type_button_group.idClicked.connect(self._chordTypeChanged)

        for i, id in enumerate(CHORD_TYPES.keys()):
            chord = CHORD_TYPES[id]

            button = QPushButton(chord.shortName(self._currentRoot()))
            button.setToolTip(chord.longName(self._currentRoot()))
            button.setCheckable(True)
            
            if i == 0:
                button.setChecked(True)
            else:
                button.setChecked(False)

            self.chord_type_button_group.addButton(button, id)
            self.grid_layout.addWidget(button, 0, i + 1)
        
        self.flag_button_group = QButtonGroup()
        self.flag_button_group.setExclusive(False)
        self.flag_button_group.idClicked.connect(self._chordModifierChanged)

        for i, mod_id in enumerate(CHORD_MODIFIERS.keys()):
            modfier = CHORD_MODIFIERS[mod_id]

            button = QPushButton(modfier.shortName())
            button.setToolTip(modfier.longName())
            button.setCheckable(True)            

            self.flag_button_group.addButton(button, mod_id)
            self.grid_layout.addWidget(button, 1 + i // no_of_columns, i % no_of_columns)

        self.chord_edit_button = GChordButton()
        self.chord_edit_button.buttonClicked.connect(self._chordEditButtonClicked)
        self.chord_edit_button.buttonCtrlClicked.connect(self._chordEditButtonCtrlClicked)
        self.chord_edit_button.chordChanged.connect(self._editChordChanged)
        self.chord_edit_button.setAcceptDrops(True)
        self.grid_layout.addWidget(self.chord_edit_button, self.grid_layout.rowCount() - 1, self.grid_layout.columnCount() - 1, 1, 1)

        self.setLayout(self.grid_layout)

        self.chord_edit_button.setChord(GDynamicChord(self._currentRoot(), self._checkedChordType(), self._checkedModifierFlags()))


    def rowCount(self) -> int:
        return self.grid_layout.rowCount()


    def columnCount(self) -> int:
        return self.grid_layout.columnCount()


    def sizeHint(self) -> QSize:
        """Returns the preferred size of the widget."""
        button_size_hint = GChordButton().sizeHint()
        return QSize(self.columnCount() * button_size_hint.width(), self.rowCount() * button_size_hint.height())


    def enterEvent(self, event: QEnterEvent) -> None:
        """This method is called by the framework when the mouse pointer enters the widget."""
        super().enterEvent(event)
        self._updateHighlightedChord()        
        

    def leaveEvent(self, event: QEnterEvent) -> None:
        """This method is called by the framework when the mouse pointer leaves the widget."""
        super().leaveEvent(event)
        
        if self.piano_model is not None:
            self.piano_model.setHighlightedNoteValues([])

            if self.scale_model is not None:
                self.piano_model.showScale(self.scale_model.currentScale(), self.scale_model.showScale())


    def wheelEvent(self, event: QWheelEvent) -> None:
        """This method is called by the framework when a mouse wheel event occurs inside the widget."""
        super().wheelEvent(event)

        steps = event.angleDelta().y() // 120
        next_index = (self.root_combo_box.currentIndex() - steps) % self.root_combo_box.count()
        self.root_combo_box.setCurrentIndex(next_index)        
        

    def _editChordChanged(self, button: GChordButton) -> None:
        """This method is called when the current chord of the chord button is changed."""
        if button.chord is not None:
            self.root_combo_box.setCurrentText(button.chord.rootNoteName())

        
    def _chordEditButtonClicked(self, button: GChordButton) -> None:
        """This method is called when the chord button is clicked."""
        if self.piano_model is not None:
            self.piano_model.play(self.chord_edit_button.chord.noteValues())


    def _chordEditButtonCtrlClicked(self, button: GChordButton) -> None:
        """This method is called when the chord button is ctrl-clicked."""
        if self.piano_model is not None:
            self.piano_model.setSelectedNoteValues(self.chord_edit_button.chord.noteValues())


    def _checkedChordType(self) -> GDynamicChordTemplate:
        """Returns the current selection of chord type."""
        return CHORD_TYPES[self.chord_type_button_group.checkedId()]


    def _checkedModifierFlags(self) -> list[int]:
        """Returns the flags for all selected chord modifiers."""
        return [self.flag_button_group.id(button) for button in self.flag_button_group.buttons() if button.isChecked()]


    def _updateHighlightedChord(self) -> None:
        """Updates the highlighted notes in the piano model."""
        highlighted_note_values = []
        current_cord = self.chord_edit_button.chord
        current_scale = None

        if current_cord is not None:
            highlighted_note_values = current_cord.noteValues()
            current_scale = GScale(current_cord.rootNoteValue(), "Natural Major")

        if self.piano_model is not None:
            self.piano_model.setHighlightedNoteValues(highlighted_note_values)

            if current_scale is not None:
                self.piano_model.showScale(current_scale, show=True)


    def _updateEditChord(self, play=True) -> None:
        """Updates the chord of the chord button according to selected chord type and chord modifiers."""
        self.chord_edit_button.setChord(GDynamicChord(self._currentRoot(), self._checkedChordType(), self._checkedModifierFlags()))

        if play and (self.piano_model is not None):
            self.piano_model.play(self.chord_edit_button.chord.noteValues())

        self._updateHighlightedChord()


    def _currentRoot(self) -> int:
        """Returns the current note value of the root note combo box."""
        return self.root_combo_box.currentIndex()


    def _chordTypeChanged(self, button_id: int) -> None:
        """This method is called when the chord type selection is changed."""
        self._updateEditChord()


    def _chordModifierChanged(self, button_id: int) -> None:
        """This method is called when the chord modifier selection is changed."""
        self._updateEditChord()


    def _rootChanged(self, note_name) -> None:
        """This method is called when the current value of the root note combo box is changed."""

        for button in self.chord_type_button_group.buttons():            
            chord = CHORD_TYPES[self.chord_type_button_group.id(button)]
            button.setText(chord.shortName(self._currentRoot()))
            button.setToolTip(chord.longName(self._currentRoot()))

        self._updateEditChord(play=False)

