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

from logger import getLogger


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
        add_order = QPushButton("Ajouter une commande")
        delete_order = QPushButton("Supprimer la commande")
        bottom_bar.addWidget(add_order)
        bottom_bar.addWidget(delete_order)

        layout = QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(table)
        layout.addLayout(bottom_bar)

        self.setLayout(layout)

        _delete_profile.clicked.connect(self.delete_profile)

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
        logger.info(
            f"The profile ({self._profile_name}) has been deleted from the database."
        )
        self.close()

    def delete_profile(self):
        logger = getLogger("profile_tab.py")

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
