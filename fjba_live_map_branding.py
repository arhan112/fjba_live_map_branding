
# -*- coding: utf-8 -*-
"""
FjBa LIVE MAP BRANDING
AURORA VORTEX — CHRONO EDITION V2.1

QGIS 3.28.4 | Python 3.9 | PyQt5

Visual themes:
- Emerald Aurora
- Obsidian Gold
- Arctic Pulse
- Violet Nebula

Features:
- Animated Aurora Vortex clock
- Five-second milestone numbers: 5, 10, 15 ... 55, 60
- Continuous active milestone pulse for the complete five-second interval
- Expanding transition ring at every milestone change
- Triangular hour, minute and second hands
- Three synchronized structural triangles
- Mechanical stepping second triangle
- Four synchronized infinity particles
- Golden ratio spiral and golden-angle particles
- Purpose-driven five-second particle stream toward the next milestone
- Five-second progress arc and countdown beacon
- Milestone lock pulse with directional particle handoff
- Minute-boundary energy burst and centre convergence
- PNG/JPG logo support
- Four-corner positioning, drag and snap
- Adjustable size, opacity and margin
- Persistent QGIS settings
- Canvas event filter and cleanup

Compatible with QGIS 3.28.4, Python 3.9 and PyQt5.
"""

import os
import math
import time
import traceback

from qgis.PyQt.QtCore import (
    QObject, Qt, QTimer, QPoint, QPointF, QRect, QRectF,
    QSettings, QEvent, QSize
)

from qgis.PyQt.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont,
    QLinearGradient, QRadialGradient, QPainterPath,
    QPixmap, QPolygonF
)

from qgis.PyQt.QtWidgets import (
    QAction, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSlider, QCheckBox,
    QFileDialog, QSpinBox, QMessageBox, QFrame, QFormLayout
)

from qgis.core import QgsMessageLog, Qgis


# ============================================================
# CONSTANTS AND THEMES
# ============================================================

PLUGIN_NAME = "FjBa Live Map Branding"
SETTINGS_PREFIX = "FjBa/LiveMapBranding/"

POSITIONS = [
    "Top right",
    "Top left",
    "Bottom right",
    "Bottom left"
]

THEME_NAMES = [
    "Emerald Aurora",
    "Obsidian Gold",
    "Arctic Pulse",
    "Violet Nebula"
]

THEMES = {
    "Emerald Aurora": {
        "background": (8, 62, 48),
        "background_mid": (4, 34, 32),
        "background_edge": (1, 12, 18),
        "glow": (20, 255, 180),
        "ring": (50, 255, 190),
        "gold": (255, 205, 105),
        "bright": (255, 232, 165),
        "magenta": (255, 65, 190),
        "cyan": (65, 225, 255),
        "emerald": (45, 245, 185),
        "panel": (5, 54, 43),
        "panel_mid": (3, 30, 30),
        "panel_edge": (2, 15, 23),
        "panel_glow": (30, 255, 185),
        "border": (65, 235, 180),
        "title": (240, 255, 248),
        "subtitle": (90, 245, 195),
        "footer": (185, 225, 213),
        "status": (35, 255, 175),
        "accent": (255, 220, 150)
    },

    "Obsidian Gold": {
        "background": (48, 37, 24),
        "background_mid": (24, 22, 22),
        "background_edge": (8, 10, 15),
        "glow": (255, 190, 85),
        "ring": (255, 195, 95),
        "gold": (235, 174, 82),
        "bright": (255, 226, 165),
        "magenta": (222, 125, 115),
        "cyan": (105, 205, 190),
        "emerald": (105, 190, 155),
        "panel": (35, 29, 23),
        "panel_mid": (22, 22, 23),
        "panel_edge": (9, 11, 16),
        "panel_glow": (255, 190, 85),
        "border": (215, 165, 90),
        "title": (255, 245, 225),
        "subtitle": (235, 190, 115),
        "footer": (205, 190, 165),
        "status": (225, 185, 105),
        "accent": (255, 220, 165)
    },

    "Arctic Pulse": {
        "background": (18, 51, 79),
        "background_mid": (9, 30, 55),
        "background_edge": (4, 12, 27),
        "glow": (65, 210, 255),
        "ring": (100, 220, 255),
        "gold": (165, 220, 255),
        "bright": (230, 250, 255),
        "magenta": (135, 155, 255),
        "cyan": (65, 225, 255),
        "emerald": (105, 245, 225),
        "panel": (13, 42, 68),
        "panel_mid": (8, 25, 48),
        "panel_edge": (3, 13, 29),
        "panel_glow": (65, 210, 255),
        "border": (85, 205, 255),
        "title": (235, 250, 255),
        "subtitle": (115, 220, 255),
        "footer": (185, 220, 240),
        "status": (90, 230, 255),
        "accent": (180, 235, 255)
    },

    "Violet Nebula": {
        "background": (49, 25, 83),
        "background_mid": (27, 17, 54),
        "background_edge": (10, 8, 27),
        "glow": (180, 90, 255),
        "ring": (195, 110, 255),
        "gold": (255, 190, 135),
        "bright": (255, 225, 205),
        "magenta": (255, 90, 220),
        "cyan": (95, 220, 255),
        "emerald": (125, 245, 210),
        "panel": (43, 23, 70),
        "panel_mid": (25, 15, 48),
        "panel_edge": (10, 8, 27),
        "panel_glow": (180, 90, 255),
        "border": (175, 105, 245),
        "title": (250, 240, 255),
        "subtitle": (220, 155, 255),
        "footer": (205, 190, 230),
        "status": (225, 125, 255),
        "accent": (255, 190, 220)
    }
}

