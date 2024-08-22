from PySide6.QtWidgets import QTabWidget

from actions_tab import ActionsTab


class MainWidget(QTabWidget):
    """The central widget of the application."""

    def __init__(self):
        super().__init__()

        _profile_tab = ActionsTab()
        self.addTab(_profile_tab, "Actions principales")
