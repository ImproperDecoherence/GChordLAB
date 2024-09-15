"""
Module defineing a widget to be used for visualizing note intervals.
"""

__author__ = "https://github.com/ImproperDecoherence"


import math

from collections import deque
from itertools import combinations

from GModels import GPianoModel, GPianoKeyState, GKeyScaleModel
from GMusicIntervals import (GToneInterval, GScale,
                             INTERVAL_SHORT_NAMES, listOfNoteNames)

from PyQt6.QtWidgets import QWidget, QGroupBox, QApplication, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, QRectF, QSize
from PyQt6.QtGui import QColor, QPainter, QPen, QFont, QPaintEvent



def polarToPoint(center: QPoint, radius: float, angle: float) -> QPoint:
        """Converts polar coordinates to cartesian coordinates.
        
        Args:
            center: The center point in cartesian coordinates.
            radius: The radius from the center point.
            angle: The angle in radians.
        """
        return QPointF(center.x() + radius * math.sin(angle), center.y() - radius * math.cos(angle))


class GIntervalCircleWidget(QWidget):
    """This widget crates a visual intrepretation of the selected and highlighted note intevals in the piano model."""

    def __init__(self, piano_model: GPianoModel, scale_model: GKeyScaleModel, style="flat", parent=None):
        """
        Args:
            piano_model: The piano model which state shall be visualized.
            scale_model: The scale model provides the current key.
            style (optional): 'sharp' or 'flat'; the style for writing non-diatonic note names.
            parent (optional): Parent widget.
        """
        super().__init__(parent)

        self.piano_model = piano_model
        self.piano_model.keyStateChanged.connect(self._pianoModelUpdated)

        self.scale_model = scale_model
        self.scale_model.modelUpdated.connect(self._scaleModelUpdated)

        self.style = style
        self.note_names = listOfNoteNames(0, GToneInterval.Octave, self.style, show_octave=False)

        interval_angle = 2 * math.pi / GToneInterval.Octave
        self.interval_angles = [i * interval_angle for i in range(GToneInterval.Octave)]

        max_distance = GToneInterval.Diminished5th
        self.distance_colors = {d + 1: QColor.fromHslF(d / max_distance, 1.0, 0.4) for d in range(max_distance)}

        self.interval_short_names = [f"{INTERVAL_SHORT_NAMES[i]} / {INTERVAL_SHORT_NAMES[GToneInterval.Octave - i]}" for i in range(GToneInterval.Diminished5th)]
        self.interval_short_names.append(INTERVAL_SHORT_NAMES[GToneInterval.Diminished5th])

        self.shown_intervals = set()

        self._scaleModelUpdated(self.scale_model)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)


    def sizeHint(self):
        """Returns the preferred size of the widget."""
        return QSize(800, 600)
    

    def minimumSizeHint(self) -> QSize:
        """Returns the minimum size of the widget."""
        return QSize(400, 300)


    def _paintBackground(self, painter: QPainter):
        """Paints the background of the widget."""
        painter.fillRect(QRect(0, 0, painter.device().width(), painter.device().height()), QColor('white'))


    def _paintCircle(self, painter: QPainter, circle_area: QRectF):
        """Paints the circle around the intervals, including note names and note position marks."""
        
        # Rotate the note names to put the root note at the top of the circle
        current_scale = self.scale_model.currentScale()
        current_root = current_scale.rootNoteName(self.style)
        index = self.note_names.index(current_root)
        queue = deque(self.note_names)
        queue.rotate(-index)
        note_names_to_draw = list(queue)

        pen = QPen(QColor("black"))
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setWidth(6)
        painter.setPen(pen)

        painter.drawEllipse(circle_area)

        interval_mark_length = circle_area.width() * 0.02
        interval_name_margin = circle_area.width() * 0.06
        circle_center = circle_area.center()
        circle_radius = circle_area.width() / 2
    
        for angle in self.interval_angles:
            mark_start = polarToPoint(circle_center, circle_radius - interval_mark_length / 2, angle)
            mark_stop = polarToPoint(circle_center, circle_radius + interval_mark_length / 2, angle)
            painter.drawLine(mark_start, mark_stop)

        base_font_size = int(circle_area.width() * 0.04)
        font_name = "Arial"
        
        for angle, note in zip(self.interval_angles, note_names_to_draw):
            text_center_point = polarToPoint(circle_center, circle_radius + interval_name_margin, angle)
            text_rect_side = 2 * interval_name_margin
            text_rect = QRectF(text_center_point.x() - text_rect_side / 2, text_center_point.y() - text_rect_side / 2, text_rect_side, text_rect_side)

            if current_scale.noteNameBelongsToScale(note):
                font_size = base_font_size + 5
                pen.setColor(QColor("black"))
            else:
                font_size = base_font_size
                pen.setColor(QColor("darkGray"))

            painter.setFont(QFont(font_name, font_size))            
            painter.setPen(pen)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, note)


    def _paintIntervals(self, painter: QPainter, circle_area: QRectF):
        """Paints the interval lines."""

        selected_intervals = self.piano_model.selectedNoteValues()
        highlighted_intervals = self.piano_model.highlightedNoteValues()

        if len(highlighted_intervals) > 0:
            intervals = highlighted_intervals
        else:
            intervals = selected_intervals

        root_note_value = self.scale_model.currentKeyValue()
        normalized_intervals = [(GToneInterval.Octave + i - root_note_value) % GToneInterval.Octave for i in intervals]
        self.shown_intervals = set()
        root_note_in_seleced_intervals = (0 in normalized_intervals)

        if not root_note_in_seleced_intervals:
            normalized_intervals.insert(0, 0)

        if len(normalized_intervals) >= 2:
            
            possible_normalized_pairs = list(combinations(normalized_intervals, 2))
        
            circle_center = circle_area.center()
            circle_radius = circle_area.width() / 2
            angle_pairs = [(self.interval_angles[a], self.interval_angles[b]) for a, b in possible_normalized_pairs]
            point_pairs = [(polarToPoint(circle_center, circle_radius, v), polarToPoint(circle_center, circle_radius, w)) for v, w in angle_pairs]

            clockwise_distances = [min((b - a) % GToneInterval.Octave, (a - b) % GToneInterval.Octave) for a, b in possible_normalized_pairs]
            counter_clockwise_distances = [GToneInterval.Octave - d for d in clockwise_distances]
            shortest_distances = [min(cd, ccd) for cd, ccd in zip(clockwise_distances, counter_clockwise_distances)]
            non_zero_distances = [d for d in shortest_distances if d > 0]

            pen = QPen()            

            for (p1, p2), d, (a, b) in zip(point_pairs, non_zero_distances, possible_normalized_pairs):
                self.shown_intervals.add(d)

                pen.setColor(self.distance_colors[d])
                if not root_note_in_seleced_intervals and (0 in {a, b}):
                    pen.setStyle(Qt.PenStyle.DotLine)
                    pen.setWidth(4)
                else:
                    pen.setStyle(Qt.PenStyle.SolidLine)
                    pen.setWidth(8)

                painter.setPen(pen)
                painter.drawLine(p1, p2)


    def _paintLegend(self, painter: QPainter, widget_area: QRectF):
        """Paints the color ledgend of the widget."""

        legend_row_height = widget_area.height() * 0.05
        legend_row_width = legend_row_height * 4
        legend_row_space = widget_area.height() * 0.02
        legend_row_offset = widget_area.width() * 0.03

        legend_row_rect = QRectF(widget_area.x() + legend_row_offset, widget_area.y() + legend_row_offset, legend_row_width, legend_row_height)

        pen = QPen()
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setColor(QColor("white"))
        painter.setFont(QFont("Arial", int(legend_row_height * 0.5)))

        for d in list(self.shown_intervals):
            painter.setPen(pen)
            painter.fillRect(legend_row_rect, self.distance_colors[d])
            painter.drawText(legend_row_rect, Qt.AlignmentFlag.AlignCenter, self.interval_short_names[d])

            legend_row_rect.moveTo(legend_row_rect.topLeft().x(), legend_row_rect.topLeft().y() + (legend_row_space + legend_row_height))


    def paintEvent(self, event: QPaintEvent):
        """This method is called by the framework when the widget needs to be re-painted."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._paintBackground(painter)

        dw = painter.device().width()
        dh = painter.device().height()

        widget_area = QRectF(0, 0, dw, dh)

        if dw > dh:
            x_inset = (dw - dh) / 2
            draw_area = widget_area.adjusted(x_inset, 0, -x_inset, 0)
        else:
            y_inset = (dh - dw) / 2
            draw_area = widget_area.adjusted(0, y_inset, 0, -y_inset)

        circle_margin = draw_area.width() * 0.1
        circle_area = draw_area.adjusted(circle_margin, circle_margin, -circle_margin, -circle_margin)

        self._paintIntervals(painter, circle_area)
        self._paintCircle(painter, circle_area)
        self._paintLegend(painter, widget_area)


    def _pianoModelUpdated(self, key_state: GPianoKeyState):
        """Triggers a re-paint of this widget when a piano key state has changed."""
        self.update()


    def _scaleModelUpdated(self, model: GKeyScaleModel):
        """Triggers a re-paint of this widget when a the current key has changed."""
        self.update()


class GIntervalCircleBox(QGroupBox):
    """A group box which contains a GIntervalCircleWidget."""

    def __init__(self, piano_model: GPianoModel, scale_model: GKeyScaleModel, style="flat", parent=None):
        """
        Args:
            piano_model: The piano model which state shall be visualized.
            scale_model: The scale model provides the current key.
            style (optional): 'sharp' or 'flat'; the style for writing non-diatonic note names.
            parent (optional): Parent widget.
        """
        super().__init__("Interval Circle", parent)

        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        layout = QGridLayout(self)
        self.circle_widget = GIntervalCircleWidget(piano_model, scale_model, style)
        layout.addWidget(self.circle_widget, 0, 0)
        self.setLayout(layout)


    def sizeHint(self):
        """Returns the preferred size of the widget."""
        return self.circle_widget.sizeHint()


def unitTest():

    app = QApplication([])
    piano_model = GPianoModel(number_of_octaves=3)
    scale_model = GKeyScaleModel()

    scale_model.setCurrentKeyScale("D", "Natural Major")

    piano_widget = GIntervalCircleBox(piano_model, scale_model, "sharp")
    piano_widget.resize(400, 400)
    piano_widget.show()
    app.exec()



if __name__ == "__main__":
    unitTest()