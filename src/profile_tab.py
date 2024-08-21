from PySide6.QtWidgets import QPushButton, QSizePolicy, QVBoxLayout, QWidget

from add_client_dialog import AddClientDialog
from add_food_dialog import AddFoodDialog
from delete_client_dialog import DeleteClientDialog
from delete_food_dialog import DeleteFoodDialog


class ProfileTab(QWidget):
    """An extra tab that prompts the user to add or delete client/food"""

    def __init__(self):
        super().__init__()

        self._add_client = QPushButton("Ajouter un client")
        self._delete_client = QPushButton("Supprimer le client")
        self._add_food = QPushButton("Ajouter de la nourriture")
        self._delete_food = QPushButton("Supprimer la nourriture")

        layout = QVBoxLayout()
        layout.addWidget(self._add_client)
        layout.addWidget(self._delete_client)
        layout.addWidget(self._add_food)
        layout.addWidget(self._delete_food)

        self.setLayout(layout)

        self._add_client.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self._delete_client.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self._add_food.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self._delete_food.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.update_fonts()

        self._add_client.clicked.connect(self.add_client)
        self._delete_client.clicked.connect(self.delete_client)
        self._add_food.clicked.connect(self.add_food)
        self._delete_food.clicked.connect(self.delete_food)

    def add_client(self):
        add_dialog = AddClientDialog()
        add_dialog.exec()

    def delete_client(self):
        delete_dialog = DeleteClientDialog()
        delete_dialog.exec()

    def add_food(self):
        add_dialog = AddFoodDialog()
        add_dialog.exec()

    def delete_food(self):
        delete_dialog = DeleteFoodDialog()
        delete_dialog.exec()

    def update_fonts(self):
        font = self._add_client.font()

        BASE_SIZE = 15
        SCALING = 0.01

        font_size = BASE_SIZE + SCALING * self.width()
        font.setPointSize(font_size)

        self._add_client.setFont(font)
        self._delete_client.setFont(font)
        self._add_food.setFont(font)
        self._delete_food.setFont(font)

    def resizeEvent(self, event):
        self.update_fonts()
        super().resizeEvent(event)
