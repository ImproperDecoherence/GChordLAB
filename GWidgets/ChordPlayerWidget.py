"""
Module defining a simple widget wich can play a sequence of chords.
"""

__author__ = "https://github.com/ImproperDecoherence"


from GModels import GPianoModel, GPlayer
from .ChordButton import GChordButton 
from .ChordButtonPanel import GChordButtonLayout
from GUtils import GSignal

from PyQt6.QtWidgets import (QGridLayout, QGroupBox, QWidget, QPushButton, QSlider, QHBoxLayout, 
                             QLabel, QVBoxLayout)
from PyQt6.QtCore import QSize, QTimer, Qt


class GTempoWidget(QWidget):
    """Widget used to set player tempo."""

    def __init__(self, parent: QWidget=None) -> None:
        super().__init__(parent)

        self.MIN_PERIOD        =  100   # ms
        self.MAX_PERIOD        = 2000   # ms
        self.MIN_TEMPO_VALUE   =    1
        self.START_TEMPO_VALUE =  100
        self.MAX_TEMPO_VALUE   =  200

        # Period = P0 + K * Tempo
        self.K = (self.MAX_PERIOD - self.MIN_PERIOD) / (self.MIN_TEMPO_VALUE - self.MAX_TEMPO_VALUE)
        self.P0 = self.MAX_PERIOD - self.K * self.MIN_TEMPO_VALUE

        self.tempoChanged = GSignal()
        self.periodChanged = GSignal()

        layout = QHBoxLayout()
        label = QLabel("Tempo")
        layout.addWidget(label)

        self.tempo_slider = QSlider(Qt.Orientation.Horizontal)
        self.tempo_slider.setMinimum(self.MIN_TEMPO_VALUE)
        self.tempo_slider.setMaximum(self.MAX_TEMPO_VALUE)
        self.tempo_slider.setSingleStep(1)
        self.tempo_slider.setPageStep(20)
        self.tempo_slider.setTickInterval(20)
        self.tempo_slider.setValue(self.START_TEMPO_VALUE)
        self.tempo_slider.valueChanged.connect(self._tempoChanged)
        layout.addWidget(self.tempo_slider)

        self.indicator = QLabel(self._tempoValueToString(self.tempo_slider.value()))
        layout.addWidget(self.indicator)

        self.setLayout(layout)


    def currentTempo(self) -> int:
        """Returns the current tempo; an integer between MIN_TEMPO_VALUE and MAX_TEMPO_VALUE."""
        return self.tempo_slider.value()
    

    def currentPeriod(self) -> int:
        """Returns the current time period between chords in ms."""
        return int(self.P0 + self.K * self.currentTempo())
    

    def _tempoValueToString(self, value: int | float) -> str:
        """Converts the tempo value to a string for presentation."""
        return f"{value / 100 :.2f}"


    def _tempoChanged(self, tempo_value: int) -> None:
        """This method is called when the current value of the tempo slider is changed."""
        self.indicator.setText(self._tempoValueToString(tempo_value))
        self.tempoChanged.emit(tempo_value)
        self.periodChanged.emit(self.currentPeriod())



class GChordPlayerWidget(QGroupBox):
    """Simple widget wich can play a sequence of chords."""

    def __init__(self, piano_model: GPianoModel, parent: QWidget=None) -> None:
        """
        Args:
            piano_model: The piano model which is used to play the chord sequence.
        """
        super().__init__("Chord Player", parent)

        self.piano_model = piano_model
        
        self.piano_model.nextPlayStarted.connect(self._startingPlayingNext)
        self.piano_model.playEnded.connect(self._playingEnded)

        main_layout = QVBoxLayout()
        control_buttons_layout = QHBoxLayout()

        self.NUMBER_OF_CHORD_BUTTON_ROWS = 4
        self.NUMBER_OF_CHORD_BUTTON_COLUMNS = 4
        
        self.chord_panel_layout = GChordButtonLayout(self.NUMBER_OF_CHORD_BUTTON_ROWS, 
                                                    self.NUMBER_OF_CHORD_BUTTON_COLUMNS,
                                                    piano_model=self.piano_model)

        self.chord_panel_layout.chordChanged.connect(self._chordChanged)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self._playButtonClicked)
        self.play_button.setFixedWidth(GChordButton().width())
        self.play_button.setDisabled(True)
        control_buttons_layout.addWidget(self.play_button)

        self.tempo_widget = GTempoWidget()
        self.tempo_widget.periodChanged.connect(self._peroidChanged)
        control_buttons_layout.addWidget(self.tempo_widget)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._clearButtonClicked)
        self.clear_button.setFixedWidth(GChordButton().width())
        self.clear_button.setDisabled(True)
        control_buttons_layout.addWidget(self.clear_button)

        main_layout.addLayout(control_buttons_layout)
        main_layout.addLayout(self.chord_panel_layout)
        self.setLayout(main_layout)

        self.is_playing = False


    def _startingPlayingNext(self, note_values, sequence_number) -> None:
        """This method is called when the player is about to play next chord."""

        if self.is_playing:

            chord_buttons = self.chord_panel_layout.chordButtons()
            current_chord_button = chord_buttons[sequence_number]

            for b in chord_buttons:
                b.setHighlight(False)

            current_chord_button.setHighlight(True)
            if len(note_values) > 0:
                self.piano_model.setHighlightedNoteValues(note_values)


    def _playingEnded(self) -> None:
        """This method is called when the player has finished to play all chords in the sequence."""

        if self.is_playing:
            chord_buttons = self.chord_panel_layout.chordButtons()        

            for b in chord_buttons:
                b.setHighlight(False)

            self.play_button.setDisabled(False)
            self.piano_model.setHighlightedNoteValues([])

            self.is_playing = False


    def _peroidChanged(self, value: int) -> None:
        """This method is called when the value of the tempo slider has changed."""
        self.piano_model.setPlayPeriod(value)


    def _chordChanged(self, chord_button: GChordButton) -> None:
        """This method is called when a chord is updated in the chords to play panel."""
        at_least_one_chord = any([chord for chord in self.chord_panel_layout.currentChords() if chord is not None])
        self.play_button.setDisabled(not at_least_one_chord)
        self.clear_button.setDisabled(not at_least_one_chord)


    def sizeHint(self):
        """Returns the preferred size of the widget."""
        button_size = self.play_button.sizeHint()
        return QSize(self.NUMBER_OF_CHORD_BUTTON_COLUMNS * button_size.width() + 10, 
                     (self.NUMBER_OF_CHORD_BUTTON_ROWS + 1) * button_size.height() + 10)


    def _playButtonClicked(self):
        """This method is called when the Play button is pressed."""
        last_chord_index = 0
        chord_buttons = self.chord_panel_layout.chordButtons()

        for i, button in enumerate(chord_buttons):
            if button.chord is not None:
                last_chord_index = i

        chord_play_sequence = [button.chord for button in chord_buttons[:last_chord_index + 1]]

        note_values_play_sequence = []
        for chord in chord_play_sequence:
            if chord is not None:
                note_values_play_sequence.append(chord.noteValues())
            else:
                note_values_play_sequence.append([])

        if len(note_values_play_sequence) > 0:
            self.is_playing = True
            self.play_button.setDisabled(True)
            self.piano_model.play(note_values_play_sequence, arpeggio_period=self.tempo_widget.currentPeriod())            


    def _clearButtonClicked(self):
        """This method is called when the Clear button is pressed."""
        for chord_button in self.chord_panel_layout.chordButtons():
            chord_button.setChord(None)


