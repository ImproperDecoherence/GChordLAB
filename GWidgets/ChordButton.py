"""
Module ChordButton
"""

__author__ = "https://github.com/ImproperDecoherence"


import copy

from PyQt6.QtWidgets import (QWidget, QSizePolicy, QApplication, QMenu, QGridLayout, QComboBox, QButtonGroup,
                             QPushButton, QGroupBox)
from PyQt6.QtGui import (QContextMenuEvent, QDropEvent, QEnterEvent, QMouseEvent, QPalette,
                         QDrag, QDragEnterEvent, QPaintEvent, QColor, QPainter, QPen, QBrush, QFont,
                         QFontMetrics)
from PyQt6.QtCore import (Qt, QMimeData, QRect, QSize)

from GUtils import GSignal, debugVariable
from GModels import GPianoModel, GPlayer, GKeyScaleModel
from GMusicIntervals import (GDynamicChord, GDynamicChordTemplate, GScale, 
                             CHORD_TYPES, CHORD_MODIFIERS, GToneInterval, listOfNoteNames)



class GChordButton(QWidget):

    def __init__(self, chord: GDynamicChord = None, parent=None):
        super().__init__(parent)

        self.enterButton = GSignal()
        self.leaveButton = GSignal()
        self.buttonClicked = GSignal()
        self.buttonCtrlClicked = GSignal()
        self.chordChanged = GSignal()

        self.edit_enabled = False
        self.highlighted = False
        self.current = False

        self.context_menu = QMenu()
        clear_action = self.context_menu.addAction("Clear")
        clear_action.triggered.connect(self.clear)
        invert_action = self.context_menu.addAction("Cycle Inversion")
        invert_action.triggered.connect(self.cycleChordInversion)        

        self.setFixedWidth(55)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.TYPE_FONT = QApplication.font()
        self.MOD_FONT = QFont(self.TYPE_FONT)
        self.MOD_FONT.setPointSize(self.TYPE_FONT.pointSize() - 2)

        self.DEFAULT_BACKGROUND_COLOR = QApplication.palette().color(QPalette.ColorRole.Midlight)
        self.CURRENT_BACKGROUND_COLOR = QApplication.palette().color(QPalette.ColorRole.Button)
        self.HIGHLIGHT_BACKGROUND_COLOR = QColor.fromHsl(100, 200, 100)

        self.DEFUALT_TEXT_COLOR = QApplication.palette().color(QPalette.ColorRole.ButtonText)
        self.HIGHLIGHT_TEXT_COLOR = QColor('white')

        self.DEFAULT_BORDER_COLOR = QApplication.palette().color(QPalette.ColorRole.Dark)
        self.CURRENT_BORDER_COLOR = QApplication.palette().color(QPalette.ColorRole.Highlight)
        self.EMPTY_BORDER_COLOR = self.DEFAULT_BACKGROUND_COLOR

        self.setChord(chord)


    def sizeHint(self):
        return QSize(55, 30)


    def enableEdit(self, enable: bool):
        self.edit_enabled = enable


    def setHighlight(self, highlight: bool):
        self.highlighted = highlight
        self.update()


    def clear(self):
        self.setChord(None)


    def cycleChordInversion(self):
        if self.chord is not None:
            self.chord.cycleInversion()
            self.update()


    def contextMenuEvent(self, event: QContextMenuEvent | None) -> None:
        if self.chord is not None:
            if self.edit_enabled:
                self.context_menu.exec(event.globalPos())


    def mousePressEvent(self, event: QMouseEvent):        
        self.mouse_press_modifiers = QApplication.keyboardModifiers()
        self.mouse_press_buttons = QApplication.mouseButtons()
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.chord is not None:
            if self.mouse_press_buttons == Qt.MouseButton.LeftButton:
                if self.mouse_press_modifiers == Qt.KeyboardModifier.ControlModifier:
                    self.buttonCtrlClicked.emit(self)
                else:
                    self.buttonClicked.emit(self)

        super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.chord is not None:
                drag = QDrag(self)
                mime = QMimeData()
                mime.setText(self.chord.shortName())
                drag.setMimeData(mime)
                drag.exec(Qt.DropAction.MoveAction)


    def dragEnterEvent(self, drag: QDragEnterEvent):
        drag.accept()


    def dropEvent(self, event: QDropEvent | None) -> None:
        dropped_chord = event.source().chord
        self.setChord(dropped_chord)


    def setChord(self, chord_to_set: GDynamicChord):
        debugVariable("chord_to_set", True)
        self.chord = copy.copy(chord_to_set)

        if self.chord is not None:
            self.setToolTip(chord_to_set.longName())            
        else:
            self.setToolTip("")
            
        self.chordChanged.emit(self)
        self.update()


    def enterEvent(self, event: QEnterEvent):        
        super().enterEvent(event)

        if self.chord is not None:
            self.enterButton.emit(self)
            self.current = True
            self.update()


    def leaveEvent(self, event: QEnterEvent):        
        super().leaveEvent(event)

        self.current = False
        self.border_color = self.DEFAULT_BORDER_COLOR
        self.leaveButton.emit(self)
        self.update()


    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        boundary = QRect(0, 0, painter.device().width(), painter.device().height())

        background_color = self.DEFAULT_BACKGROUND_COLOR
        text_color = self.DEFUALT_TEXT_COLOR
        border_color = self.DEFAULT_BORDER_COLOR

        if self.highlighted:
            background_color = self.HIGHLIGHT_BACKGROUND_COLOR
            text_color = self.HIGHLIGHT_TEXT_COLOR            

        if self.current:
            background_color = self.CURRENT_BACKGROUND_COLOR            
            border_color = self.CURRENT_BORDER_COLOR

        if self.chord is None:
            border_color = self.EMPTY_BORDER_COLOR

        pen = QPen(border_color)    
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        brush = QBrush(background_color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)

        corner_radius = 5
        painter.drawRoundedRect(boundary, corner_radius, corner_radius)

        if self.chord is not None:
            type_text = self.chord.shortTypeName()
            mod_text = self.chord.shortModName()
        else:
            type_text = ""
            mod_text = ""

        type_text_metrics = QFontMetrics(self.TYPE_FONT).boundingRect(type_text)
        mod_text_metrics = QFontMetrics(self.MOD_FONT).boundingRect(mod_text)
        
        total_text_width = type_text_metrics.width() + mod_text_metrics.width()

        type_text_rect = QRect(boundary.x() + (boundary.width() - total_text_width) // 2,
                               boundary.y() + (boundary.height() - type_text_metrics.height()) // 2,
                               type_text_metrics.width(),
                               type_text_metrics.height())
        
        mod_text_rect = QRect(type_text_rect.right() + 3,
                              type_text_rect.top(),
                              mod_text_metrics.width(),
                              mod_text_metrics.height())

        painter.setFont(self.TYPE_FONT)
        pen.setColor(text_color)
        painter.setPen(pen)
        painter.drawText(type_text_rect, Qt.AlignmentFlag.AlignCenter, type_text)

        painter.setFont(self.MOD_FONT)
        pen.setColor(text_color)
        painter.setPen(pen)
        painter.drawText(mod_text_rect, Qt.AlignmentFlag.AlignCenter, mod_text)



