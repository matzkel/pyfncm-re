from PySide6.QtWidgets import QDialog


class DeleteClientDialog(QDialog):
    """A dialog to delete a client from the database"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")
