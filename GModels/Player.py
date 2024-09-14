"""
Module which contains functionallity for playing notes and chords.
"""


__author__ = "https://github.com/ImproperDecoherence"


from os import listdir
from os.path import isfile, join

from pathlib import Path

from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtMultimedia import QSoundEffect

from GUtils import GSignal
from GMusicIntervals import sortNoteNames, listOfNoteNames, noteNamesToNoteValues, noteName


class GPlayer:
    """A component which can be used to play notes and chords."""

    class ArpeggioType:
        """Defines identifiers for different ways to play arpeggio."""
        Forward = 1
        Backward = 2
        ForwardBackward = 3


    class Instrument:
        """Represents an instrument which can play a set of notes.
        
        The musical notes are defined in a set of wav-files - one for each note. The wav-files are
        expected to be located in a single folder which path is provided in the constructor. The
        name of each file is expected to be '<note name in flat style><octave>.wav', e.g. 'C0.wav, 
        'Db0.wav' etc.

        The name of the folder is used as name for the instrument.
        """
        
        def __init__(self, path: Path) -> None:
            """
            Args:
                path: Path to folder which contains the wav-files which defines the notes of the 
                  instrument. See class description for expectations on file names.

            Raises:
                ValueError if the file names do not define a continious set of correct note names.
            """
            self.path = path

            self.effect_files = {file.stem: file for file in self.path.iterdir() if file.is_file() and file.suffix == ".wav"}
            """Dictionary dict[note name, Path] containing the path to the sound files defining the notes."""

            supported_note_names = self.supportedNoteNames()
            expected_note_names = listOfNoteNames(supported_note_names[0], len(supported_note_names))
            not_matching_note_names = [(a, b) for a, b in zip(supported_note_names, expected_note_names) if (a != b)]

            if any(not_matching_note_names):
                raise ValueError(f"Missmatch in expected notes for instrument {self.name()} (given, expected): {not_matching_note_names}")
            
            print(f"Successfully loaded instrument {self.name()} supporting note interval {self.supportedNoteNameInterval()}")
                    

        def name(self) -> str:
            """Returns the name of the instrument."""
            return self.path.name.translate(str.maketrans('_', ' '))
        

        def effectFiles(self) -> list[Path]:
            """Returns a list with paths to each wav-file that defines the notes."""
            return self.effect_files
        

        def supportedNoteNames(self) -> list[str]:
            """Returns a list with the note names which are supported by the instrument."""
            return sortNoteNames(self.effect_files.keys())
        

        def supportedNoteValues(self) -> list[int]:
            """Returns a list with the note values which are supported by the instrument."""
            return noteNamesToNoteValues(self.supportedNoteNames())


        def supportedNoteNameInterval(self) -> tuple[str, str]:
            """Returns a tuple with the names of the first supported note and the last supported note."""
            supporded_note_names = self.supportedNoteNames()
            return supporded_note_names[0], supporded_note_names[-1]
        

        def noteUrl(self, note_value: int) -> QUrl:
            """Returns the URL to the sound file which represents a given note value."""
            return QUrl(f"file:{self.effect_files[noteName(note_value)]}")



    def __init__(self, instrument_library_path="res/") -> None:
        """
        Args:
            instrument_library_path: The relative path to the folder which contains the sound
            files for the different instruments.
        """

        self.instrument_library_path = Path(instrument_library_path)        
        self.is_muted = False

        self.effects: dict[str, QSoundEffect] = dict()
        """Mapping between note names and the objects which represent the sound file of the note."""

        self.DEFAULT_VOLUME = 0.25

        loaded_instruments = [self.Instrument(dir) for dir in self.instrument_library_path.iterdir() if dir.is_dir()]
        self.instruments = {instrument.name(): instrument for instrument in loaded_instruments}
        
        if len(self.instruments) > 0:            
            self.current_instrument = loaded_instruments[0]
        else:
            self.current_instrument = None

        self.arpeggioEnded = GSignal()
        """This signal is emitted without parameter when the playing of an arpeggio has ended."""
        self.startingNextApeggio = GSignal()
        """startingNextApeggio(list[note values to be played]) is emitted when playing of an arpeggio is about to start."""
        self.instrumentChanged = GSignal()
        """instrumentChanged(Instrument) is emitted when the current instrument has changed."""

        self.setInstrument(self.current_instrument.name())

        self.player_timer = QTimer()
        """This timer is used when the notes to be played are spread out in time (arpeggio)."""
        self.player_timer.setSingleShot(True)
        self.player_timer.timeout.connect(self._playerTimerTimeout)
        self.arpeggio_period = 500


    def setArpeggioPeriod(self, period: int) -> None:
        """Sets the period time for playing arpeggio.

        Args:
            period: Time between the notes in ms.
        """

        self.arpeggio_period = period


    def currentInstrumentName(self) -> str:
        """Returns the name of the current instrument."""
        return self.current_instrument.name()


    def setInstrument(self, instrument_name: str) -> None:
        """Sets the instument to be used for playing notes."""

        old_volume = self.volume()
        
        self.effects = dict()
        self.current_instrument = self.instruments[instrument_name]

        if self.current_instrument is not None:
            for note_value in self.current_instrument.supportedNoteValues():
                self.effects[note_value] = QSoundEffect()            
                self.effects[note_value].setVolume(old_volume)
                self.effects[note_value].setSource(self.current_instrument.noteUrl(note_value))

        self.instrumentChanged.emit(self.current_instrument)


    def availableIstrumentNames(self) -> list[str]:
        """Returns a list of names for available instruments."""
        return [instrument.name() for instrument in self.instruments.values()]
    

    def supportedNoteNames(self) -> list[str]:
        """Returns a list with note names which are supported by the current instrument."""

        if self.current_instrument is not None:
            return self.current_instrument.supportedNoteNames()
        else:
            return []


    def volume(self) -> float:
        """Returns the current sound volume which is a value between 0.0 and 1.0."""

        if len(self.effects) > 0:
            effects = list(self.effects.values())
            return effects[0].volume()
        else:
            return self.DEFAULT_VOLUME
    

    def setVolume(self, volume: float):
        """Sets the current sound volume.
        
        Args:
            volume: A value between 0.0 and 1.0.
        """

        for effect in self.effects.values():
            effect.setVolume(volume)


    def play(self, note_values: list[int] | list[list[int]] = None, 
             arpeggio_period: int = 500, arpeggio: ArpeggioType = ArpeggioType.Forward) -> None:
        """Starts to play the provided note values.

        Any ongoing playing is immediately halted.
        
        Args:
            note_values: A list of note values OR a list of lists of note values.
              The first alternative results in that a single chord is played.
              The second alternative results in that a sequence of chords are played.
            arpeggio_period: The time period between each played chord in ms.
              Is only applicable when the input is a list of lists of note values.
            arpeggio: The type of arpeggio to be played; default is forward.
              Is only applicable when the input is a list of lists of note values.
        """
        
        self.arpeggio_period = arpeggio_period
        self.stop()
        
        if (len(note_values) > 0) and (not self.is_muted):

            if isinstance(note_values[0], int):                
                self._playNonArpeggio(note_values)

            if isinstance(note_values[0], list):
                self._playArpeggio(note_values, arpeggio)


    def _playNonArpeggio(self, note_values=None) -> None:
        """Immediately plays the provided note values."""
        
        if not self.is_muted:
            for note_value in note_values:
                self.effects[note_value].play()


    def _playerTimerTimeout(self) -> None:
        """This method is called at timeout of the arpeggio timer."""
        self._playNext()


    def _playNext(self) -> None:
        """Plays next chord in a sequence and invokes the timer for playing next chord."""

        try:
            note_values, index = next(self.play_iterator)
        except StopIteration:
            self.arpeggioEnded.emit()            
            return

        self.startingNextApeggio.emit(note_values, index)

        if len(note_values) > 0:            
            self._playNonArpeggio(note_values)

        self.player_timer.start(self.arpeggio_period)


    def _playArpeggio(self, note_values: list[list[int]], arpeggio: ArpeggioType) -> None:
        """Initiates the playing of a sequence of chords."""

        self.arpeggio_sequence = [(values, i) for i, values in enumerate(note_values)]

        match arpeggio:
            case GPlayer.ArpeggioType.Forward:
                pass
            case GPlayer.ArpeggioType.Backward:
                self.arpeggio_sequence = list(reversed(self.arpeggio_sequence))
            case GPlayer.ArpeggioType.ForwardBackward:                
                self.arpeggio_sequence = self.arpeggio_sequence[:-1] + list(reversed(self.arpeggio_sequence))

        self.play_iterator = iter(self.arpeggio_sequence)
        self._playNext()


    def isMuted(self) -> bool:
        """Tests if the player is muted."""
        return self.is_muted
    

    def mute(self, is_muted) -> None:
        """Sets if the player is muted or not.
        
        If is_muted is True, any ongoing playing is immediately muted.
        """
        self.is_muted = is_muted

        if self.is_muted:
            self.stop()


    def stop(self):
        """Immediately halts any ongoing playing."""
        for effect in self.effects.values():
            effect.stop()


