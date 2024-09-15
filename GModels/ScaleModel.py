"""
Module defining a model which represents a selected scale.
"""


__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtCore import Qt, QAbstractListModel

from GUtils import GSignal
from GMusicIntervals import GScale, GToneInterval, SCALE_TEMPLATES, noteValue, listOfNoteNames


class GKeyScaleModel:
    """Model representing a selected scale."""

    class _ShowType:
        """Values representing if a scale shall be displayed on the current instrument, or not."""
        Hide = 0
        Show = 1

    class _KeyListModel(QAbstractListModel):
        """Model to be used with QListView representing available keys."""
        
        def __init__(self, available_keys):
            super().__init__()
            self.available_keys = available_keys


        def data(self, index, role):            
            if role == Qt.ItemDataRole.DisplayRole:
                return self.available_keys[index.row()]
            

        def rowCount(self, index):
            return len(self.available_keys)


    class _ScaleListModel(QAbstractListModel):
        """Model to be used with QListView representing available scale intervals."""
        
        def __init__(self, available_scales):
            super().__init__()
            self.available_scales = available_scales


        def data(self, index, role):            
            if role == Qt.ItemDataRole.DisplayRole:
                return self.available_scales[index.row()]
            

        def rowCount(self, index):
            return len(SCALE_TEMPLATES)
        

    def __init__(self, current_key="C", current_scale="Natural Major") -> None:
        """
        Args:
            current_key (optional): The name of the initial key, e.g. 'C'.
            current_scale: (optional): The name of the initial scale intervals, e.g. 'Natural Major'.
        """
                
        self.current_key = current_key
        self.current_scale = current_scale
        self.show_scale = GKeyScaleModel._ShowType.Hide

        self.available_keys = listOfNoteNames(0, GToneInterval.Octave, style="flat", show_octave=False)

        self.key_index = {name: index for index, name in enumerate(self.available_keys)}
        self.available_scales = [scale.name for scale in SCALE_TEMPLATES.values()]
        self.scale_index = {name: index for index, name in enumerate(self.available_scales)}
        
        self.key_model = GKeyScaleModel._KeyListModel(self.available_keys)
        self.scale_model = GKeyScaleModel._ScaleListModel(self.available_scales)
        
        self.modelUpdated = GSignal()
        """modelUpdated(GScaleModel) is emitted when the state of the scale model is updated."""


    def showScale(self) -> bool:
        """Tests if the scale shall be indicated on the instrument, or not."""
        return self.show_scale
    

    def currentKeyValue(self) -> int:
        """Returns the note value of the current key."""
        return noteValue(self.current_key)


    def currentScale(self) -> GScale:
        """Returns the current key and scale."""
        return GScale(self.current_key, self.current_scale)
    

    def setShowScale(self, show:bool) -> None:
        """Sets if the scale shall be indicated on the instrument, or not."""
        self.show_scale = show
        self.modelUpdated.emit(self)


    def setCurrentScale(self, scale: GScale) -> None:
        """Sets the current key and scale."""
        self.setCurrentKeyName(scale.rootNoteName())
        self.setCurrentScaleName(scale.scaleName())


    def setCurrentKeyName(self, key: str) -> None:
        """Sets the current key."""

        if key not in self.available_keys:
            raise ValueError("Unkown key!")        

        old_key = self.current_key
        self.current_key = key

        if (key != old_key):
            self.modelUpdated.emit(self)
            

    def setCurrentScaleName(self, scale: str) -> None:
        """Sets the current scale."""

        if scale not in self.available_scales:
            raise ValueError("Unkown key!")        
        
        old_scale = self.current_scale
        self.current_scale = scale
        
        if (scale != old_scale):
            self.modelUpdated.emit(self)

    