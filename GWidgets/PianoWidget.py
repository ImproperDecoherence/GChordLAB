"""
Module GPianoWidget
"""

__author__ = "https://github.com/ImproperDecoherence"


from GUtils import debugVariable
from GMusicIntervals import GDynamicChord
from GModels import GPianoModel, GPianoKeyState

from PyQt6.QtWidgets import (QWidget, QApplication, QMenu)
                             
from PyQt6.QtCore import Qt, QRect, QPoint, QSize
from PyQt6.QtGui import (QColor, QPainter, QPen, QBrush, QFont, QMouseEvent, QPaintEvent, 
                         QDragEnterEvent, QDropEvent, QContextMenuEvent)



class GPianoWidget(QWidget):

    def __init__(self, piano_model: GPianoModel, parent=None):
        super().__init__(parent)

        self.piano_model = piano_model

        self.black_key_rects = {key.key_value: QRect() for key in piano_model.blackKeyStates()}
        self.white_key_rects = {key.key_value: QRect() for key in piano_model.whiteKeyStates()}

        self.piano_model.keyStateChanged.connect(self._keyUpdateEvent)   
        self.piano_model.keyLayoutChanged.connect(self._keyLayoutChanged)

        self.setMinimumHeight(125)
        self.setAcceptDrops(True)

        self.context_menu = QMenu()

        clear_action = self.context_menu.addAction("Clear Selection")
        clear_action.triggered.connect(self._clearSelection)

        clear_action = self.context_menu.addAction("Play Selection")
        clear_action.triggered.connect(self._playSelection)
        

    def sizeHint(self):
        hight = 250
        width = len(self.white_key_rects.values()) * 8
        return QSize(width, hight)
    

    def _paintBackground(self, painter: QPainter):
        painter.fillRect(QRect(0, 0, painter.device().width(), painter.device().height()), QColor('black'))


    def _paintKey(self, rect: QRect, key_state: GPianoKeyState, painter: QPainter, outline_color: QColor, fill_color: 
                 QColor, text_color: QColor, corner_radius: float, white_key_width: int):
        
        pen = QPen(outline_color)    
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        brush = QBrush(fill_color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)

        painter.drawRoundedRect(rect, corner_radius, corner_radius)

        brush.setStyle(Qt.BrushStyle.NoBrush)
        painter.setBrush(brush)

        gradient_start_value = outline_color.valueF()
        gradient_end_value = fill_color.valueF()
        number_of_gradient_lines = round(corner_radius / 2)
        gradient_step = (gradient_end_value - gradient_start_value) / (number_of_gradient_lines + 1)
        gradient_color = QColor(outline_color)
        gradient_rect = QRect(rect)
        gradient_corner_radius = corner_radius
        
        for _ in range(number_of_gradient_lines):
            gradient_rect = gradient_rect.adjusted(+1, +1, -1, -1)
            gradient_corner_radius -= 2
            gradient_color.setHsvF(gradient_color.hueF(), gradient_color.saturationF(), gradient_color.valueF() + gradient_step)
            pen.setColor(gradient_color)
            painter.setPen(pen)
            painter.drawRoundedRect(gradient_rect, gradient_corner_radius, gradient_corner_radius)

        text_size = round(0.20 * white_key_width)
        painter.setFont(QFont("Arial", text_size))
        pen.setColor(text_color)
        painter.setPen(pen)

        number_rect = QRect(rect)
        number_rect.adjust(0, rect.height() - round(1.50 * white_key_width), 0, 0)
        painter.drawText(number_rect, Qt.AlignmentFlag.AlignCenter, key_state.keyInScaleName())

        name_rect = QRect(rect)
        name_rect.adjust(0, rect.height() - round(0.75 * white_key_width), 0, 0)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, key_state.key_name)

        
    def _paintWhiteKey(self, rect: QRect, key_state: GPianoKeyState, painter: QPainter, white_key_width):
        corner_radius=10.0

        if key_state.isSelected():
            outline_color = QColor.fromHsl(0, 200, 10)
            fill_color = QColor.fromHsl(0, 200, 120)
            text_color = QColor('white')
        elif not key_state.isInCurrentScale():
            outline_color = QColor('gray')
            fill_color = QColor('lightGray')
            text_color = QColor('white')
        else:
            outline_color = QColor('black')
            fill_color = QColor('white')
            text_color = QColor('black')
        
        if key_state.isHighlighted():
            outline_color = QColor.fromHsl(100, 200, 10)
            fill_color = QColor.fromHsl(100, 200, 120)
            text_color = QColor('white')

        self._paintKey(rect, key_state, painter, outline_color, fill_color, text_color, corner_radius, white_key_width)


    def _paintBlackKey(self, rect: QRect, key_state: GPianoKeyState, painter: QPainter, white_key_width):
        corner_radius = 8.0

        if key_state.isSelected():
            outline_color = QColor.fromHsl(0, 200, 160)
            fill_color = QColor.fromHsl(0, 200, 100)
            text_color = QColor('white')
        elif not key_state.isInCurrentScale():
            outline_color = QColor('gray')
            fill_color = QColor('darkGray')
            text_color = QColor('lightGray')
        else:
            outline_color = QColor('lightGray')
            fill_color = QColor('black')
            text_color = QColor('white')

        if key_state.isHighlighted():
            outline_color = QColor.fromHsl(100, 200, 160)
            fill_color = QColor.fromHsl(100, 200, 100)
            text_color = QColor('white')

        self._paintKey(rect, key_state, painter, outline_color, fill_color, text_color, corner_radius, white_key_width)


    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._paintBackground(painter)

        white_keys = self.piano_model.whiteKeyStates()
        white_key_width = painter.device().width() / len(white_keys)
        white_key_height = painter.device().height()
        white_key_rect = QRect(0, 0, round(white_key_width), white_key_height)

        for i, key in enumerate(white_keys):
            white_key_rect.moveLeft(round(i * white_key_width))
            self.white_key_rects[key.key_value] = QRect(white_key_rect)
            self._paintWhiteKey(white_key_rect, key, painter, white_key_width)
            
        black_keys = self.piano_model.blackKeyStates()
        black_key_width = white_key_width * 2 / 3
        black_key_height = white_key_height * 2 / 3
        black_key_rect = QRect(0, 0, round(black_key_width), round(black_key_height))

        b2b_1 = (3 * white_key_width - 2 * black_key_width) / 3 # distance between black keys for the pair
        b2b_2 = (4 * white_key_width - 3 * black_key_width) / 4 # distance between black keys for the trio

        first_black_note = black_keys[0].key_name

        if ('C#' in first_black_note) or ('Db' in first_black_note):
            black_key_x_translations = [black_key_width + b2b_1, 
                                        black_key_width + b2b_1 + b2b_2, 
                                        black_key_width + b2b_2, 
                                        black_key_width + b2b_2, 
                                        black_key_width + b2b_2 + b2b_1]
            x_pos = b2b_1
        else:
            black_key_x_translations = [black_key_width + b2b_2,
                                        black_key_width + b2b_2, 
                                        black_key_width + b2b_2 + b2b_1, 
                                        black_key_width + b2b_1,
                                        black_key_width + b2b_1 + b2b_2]
            x_pos = b2b_2

        
        for i, key in enumerate(black_keys):
            black_key_rect.moveLeft(round(x_pos))
            self.black_key_rects[key.key_value] = QRect(black_key_rect)
            self._paintBlackKey(black_key_rect, key, painter, white_key_width)
            x_pos += black_key_x_translations[i % len(black_key_x_translations)]

        painter.end()


    def _findClickedKeyRect(self, position: QPoint, key_rects: dict[int, QRect]) -> int | None:
        for key_value in key_rects:
            if key_rects[key_value].contains(position):
                return key_value
            
        return None


    def _findClickedNoteValue(self, event: QMouseEvent) -> int | None:
        clicked_pos = event.position().toPoint()

        clicked_black_key_value = self._findClickedKeyRect(clicked_pos, self.black_key_rects)
        clicked_white_key_value = self._findClickedKeyRect(clicked_pos, self.white_key_rects)

        if clicked_black_key_value is not None:
            last_clicked_key_value = clicked_black_key_value
        else:
            last_clicked_key_value = clicked_white_key_value

        return last_clicked_key_value


    def _clearSelection(self):
        self.piano_model.setSelectedNoteValues([])


    def _playSelection(self):
        self.piano_model.playSelectedNotes()


    def mousePressEvent(self, event: QMouseEvent):        
        self.mouse_press_modifiers = QApplication.keyboardModifiers()
        self.mouse_press_buttons = QApplication.mouseButtons()

        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.mouse_press_buttons == Qt.MouseButton.LeftButton:

            clicked_note_value = self._findClickedNoteValue(event)
            modifiers = QApplication.keyboardModifiers()

            debugVariable("clicked_note_value")

            if modifiers == Qt.KeyboardModifier.ControlModifier:
                self.piano_model.toggleSelection(clicked_note_value)
                self.piano_model.playSelectedNotes()
            else:                
                self.piano_model.play([clicked_note_value], rebase=False, highlight=False)

        super().mouseReleaseEvent(event)

        
    def _keyUpdateEvent(self, key_state: GPianoKeyState):
        print(key_state)
        self.update()


    def _keyLayoutChanged(self, piano_model: GPianoModel):
        self.black_key_rects = {key.key_value: QRect() for key in self.piano_model.blackKeyStates()}
        self.white_key_rects = {key.key_value: QRect() for key in self.piano_model.whiteKeyStates()}
        self.update()
   

    def contextMenuEvent(self, event: QContextMenuEvent | None) -> None:
        self.context_menu.exec(event.globalPos())


    def dragEnterEvent(self, drag: QDragEnterEvent):
        drag.accept()


    def dropEvent(self, event: QDropEvent | None) -> None:
        dropped_chord: GDynamicChord = event.source().chord
        debugVariable("dropped_chord")
        if dropped_chord is not None:
            self.piano_model.setSelectedNoteValues(dropped_chord.noteValues())



def unitTest():

    app = QApplication([])
    piano_model = GPianoModel(number_of_octaves=3)
    piano_widget = GPianoWidget(piano_model)
    piano_widget.resize(1500, 400)
    piano_widget.show()
    app.exec()



if __name__ == "__main__":
    unitTest()