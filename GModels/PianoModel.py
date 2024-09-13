"""
Module GPianoModel
"""


__author__ = "https://github.com/ImproperDecoherence"


from .ScaleModel import GKeyScaleModel
from .Player import GPlayer

from GUtils import GSignal, debugVariable, debugPrint
from GMusicIntervals import (GToneInterval, GScale, 
                             isDiatonicNoteValue, noteName, noteValue, rebaseNoteValues)


class GPianoKeyState:
    
    def __init__(self, key_value, key_update_event_callback):        
        self.key_value = key_value
        self.sendKeyUpdateEvent = key_update_event_callback

        self.is_selected = False
        self.is_in_current_scale = True
        self.is_highlighted = False
        self.key_in_scale_name = ""


    @property
    def key_name(self):
        return noteName(self.key_value)


    def setSelected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self.sendKeyUpdateEvent(self)            


    def isSelected(self) -> bool:
        return self.is_selected


    def setHighlighted(self, highlighted: bool):
        if self.is_highlighted != highlighted:
            self.is_highlighted = highlighted
            self.sendKeyUpdateEvent(self)            


    def isHighlighted(self) -> bool:
        return self.is_highlighted


    def toggleSelected(self) -> bool:
        self.setSelected(not self.is_selected)


    def isBlackKey(self):
        return not isDiatonicNoteValue(self.key_value)
    

    def isWhiteKey(self):
        return isDiatonicNoteValue(self.key_value)


    def isInCurrentScale(self) -> bool:
        return self.is_in_current_scale


    def setCurrentScale(self, scale: GScale, show: bool, base_value: int):        

        if (show):
            self.key_in_scale_name = scale.relativeNoteName(self.key_value, base_value)
            self.is_in_current_scale = scale.noteValueBelongsToScale(self.key_value)
        else:
            self.is_in_current_scale = True
            self.key_in_scale_name = ""            

        self.sendKeyUpdateEvent(self)
    

    def __str__(self):
        return f"{self.__class__.__name__} | key number: {self.key_value} | key name: {self.key_name} | selected: {self.is_selected}"



