"""
This module defines tools which can be used to add signaling between different components.
"""

__author__ = "https://github.com/ImproperDecoherence"

class GSignal:
    """A generic class for signaling between components.

    Example:
        Component A:
            self.nameChanged = GSignal()
            self.nameChanged.emit(name)

        Component B:
            A.nameChanged.connect(B._nameChanged)
            def _nameChanged(new_name):
                print(new_name)

    """

    def __init__(self) -> None:
        """Creates a signal without connections."""

        self.targets = []
        self.signals = []


    def connect(self, target) -> None:
        """Connects a function or a class method to the signal.
        
        Each connected function/method will receive a call from
        this signal when 'emit' of this signal is invoked.

        Args:
            target: Reference to function/method. The connected
              function/method must have the same parameters as
              the corresponding 'emit' call.
        
        """

        self.targets.append(target)


    def connectSignal(self, signal:'GSignal') -> None:
        """Chains the signal to another signal.

        Each connected signal will receive an 'emit' call when
        'emit' is invoked for this signal.

        Args:
            signal: Reference to GSignal.
        """

        self.signals.append(signal)


    def emit(self, *arg) -> None:
        """Inovcation of this method will invoke all connected functions/methods
        and signals and pass the provided arguments:

        Args:
            arg: The arguments can be of any type as long as they matches
              the connected functions/methods. 0, 1 or 2 arguments are supported.
        """

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
            

