from PySide6.QtWidgets import QDialog


class DeleteFoodDialog(QDialog):
    """A dialog to delete a food from the database"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")
