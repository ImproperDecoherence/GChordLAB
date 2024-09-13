
"""
Module GChordLab
"""

__author__ = "https://github.com/ImproperDecoherence"
__version__ = "0.1"


from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import QSize, QSizeF, QPointF
from PyQt6.QtGui import QResizeEvent

from GUtils import debugOn, debugVariable
from GModels import GPianoModel, GPlayer, GKeyScaleModel, GChordFinder
from GWidgets import (GPianoPanel, GScaleSelectionWidget, 
                      GChordEditPanel, GChordButtonPanel, GIntervalCircleBox, 
                      GChordPlayerWidget, GChordFinderWidget)


class Application(QApplication):

    def __init__(self):
        super().__init__([])

        debug_filter = ["_SettingsPanel",] 
        debugOn(False, debug_filter)

        self.player = GPlayer()
        self.scale_model = GKeyScaleModel()
        self.piano_model = GPianoModel(self.scale_model, self.player)        
        self.chord_finder = GChordFinder(self.piano_model)
    

class MainLayout():

    def __init__(self, parent_widget: QWidget=None) -> None:

        self.INPUT_AREA_WIDTH = 300
        self.INPUT_AREA_HEIGHT_FRACTION = 0.40
        self.INSTRUMENT_AREA_HEIGHT_FRACTION = 0.35
        self.TOOL_AREA_HEIGHT = 230
        self.MARGIN = 5

        self.parent_widget = parent_widget

        self.input_widgets: list[QWidget] = []
        self.display_widgets: list[QWidget] = []
        self.instrument_widget: QWidget = None
        self.tool_widgets: list[QWidget] = []


    def addInputWidget(self, widget: QWidget):
        self.input_widgets.append(widget)
        widget.setParent(self.parent_widget)


    def addDisplayWidget(self, widget: QWidget):
        self.display_widgets.append(widget)
        widget.setParent(self.parent_widget)


    def addToolWidget(self, widget: QWidget):
        self.tool_widgets.append(widget)
        widget.setParent(self.parent_widget)


    def setIntrumentWidget(self, widget):
        self.instrument_widget = widget
        widget.setParent(self.parent_widget)


    def widgets(self):
        return self.input_widgets + self.display_widgets + self. instrument_widget + self.tool_widgets
    

    def setParentWidget(self, parent: QWidget):
        self.parent_widget = parent


    def _resizeInputWidgets(self, app_size: QSize):

        total_width = self.INPUT_AREA_WIDTH - self.MARGIN
        total_hight = app_size.height() * self.INPUT_AREA_HEIGHT_FRACTION - self.MARGIN
        
        height_hints = [w.sizeHint().height() for w in self.input_widgets]
        total_height_hint = sum(height_hints)

        total_hight_adjustment = total_hight - total_height_hint

        sizes = [QSizeF(total_width - self.MARGIN, h + total_hight_adjustment * h / total_height_hint) 
                 for h in height_hints]

        position = QPointF(self.MARGIN, 0)

        for widget, size in zip(self.input_widgets, sizes):
            widget.resize(size.toSize())            
            widget.move(position.toPoint())            
            position = QPointF(self.MARGIN, position.y() + size.height())
        

    def _resizeDisplayWidgets(self, app_size: QSize):

        total_width = app_size.width() - self.INPUT_AREA_WIDTH
        total_hight = app_size.height() * self.INPUT_AREA_HEIGHT_FRACTION

        size = QSizeF(total_width / len(self.display_widgets) - self.MARGIN, total_hight - self.MARGIN)

        position = QPointF(self.INPUT_AREA_WIDTH, 0)

        for widget in self.display_widgets:
            widget.resize(size.toSize())
            widget.move(position.toPoint())
            position = QPointF(position.x() + size.width(), 0)


    def _resizeToolWidgets(self, app_size: QSize):

        total_width = app_size.width()
        #total_hight = app_size.height() * (1.0 - self.INPUT_AREA_HEIGHT_FRACTION - self.INSTRUMENT_AREA_HEIGHT_FRACTION)
        total_hight = self.TOOL_AREA_HEIGHT

        width_hints = [w.sizeHint().width() for w in self.tool_widgets]
        total_width_hint = sum(width_hints)
        total_width_adjustment = total_width - total_width_hint - (len(self.tool_widgets) + 1) * self.MARGIN
        
        sizes = [QSizeF(w + total_width_adjustment * w / total_width_hint, total_hight - self.MARGIN) 
                 for w in width_hints]
        
        position = QPointF(self.MARGIN, app_size.height() - total_hight)

        for widget, size in zip(self.tool_widgets, sizes):
            widget.resize(size.toSize())
            widget.move(position.toPoint())
            position = QPointF(position.x() + size.width() + self.MARGIN, position.y())


    def _resizeInstrumentWidget(self, app_size: QSize):
        total_width = int(app_size.width() - 2 * self.MARGIN)
        #total_hight = int(app_size.height() * self.INSTRUMENT_AREA_HEIGHT_FRACTION - self.MARGIN)
        total_hight = int(app_size.height() - app_size.height() * self.INPUT_AREA_HEIGHT_FRACTION - self.TOOL_AREA_HEIGHT + self.MARGIN)

        self.instrument_widget.resize(total_width, total_hight)
        self.instrument_widget.move(self.MARGIN, int(self.INPUT_AREA_HEIGHT_FRACTION * app_size.height()) - self.MARGIN)


    def resize(self, app_size: QSize):
        self._resizeInputWidgets(app_size)
        self._resizeDisplayWidgets(app_size)
        self._resizeInstrumentWidget(app_size)
        self._resizeToolWidgets(app_size)


class MainWidget(QWidget):

    def __init__(self, layout: MainLayout, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = layout
        self.layout.setParentWidget(self)


    def resizeEvent(self, event: QResizeEvent | None) -> None:
        self.layout.resize(event.size())
        super().resizeEvent(event)


class MainWindow(QMainWindow):

    def __init__(self, application: Application):
        super().__init__() 

        self.setWindowTitle(f"GChordLAB {__version__}")
        self.app = application

        main_layout = MainLayout()
        main_widget = MainWidget(main_layout)

        scale_selection_box = GScaleSelectionWidget(self.app.scale_model, self.app.piano_model, self)
        main_layout.addInputWidget(scale_selection_box)        

        chord_edit_widget = GChordEditPanel("Chord Editor", no_of_columns=5, 
                                            piano_model=self.app.piano_model,                                             
                                            scale_model=app.scale_model)
        main_layout.addInputWidget(chord_edit_widget)
        
        inteval_circle_box = GIntervalCircleBox(self.app.piano_model, self.app.scale_model, "flat")
        main_layout.addDisplayWidget(inteval_circle_box)

        piano_player = GPianoPanel("Instrument", self.app.piano_model)
        main_layout.setIntrumentWidget(piano_player)

        chord_storage = GChordButtonPanel("Chord Cache", no_of_rows=5, no_of_columns=6, 
                                          accept_drops=True, edit_enabled=True,
                                          piano_model=self.app.piano_model)
        main_layout.addToolWidget(chord_storage)
        
        chord_finder_widget = GChordFinderWidget(self.app.chord_finder, self.app.piano_model)
        main_layout.addToolWidget(chord_finder_widget)

        chord_player_widget = GChordPlayerWidget(app.piano_model)
        main_layout.addToolWidget(chord_player_widget)

        self.setCentralWidget(main_widget)
        self.setMinimumSize(QSize(1200, 800))



if __name__ == "__main__":
    app = Application()
    window = MainWindow(app)
    window.show()
    app.exec()