"""Shared, lightweight UI animations for SF Encryptor."""

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer
from PyQt6.QtWidgets import QGraphicsOpacityEffect


class AnimationManager:
    """Central animation service used by the main window and tabs."""

    def __init__(self, parent=None, settings=None):
        self.parent = parent
        settings = settings or {}
        self.enabled = settings.get("animations_enabled", True)
        self.transition_effects = settings.get("transition_effects", True)
        self.fade_duration = settings.get("fade_duration", 240)
        self.slide_duration = settings.get("slide_duration", 320)
        self._animations = []

    def set_enabled(self, enabled):
        self.enabled = enabled

    def set_transition_effects(self, enabled):
        self.transition_effects = enabled

    def set_fade_duration(self, duration):
        self.fade_duration = max(80, int(duration))

    def set_slide_duration(self, duration):
        self.slide_duration = max(100, int(duration))

    def _run_opacity(self, widget, start, end, duration):
        if not self.enabled or widget is None:
            return

        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        effect.setOpacity(start)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(duration)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animations.append(animation)

        def cleanup():
            if animation in self._animations:
                self._animations.remove(animation)
            if widget.graphicsEffect() is effect:
                widget.setGraphicsEffect(None)

        animation.finished.connect(cleanup)
        animation.start()

    def animate_page(self, widget):
        """Fade a newly selected page into view."""
        if self.transition_effects:
            self._run_opacity(widget, 0.0, 1.0, self.fade_duration)

    def animate_button_press(self, button):
        """Give button presses a subtle, non-blocking visual response."""
        if not self.enabled or button is None:
            return
        self._run_opacity(button, 0.68, 1.0, 140)

    def test_animation_showcase(self, window):
        """Preview the configured transition on the active window content."""
        if not self.enabled:
            return
        active_widget = getattr(window, "stacked_widget", None)
        if active_widget is not None:
            self.animate_page(active_widget.currentWidget())

        page_header = getattr(window, "page_title", None)
        if page_header is not None:
            QTimer.singleShot(80, lambda: self._run_opacity(
                page_header, 0.35, 1.0, self.fade_duration
            ))
