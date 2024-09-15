"""
Module defining a model of a piano keyboard.
"""


__author__ = "https://github.com/ImproperDecoherence"


from .ScaleModel import GKeyScaleModel
from .Player import GPlayer

from GUtils import GSignal, debugVariable, debugPrint
from GMusicIntervals import (GToneInterval, GScale, 
                             isDiatonicNoteValue, noteName, noteValue, rebaseNoteValues)


class GPianoKeyState:
    """Represents the state of a single piano key."""
    
    def __init__(self, key_value, key_update_event_callback) -> None:
        """
        Args:
            key_value: The note value for this piano key.
            key_update_event_callback: Reference to a function to be called
              when the state of this piano key is changed.
        """

        self.key_value = key_value
        self.sendKeyUpdateEvent = key_update_event_callback

        self.is_selected = False
        self.is_in_current_scale = True
        self.is_highlighted = False
        self.key_in_scale_name = ""


    @property
    def key_name(self) -> str:
        """Returns the note name this piano key represents."""
        return noteName(self.key_value)


    def setSelected(self, selected: bool) -> None:
        """Sets the selected state of the piano key."""
        if self.is_selected != selected:
            self.is_selected = selected
            self.sendKeyUpdateEvent(self)            


    def isSelected(self) -> bool:
        """Tests the selected state of the piano key."""
        return self.is_selected


    def setHighlighted(self, highlighted: bool) -> None:
        """Sets the highlight state of the piano key."""
        if self.is_highlighted != highlighted:
            self.is_highlighted = highlighted
            self.sendKeyUpdateEvent(self)            


    def isHighlighted(self) -> bool:
        """Tests the highlight state of the piano key."""
        return self.is_highlighted


    def toggleSelected(self) -> None:
        """Toggles the selected state of the piano key."""
        self.setSelected(not self.is_selected)


    def isBlackKey(self) -> bool:
        """Tests if the piano key is a black key."""
        return not isDiatonicNoteValue(self.key_value)
    

    def isWhiteKey(self) -> bool:
        """Tests if the piano key is a white key."""
        return isDiatonicNoteValue(self.key_value)


    def isInCurrentScale(self) -> bool:
        """Tests if the note which the piano key represents is in the current scale."""
        return self.is_in_current_scale


    def keyInScaleName(self) -> str:
        """Returns the relative scale name of the note of the piano key, e.g. '1', 'b2', '2' etc."""
        return self.key_in_scale_name


    def setCurrentScale(self, scale: GScale, show: bool):
        """Sets the scale context which the piano key belongs to.
        
        Args:
            scale: The scale.
            show: Indicates if the relative scale name of the piano key's note shall be shown."        
        """

        if (show):
            self.key_in_scale_name = scale.relativeNoteName(self.key_value)
            self.is_in_current_scale = scale.noteValueBelongsToScale(self.key_value)
        else:
            self.is_in_current_scale = True
            self.key_in_scale_name = ""            

        self.sendKeyUpdateEvent(self)
    

    def __str__(self):
        """Enables printing of GPianoKeyState."""
        return f"{self.__class__.__name__} | key number: {self.key_value} | key name: {self.key_name} | selected: {self.is_selected}"