DEFAULTS = {
    "enabled": True,
    "position": "Top right",
    "width": 410,
    "opacity": 94,
    "margin": 14,
    "clock_enabled": True,
    "logo_path": "",
    "title": "FjBa",
    "subtitle": "LIVE MAP BRANDING",
    "footer": "GEOSPATIAL VISUAL EXPERIENCE",
    "theme": "Emerald Aurora"
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def clamp(value, low, high):
    return max(low, min(high, value))


def log_message(message, level=Qgis.Info):
    QgsMessageLog.logMessage(str(message), PLUGIN_NAME, level)


def read_setting(key, default):
    return QSettings().value(SETTINGS_PREFIX + key, default)


def write_setting(key, value):
    QSettings().setValue(SETTINGS_PREFIX + key, value)


def setting_as_bool(value):
    if isinstance(value, str):
        return value.strip().lower() in (
            "true", "1", "yes", "on"
        )
    return bool(value)


def minute_identifier():
    local = time.localtime()
    return (
        local.tm_year,
        local.tm_yday,
        local.tm_hour,
        local.tm_min
    )


def clock_values():
    now = time.time()
    local = time.localtime(now)

    fractional_second = (
        local.tm_sec + now - math.floor(now)
    )

    fractional_minute = (
        local.tm_min + fractional_second / 60.0
    )

    fractional_hour = (
        (local.tm_hour % 12) + fractional_minute / 60.0
    )

    return (
        fractional_hour * 30.0,
        fractional_minute * 6.0,
        fractional_second * 6.0,
        local,
        fractional_second
    )


def theme_color(theme, key, alpha=255):
    values = THEMES.get(
        theme,
        THEMES["Emerald Aurora"]
    ).get(key, (255, 255, 255))

    return QColor(
        values[0], values[1], values[2], alpha
    )


# ============================================================
# GEOMETRY HELPERS
# ============================================================

def polar_point(cx, cy, radius, degrees):
    angle = math.radians(degrees - 90.0)
    return QPointF(
        cx + math.cos(angle) * radius,
        cy + math.sin(angle) * radius
    )


def local_triangle_polygon(radius):
    return QPolygonF([
        QPointF(0, -radius),
        QPointF(
            math.sqrt(3.0) * radius / 2.0,
            radius / 2.0
        ),
        QPointF(
            -math.sqrt(3.0) * radius / 2.0,
            radius / 2.0
        )
    ])


def triangular_hand_polygon(
    cx, cy, angle_degrees,
    length, base_width, tail_length
):
    angle = math.radians(angle_degrees)

    dx = math.sin(angle)
    dy = -math.cos(angle)

    px = math.cos(angle)
    py = math.sin(angle)

    tip = QPointF(
        cx + dx * length,
        cy + dy * length
    )

    base_center = QPointF(
        cx - dx * tail_length,
        cy - dy * tail_length
    )

    left = QPointF(
        base_center.x() + px * base_width / 2.0,
        base_center.y() + py * base_width / 2.0
    )

    right = QPointF(
        base_center.x() - px * base_width / 2.0,
        base_center.y() - py * base_width / 2.0
    )

    return QPolygonF([tip, left, right])


def cubic_bezier(p0, p1, p2, p3, progress):
    u = 1.0 - progress

    x = (
        u ** 3 * p0.x()
        + 3.0 * u ** 2 * progress * p1.x()
        + 3.0 * u * progress ** 2 * p2.x()
        + progress ** 3 * p3.x()
    )

    y = (
        u ** 3 * p0.y()
        + 3.0 * u ** 2 * progress * p1.y()
        + 3.0 * u * progress ** 2 * p2.y()
        + progress ** 3 * p3.y()
    )

    return QPointF(x, y)


# ============================================================
# AURORA VORTEX CLOCK
# ============================================================

class AuroraVortexClock(QWidget):

    CLOCK_CENTRE = 87
    CLOCK_SIZE = 174

    ENERGY_DURATION = 2.35
    CENTRE_HOLD_DURATION = 0.24

    MILESTONE_BURST_DURATION = 0.85
    SECOND_WAKE_DURATION = 0.42
    LOCK_DURATION = 0.68

    def __init__(self, parent=None, theme_name="Emerald Aurora"):
        super().__init__(parent)

        self.theme_name = (
            theme_name if theme_name in THEMES
            else "Emerald Aurora"
        )

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setFixedSize(self.CLOCK_SIZE, self.CLOCK_SIZE)

        self.animation_time = 0.0
        self.last_tick = time.monotonic()

        self.last_minute_id = minute_identifier()
        self.energy_started = None

        # Five-second milestone animation state.
        self.last_milestone = self.get_current_milestone()
        self.milestone_change_time = None
        self.previous_milestone = self.last_milestone

        self.timer = QTimer(self)
        # 30 FPS gives smooth motion without an unnecessarily tight repaint loop.
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.animate)
        self.timer.start()

    def color(self, key, alpha=255):
        return theme_color(self.theme_name, key, alpha)

    def set_theme(self, theme_name):
        if theme_name not in THEMES:
            theme_name = "Emerald Aurora"

        self.theme_name = theme_name
        self.update()

    # --------------------------------------------------------
    # FIVE-SECOND MILESTONE TRACKING
    # --------------------------------------------------------

    def get_current_milestone(self):
        """
        Return the active five-second milestone.

        00-04 seconds: 60
        05-09 seconds: 5
        10-14 seconds: 10
        ...
        55-59 seconds: 55
        """
        second = int(time.localtime().tm_sec)

        if second < 5:
            return 60

        return (second // 5) * 5

    def update_milestone(self):
        current = self.get_current_milestone()

        if current != self.last_milestone:
            self.previous_milestone = self.last_milestone
            self.last_milestone = current
            self.milestone_change_time = time.monotonic()

    # --------------------------------------------------------
    # ANIMATION
    # --------------------------------------------------------

    def animate(self):
        now = time.monotonic()
        elapsed = now - self.last_tick
        self.last_tick = now

        self.animation_time += elapsed

        if self.animation_time > 100000:
            self.animation_time = 0.0

        self.update_milestone()

        current_minute = minute_identifier()

        if current_minute != self.last_minute_id:
            self.last_minute_id = current_minute
            self.energy_started = time.monotonic()

        self.update()

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()

    def start(self):
        self.last_tick = time.monotonic()

        if not self.timer.isActive():
            self.timer.start()

    def energy_progress(self):
        if self.energy_started is None:
            return 0.0

        elapsed = time.monotonic() - self.energy_started

        if elapsed < 0.0:
            return 0.0

        if elapsed >= self.ENERGY_DURATION:
            self.energy_started = None
            return 0.0

        return elapsed / self.ENERGY_DURATION

    def infinity_centre_convergence_active(self):
        if self.energy_started is None:
            return False

        elapsed = time.monotonic() - self.energy_started

        return 0.0 <= elapsed < self.CENTRE_HOLD_DURATION

    # --------------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------------

    def draw_background(self, painter):
        cx = cy = 87

        gradient = QRadialGradient(QPointF(cx, cy), 87)
        gradient.setColorAt(0.0, self.color("background", 235))
        gradient.setColorAt(0.55, self.color("background_mid", 210))
        gradient.setColorAt(1.0, self.color("background_edge", 10))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(cx, cy), 86, 86)

        glow_x = cx + math.sin(self.animation_time * 0.7) * 7
        glow_y = cy + math.cos(self.animation_time * 0.8) * 7

        glow = QRadialGradient(QPointF(glow_x, glow_y), 66)
        glow.setColorAt(0.0, self.color("glow", 48))
        glow.setColorAt(1.0, self.color("glow", 0))

        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QPointF(cx, cy), 66, 66)

    # --------------------------------------------------------
    # ORBITAL RINGS
    # --------------------------------------------------------

    def draw_rings(self, painter):
        cx = cy = 87

        rings = [
            (78, self.color("ring", 150), 1.1),
            (70, self.color("gold", 190), 1.2),
            (59, self.color("cyan", 145), 0.9),
            (48, self.color("magenta", 135), 0.9)
        ]

        pulse = math.sin(self.animation_time * 1.2)

        for index, (radius, color, width) in enumerate(rings):
            if index == 1:
                radius += pulse * 1.2

            painter.setPen(QPen(color, width))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), radius, radius)

        for index in range(3):
            radius = 54 + index * 9
            rect = QRectF(
                cx - radius, cy - radius,
                radius * 2, radius * 2
            )

            painter.setPen(QPen(
                self.color("gold", 90 - index * 18), 1.0
            ))

            painter.drawArc(
                rect,
                int(self.animation_time * (22 + index * 9) * 16),
                92 * 16
            )

    # --------------------------------------------------------
    # GOLDEN RATIO SPIRAL
    # --------------------------------------------------------

    def draw_golden_spiral(self, painter):
        cx = cy = 87
        path = QPainterPath()

        a = 1.3
        b = math.log(1.61803398875) / (math.pi / 2.0)
        started = False
        rotation = self.animation_time * 0.025

        for index in range(500):
            theta = index * 0.035 + rotation
            radius = a * math.exp(b * theta)

            if radius > 48:
                break

            x = cx + math.cos(theta) * radius
            y = cy + math.sin(theta) * radius

            if not started:
                path.moveTo(x, y)
                started = True
            else:
                path.lineTo(x, y)

        gradient = QLinearGradient(45, 40, 132, 137)
        gradient.setColorAt(0.0, self.color("bright", 35))
        gradient.setColorAt(0.55, self.color("gold", 220))
        gradient.setColorAt(1.0, self.color("gold", 65))

        painter.setPen(QPen(QBrush(gradient), 1.25))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

    # --------------------------------------------------------
    # INFINITY PARTICLES
    # --------------------------------------------------------

    def infinity_particle_path(self, side, branch):
        cx = cy = 87.0

        start = QPointF(cx + side * 48.0, cy)
        centre = QPointF(cx, cy)

        control1 = QPointF(
            cx + side * 36.0,
            cy - branch * 42.0
        )

        control2 = QPointF(
            cx + side * 15.0,
            cy - branch * 27.0
        )

        return start, control1, control2, centre

    def infinity_particle_position(
        self, side, branch, cycle_progress,
        forced_progress=None
    ):
        start, control1, control2, centre = (
            self.infinity_particle_path(side, branch)
        )

        if forced_progress is None:
            progress = (
                0.5 - 0.5 * math.cos(
                    2.0 * math.pi * cycle_progress
                )
            )
        else:
            progress = clamp(forced_progress, 0.0, 1.0)

        return (
            cubic_bezier(
                start, control1, control2, centre, progress
            ),
            progress
        )

    def draw_infinity_particle_trail(
        self, painter, side, branch,
        cycle_progress, color, forced_progress=None
    ):
        if forced_progress is not None:
            return

        path = QPainterPath()
        trail_samples = 20
        trail_duration = 0.22
        started = False

        for index in range(trail_samples + 1):
            age = trail_duration * index / trail_samples
            previous_cycle = (cycle_progress - age) % 1.0

            point, unused_progress = self.infinity_particle_position(
                side, branch, previous_cycle
            )

            if not started:
                path.moveTo(point)
                started = True
            else:
                path.lineTo(point)

        trail_color = QColor(color)
        trail_color.setAlpha(190)

        pen = QPen(trail_color, 2.0)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

    def draw_one_infinity_particle(
        self, painter, side, branch,
        cycle_progress, color, forced_progress=None
    ):
        point, unused_progress = self.infinity_particle_position(
            side, branch, cycle_progress, forced_progress
        )

        self.draw_infinity_particle_trail(
            painter, side, branch,
            cycle_progress, color, forced_progress
        )

        if forced_progress is not None:
            glow_radius = 16.0
            centre_alpha = 255
        else:
            glow_radius = 12.0
            centre_alpha = 235

        glow = QRadialGradient(point, glow_radius)

        glow.setColorAt(0.0, QColor(255, 255, 245, centre_alpha))
        glow.setColorAt(
            0.25,
            QColor(color.red(), color.green(), color.blue(), 245)
        )
        glow.setColorAt(
            0.65,
            QColor(color.red(), color.green(), color.blue(), 85)
        )
        glow.setColorAt(
            1.0,
            QColor(color.red(), color.green(), color.blue(), 0)
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(point, glow_radius, glow_radius)

        painter.setBrush(QColor(255, 255, 245, 255))
        painter.drawEllipse(point, 2.7, 2.7)

    def draw_infinity_path(self, painter):
        """
        AURORA VORTEX V2.2
        Premium animated infinity path.

        Compatible with:
        QGIS 3.28.4
        Python 3.9
        PyQt5

        Uses the existing AuroraVortexClock attributes:
        self.animation_time
        self.color()
        """

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        t = self.animation_time

        cx = 87.0
        cy = 87.0

        # ----------------------------------------------------
        # 1. SIZE AND BREATHING
        # ----------------------------------------------------

        breathing = (
            1.0 + 0.025 * math.sin(t * 1.35)
        )

        scale = 43.0 * breathing

        # ----------------------------------------------------
        # 2. INFINITY GEOMETRY
        # ----------------------------------------------------

        def infinity_point(angle, size=None):
            if size is None:
                size = scale

            wobble = (
                1.0
                + 0.009 * math.sin(
                    t * 1.8 + angle * 3.0
                )
            )

            x = math.sin(angle) * size * wobble

            y = (
                math.sin(angle)
                * math.cos(angle)
                * size
                * wobble
            )

            return QPointF(cx + x, cy + y)

        # ----------------------------------------------------
        # 3. BUILD SMOOTH PATH
        # ----------------------------------------------------

        path = QPainterPath()

        steps = 280

        for i in range(steps + 1):
            angle = math.tau * i / steps
            point = infinity_point(angle)

            if i == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)

        # ----------------------------------------------------
        # 4. DEEP AURORA GLOW
        # ----------------------------------------------------

        glow_layers = [
            (17.0, 12),
            (13.0, 19),
            (9.0, 30),
            (6.0, 45),
        ]

        for width, alpha in glow_layers:
            color = self.color("cyan", alpha)

            pen = QPen(color)
            pen.setWidthF(width)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)

            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

        # ----------------------------------------------------
        # 5. CINEMATIC COLOUR RIBBON
        # ----------------------------------------------------

        colours = [
            "cyan",
            "magenta",
            "gold",
            "emerald"
        ]

        ribbon_steps = 240

        for i in range(ribbon_steps):
            a1 = math.tau * i / ribbon_steps
            a2 = math.tau * (i + 1) / ribbon_steps

            p1 = infinity_point(a1)
            p2 = infinity_point(a2)

            colour_position = (
                math.sin(a1 * 2.0 - t * 1.6) + 1.0
            ) * 0.5

            colour_index = int(
                colour_position * len(colours)
            ) % len(colours)

            colour = self.color(
                colours[colour_index],
                220
            )

            pen = QPen(colour)
            pen.setWidthF(1.9)
            pen.setCapStyle(Qt.RoundCap)

            painter.setPen(pen)
            painter.drawLine(p1, p2)

        # ----------------------------------------------------
        # 6. WHITE INNER LIGHT
        # ----------------------------------------------------

        inner_pen = QPen(
            QColor(255, 255, 255, 115),
            0.75
        )

        inner_pen.setCapStyle(Qt.RoundCap)

        painter.setPen(inner_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        # ----------------------------------------------------
        # 7. FOUR SYNCHRONIZED PARTICLES
        # ----------------------------------------------------

        particle_count = 4

        for index in range(particle_count):

            phase = (
                t * 0.75
                + index * math.tau / particle_count
            )

            angle = phase % math.tau

            point = infinity_point(angle)

            particle_colour = self.color(
                "cyan" if index % 2 == 0 else "magenta"
            )

            pulse = (
                0.5
                + 0.5 * math.sin(
                    t * 4.0 + index * 1.7
                )
            )

            radius = 2.5 + pulse * 2.0

            # PARTICLE TRAIL
            for trail_index in range(13):

                trail_fraction = trail_index / 12.0

                trail_angle = (
                    angle - trail_fraction * 0.25
                )

                trail_point = infinity_point(
                    trail_angle
                )

                trail_alpha = int(
                    105 * (1.0 - trail_fraction)
                )

                trail_radius = (
                    radius * (1.0 - trail_fraction * 0.65)
                )

                trail_colour = QColor(particle_colour)
                trail_colour.setAlpha(trail_alpha)

                painter.setPen(Qt.NoPen)
                painter.setBrush(trail_colour)

                painter.drawEllipse(
                    trail_point,
                    trail_radius,
                    trail_radius
                )

            # PARTICLE HALO
            halo = QRadialGradient(
                point,
                radius * 4.5
            )

            halo.setColorAt(
                0.0,
                QColor(255, 255, 255, 240)
            )

            halo.setColorAt(
                0.25,
                QColor(
                    particle_colour.red(),
                    particle_colour.green(),
                    particle_colour.blue(),
                    225
                )
            )

            halo.setColorAt(
                1.0,
                QColor(0, 0, 0, 0)
            )

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(halo))

            painter.drawEllipse(
                point,
                radius * 4.5,
                radius * 4.5
            )

            # PARTICLE BODY
            painter.setBrush(particle_colour)

            painter.drawEllipse(
                point,
                radius,
                radius
            )

            # WHITE-HOT CENTRE
            painter.setBrush(
                QColor(255, 255, 255, 245)
            )

            painter.drawEllipse(
                point,
                radius * 0.32,
                radius * 0.32
            )

        # ----------------------------------------------------
        # 8. CENTRAL ENERGY CORE
        # ----------------------------------------------------

        core_pulse = (
            0.5 + 0.5 * math.sin(t * 3.2)
        )

        core_radius = (
            4.0 + core_pulse * 2.2
        )

        core_glow = QRadialGradient(
            QPointF(cx, cy),
            22.0 + core_pulse * 5.0
        )

        core_glow.setColorAt(
            0.0,
            QColor(255, 255, 255, 245)
        )

        core_glow.setColorAt(
            0.20,
            self.color("bright", 235)
        )

        core_glow.setColorAt(
            0.48,
            self.color("gold", 150)
        )

        core_glow.setColorAt(
            1.0,
            QColor(0, 0, 0, 0)
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(core_glow))

        painter.drawEllipse(
            QPointF(cx, cy),
            27.0,
            27.0
        )

        painter.setBrush(
            QColor(255, 255, 255, 245)
        )

        painter.drawEllipse(
            QPointF(cx, cy),
            core_radius * 0.45,
            core_radius * 0.45
        )

        # ----------------------------------------------------
        # 9. ROTATING MICRO-SPARKS
        # ----------------------------------------------------

        spark_count = 24

        for index in range(spark_count):

            angle = (
                index * math.tau / spark_count
                + t * 0.24
            )

            point = infinity_point(
                angle,
                scale * 1.075
            )

            pulse = (
                0.5
                + 0.5 * math.sin(
                    t * 4.5 + index * 1.31
                )
            )

            radius = 0.6 + pulse * 1.15

            if index % 3 == 0:
                colour = self.color("gold")
            elif index % 3 == 1:
                colour = self.color("cyan")
            else:
                colour = self.color("magenta")

            colour.setAlpha(
                int(65 + pulse * 160)
            )

            painter.setPen(Qt.NoPen)
            painter.setBrush(colour)

            painter.drawEllipse(
                point,
                radius,
                radius
            )

        painter.restore()

    # --------------------------------------------------------
    # VERTEX GLOW AND TIME INDICATORS
    # --------------------------------------------------------

    def draw_vertex_glow(self, painter, point, color):
        glow = QRadialGradient(point, 13.0)

        glow.setColorAt(0.0, QColor(255, 255, 245, 255))
        glow.setColorAt(
            0.20,
            QColor(color.red(), color.green(), color.blue(), 255)
        )
        glow.setColorAt(
            0.55,
            QColor(color.red(), color.green(), color.blue(), 115)
        )
        glow.setColorAt(
            1.0,
            QColor(color.red(), color.green(), color.blue(), 0)
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(point, 13, 13)

        painter.setBrush(QColor(255, 255, 245, 255))
        painter.drawEllipse(point, 3, 3)

        painter.setPen(QPen(color.lighter(150), 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(point, 5, 5)

    def draw_time_indicator(self, painter, angle, radius, color, label):
        cx = cy = 87.0
        point = polar_point(cx, cy, radius, angle)

        painter.save()

        inner = polar_point(cx, cy, radius - 7.0, angle)

        painter.setPen(QPen(
            QColor(color.red(), color.green(), color.blue(), 190),
            1.2
        ))

        painter.drawLine(inner, point)
        self.draw_vertex_glow(painter, point, color)

        painter.setPen(QPen(QColor(255, 255, 245, 230), 0.8))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(point, 6.2, 6.2)

        painter.restore()

    def draw_fixed_time_indicators(self, painter):
        hour_angle, minute_angle, second_angle, local, fractional = (
            clock_values()
        )

        self.draw_time_indicator(
            painter, hour_angle, 72.0, self.color("bright"), "H"
        )

        self.draw_time_indicator(
            painter, minute_angle, 75.0, self.color("magenta"), "M"
        )

        self.draw_time_indicator(
            painter, second_angle, 81.0, self.color("cyan"), "S"
        )

    # --------------------------------------------------------
    # STRUCTURAL TRIANGLES
    # --------------------------------------------------------

    # --------------------------------------------------------
    # STRUCTURAL TRIANGLES
    # --------------------------------------------------------

    def draw_structural_triangles(self, painter):
        cx = cy = 87.0

        (
            hour_angle,
            minute_angle,
            unused_second_angle,
            local,
            fractional_second
        ) = clock_values()

        mechanical_second = int(local.tm_sec) % 60

        mechanical_fraction = clamp(
            fractional_second / 0.16, 0.0, 1.0
        )

        mechanical_ease = (
            1.0 - math.cos(math.pi * mechanical_fraction)
        ) / 2.0

        mechanical_angle = (
            mechanical_second * 6.0 + mechanical_ease * 6.0
        )

        # Hour and minute triangles retain their original colours.
        configurations = [
            (64.0, hour_angle, self.color("bright"), 2.0),
            (53.0, minute_angle, self.color("magenta"), 1.8)
        ]

        for radius, angle, color, width in configurations:
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(angle)

            polygon = local_triangle_polygon(radius)

            color.setAlpha(205)

            pen = QPen(color, width)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)

            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPolygon(polygon)

            painter.setPen(Qt.NoPen)
            painter.setBrush(color)

            for vertex in polygon:
                painter.drawEllipse(vertex, 1.8, 1.8)

            painter.restore()

        # ----------------------------------------------------
        # DISTINCT ELECTRIC TURQUOISE SECONDS TRIANGLE
        # ----------------------------------------------------

        seconds_color = QColor(0, 255, 225)
        seconds_outline = QColor(170, 255, 250)

        pulse = (
            0.5 + 0.5 * math.sin(self.animation_time * 5.0)
        )

        glow_alpha = int(85 + pulse * 100)
        seconds_width = 2.0 + pulse * 0.8

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(mechanical_angle)

        polygon = local_triangle_polygon(41.0)

        # Soft turquoise glow around the triangle.
        glow_color = QColor(seconds_color)
        glow_color.setAlpha(glow_alpha)

        glow_pen = QPen(glow_color, 7.0 + pulse * 3.0)
        glow_pen.setCapStyle(Qt.RoundCap)
        glow_pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(glow_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(polygon)

        # Bright, clearly visible triangle outline.
        main_pen = QPen(
            seconds_color,
            seconds_width
        )

        main_pen.setCapStyle(Qt.RoundCap)
        main_pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(main_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(polygon)

        # Bright vertex points.
        painter.setPen(Qt.NoPen)

        for vertex in polygon:
            vertex_glow = QRadialGradient(vertex, 7.0)

            vertex_glow.setColorAt(
                0.0,
                QColor(255, 255, 255, 255)
            )

            vertex_glow.setColorAt(
                0.3,
                QColor(0, 255, 225, 245)
            )

            vertex_glow.setColorAt(
                1.0,
                QColor(0, 255, 225, 0)
            )

            painter.setBrush(QBrush(vertex_glow))
            painter.drawEllipse(vertex, 7.0, 7.0)

            painter.setBrush(QColor(220, 255, 250))
            painter.drawEllipse(vertex, 2.0, 2.0)

        painter.restore()

    # --------------------------------------------------------
    # GOLDEN ANGLE PARTICLES + TIME-FLOW SIGNAL
    # --------------------------------------------------------

    def second_progress_state(self):
        """Return second, fractional second and five-second progress."""
        now = time.time()
        local = time.localtime(now)
        fractional = local.tm_sec + (now - math.floor(now))
        block_second = local.tm_sec % 5
        progress = clamp(block_second / 5.0 + (fractional - local.tm_sec) / 5.0, 0.0, 0.9999)

        active = 60 if local.tm_sec < 5 else (local.tm_sec // 5) * 5
        next_value = 5 if active == 60 else active + 5

        return local.tm_sec, fractional, progress, active, next_value

    def milestone_point(self, value, radius=65.0):
        return polar_point(87.0, 87.0, radius, value * 6.0)

    def draw_time_flow_signal(self, painter):
        """Show where the current five-second interval is heading."""
        _second, _fractional, progress, active, next_value = self.second_progress_state()

        cx = cy = 87.0
        active_angle = active * 6.0
        next_angle = next_value * 6.0

        # The next 5-second sector is deliberately subtle: it acts as a
        # directional guide rather than another competing clock hand.
        painter.save()
        painter.setBrush(Qt.NoBrush)

        arc_rect = QRectF(cx - 65.0, cy - 65.0, 130.0, 130.0)
        painter.setPen(QPen(self.color("cyan", 38), 2.8))
        painter.drawArc(arc_rect, int((90.0 - next_angle) * 16), int(-30.0 * 16))

        # Progress arc: it grows through the five-second sector.
        progress_color = self.color("bright", int(80 + 90 * progress))
        painter.setPen(QPen(progress_color, 2.4))
        painter.drawArc(arc_rect, int((90.0 - active_angle) * 16), int(-30.0 * progress * 16))

        # A tiny moving head marks the exact progress position.
        head_angle = active_angle + 30.0 * progress
        head = polar_point(cx, cy, 65.0, head_angle)
        head_glow = QRadialGradient(head, 9.0)
        head_glow.setColorAt(0.0, self.color("bright", 230))
        head_glow.setColorAt(0.35, self.color("cyan", 150))
        head_glow.setColorAt(1.0, self.color("cyan", 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(head_glow))
        painter.drawEllipse(head, 9.0, 9.0)
        painter.setBrush(self.color("bright", 245))
        painter.drawEllipse(head, 1.9, 1.9)

        painter.restore()

    def milestone_burst_progress(self):
        if self.milestone_change_time is None:
            return -1.0
        elapsed = time.monotonic() - self.milestone_change_time
        if 0.0 <= elapsed < self.MILESTONE_BURST_DURATION:
            return elapsed / self.MILESTONE_BURST_DURATION
        return -1.0

    def draw_second_hand_wake(self, painter):
        """A restrained wake makes the real second hand drive the particle field."""
        _hour, _minute, second_angle, _local, fractional = clock_values()
        cx = cy = 87.0
        painter.save()
        painter.setPen(Qt.NoPen)
        for index in range(8):
            age = index / 8.0
            angle = second_angle - age * (1.8 + fractional * 0.8)
            radius = 56.0 - age * 11.0
            point = polar_point(cx, cy, radius, angle)
            alpha = int(95 * (1.0 - age) ** 1.7)
            size = 1.0 + 1.3 * (1.0 - age)
            glow = QRadialGradient(point, 5.5)
            glow.setColorAt(0.0, self.color("cyan", alpha))
            glow.setColorAt(0.45, self.color("bright", int(alpha * 0.55)))
            glow.setColorAt(1.0, self.color("cyan", 0))
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(point, 5.5, 5.5)
            painter.setBrush(self.color("bright", alpha))
            painter.drawEllipse(point, size, size)
        painter.restore()

    def draw_milestone_lock(self, painter):
        """Tiny geometric lock at a five-second transition."""
        progress = self.milestone_burst_progress()
        if progress < 0.0:
            return
        point = self.milestone_point(self.last_milestone, 65.0)
        remaining = 1.0 - progress
        radius = 3.5 + 9.0 * remaining
        alpha = int(220 * remaining ** 1.2)
        painter.save()
        painter.translate(point)
        painter.rotate(self.animation_time * 140.0)
        diamond = QPolygonF([
            QPointF(0, -radius), QPointF(radius, 0),
            QPointF(0, radius), QPointF(-radius, 0)
        ])
        painter.setPen(QPen(self.color("bright", alpha), 1.1 + 0.9 * remaining))
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(diamond)
        painter.restore()

    def draw_minute_convergence(self, painter):
        """During the minute event, selected particles briefly collapse into the core."""
        progress = self.energy_progress()
        if progress <= 0.0:
            return
        if progress > 0.55:
            return
        t = progress / 0.55
        cx = cy = 87.0
        painter.save()
        painter.setPen(Qt.NoPen)
        for index in range(18):
            angle = math.radians(index * 20.0) + self.animation_time * 0.25
            start_r = 62.0 + (index % 3) * 4.0
            radius = start_r * (1.0 - t)
            point = QPointF(cx + math.cos(angle) * radius,
                            cy + math.sin(angle) * radius)
            alpha = int(180 * (1.0 - t))
            size = 1.1 + 1.0 * (1.0 - t)
            painter.setBrush(self.color("bright" if index % 2 == 0 else "cyan", alpha))
            painter.drawEllipse(point, size, size)
        painter.restore()

    def draw_particles(self, painter):
        cx = cy = 87
        golden_angle = math.radians(137.507764)

        colors = [
            self.color("bright", 175),
            self.color("emerald", 165),
            self.color("magenta", 165),
            self.color("cyan", 175)
        ]

        painter.setPen(Qt.NoPen)

        # Ambient golden-angle field. These remain restrained so the
        # time-flow particles have a clear visual hierarchy.
        for index in range(58):
            angle = (
                index * golden_angle
                + self.animation_time * 0.19
            )

            radius = min(73, 7.0 + 5.4 * math.sqrt(index))

            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius

            flow_gain = 0.75 + 0.25 * math.sin(self.animation_time * 0.9 + index * 0.21)
            pulse = (
                1.0 + math.sin(
                    self.animation_time * 2.0 + index * 0.55
                ) * 0.30
            )

            size = max(0.55, 1.02 * pulse)

            base = QColor(colors[index % len(colors)])
            base.setAlpha(int(base.alpha() * flow_gain))
            painter.setBrush(QBrush(base))
            painter.drawEllipse(QPointF(x, y), size, size)

        self.draw_time_flow_signal(painter)

        # ----------------------------------------------------
        # DIRECTIONAL PARTICLE STREAM
        # ----------------------------------------------------
        # Sixteen particles travel from the clock's inner field toward
        # the next five-second number. Their spacing is locked to the
        # five-second progress value, so they visually communicate
        # elapsed time instead of being purely decorative.
        _second, _fractional, progress, active, next_value = self.second_progress_state()

        start = QPointF(cx, cy)
        target = self.milestone_point(next_value, 65.0)
        dx = target.x() - cx
        dy = target.y() - cy
        length = math.hypot(dx, dy) or 1.0
        nx = -dy / length
        ny = dx / length

        for index in range(16):
            phase = (index / 16.0 + progress * 0.95) % 1.0
            travel = 0.10 + 0.82 * phase
            eased = 1.0 - (1.0 - travel) ** 2

            # Slight orbital offset keeps the stream alive without
            # obscuring the main hands.
            offset = math.sin(self.animation_time * 3.0 + index * 1.7) * (1.4 + 1.5 * phase)
            curve = math.sin(math.pi * eased) * (2.5 + 3.0 * progress)
            x = start.x() + dx * eased + nx * (offset + curve)
            y = start.y() + dy * eased + ny * (offset + curve)

            alpha = int(80 + 170 * (1.0 - phase))
            radius = 1.0 + 1.2 * (1.0 - phase)

            glow = QRadialGradient(QPointF(x, y), 6.0)
            glow.setColorAt(0.0, self.color("cyan", alpha))
            glow.setColorAt(0.45, self.color("bright", int(alpha * 0.55)))
            glow.setColorAt(1.0, self.color("cyan", 0))

            painter.setBrush(QBrush(glow))
            painter.drawEllipse(QPointF(x, y), 6.0, 6.0)
            painter.setBrush(self.color("bright", alpha))
            painter.drawEllipse(QPointF(x, y), radius, radius)

        # The leading particle becomes a slightly stronger beacon as
        # the next milestone approaches.
        beacon_alpha = int(110 + 125 * progress)
        beacon = QRadialGradient(target, 11.0 + progress * 5.0)
        beacon.setColorAt(0.0, self.color("bright", beacon_alpha))
        beacon.setColorAt(0.3, self.color("cyan", int(beacon_alpha * 0.8)))
        beacon.setColorAt(1.0, self.color("cyan", 0))
        painter.setBrush(QBrush(beacon))
        painter.drawEllipse(target, 11.0 + progress * 5.0, 11.0 + progress * 5.0)

    # --------------------------------------------------------
    # FIVE-SECOND MILESTONE NUMBERS
    # --------------------------------------------------------

    def draw_second_milestones(self, painter):
        cx = 87.0
        cy = 87.0

        current = self.last_milestone

        # Smooth repeating pulse. This is deliberately independent
        # of milestone age, so the number stays highlighted for
        # the entire five-second interval.
        phase = (
            time.monotonic() % 1.05
        ) / 1.05

        wave = (
            0.5 + 0.5 * math.sin(2.0 * math.pi * phase)
        )

        pulse_scale = 1.0 + 0.13 * wave
        active_alpha = int(175 + 80 * wave)

        # Check the short arrival animation.
        burst_progress = -1.0

        if self.milestone_change_time is not None:
            elapsed = (
                time.monotonic() - self.milestone_change_time
            )

            if 0.0 <= elapsed < self.MILESTONE_BURST_DURATION:
                burst_progress = (
                    elapsed / self.MILESTONE_BURST_DURATION
                )

        painter.save()

        for value in range(5, 61, 5):
            angle = value * 6.0

            point = polar_point(
                cx, cy, 65.0, angle
            )

            is_active = value == current

            painter.save()
            painter.translate(point)

            if is_active:
                painter.scale(pulse_scale, pulse_scale)

                # Outer active-number glow.
                halo = QRadialGradient(
                    QPointF(0, 0), 19.0
                )

                halo.setColorAt(
                    0.0,
                    self.color("glow", int(active_alpha * 0.65))
                )

                halo.setColorAt(
                    0.45,
                    self.color("cyan", int(active_alpha * 0.35))
                )

                halo.setColorAt(
                    1.0,
                    self.color("cyan", 0)
                )

                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(halo))
                painter.drawEllipse(
                    QPointF(0, 0), 19.0, 19.0
                )

                # Active milestone number.
                painter.setFont(
                    QFont("Segoe UI", 9, QFont.Bold)
                )

                painter.setPen(
                    self.color("bright", active_alpha)
                )

                painter.drawText(
                    QRectF(-17, -12, 34, 24),
                    Qt.AlignCenter,
                    str(value)
                )

                # Active number outline.
                painter.setPen(
                    QPen(
                        self.color("gold", active_alpha),
                        1.1
                    )
                )

                painter.setBrush(Qt.NoBrush)

                painter.drawEllipse(
                    QRectF(-16, -11, 32, 22)
                )

            else:
                # All inactive milestone numbers remain visible.
                painter.setFont(
                    QFont("Segoe UI", 7, QFont.DemiBold)
                )

                painter.setPen(
                    self.color("footer", 155)
                )

                painter.drawText(
                    QRectF(-17, -11, 34, 22),
                    Qt.AlignCenter,
                    str(value)
                )

            painter.restore()

        # Expanding ring at every five-second transition.
        if burst_progress >= 0.0:
            active_angle = current * 6.0

            active_point = polar_point(
                cx, cy, 65.0, active_angle
            )

            burst_radius = (
                10.0 + burst_progress * 22.0
            )

            burst_alpha = int(
                230 * (1.0 - burst_progress)
            )

            painter.setPen(
                QPen(
                    self.color("bright", burst_alpha),
                    max(0.7, 2.0 * (1.0 - burst_progress))
                )
            )

            painter.setBrush(Qt.NoBrush)

            painter.drawEllipse(
                active_point,
                burst_radius,
                burst_radius
            )

            # Short geometric lock pulse: the arriving milestone is
            # acknowledged before the directional stream moves on.
            lock = 1.0 - burst_progress
            painter.setPen(QPen(
                self.color("cyan", int(210 * lock)),
                1.0 + 1.5 * lock
            ))
            painter.drawLine(
                polar_point(active_point.x(), active_point.y(), 5.0 * lock, 0),
                polar_point(active_point.x(), active_point.y(), 5.0 * lock, 180)
            )
            painter.drawLine(
                polar_point(active_point.x(), active_point.y(), 5.0 * lock, 90),
                polar_point(active_point.x(), active_point.y(), 5.0 * lock, 270)
            )

        painter.restore()

    # --------------------------------------------------------
    # MINUTE ENERGY BURST
    # --------------------------------------------------------


    # --------------------------------------------------------
    # AURORA VORTEX — CINEMATIC ENERGY FLASH V2.2
    # --------------------------------------------------------


    def draw_energy_flash(self, painter):
        progress = self.energy_progress()

        if progress <= 0.0:
            return

        cx = cy = 87.0

        # ----------------------------------------------------
        # 1. EIGHT-SECOND CINEMATIC ANIMATION
        # ----------------------------------------------------

        progress = clamp(progress, 0.0, 1.0)
        elapsed = progress * 8.0

        ignition = clamp(elapsed / 2.0, 0.0, 1.0)
        ignition = 1.0 - (1.0 - ignition) ** 3

        hold = 1.0 if 2.0 <= elapsed <= 5.0 else 0.0

        fade = clamp((8.0 - elapsed) / 3.0, 0.0, 1.0)
        fade = fade * fade * (3.0 - 2.0 * fade)

        secondary_pulse = math.exp(
            -((elapsed - 5.4) / 0.65) ** 2
        )

        envelope = max(
            ignition * 0.65,
            hold,
            fade * 0.85
        )

        breathing = (
            0.90 + 0.10 *
            math.sin(self.animation_time * 4.0)
        )

        envelope = clamp(
            envelope * breathing + secondary_pulse * 0.25,
            0.0,
            1.0
        )

        ease_out = ignition

        peak = (
            math.exp(-elapsed * 1.5)
            + secondary_pulse
        )

        pulse = (
            0.5 + 0.5 *
            math.sin(self.animation_time * 8.0)
        )

        alpha = int(255 * envelope)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # ----------------------------------------------------
        # 2. CENTRAL AURORA BLOOM
        # ----------------------------------------------------

        bloom_radius = (
            24.0 + 65.0 * ease_out
            + secondary_pulse * 12.0
        )

        bloom = QRadialGradient(
            QPointF(cx, cy),
            bloom_radius
        )

        bloom.setColorAt(
            0.0,
            self.color("bright", int(245 * envelope))
        )
        bloom.setColorAt(
            0.12,
            self.color("gold", int(230 * envelope))
        )
        bloom.setColorAt(
            0.35,
            self.color("glow", int(155 * envelope))
        )
        bloom.setColorAt(
            0.68,
            self.color("cyan", int(75 * envelope))
        )
        bloom.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bloom))

        painter.drawEllipse(
            QPointF(cx, cy),
            bloom_radius,
            bloom_radius
        )

        # ----------------------------------------------------
        # 3. FOUR EXPANDING ENERGY RINGS
        # ----------------------------------------------------

        ring_configurations = [
            (0.00, "gold", 3.0),
            (0.12, "cyan", 2.2),
            (0.25, "magenta", 1.7),
            (0.38, "bright", 1.1)
        ]

        for delay, color_key, base_width in ring_configurations:

            local_progress = clamp(
                (progress - delay) / (1.0 - delay),
                0.0,
                1.0
            )

            ring_ease = (
                1.0 - (1.0 - local_progress) ** 2.4
            )

            radius = 9.0 + ring_ease * 82.0

            # Secondary pulse adds a new outward wave.
            radius += secondary_pulse * 15.0

            ring_alpha = int(
                245 * envelope *
                (1.0 - local_progress) ** 0.65
            )

            width = max(
                0.55,
                base_width * envelope
            )

            painter.setPen(
                QPen(
                    self.color(color_key, ring_alpha),
                    width
                )
            )

            painter.setBrush(Qt.NoBrush)

            painter.drawEllipse(
                QPointF(cx, cy),
                radius,
                radius
            )

        # ----------------------------------------------------
        # 4. SECONDARY GOLDEN ENERGY RING
        # ----------------------------------------------------

        if secondary_pulse > 0.01:

            secondary_radius = (
                12.0 + (1.0 - secondary_pulse) * 88.0
            )

            painter.setPen(
                QPen(
                    self.color(
                        "gold",
                        int(240 * secondary_pulse)
                    ),
                    2.5 + secondary_pulse * 2.0
                )
            )

            painter.setBrush(Qt.NoBrush)

            painter.drawEllipse(
                QPointF(cx, cy),
                secondary_radius,
                secondary_radius
            )

        # ----------------------------------------------------
        # 5. ROTATING AURORA ARCS
        # ----------------------------------------------------

        painter.save()
        painter.translate(cx, cy)

        rotation = self.animation_time * 95.0
        painter.rotate(rotation)

        for index in range(6):

            radius = 31.0 + index * 8.0

            arc_rect = QRectF(
                -radius,
                -radius,
                radius * 2.0,
                radius * 2.0
            )

            color_key = (
                "gold" if index % 3 == 0
                else "cyan" if index % 3 == 1
                else "magenta"
            )

            arc_alpha = int(
                alpha * (0.75 - index * 0.07)
            )

            painter.setPen(
                QPen(
                    self.color(color_key, arc_alpha),
                    max(0.7, 2.1 - index * 0.18)
                )
            )

            start_angle = index * 53
            sweep_angle = 78 + int(pulse * 28)

            painter.drawArc(
                arc_rect,
                start_angle * 16,
                sweep_angle * 16
            )

        painter.restore()

        # ----------------------------------------------------
        # 6. RADIAL LIGHT RAYS
        # ----------------------------------------------------

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self.animation_time * 55.0)

        for index in range(36):

            angle = math.radians(index * 10.0)

            inner_radius = 13.0

            outer_radius = (
                24.0 + 61.0 * ease_out
                + math.sin(
                    self.animation_time * 4.0 + index
                ) * 3.0
                + secondary_pulse * 12.0
            )

            p1 = QPointF(
                math.cos(angle) * inner_radius,
                math.sin(angle) * inner_radius
            )

            p2 = QPointF(
                math.cos(angle) * outer_radius,
                math.sin(angle) * outer_radius
            )

            ray_alpha = int(
                alpha * (
                    0.65 if index % 3 == 0 else 0.28
                )
            )

            ray_color = (
                self.color("bright", ray_alpha)
                if index % 3 == 0
                else self.color("cyan", ray_alpha)
            )

            painter.setPen(
                QPen(
                    ray_color,
                    1.5 if index % 6 == 0 else 0.65
                )
            )

            painter.drawLine(p1, p2)

        painter.restore()

        # ----------------------------------------------------
        # 7. GOLDEN-ANGLE PARTICLES
        # ----------------------------------------------------

        golden_angle = math.radians(137.507764)

        painter.setPen(Qt.NoPen)

        for index in range(36):

            angle = index * golden_angle

            start_radius = 7.0 + (index % 5) * 2.0

            end_radius = (
                42.0 + (index % 7) * 7.0
            )

            radius = (
                start_radius
                + (end_radius - start_radius) * ease_out
            )

            radius += math.sin(
                self.animation_time * 3.0 + index * 0.8
            ) * 2.0 * envelope

            radius += secondary_pulse * 5.0

            px = cx + math.cos(angle) * radius
            py = cy + math.sin(angle) * radius

            point = QPointF(px, py)

            particle_alpha = int(
                245 * envelope
            )

            particle_size = (
                0.8 + 2.0 * envelope
            )

            if index % 4 == 0:
                color_key = "bright"
            elif index % 4 == 1:
                color_key = "gold"
            elif index % 4 == 2:
                color_key = "cyan"
            else:
                color_key = "magenta"

            glow_size = 7.0 * envelope + 1.0

            particle_glow = QRadialGradient(
                point,
                glow_size
            )

            particle_glow.setColorAt(
                0.0,
                self.color(color_key, particle_alpha)
            )

            particle_glow.setColorAt(
                0.35,
                self.color(
                    color_key,
                    int(particle_alpha * 0.6)
                )
            )

            particle_glow.setColorAt(
                1.0,
                QColor(0, 0, 0, 0)
            )

            painter.setBrush(QBrush(particle_glow))

            painter.drawEllipse(
                point,
                glow_size,
                glow_size
            )

            painter.setBrush(
                self.color("bright", particle_alpha)
            )

            painter.drawEllipse(
                point,
                particle_size,
                particle_size
            )

        # ----------------------------------------------------
        # 8. CENTRAL WHITE-HOT ENERGY CORE
        # ----------------------------------------------------

        core_radius = (
            5.0 + 15.0 * min(1.0, peak)
        )

        core_glow = QRadialGradient(
            QPointF(cx, cy),
            core_radius * 3.5
        )

        core_glow.setColorAt(
            0.0,
            QColor(
                255, 255, 255,
                int(255 * envelope)
            )
        )

        core_glow.setColorAt(
            0.16,
            self.color(
                "bright",
                int(255 * envelope)
            )
        )

        core_glow.setColorAt(
            0.38,
            self.color(
                "gold",
                int(235 * envelope)
            )
        )

        core_glow.setColorAt(
            0.70,
            self.color(
                "glow",
                int(110 * envelope)
            )
        )

        core_glow.setColorAt(
            1.0,
            QColor(0, 0, 0, 0)
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(core_glow))

        painter.drawEllipse(
            QPointF(cx, cy),
            core_radius * 3.5,
            core_radius * 3.5
        )

        # ----------------------------------------------------
        # 9. LUMINOUS CENTRAL DIAMOND
        # ----------------------------------------------------

        diamond_radius = (
            4.0 + min(1.0, peak) * 5.0
        )

        diamond = QPolygonF([
            QPointF(cx, cy - diamond_radius),
            QPointF(cx + diamond_radius, cy),
            QPointF(cx, cy + diamond_radius),
            QPointF(cx - diamond_radius, cy)
        ])

        painter.setPen(
            QPen(
                self.color("bright", alpha),
                1.2
            )
        )

        painter.setBrush(
            self.color("gold", alpha)
        )

        painter.drawPolygon(diamond)

        painter.restore()


    # --------------------------------------------------------
    # CLOCK HANDS
    # --------------------------------------------------------

    def draw_triangle_hand(
        self, painter, angle, length, width,
        tail, color, outline=None
    ):
        polygon = triangular_hand_polygon(
            87.0, 87.0, angle, length, width, tail
        )

        if outline is None:
            outline = color.lighter(145)

        painter.setPen(QPen(outline, 0.9))
        painter.setBrush(QBrush(color))
        painter.drawPolygon(polygon)

    def draw_clock_hands(self, painter):
        hour_angle, minute_angle, second_angle, local, fractional = (
            clock_values()
        )

        self.draw_triangle_hand(
            painter, hour_angle, 29.0, 8.0, 7.0,
            self.color("gold"),
            self.color("bright")
        )

        self.draw_triangle_hand(
            painter, minute_angle, 46.0, 5.4, 8.0,
            self.color("magenta"),
            self.color("bright")
        )

        self.draw_triangle_hand(
            painter, second_angle, 57.0, 2.2, 11.0,
            self.color("cyan"),
            self.color("bright")
        )

    # --------------------------------------------------------
    # CENTRAL VORTEX CORE
    # --------------------------------------------------------

    def draw_center_core(self, painter):
        cx = cy = 87

        pulse = (
            1.0 + math.sin(self.animation_time * 2.4) * 0.12
        )

        radius = 6.0 * pulse

        glow = QRadialGradient(QPointF(cx, cy), 16)
        glow.setColorAt(0.0, self.color("bright", 245))
        glow.setColorAt(0.35, self.color("emerald", 160))
        glow.setColorAt(1.0, self.color("emerald", 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QPointF(cx, cy), 16, 16)

        diamond = QPolygonF([
            QPointF(cx, cy - radius),
            QPointF(cx + radius, cy),
            QPointF(cx, cy + radius),
            QPointF(cx - radius, cy)
        ])

        painter.setPen(QPen(self.color("bright"), 1.0))
        painter.setBrush(QBrush(self.color("gold")))
        painter.drawPolygon(diamond)

    # --------------------------------------------------------
    # SUB-SECOND PRECISION ORBIT
    # --------------------------------------------------------

    def draw_subsecond_orbit(self, painter):
        """A compact 12-step orbit visualizes progress inside the current second."""
        cx = cy = 87
        unused_hour, unused_minute, unused_second, unused_local, fraction = clock_values()
        progress = fraction - math.floor(fraction)
        orbit_radius = 19.0

        painter.save()
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.color("ring", 42), 0.8))
        painter.drawEllipse(QPointF(cx, cy), orbit_radius, orbit_radius)

        for index in range(12):
            angle = index * 30.0
            point = polar_point(cx, cy, orbit_radius, angle)
            active = (index / 12.0) <= progress
            color = self.color("bright" if active else "cyan", 205 if active else 65)
            painter.setPen(QPen(color, 1.35 if active else 0.8))
            painter.setBrush(QBrush(color) if active else Qt.NoBrush)
            painter.drawEllipse(point, 1.25 if active else 0.8,
                                1.25 if active else 0.8)

        # A moving bead makes sub-second motion legible at a glance.
        bead = polar_point(cx, cy, orbit_radius, progress * 360.0)
        bead_glow = QRadialGradient(bead, 5.5)
        bead_glow.setColorAt(0.0, self.color("bright", 230))
        bead_glow.setColorAt(1.0, self.color("glow", 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bead_glow))
        painter.drawEllipse(bead, 5.5, 5.5)
        painter.setBrush(QBrush(self.color("bright", 245)))
        painter.drawEllipse(bead, 1.7, 1.7)
        painter.restore()

    # --------------------------------------------------------
    # OUTER ACCENTS
    # --------------------------------------------------------

    def draw_outer_accents(self, painter):
        cx = cy = 87

        for index in range(24):
            angle = index * 15.0

            p1 = polar_point(cx, cy, 77, angle)
            p2 = polar_point(cx, cy, 80, angle)

            color = (
                self.color("cyan")
                if index % 6 == 0
                else self.color("accent", 150)
            )

            pen = QPen(color)
            pen.setWidthF(1.4 if index % 6 == 0 else 0.8)

            painter.setPen(pen)
            painter.drawLine(p1, p2)

    # --------------------------------------------------------
    # PAINT EVENT
    # --------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(
            QPainter.SmoothPixmapTransform, True
        )

        self.draw_background(painter)
        self.draw_rings(painter)
        self.draw_golden_spiral(painter)
        self.draw_infinity_path(painter)
        self.draw_structural_triangles(painter)
        self.draw_particles(painter)
        self.draw_second_hand_wake(painter)
        self.draw_outer_accents(painter)

        # Five-second milestone visualization.
        self.draw_second_milestones(painter)
        self.draw_milestone_lock(painter)

        # Minute event: convergence first, then the existing energy burst.
        self.draw_minute_convergence(painter)
        self.draw_energy_flash(painter)

        self.draw_fixed_time_indicators(painter)
        self.draw_clock_hands(painter)
        self.draw_center_core(painter)
        self.draw_subsecond_orbit(painter)

        painter.end()


