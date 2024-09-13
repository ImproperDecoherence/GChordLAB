"""
Module WidgetUtils
"""

__author__ = "https://github.com/ImproperDecoherence"


from PyQt6.QtCore import Qt


def boolToCheckState(is_checked: bool):
    if is_checked:
        return Qt.CheckState.Checked
    else:
        return Qt.CheckState.Unchecked


def checkStateToBool(state: Qt.CheckState):
    return (state == Qt.CheckState.Checked)