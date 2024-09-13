"""
Module Player
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

    class ArpeggioType:        
        Forward = 1
        Backward = 2
        ForwardBackward = 3


    class Instrument:
        
        def __init__(self, path: Path):
            self.path = path

            self.effect_files = {file.stem: file for file in self.path.iterdir() if file.is_file() and file.suffix == ".wav"}

            supported_note_names = self.supportedNoteNames()
            expected_note_names = listOfNoteNames(supported_note_names[0], len(supported_note_names))
            not_matching_note_names = [(a, b) for a, b in zip(supported_note_names, expected_note_names) if (a != b)]

            if any(not_matching_note_names):
                raise ValueError(f"Missmatch in expected notes for instrument {self.name()} (given, expected): {not_matching_note_names}")
            
            print(f"Successfully loaded instrument {self.name()} supporting note interval {self.supportedNoteNameInterval()}")
                    

        def name(self) -> str:
            return self.path.name.translate(str.maketrans('_', ' '))
        

        def effectFiles(self) -> list[Path]:
            return self.effect_files
        

        def supportedNoteNames(self) -> list[str]:
            return sortNoteNames(self.effect_files.keys())
        

        def supportedNoteValues(self) -> list[int]:
            return noteNamesToNoteValues(self.supportedNoteNames())


        def supportedNoteNameInterval(self) -> tuple[str, str]:
            supporded_note_names = self.supportedNoteNames()
            return supporded_note_names[0], supporded_note_names[-1]
        

        def noteUrl(self, note_value: int) -> QUrl:
            return QUrl(f"file:{self.effect_files[noteName(note_value)]}")



    def __init__(self, instrument_library_path="res/"):

        self.instrument_library_path = Path(instrument_library_path)
        self.effects: dict[str, QSoundEffect] = dict()
        self.is_muted = False

        self.DEFAULT_VOLUME = 0.25

        loaded_instruments = [self.Instrument(dir) for dir in self.instrument_library_path.iterdir() if dir.is_dir()]
        self.instruments = {instrument.name(): instrument for instrument in loaded_instruments}
        
        if len(self.instruments) > 0:            
            self.current_instrument = loaded_instruments[0]
        else:
            self.current_instrument = None

        self.appeggioEnded = GSignal()
        self.startingNextApeggio = GSignal()
        self.instrumentChanged = GSignal()

        self.setInstrument(self.current_instrument.name())

        self.player_timer = QTimer()
        self.player_timer.setSingleShot(True)
        self.player_timer.timeout.connect(self._playerTimerTimeout)
        self.arpeggio_period = 500


    def _playerTimerTimeout(self):
        self._playNext()


    def setArpeggioPeriod(self, period: int):
        self.arpeggio_period = period


    def currentInstrumentName(self):
        return self.current_instrument.name()


    def setInstrument(self, instrument_name: str):

        old_volume = self.volume()
        
        self.effects = dict()
        self.current_instrument = self.instruments[instrument_name]

        if self.current_instrument is not None:
            for note_value in self.current_instrument.supportedNoteValues():
                self.effects[note_value] = QSoundEffect()            
                self.effects[note_value].setVolume(old_volume)
                self.effects[note_value].setSource(self.current_instrument.noteUrl(note_value))

        self.instrumentChanged.emit(self.current_instrument)


    def availableIstrumentNames(self):
        return [instrument.name() for instrument in self.instruments.values()]
    

    def supportedNoteNames(self):
        if self.current_instrument is not None:
            return self.current_instrument.supportedNoteNames()
        else:
            return []


    def volume(self):
        if len(self.effects) > 0:
            effects = list(self.effects.values())
            return effects[0].volume()
        else:
            return self.DEFAULT_VOLUME
    

    def setVolume(self, volume: float):        
        for effect in self.effects.values():
            effect.setVolume(volume)


    def play(self, note_values: list[int] | list[list[int]] = None, 
             arpeggio_period: int = 500, arpeggio: ArpeggioType = ArpeggioType.Forward):
        
        self.arpeggio_period = arpeggio_period
        self.stop()
        
        if (len(note_values) > 0) and (not self.is_muted):

            if isinstance(note_values[0], int):                
                self._playNonArpeggio(note_values)

            if isinstance(note_values[0], list):
                self._playArpeggio(note_values, arpeggio)


    def _playNonArpeggio(self, note_values=None):
        
        if not self.is_muted:
            for note_value in note_values:
                self.effects[note_value].play()


    def _playNext(self):
        try:
            note_values, index = next(self.play_iterator)
        except StopIteration:
            self.appeggioEnded.emit()            
            return

        self.startingNextApeggio.emit(note_values, index)

        if len(note_values) > 0:            
            self._playNonArpeggio(note_values)

        self.player_timer.start(self.arpeggio_period)


    def _playArpeggio(self, note_values: list[list[int]], arpeggio: ArpeggioType):
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


    def isMuted(self):
        return self.is_muted
    

    def mute(self, is_muted):
        self.is_muted = is_muted

        if self.is_muted:
            self.stop()


    def stop(self):
        for effect in self.effects.values():
            effect.stop()


