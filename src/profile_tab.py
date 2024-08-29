import asyncio

import aiosqlite as sql
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from add_order_dialog import AddOrderDialog
from logger import get_logger


class ProfileTab(QWidget):
    """An extra tab that shows selected profile and offers to create/delete orders and etc."""

    def __init__(self, parent, profile_name):
        super().__init__()
        self._parent = parent
        self._profile_name = profile_name

        top_bar = QHBoxLayout()
        _delete_profile = QPushButton("Supprimer le profil")
        search = QPushButton("Recherche")
        top_bar.addWidget(_delete_profile, 4)
        top_bar.addWidget(search, 12)

        table = QTableWidget()
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        bottom_bar = QHBoxLayout()
        _add_order = QPushButton("Ajouter une commande")
        _delete_order = QPushButton("Supprimer la commande")
        bottom_bar.addWidget(_add_order)
        bottom_bar.addWidget(_delete_order)

        layout = QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(table)
        layout.addLayout(bottom_bar)

        self.setLayout(layout)

        _delete_profile.clicked.connect(self.delete_profile)

        _add_order.clicked.connect(self.add_order)
        _delete_order.clicked.connect(self.delete_order)

    async def delete_profile_from_database(self, logger):
        """Delete a profile from the database."""
        async with sql.connect("data.db") as db:
            # No need to sanitize, since profile names are sanitized on creation
            await db.execute(f"DROP TABLE IF EXISTS {self._profile_name};")
        QMessageBox.information(
            self,
            "Succès!",
            f"Le profil ({self._profile_name}) a été supprimé de la base de données.",
        )
        logger.info(f"Deleted table ({self._profile_name}) from the database.")
        self.close()

    def delete_profile(self):
        logger = get_logger("profile_tab.py")

        question = QMessageBox.question(
            self,
            "Es-tu sûr?",
            f"Êtes-vous sûr de vouloir supprimer le profil ({self._profile_name}) de la base de données?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if question == QMessageBox.No:
            return

        asyncio.run(self.delete_profile_from_database(logger), debug=False)

        idx = self._parent._profiles.index(self._profile_name)
        # Add 1 to account for main actions tab
        self._parent.removeTab(idx + 1)
        self._parent._profiles.pop(idx)

    def add_order(self):
        add_order_dialog = AddOrderDialog(self._profile_name)
        add_order_dialog.exec()

    def delete_order(self):
        raise NotImplementedError()
