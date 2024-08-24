import asyncio

import aiosqlite as sql
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from logger import getLogger


class DeleteClientDialog(QDialog):
    """A dialog to delete a client from the database"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")

        table = QTableWidget()
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self._clients = asyncio.run(self.get_clients())
        self.__client_idx = None

        # Populate a table if there are any clients
        if self._clients:
            table.setColumnCount(len(self._clients[0]) - 1)
            table.setRowCount(len(self._clients))
            table.setHorizontalHeaderLabels(
                ["Prénom", "Nom de famille", "Addresse", "Numéro de téléphone"]
            )

            for row, (_, first_name, last_name, address, phone_number) in enumerate(
                self._clients
            ):
                table.setItem(row, 0, QTableWidgetItem(first_name))
                table.setItem(row, 1, QTableWidgetItem(last_name))
                table.setItem(row, 2, QTableWidgetItem(address))
                table.setItem(row, 3, QTableWidgetItem(phone_number))

            table.cellClicked.connect(lambda row, _: self.set_client_idx(row))

            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
            # Add 35, lest part of the last section gets swallowed
            self.setMinimumWidth(header.length() + 35)

            header.setSectionResizeMode(2, QHeaderView.Stretch)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout(self)
        layout.addWidget(table)
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def set_client_idx(self, row):
        """Set client row index."""
        self.__client_idx = row

    def get_client_idx(self):
        """Return chosen client row index (through clicking table item)."""
        return self.__client_idx

    async def get_clients(self):
        """Return a list containing clients from the database"""
        clients = []
        async with sql.connect("data.db") as db:
            async with db.execute(
                "SELECT id, first_name, last_name, address, phone_number FROM clients"
            ) as cursor:
                async for row in cursor:
                    clients.append(row)
        return clients

    async def delete_client_from_database(self, logger, client):
        # TODO: Delete also orders from all profiles when implemented.
        (client_id, first_name, last_name, address, phone_number) = client

        async with sql.connect("data.db") as db:
            operation = "DELETE FROM clients WHERE id = (?);"
            await db.execute(operation, (client_id,))
            await db.commit()
        QMessageBox.information(
            self,
            "Succès!",
            f"Le client ({first_name} {last_name}, {address}, {phone_number}) a été supprimé de la base de données",
        )
        logger.info(
            f"Deleted ({first_name}, {last_name}, {address}, {phone_number}) values from the 'clients' table."
        )
        self.close()

    def accept(self):
        logger = getLogger("delete_client_dialog.py")

        row = self.get_client_idx()
        if row is None:
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "Veuillez choisir le client que vous souhaitez supprimer de la base de données.",
            )
            logger.warn("The client for deletion has not been chosen; choose one.")
            return

        (client_id, first_name, last_name, address, phone_number) = self._clients[row]

        question = QMessageBox.question(
            self,
            "Es-tu sûr?",
            f"Êtes-vous sûr de vouloir supprimer le client ({first_name} {last_name}, {address}, {phone_number}) de la base de données?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if question == QMessageBox.No:
            return

        asyncio.run(
            self.delete_client_from_database(logger, self._clients[row]), debug=False
        )
