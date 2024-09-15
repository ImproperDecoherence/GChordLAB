"""
Module defining a button which can be related to a GDynamicChord.
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
    """Button which represents a GDynamicChord - supports drag'n'drop."""

    def __init__(self, chord: GDynamicChord = None, parent=None):
        """
        Args:
            chord: The chord which shall be related to the button.
            parent (optional): Partent widget.
        """
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
        """Returns the preferred size of the widget."""
        return QSize(55, 30)


    def enableEdit(self, enable: bool):
        """Sets if the button shall enable its context menu."""
        self.edit_enabled = enable


    def setHighlight(self, highlight: bool):
        """Sets if the button shall be highlighted or not."""
        self.highlighted = highlight
        self.update()


    def clear(self):
        """Sets the related chord to None."""
        self.setChord(None)


    def cycleChordInversion(self):
        """Cycles to next inversion of the chord (modulu number of notes in the chord)."""
        if self.chord is not None:
            self.chord.cycleInversion()
            self.update()


    def contextMenuEvent(self, event: QContextMenuEvent | None) -> None:
        """This method is called by the framework when a context menu is requested (right click)."""
        if self.chord is not None:
            if self.edit_enabled:
                self.context_menu.exec(event.globalPos())


    def mousePressEvent(self, event: QMouseEvent):
        """This method is called by the framework when there is a mouse press event insde the widget."""
        self.mouse_press_modifiers = QApplication.keyboardModifiers()
        self.mouse_press_buttons = QApplication.mouseButtons()
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event: QMouseEvent):
        """This method is called by the framework when there is a mouse release event insde the widget."""
        if self.chord is not None:
            if self.mouse_press_buttons == Qt.MouseButton.LeftButton:
                if self.mouse_press_modifiers == Qt.KeyboardModifier.ControlModifier:
                    self.buttonCtrlClicked.emit(self)
                else:
                    self.buttonClicked.emit(self)

        super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event: QMouseEvent):
        """This method is called by the framework when a mouse move event occurs within the widget."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.chord is not None:
                drag = QDrag(self)
                mime = QMimeData()
                mime.setText(self.chord.shortName())
                drag.setMimeData(mime)
                drag.exec(Qt.DropAction.MoveAction)


    def dragEnterEvent(self, drag: QDragEnterEvent):
        """This method is called by the framework when a mouse drag event starts."""
        drag.accept()


    def dropEvent(self, event: QDropEvent | None) -> None:
        """This method is called by the framework when a drop event occurs."""
        dropped_chord = event.source().chord
        self.setChord(dropped_chord)


    def setChord(self, chord_to_set: GDynamicChord):
        """Sets the current chord of the widget."""

        debugVariable("chord_to_set", True)
        self.chord = copy.copy(chord_to_set)

        if self.chord is not None:
            self.setToolTip(chord_to_set.longName())            
        else:
            self.setToolTip("")
            
        self.chordChanged.emit(self)
        self.update()


    def enterEvent(self, event: QEnterEvent):
        """This method is called by the framework when the mouse pointer enters the button."""
        super().enterEvent(event)

        if self.chord is not None:
            self.enterButton.emit(self)
            self.current = True
            self.update()


    def leaveEvent(self, event: QEnterEvent):
        """This method is called by the framework when the mouse pointer leaves the button."""
        super().leaveEvent(event)

        self.current = False
        self.border_color = self.DEFAULT_BORDER_COLOR
        self.leaveButton.emit(self)
        self.update()


    def paintEvent(self, event: QPaintEvent):
        """This method is called by the framework when the widget needs to be re-painted."""
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



def unitTest():

    app = QApplication([])
    widget = GChordButton()
    widget.show()
    app.exec()



if __name__ == "__main__":
    unitTest()
