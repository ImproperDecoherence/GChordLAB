"""
Module Signaling
"""

__author__ = "https://github.com/ImproperDecoherence"

class GSignal:

    def __init__(self) -> None:
        self.targets = []
        self.signals = []


    def connect(self, target):
        self.targets.append(target)


    def connectSignal(self, signal):
        self.signals.append(signal)


    def emit(self, *arg):

        for target in self.targets:
            match len(arg):
                case 0:
                    target()
                case 1:
                    target(arg[0])
                case 2:
                    target(arg[0], arg[1])

        for signal in self.signals:
            match len(arg):
                case 0:
                    signal.emit()
                case 1:
                    signal.emit(arg[0])
                case 2:
                    signal.emit(arg[0], arg[1])
            