class GChordEditPanel(QGroupBox):

    def __init__(self, title: str, no_of_columns: int, 
                 piano_model: GPianoModel = None, 
                 player: GPlayer = None, 
                 scale_model: GKeyScaleModel = None,
                 parent=None):
        
        super().__init__(title, parent)

        self.piano_model = piano_model
        self.player = player
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
        self.flag_button_group.idClicked.connect(self._chordFlagChanged)

        for i, mod_id in enumerate(CHORD_MODIFIERS.keys()):
            modfier = CHORD_MODIFIERS[mod_id]

            button = QPushButton(modfier.shortName())
            button.setToolTip(modfier.longName())
            button.setCheckable(True)            

            self.flag_button_group.addButton(button, mod_id)
            self.grid_layout.addWidget(button, 1 + i // no_of_columns, i % no_of_columns)

        self.chord_edit_button = GChordButton()
        self.chord_edit_button.buttonClicked.connect(self._chordEditButtonClicked)
        self.grid_layout.addWidget(self.chord_edit_button, self.grid_layout.rowCount() - 1, self.grid_layout.columnCount() - 1, 1, 1)

        self.setLayout(self.grid_layout)

        self.chord_edit_button.setChord(GDynamicChord(self._currentRoot(), self._chechedType(), self._checkedFlags()))


    def rowCount(self):
        return self.grid_layout.rowCount()


    def columnCount(self):
        return self.grid_layout.columnCount()


    def sizeHint(self):
        button_size_hint = GChordButton().sizeHint()
        return QSize(self.columnCount() * button_size_hint.width(), self.rowCount() * button_size_hint.height())


    def enterEvent(self, event: QEnterEvent):        
        super().enterEvent(event)
        self._updateHighlightedChords()        
        

    def leaveEvent(self, event: QEnterEvent):        
        super().leaveEvent(event)
        
        if self.piano_model is not None:
            self.piano_model.setHighlightedNoteValues([])

            if self.scale_model is not None:
                self.piano_model.showScale(self.scale_model.currentScale(), self.scale_model.showScale())


    def _chordEditButtonClicked(self, button: GChordButton):
        pass


    def _chechedType(self) -> GDynamicChordTemplate:
        return CHORD_TYPES[self.chord_type_button_group.checkedId()]


    def _checkedFlags(self) -> list[int]:
        return [self.flag_button_group.id(button) for button in self.flag_button_group.buttons() if button.isChecked()]


    def _updateHighlightedChords(self):
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


    def _updateEditChord(self):        
        self.chord_edit_button.setChord(GDynamicChord(self._currentRoot(), self._chechedType(), self._checkedFlags()))

        if self.player is not None:
            self.player.play(self.chord_edit_button.chord.noteValues())

        self._updateHighlightedChords()


    def _currentRoot(self):
        return self.root_combo_box.currentIndex()


    def _chordTypeChanged(self, button_id: int):
        self._updateEditChord()


    def _chordFlagChanged(self, button_id: int):
        self._updateEditChord()


    def _rootChanged(self, note_name):
        for button in self.chord_type_button_group.buttons():            
            chord = CHORD_TYPES[self.chord_type_button_group.id(button)]
            button.setText(chord.shortName(self._currentRoot()))
            button.setToolTip(chord.longName(self._currentRoot()))

        self._updateEditChord()


def unitTest():

    app = QApplication([])
    widget = GChordButton()
    widget.show()
    app.exec()



if __name__ == "__main__":
    unitTest()