class GPianoModel:
    """Represents a piano keyboard."""

    def __init__(self, scale_model: GKeyScaleModel = None, player: GPlayer = None) -> None:
        """
        Args:
            scale_model: Reference to a scale model which handles the current scale.
            player: Reference to player which is used for playing notes.
        """

        self.scale_model = scale_model
        self.player = player

        self.key_states: dict[int, GPianoKeyState] = dict()

        self.first_piano_key_state: GPianoKeyState = None
        """The piano key state with the lowest note."""

        self.keyStateChanged = GSignal()
        self.selectionChanged = GSignal()
        self.highlightChanged = GSignal()
        self.keyLayoutChanged = GSignal()        
        self.playEnded = GSignal()
        self.nextPlayStarted = GSignal()

        if self.player is not None:
            self.player.startingNextApeggio.connect(self._startingPlayingNext)
            self.player.arpeggioEnded.connect(self._playingEnded)

        if self.scale_model is not None:
            self.scale_model.modelUpdated.connect(self._scaleModelUpdated)        

        base_note_value = noteValue("C2")
        self._initializeKeyStates([base_note_value + i for i in range(3 * GToneInterval.Octave + 1)])


    def _initializeKeyStates(self, note_values: list[int]) -> None:
        """Resets all existing piano key states and give them the provided note values."""

        self.key_states = {value: GPianoKeyState(value, self._keyUpdateEvent) for value in note_values}

        c_keys = [key for key in self.key_states.values() if ((key.key_value % GToneInterval.Octave) == 0)]
        self.first_piano_key_state = c_keys[0]

        self.keyLayoutChanged.emit(self)
    

    def firstNoteValue(self) -> int:
        """Resurns the note value of the lowest note of the piano keybord."""
        return self.first_piano_key_state.key_value
    

    def setFirstNoteValue(self, first_value: int) -> None:
        """Transposes all piano keys in such way that the lowest piano key has the provided note value.
        
        Args:
            first_value: The note value of the lowest piano key; must be C or F.

        Raises:
            ValueError is the provided note is not C or F.
        """

        if (first_value % GToneInterval.Octave) in [noteValue("C"), noteValue("F")] :
            number_of_keys = self.numberOfPianoKeys()
            self._initializeKeyStates([first_value + i for i in range(number_of_keys)])
        else:
            raise ValueError("First note mus be C or F")


    def supportedNoteValues(self) -> list[int]:
        """Returns a list with supported note values."""
        return [key_state.key_value for key_state in self.key_states.values()]    


    def numberOfPianoKeys(self) -> int:
        """Returns the number of piano keys."""
        return len(self.key_states)
    
    
    def selectedNoteValues(self) -> list[int]:
        """Returns the note values of the piano keys which are in state Selected."""
        return [k.key_value for k in self.key_states.values() if k.isSelected()]
    

    def highlightedNoteValues(self) -> list[int]:
        """Returns the note values of the piano keys which are in state Highlighted."""
        return [k.key_value for k in self.key_states.values() if k.isHighlighted()]


    def keyStates(self) -> list[GPianoKeyState]:
        """Returns all piano key states."""
        return self.key_states.values()
    

    def whiteKeyStates(self) -> list[GPianoKeyState]:
        """Returns the states of all white piano keys."""
        return [key for key in self.keyStates() if key.isWhiteKey()]
    

    def blackKeyStates(self) -> list[GPianoKeyState]:
        """Returns the states of all black piano keys."""
        return [key for key in self.keyStates() if key.isBlackKey()]
    

    def showScale(self, scale: GScale, show: bool) -> None:
        """Updates all piano key states with information about the current scale.
        
        Args:
            scale: The current scale.
            show: Indicates if the relative scale name of the note shall be displayed.
        """
        debugVariable("scale")
        for key in self.key_states.values():
            key.setCurrentScale(scale, show)


    def setHighlightedNoteValues(self, note_values: list[int], rebase: bool = True) -> None:
        """Sets matching piano key states to state Highlighted; the Highlighted is removed from all other piano keys.
        
        Args:
            note_values: The piano keys with these note values will be highlighted.
            rebase: Indicates if the provided note values shall be rebased to be close
              to the lowest piano key of the keyboard.        
        """
        note_values_to_be_highlighted = note_values

        if rebase:
            note_values_to_be_highlighted = rebaseNoteValues(note_values, self.first_piano_key_state.key_value)
        
        for note_values in self.key_states.keys():
            self.key_states[note_values].setHighlighted(note_values in note_values_to_be_highlighted)

        self.highlightChanged.emit(self.highlightedNoteValues())


    def play(self, note_values: list[int] | list[list[int]], rebase: bool = True, highlight: bool = True,
             arpeggio_period: int = 250, arpeggio: GPlayer.ArpeggioType = GPlayer.ArpeggioType.Forward) -> None:
        """Starts to play the provided note values if a player is available.
        
        Args:
            note_values: A list of note values OR a list of lists of note values.
              The first alternative results in that a single chord is played.
              The second alternative results in that a sequence of chords are played.
            rebase: Indicates if the provided note values shall be rebased to be close
              to the lowest piano key before they are played.
            highlight: Indicates if the played notes shall be highlighted on the
              keyboard while playing.
            arpeggio_period: The time period between each played chord in ms.
              Is only applicable when the input is a list of lists of note values.
            arpeggio: The type of arpeggio to be played; default is forward.
              Is only applicable when the input is a list of lists of note values.
        """
        
        if (self.player is not None) and (len(note_values) > 0):
            notes_to_play = note_values

            debugVariable("note_values")

            if rebase:
                notes_to_play = rebaseNoteValues(note_values, self.first_piano_key_state.key_value)

            debugVariable("notes_to_play")
            debugVariable("arpeggio_period")
            
            if highlight:
                self.setHighlightedNoteValues(notes_to_play, rebase=rebase)

            self.player.play(notes_to_play, arpeggio_period, arpeggio)


    def setPlayPeriod(self, play_period: int) -> None:
        """
        Args:
            play_period: Time period between played chords in ms.
        """
        if self.player is not None:
            self.player.setArpeggioPeriod(play_period)


    def playSelectedNotes(self) -> None:
        """Play the notes of the piano keys which have the Selected state."""
        self.play(self.selectedNoteValues(), rebase=False, highlight=False)


    def toggleSelection(self, note_value: int) -> None:
        """Toggle the Selected state of the piano key with provided note value."""
        self.key_states[note_value].toggleSelected()
        self.selectionChanged.emit(self.selectedNoteValues())


    def setSelectedNoteValues(self, note_values: list[int], rebase: bool = True) -> None:
        """Sets matching piano key states to state Selected; the Selected state is removed from all other piano keys.
        
        Args:
            note_values: The piano keys with these note values will be selected.
            rebase: Indicates if the provided note values shall be rebased to be close
              to the lowest piano key of the keyboard.        
        """
        note_values_to_be_selected = note_values

        if rebase:
            note_values_to_be_selected = rebaseNoteValues(note_values, self.first_piano_key_state.key_value)
        
        for note_values in self.key_states.keys():
            self.key_states[note_values].setSelected(note_values in note_values_to_be_selected)

        self.selectionChanged.emit(self.selectedNoteValues())


    def _keyUpdateEvent(self, key_state: GPianoKeyState) -> None:
        """Is called when a piano key state has been updated."""
        self.keyStateChanged.emit(key_state)


    def _scaleModelUpdated(self, scale_model: GKeyScaleModel) -> None:
        """Is called when the scale model is updated."""
        self.showScale(scale_model.currentScale(), scale_model.showScale()) 


    def _startingPlayingNext(self, note_values, sequence_number) -> None:
        """Is called when next chord is about to be played by the player."""
        debugVariable("note_values")
        self.setHighlightedNoteValues(note_values, rebase=False)
        self.nextPlayStarted.emit(note_values, sequence_number)


    def _playingEnded(self) -> None:
        """Is called by the player when the last chord in a sequence has been played."""
        self.setHighlightedNoteValues([])
        self.playEnded.emit()