# ============================================================
# BRANDING OVERLAY
# ============================================================

class FjBaBrandingOverlay(QWidget):

    PANEL_HEIGHT = 194
    CLOCK_SIZE = 174

    def __init__(self, canvas, settings):
        super().__init__(canvas)

        self.canvas = canvas
        self.settings_data = dict(settings)

        self.dragging = False
        self.drag_offset = QPoint()
        
        self.logo_animation = 0.0
        self.logo_timer = QTimer(self)
        self.logo_timer.setInterval(33)
        self.logo_timer.timeout.connect(self.animate_logo)
        
        self.logo_timer.start()
        self.clock = None
        self.logo_pixmap = QPixmap()

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setMouseTracking(True)

        self.load_logo()
        self.update_dimensions()
        self.create_clock()
        self.position_panel()

        self.show()
        self.raise_()

    def current_theme(self):
        return self.settings_data.get(
            "theme", "Emerald Aurora"
        )

    def color(self, key, alpha=255):
        return theme_color(self.current_theme(), key, alpha)

    def animate_logo(self):
        self.logo_animation += 0.035
        if self.logo_animation >= math.tau:
            self.logo_animation -= math.tau
        self.update()

    def create_clock(self):
        if not self.settings_data.get("clock_enabled", True):
            return

        if self.clock is not None:
            return

        self.clock = AuroraVortexClock(
            self,
            self.current_theme()
        )

        self.position_clock()
        self.clock.show()
        self.clock.raise_()
        self.clock.start()

    def destroy_clock(self):
        if self.clock is None:
            return

        clock = self.clock
        self.clock = None

        clock.stop()
        clock.hide()
        clock.setParent(None)
        clock.deleteLater()

    def position_clock(self):
        if self.clock is None:
            return

        x = self.width() - self.CLOCK_SIZE - 10
        y = (self.height() - self.CLOCK_SIZE) // 2

        self.clock.move(x, y)

    def load_logo(self):
        self.logo_pixmap = QPixmap()
        path = self.settings_data.get("logo_path", "")

        if path and os.path.isfile(path):
            self.logo_pixmap.load(path)

    def update_dimensions(self):
        width = int(self.settings_data.get("width", 410))
        width = clamp(width, 330, 720)

        self.setFixedSize(width, self.PANEL_HEIGHT)
        self.position_clock()

    def position_panel(self):
        margin = int(self.settings_data.get("margin", 14))

        width = self.width()
        height = self.height()

        canvas_width = self.canvas.width()
        canvas_height = self.canvas.height()

        position = self.settings_data.get(
            "position", "Top right"
        )

        if position == "Top left":
            x, y = margin, margin
        elif position == "Bottom left":
            x, y = margin, canvas_height - height - margin
        elif position == "Bottom right":
            x = canvas_width - width - margin
            y = canvas_height - height - margin
        else:
            x = canvas_width - width - margin
            y = margin

        x = clamp(x, 0, max(0, canvas_width - width))
        y = clamp(y, 0, max(0, canvas_height - height))

        self.move(x, y)
        self.position_clock()

    # --------------------------------------------------------
    # PANEL BACKGROUND
    # --------------------------------------------------------

    def draw_background(self, painter):
        rect = QRectF(0, 0, self.width(), self.height())

        opacity = int(self.settings_data.get("opacity", 94))
        alpha = int(255 * clamp(opacity, 20, 100) / 100.0)

        gradient = QLinearGradient(
            rect.topLeft(), rect.bottomRight()
        )

        gradient.setColorAt(0.0, self.color("panel", alpha))
        gradient.setColorAt(0.48, self.color("panel_mid", alpha))
        gradient.setColorAt(1.0, self.color("panel_edge", alpha))

        path = QPainterPath()
        path.addRoundedRect(rect, 20, 20)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        highlight = QLinearGradient(
            0, 0, self.width(), self.height()
        )

        highlight.setColorAt(
            0.0, self.color("panel_glow", 40)
        )
        highlight.setColorAt(
            0.5, self.color("panel_glow", 5)
        )
        highlight.setColorAt(
            1.0, QColor(0, 0, 0, 0)
        )

        painter.setBrush(QBrush(highlight))
        painter.drawPath(path)

        painter.setPen(QPen(self.color("border", 210), 1.3))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        inner = QRectF(
            5, 5,
            self.width() - 10,
            self.height() - 10
        )

        painter.setPen(QPen(QColor(255, 255, 255, 28), 0.8))
        painter.drawRoundedRect(inner, 16, 16)

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    def draw_logo(self, painter):
        if self.logo_pixmap.isNull():
            return

        scaled = self.logo_pixmap.scaled(
            QSize(58, 58),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        painter.drawPixmap(22, 24, scaled)




    def draw_content(self, painter):
        left = 24

        if not self.logo_pixmap.isNull():
            self.draw_logo(painter)
            left = 92

        # ----------------------------------------
        # ANIMATED GOLD + EMERALD FjBa TITLE
        # ----------------------------------------

        title = str(self.settings_data.get("title", "FjBa"))
        t = self.logo_animation
        pulse = 0.5 + 0.5 * math.sin(t * 2.0)

        font = QFont("Segoe UI", 25, QFont.Bold)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setFont(font)

        # Build the exact letter shapes
        title_path = QPainterPath()
        title_path.addText(left, 60, font, title)
        bounds = title_path.boundingRect()

        # Soft emerald outer glow
        for width, alpha in (
            (10, int(18 + pulse * 15)),
            (7, int(30 + pulse * 20)),
            (4, int(55 + pulse * 25))
        ):
            glow = QPen(
                self.color("emerald", alpha),
                width
            )
            glow.setJoinStyle(Qt.RoundJoin)
            painter.setPen(glow)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(title_path)

        # Gold-to-emerald metallic lettering
        metal = QLinearGradient(
            0, bounds.top(),
            0, bounds.bottom()
        )

        metal.setColorAt(0.0, QColor(255, 255, 220))
        metal.setColorAt(0.20, QColor(255, 215, 105))
        metal.setColorAt(0.42, QColor(35, 235, 165))
        metal.setColorAt(0.68, QColor(5, 135, 100))
        metal.setColorAt(0.88, QColor(205, 255, 225))
        metal.setColorAt(1.0, QColor(255, 205, 90))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(metal))
        painter.drawPath(title_path)

        # Moving golden-white reflection, clipped to letters
        painter.save()
        painter.setClipPath(title_path)

        sweep = (t * 0.45) % 1.0
        shine_x = (
            bounds.left() - 35
            + sweep * (bounds.width() + 70)
        )

        shine = QLinearGradient(
            shine_x - 18, bounds.top(),
            shine_x + 18, bounds.bottom()
        )

        shine.setColorAt(0.0, QColor(255, 255, 255, 0))
        shine.setColorAt(
            0.5,
            QColor(255, 245, 190, int(130 + pulse * 100))
        )
        shine.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.fillRect(bounds, QBrush(shine))
        painter.restore()

        # Subtle emerald highlight along the lower edge
        edge = QPen(
            QColor(80, 255, 190, int(70 + pulse * 80)),
            1
        )
        painter.setPen(edge)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(title_path)

        painter.restore()

        # ----------------------------------------
        # SUBTITLE
        # ----------------------------------------

        painter.setPen(self.color("subtitle"))
        painter.setFont(QFont("Segoe UI", 8, QFont.DemiBold))

        painter.drawText(
            left, 85,
            str(self.settings_data.get(
                "subtitle", "LIVE MAP BRANDING"
            ))
        )

        # ----------------------------------------
        # DIVIDER
        # ----------------------------------------

        divider = QLinearGradient(
            left, 98, self.width() - 190, 98
        )

        divider.setColorAt(
            0.0, self.color("panel_glow", 220)
        )

        divider.setColorAt(
            1.0, self.color("panel_glow", 0)
        )

        painter.setPen(QPen(QBrush(divider), 1.3))
        painter.drawLine(
            left, 98, self.width() - 190, 98
        )

        # ----------------------------------------
        # FOOTER
        # ----------------------------------------

        painter.setPen(self.color("footer"))
        painter.setFont(QFont("Segoe UI", 7))

        painter.drawText(
            left, 121,
            str(self.settings_data.get(
                "footer", "GEOSPATIAL VISUAL EXPERIENCE"
            ))
        )

        # LIVE STATUS
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color("status"))
        painter.drawEllipse(
            QPointF(left + 4, 151), 3, 3
        )

        painter.setBrush(self.color("status", 45))
        painter.drawEllipse(
            QPointF(left + 4, 151), 8, 8
        )

        painter.setPen(self.color("footer"))
        painter.setFont(QFont("Segoe UI", 7))

        painter.drawText(
            left + 18, 155, "LIVE MAP SYSTEM"
        )


    # --------------------------------------------------------
    # PAINT
    # --------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(
            QPainter.SmoothPixmapTransform, True
        )

        self.draw_background(painter)
        self.draw_content(painter)

        painter.end()

    # --------------------------------------------------------
    # RESIZE AND DRAGGING
    # --------------------------------------------------------

    def resizeEvent(self, event):
        self.position_clock()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True

            canvas_mouse = self.canvas.mapFromGlobal(
                event.globalPos()
            )

            self.drag_offset = canvas_mouse - self.pos()
            self.setCursor(Qt.ClosedHandCursor)

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            canvas_position = self.canvas.mapFromGlobal(
                event.globalPos()
            )

            new_position = canvas_position - self.drag_offset

            x = clamp(
                new_position.x(),
                0,
                max(0, self.canvas.width() - self.width())
            )

            y = clamp(
                new_position.y(),
                0,
                max(0, self.canvas.height() - self.height())
            )

            self.move(x, y)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.unsetCursor()
            self.snap_to_corner()

            event.accept()
            return

        super().mouseReleaseEvent(event)

    # --------------------------------------------------------
    # SNAP TO CORNER
    # --------------------------------------------------------

    def snap_to_corner(self):
        margin = int(self.settings_data.get("margin", 14))

        cw = self.canvas.width()
        ch = self.canvas.height()

        w = self.width()
        h = self.height()

        corners = {
            "Top left": QPoint(margin, margin),
            "Top right": QPoint(cw - w - margin, margin),
            "Bottom left": QPoint(margin, ch - h - margin),
            "Bottom right": QPoint(
                cw - w - margin, ch - h - margin
            )
        }

        current = self.pos()

        nearest = min(
            corners,
            key=lambda name: (
                (corners[name].x() - current.x()) ** 2
                + (corners[name].y() - current.y()) ** 2
            )
        )

        self.settings_data["position"] = nearest
        write_setting("position", nearest)

        self.position_panel()

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    def refresh(self, settings):
        self.settings_data = dict(settings)

        self.load_logo()
        self.update_dimensions()

        if self.settings_data.get("clock_enabled", True):
            if self.clock is None:
                self.create_clock()
            else:
                self.clock.set_theme(self.current_theme())
                self.position_clock()
                self.clock.start()
                self.clock.show()
                self.clock.raise_()
        else:
            self.destroy_clock()

        self.position_panel()
        self.update()
        self.raise_()

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    def closeEvent(self, event):
        self.destroy_clock()
        event.accept()


