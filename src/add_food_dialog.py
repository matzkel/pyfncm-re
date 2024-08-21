from PySide6.QtWidgets import QDialog


class AddFoodDialog(QDialog):
    """A dialog to add a new food to the database"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")
