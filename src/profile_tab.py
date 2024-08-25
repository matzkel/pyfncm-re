from PySide6.QtWidgets import QWidget


class ProfileTab(QWidget):
    """An extra tab that shows selected profile and offers to create/delete orders and etc."""

    def __init__(self):
        super().__init__()
