from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class ProfileTab(QWidget):
    """An extra tab that shows selected profile and offers to create/delete orders and etc."""

    def __init__(self):
        super().__init__()

        top_bar = QHBoxLayout()
        delete_profile = QPushButton("Supprimer le profil")
        search = QPushButton("Recherche")
        top_bar.addWidget(delete_profile, 4)
        top_bar.addWidget(search, 12)

        table = QTableWidget()
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        bottom_bar = QHBoxLayout()
        add_order = QPushButton("Ajouter une commande")
        delete_order = QPushButton("Supprimer la commande")
        bottom_bar.addWidget(add_order)
        bottom_bar.addWidget(delete_order)

        layout = QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(table)
        layout.addLayout(bottom_bar)

        self.setLayout(layout)
