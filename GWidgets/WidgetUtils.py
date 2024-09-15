"""
Module containing utilities for PyQt6.
"""

__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtCore import Qt


def boolToCheckState(is_checked: bool):
    """Converts a boolean to Qt.CheckState.Checked if True, Qt.CheckState.Unchecked if False."""
    if is_checked:
        return Qt.CheckState.Checked
    else:
        return Qt.CheckState.Unchecked


def checkStateToBool(state: Qt.CheckState):
    """Converts a Qt.CheckState to True if Qt.CheckState.Checked, False if Qt.CheckState.Unchecked"""
    return (state == Qt.CheckState.Checked)