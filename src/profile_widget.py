from PySide6.QtWidgets import QTabWidget

from profile_tab import ProfileTab


class ProfileWidget(QTabWidget):
    """The central widget of the application."""

    def __init__(self):
        super().__init__()

        _profile_tab = ProfileTab()
        self.addTab(_profile_tab, "Actions principales")