# ============================================================
# SETTINGS DIALOG
# ============================================================

class FjBaSettingsDialog(QDialog):

    def __init__(self, settings, parent=None):
        super().__init__(parent)

        self.settings_data = dict(settings)

        self.setWindowTitle(
            "FjBa Live Map Branding Settings"
        )

        self.setMinimumWidth(430)
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)

        heading = QLabel("FjBa LIVE MAP BRANDING")

        heading.setStyleSheet(
            """
            QLabel {
                color: #35e0a9;
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        layout.addWidget(heading)

        subheading = QLabel(
            "Aurora Vortex — Enterprise Edition V1.8"
        )

        subheading.setStyleSheet("color: #9abbb0;")
        layout.addWidget(subheading)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        form = QFormLayout()

        self.position_combo = QComboBox()
        self.position_combo.addItems(POSITIONS)
        self.position_combo.setCurrentText(
            self.settings_data.get("position", "Top right")
        )

        form.addRow("Panel position:", self.position_combo)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(330, 720)
        self.width_spin.setValue(
            int(self.settings_data.get("width", 410))
        )

        form.addRow("Panel width:", self.width_spin)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(
            int(self.settings_data.get("opacity", 94))
        )

        form.addRow("Panel opacity:", self.opacity_slider)

        self.margin_spin = QSpinBox()
        self.margin_spin.setRange(0, 100)
        self.margin_spin.setValue(
            int(self.settings_data.get("margin", 14))
        )

        form.addRow("Panel margin:", self.margin_spin)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEME_NAMES)

        current_theme = self.settings_data.get(
            "theme", "Emerald Aurora"
        )

        if current_theme not in THEME_NAMES:
            current_theme = "Emerald Aurora"

        self.theme_combo.setCurrentText(current_theme)

        form.addRow("Visual theme:", self.theme_combo)

        layout.addLayout(form)

        self.clock_checkbox = QCheckBox(
            "Enable Aurora Vortex clock"
        )

        self.clock_checkbox.setChecked(
            setting_as_bool(
                self.settings_data.get("clock_enabled", True)
            )
        )

        layout.addWidget(self.clock_checkbox)

        self.logo_label = QLabel()
        self.update_logo_label()
        layout.addWidget(self.logo_label)

        logo_button = QPushButton("Choose PNG / JPG logo")
        logo_button.clicked.connect(self.choose_logo)
        layout.addWidget(logo_button)

        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)

        save = QPushButton("Save settings")
        save.clicked.connect(self.accept)
        save.setDefault(True)

        buttons.addWidget(cancel)
        buttons.addWidget(save)

        layout.addLayout(buttons)

        self.setStyleSheet(
            """
            QDialog {
                background: #10241f;
                color: #e7fff6;
            }

            QLabel {
                color: #d7eee6;
            }

            QComboBox, QSpinBox {
                background: #183a30;
                color: white;
                border: 1px solid #279a70;
                padding: 5px;
                border-radius: 4px;
            }

            QPushButton {
                background: #087d5b;
                color: white;
                border: 1px solid #28c995;
                padding: 8px 12px;
                border-radius: 5px;
            }

            QPushButton:hover {
                background: #0b9b70;
            }

            QCheckBox {
                color: #c7f7e5;
                padding: 5px;
            }

            QSlider::groove:horizontal {
                background: #24483c;
                height: 5px;
            }

            QSlider::handle:horizontal {
                background: #25d9a2;
                width: 13px;
                margin: -5px 0;
                border-radius: 6px;
            }
            """
        )

    def update_logo_label(self):
        path = self.settings_data.get("logo_path", "")

        if path:
            self.logo_label.setText(os.path.basename(path))
        else:
            self.logo_label.setText("No logo selected")

    def choose_logo(self):
        filename, unused_filter = QFileDialog.getOpenFileName(
            self,
            "Choose logo",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if filename:
            self.settings_data["logo_path"] = filename
            self.update_logo_label()

    def get_settings(self):
        return {
            "enabled": True,
            "position": self.position_combo.currentText(),
            "width": self.width_spin.value(),
            "opacity": self.opacity_slider.value(),
            "margin": self.margin_spin.value(),
            "clock_enabled": self.clock_checkbox.isChecked(),
            "logo_path": self.settings_data.get("logo_path", ""),
            "title": self.settings_data.get("title", "FjBa"),
            "subtitle": self.settings_data.get(
                "subtitle", "LIVE MAP BRANDING"
            ),
            "footer": self.settings_data.get(
                "footer", "GEOSPATIAL VISUAL EXPERIENCE"
            ),
            "theme": self.theme_combo.currentText()
        }


# ============================================================
# CONTROLLER
# ============================================================

class FjBaLiveBrandingController(QObject):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface
        self.canvas = iface.mapCanvas()

        self.overlay = None
        self.settings = self.load_settings()

        self.canvas.installEventFilter(self)

    def load_settings(self):
        result = {}

        for key, default in DEFAULTS.items():
            value = read_setting(key, default)

            if key in ("enabled", "clock_enabled"):
                value = setting_as_bool(value)

            elif key in ("width", "opacity", "margin"):
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    value = default

            result[key] = value

        if result["position"] not in POSITIONS:
            result["position"] = DEFAULTS["position"]

        if result["theme"] not in THEME_NAMES:
            result["theme"] = DEFAULTS["theme"]

        result["width"] = clamp(result["width"], 330, 720)
        result["opacity"] = clamp(result["opacity"], 20, 100)
        result["margin"] = clamp(result["margin"], 0, 100)

        return result

    def save_settings(self):
        for key, value in self.settings.items():
            write_setting(key, value)

    def show(self):
        self.settings["enabled"] = True
        self.save_settings()

        if self.overlay is None:
            self.overlay = FjBaBrandingOverlay(
                self.canvas,
                self.settings
            )
        else:
            self.overlay.refresh(self.settings)
            self.overlay.show()
            self.overlay.raise_()

        self.overlay.position_panel()

    def hide(self):
        self.settings["enabled"] = False
        self.save_settings()

        if self.overlay is not None:
            overlay = self.overlay
            self.overlay = None

            overlay.close()
            overlay.deleteLater()

    def toggle(self):
        if self.overlay and self.overlay.isVisible():
            self.hide()
        else:
            self.show()

    def show_settings(self):
        dialog = FjBaSettingsDialog(
            self.settings,
            self.iface.mainWindow()
        )

        if dialog.exec_() == QDialog.Accepted:
            self.settings.update(dialog.get_settings())
            self.settings["enabled"] = True

            self.save_settings()
            self.show()

    def eventFilter(self, watched, event):
        if watched == self.canvas:
            if event.type() in (QEvent.Resize, QEvent.Show):
                if self.overlay is not None:
                    self.overlay.position_panel()
                    self.overlay.position_clock()
                    self.overlay.raise_()

        return False

    def cleanup(self):
        try:
            self.canvas.removeEventFilter(self)
        except Exception:
            pass

        if self.overlay is not None:
            overlay = self.overlay
            self.overlay = None

            overlay.close()
            overlay.deleteLater()


# ============================================================
# MAIN QGIS PLUGIN
# ============================================================

class FjBaLiveMapBranding:

    def __init__(self, iface):
        self.iface = iface

        self.controller = None
        self.toggle_action = None
        self.settings_action = None

        self.menu_name = "FjBa"

    def initGui(self):
        try:
            self.controller = FjBaLiveBrandingController(
                self.iface
            )

            self.toggle_action = QAction(
                "FjBa Live Map Branding",
                self.iface.mainWindow()
            )

            self.toggle_action.setCheckable(True)

            self.toggle_action.setChecked(
                bool(
                    self.controller.settings.get(
                        "enabled", True
                    )
                )
            )

            self.toggle_action.triggered.connect(
                self.toggle_branding
            )

            self.iface.addToolBarIcon(self.toggle_action)

            self.iface.addPluginToMenu(
                self.menu_name,
                self.toggle_action
            )

            self.settings_action = QAction(
                "FjBa Branding Settings",
                self.iface.mainWindow()
            )

            self.settings_action.triggered.connect(
                self.open_settings
            )

            self.iface.addPluginToMenu(
                self.menu_name,
                self.settings_action
            )

            if self.controller.settings.get("enabled", True):
                self.controller.show()

            log_message("FjBa Aurora Vortex V2.1 loaded.")

        except Exception as error:
            log_message(
                "Initialization error: {}".format(error),
                Qgis.Critical
            )

            log_message(
                traceback.format_exc(),
                Qgis.Critical
            )

            QMessageBox.critical(
                self.iface.mainWindow(),
                PLUGIN_NAME,
                "Plugin initialization failed:\n{}".format(error)
            )

    def toggle_branding(self, checked=False):
        if self.controller is None:
            return

        if checked:
            self.controller.show()
        else:
            self.controller.hide()

        if self.toggle_action is not None:
            self.toggle_action.setChecked(bool(checked))

    def open_settings(self):
        if self.controller is None:
            return

        self.controller.show_settings()

        if self.toggle_action is not None:
            self.toggle_action.setChecked(
                bool(
                    self.controller.settings.get(
                        "enabled", True
                    )
                )
            )

    def unload(self):
        try:
            if self.controller is not None:
                self.controller.cleanup()
                self.controller = None

            if self.toggle_action is not None:
                self.iface.removeToolBarIcon(
                    self.toggle_action
                )

                self.iface.removePluginMenu(
                    self.menu_name,
                    self.toggle_action
                )

                self.toggle_action.deleteLater()
                self.toggle_action = None

            if self.settings_action is not None:
                self.iface.removePluginMenu(
                    self.menu_name,
                    self.settings_action
                )

                self.settings_action.deleteLater()
                self.settings_action = None

            log_message("FjBa Aurora Vortex V1.8 unloaded.")

        except Exception:
            log_message(
                traceback.format_exc(),
                Qgis.Warning
            )
