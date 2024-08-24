from PySide6.QtWidgets import QTabWidget

from actions_tab import ActionsTab


class MainWidget(QTabWidget):
    """The central widget of the application."""

    def __init__(self):
        super().__init__()

        actions_tab = ActionsTab()
        self.addTab(actions_tab, "Actions principales")
