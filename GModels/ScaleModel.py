"""
Module ScaleModel
"""


__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtCore import Qt, QAbstractListModel

from GUtils import GSignal
from GMusicIntervals import GScale, GToneInterval, SCALE_TEMPLATES, noteValue, listOfNoteNames


class GKeyScaleModel:

    class _ShowType:
        Hide = 0
        Show = 1

    class _KeyListModel(QAbstractListModel):
        
        def __init__(self, available_keys):
            super().__init__()
            self.available_keys = available_keys

        def data(self, index, role):            
            if role == Qt.ItemDataRole.DisplayRole:
                return self.available_keys[index.row()]
            
        def rowCount(self, index):
            return len(self.available_keys)


    class _ScaleListModel(QAbstractListModel):
        
        def __init__(self, available_scales):
            super().__init__()
            self.available_scales = available_scales

        def data(self, index, role):            
            if role == Qt.ItemDataRole.DisplayRole:
                return self.available_scales[index.row()]
            
        def rowCount(self, index):
            return len(SCALE_TEMPLATES)
        

    def __init__(self, current_key="C", current_scale="Natural Major"):
                
        self.current_key = current_key
        self.current_scale = current_scale
        self.show_scale = GKeyScaleModel._ShowType.Hide

        self.available_keys = listOfNoteNames(0, GToneInterval.Octave, style="flat", show_octave=False)

        self.key_index = {name: index for index, name in enumerate(self.available_keys)}
        self.available_scales = [scale.name for scale in SCALE_TEMPLATES.values()]
        self.scale_index = {name: index for index, name in enumerate(self.available_scales)}
        
        self.key_model = GKeyScaleModel._KeyListModel(self.available_keys)
        self.scale_model = GKeyScaleModel._ScaleListModel(self.available_scales)

        self.currentKeyUpdated = GSignal()
        self.currentScaleUpdated = GSignal()
        self.modelUpdated = GSignal()        


    def showScale(self):
        return self.show_scale
    

    def currentKeyValue(self):
        return noteValue(self.current_key)


    def currentScale(self):
        return GScale(self.current_key, self.current_scale)
    

    def currentKeyChanged(self, key_name):
        self.current_key = key_name        
        self.modelUpdated.emit(self)


    def currentScaleChanged(self, scale_name):
        self.current_scale = scale_name        
        self.modelUpdated.emit(self)


    def setShowScale(self, show:bool):
        self.show_scale = show
        self.modelUpdated.emit(self)


    def setCurrentScale(self, scale: GScale):        
        self.setCurrentKeyScale(scale.rootNoteName(), scale.scaleName())


    def setCurrentKeyScale(self, key: str, scale: str):
        if (key not in self.available_keys) or (scale not in self.available_scales):
            raise ValueError("Unkown key or scale!")        

        old_key = self.current_key
        old_scale = self.current_scale

        self.current_key = key
        self.current_scale = scale

        if (key != old_key):
            self.currentKeyUpdated.emit(self.key_index[key])

        if (scale != old_scale):
            self.currentScaleUpdated.emit(self.scale_index[scale])
        