class GPianoModel:

    def __init__(self, scale_model: GKeyScaleModel = None, player: GPlayer = None):
        self.scale_model = scale_model
        self.player = player

        self.key_states: dict[int, GPianoKeyState] = dict()
        self.base_key: GPianoKeyState = None
        self.cog_key: GPianoKeyState = None

        self.keyStateChanged = GSignal()
        self.selectionChanged = GSignal()
        self.highlightChanged = GSignal()
        self.keyLayoutChanged = GSignal()
        self.cogChanged = GSignal()
        self.playEnded = GSignal()
        self.nextPlayStarted = GSignal()

        self.player.startingNextApeggio.connect(self._startingPlayingNext)
        self.player.appeggioEnded.connect(self._playingEnded)

        if self.scale_model is not None:
            self.scale_model.modelUpdated.connect(self._scaleModelUpdated)        

        base_note_value = noteValue("C2")
        self.setNoteValues([base_note_value + i for i in range(3 * GToneInterval.Octave + 1)])
        self._updateCoG()


    def _scaleModelUpdated(self, scale_model: GKeyScaleModel):
        self.showScale(scale_model.currentScale(), scale_model.showScale())
        self._updateCoG()


    def _updateCoG(self):
        if self.scale_model is not None:            
            current_scale = self.scale_model.currentScale()
            scale_root_key_note_values = [key.key_value for key in self.key_states.values() if current_scale.noteValueBelongsToScale(key.key_value)]
            self.cog_key = self.key_states[scale_root_key_note_values[0] + GToneInterval.Major3rd]
            self.cogChanged.emit(self)


    def setNoteValues(self, note_values: list[int]):
        self.key_states = {value: GPianoKeyState(value, self.keyUpdateEvent) for value in note_values}

        c_keys = [key for key in self.key_states.values() if ((key.key_value % GToneInterval.Octave) == 0)]
        self.base_key = c_keys[0]

        self._updateCoG()

        self.keyLayoutChanged.emit(self)
    

    def baseNoteValue(self) -> int:
        return self.base_key.key_value
    

    def cogNoteValue(self) -> int:
        return self.cog_key.key_value


    def setFirstNoteValue(self, first_value: int):                

        if (first_value % GToneInterval.Octave) in [noteValue("C"), noteValue("F")] :
            number_of_keys = self.numberOfKeys()
            self.setNoteValues([first_value + i for i in range(number_of_keys)])
        else:
            raise ValueError("First note mus be C or F")


    def supportedNoteValues(self):
        return [key_state.key_value for key_state in self.key_states.values()]


    def keyUpdateEvent(self, key_state: GPianoKeyState):
        self.keyStateChanged.emit(key_state)


    def numberOfKeys(self):
        return len(self.key_states)
    
    
    def selectedNoteValues(self):
        return [k.key_value for k in self.key_states.values() if k.isSelected()]
    

    def highlightedNoteValues(self):
        return [k.key_value for k in self.key_states.values() if k.isHighlighted()]


    def numberOfSelectedNotes(self):
        return len([k.key_value for k in self.key_states.values() if k.isSelected()])


    def keyStates(self) -> list[GPianoKeyState]:
        return self.key_states.values()
    

    def keyState(self, note_value: int) -> GPianoKeyState:
        return self.key_states[note_value]


    def whiteKeyStates(self) -> list[GPianoKeyState]:
        return [key for key in self.keyStates() if key.isWhiteKey()]
    

    def blackKeyStates(self) -> list[GPianoKeyState]:
        return [key for key in self.keyStates() if key.isBlackKey()]
    

    def showScale(self, scale: GScale, show: bool):
        debugVariable("scale")
        for key in self.key_states.values():
            key.setCurrentScale(scale, show, self.base_key.key_value)


    def setHighlightedNoteValues(self, note_values: list[int], rebase: bool = True):

        note_values_to_be_highlighted = note_values
        if rebase:
            note_values_to_be_highlighted = rebaseNoteValues(note_values, self.base_key.key_value)
        
        for note_values in self.key_states.keys():
            self.key_states[note_values].setHighlighted(note_values in note_values_to_be_highlighted)

        self.highlightChanged.emit(self.highlightedNoteValues())


    def play(self, note_values: list[int] | list[list[int]], rebase: bool = True, highlight: bool = True,
             arpeggio_period: int = 250, arpeggio: GPlayer.ArpeggioType = GPlayer.ArpeggioType.Forward):
        
        if (self.player is not None) and (len(note_values) > 0):
            notes_to_play = note_values

            debugVariable("note_values")

            if rebase:
                notes_to_play = rebaseNoteValues(note_values, self.base_key.key_value)

            debugVariable("notes_to_play")
            debugVariable("arpeggio_period")
            
            if highlight:
                self.setHighlightedNoteValues(notes_to_play, rebase=rebase)

            self.player.play(notes_to_play, arpeggio_period, arpeggio)


    def _startingPlayingNext(self, note_values, sequence_number):
        debugVariable("note_values")
        self.setHighlightedNoteValues(note_values, rebase=False)
        self.nextPlayStarted.emit(note_values, sequence_number)


    def _playingEnded(self):
        self.setHighlightedNoteValues([])
        self.playEnded.emit()


    def changePlayPeriod(self, play_period: int):
        if self.player is not None:
            self.player.setArpeggioPeriod(play_period)


    def playSelectedNotes(self):
        self.play(self.selectedNoteValues(), rebase=False, highlight=False)


    def toggleSelection(self, note_value: int):
        self.key_states[note_value].toggleSelected()
        self.selectionChanged.emit(self.selectedNoteValues())


    def setSelectedNoteValues(self, note_values: list[int], rebase: bool = True):
        note_values_to_be_selected = note_values

        if rebase:
            note_values_to_be_selected = rebaseNoteValues(note_values, self.base_key.key_value)
        
        for note_values in self.key_states.keys():
            self.key_states[note_values].setSelected(note_values in note_values_to_be_selected)

        self.selectionChanged.emit(self.selectedNoteValues())


