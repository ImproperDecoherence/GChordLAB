
"""
Module defining a list view for GDynamicChords.
"""

__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtCore import Qt, QAbstractListModel, QModelIndex, QMimeData, QSize
from PyQt6.QtWidgets import QListView, QSizePolicy
from PyQt6.QtGui import QDrag

from GMusicIntervals import GDynamicChord
from GModels import GChordFinder
from GUtils import GSignal


class _ChordListWidgetModel(QAbstractListModel):
        """Data model to be used with the GChordListWidget."""

        def __init__(self, chord_finder: GChordFinder):
            super().__init__()
            self.chord_finder = chord_finder
            self.chord_finder.chordsUpdated.connect(self._modelUpdated)


        def data(self, index, role):
            if role == Qt.ItemDataRole.DisplayRole:
                current_chords = self.chord_finder.currentChords()
                chord_name = current_chords[index.row()].shortName()                
                return chord_name
                

        def rowCount(self, index):            
            return self.chord_finder.currentNumberOfChords()
        

        def _modelUpdated(self, chord_finder: GChordFinder):
             self.modelReset.emit()


        def chord(self, index: QModelIndex) -> GDynamicChord:
             if index.isValid():
                current_chords = self.chord_finder.currentChords()
                return current_chords[index.row()]
             else:
                 return None


class GChordListWidget(QListView):    

    def __init__(self, chord_finder: GChordFinder, parent=None):
        super().__init__(parent)        
        self.list_model = _ChordListWidgetModel(chord_finder)
        self.setModel(self.list_model)

        self.selectionModel().currentChanged.connect(self._selectedItemChanged)

        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)

        self.selectedChordChanged = GSignal()
        self.drag_chord = None

        self.WIDTH = 100
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding)
        self.setMaximumWidth(self.WIDTH)


    def _selectedItemChanged(self, current: QModelIndex, previous: QModelIndex):
        selected_chord = self.list_model.chord(current)
        self.selectedChordChanged.emit(selected_chord)


    # This method is used for drop to GChordBUtton
    @property
    def chord(self):
        return self.drag_chord


    def sizeHint(self):
        """Returns the preferred size of the widget."""
        return QSize(self.WIDTH, 10 * self.model().rowCount(QModelIndex()))


    def currentChord(self) -> GDynamicChord:
        current_index: QModelIndex = self.currentIndex()
        return self.list_model.chord(current_index)
    

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mimeData = QMimeData()
            current_index = self.indexAt(event.pos())

            if current_index.isValid():
                self.drag_chord = self.list_model.chord(current_index)                
                mimeData.setText(self.drag_chord.shortName())
                drag.setMimeData(mimeData)
                drag.exec(Qt.DropAction.MoveAction)

        super().mouseMoveEvent(event)
