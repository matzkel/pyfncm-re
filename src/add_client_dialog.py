from PySide6.QtWidgets import QDialog


class AddClientDialog(QDialog):
    """A dialog to add a new client to the database"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")
