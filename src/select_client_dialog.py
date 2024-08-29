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


class SelectClientDialog(QDialog):
    """A dialog to select a client from the database."""

    def __init__(self, parent):
        super().__init__()
        self._parent = parent
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
        """Set client row index (through clicking table item)."""
        self.__client_idx = row

    def get_client_idx(self):
        """Return chosen client row index (through clicking table item)."""
        return self.__client_idx

    async def get_clients(self):
        """Return a list containing clients from the database."""
        clients = []
        async with sql.connect("data.db") as db:
            async with db.execute(
                "SELECT id, first_name, last_name, address, phone_number FROM clients;"
            ) as cursor:
                async for row in cursor:
                    clients.append(row)
        return clients

    def accept(self):
        logger = getLogger("select_client_dialog.py")

        row = self.get_client_idx()
        if row is None:
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "Veuillez choisir le client.",
            )
            logger.warn("The client has not been chosen; choose one.")
            return

        (client_id, first_name, last_name, address, phone_number) = self._clients[row]
        self._parent.client_label.setText(
            f"Client: {first_name} {last_name}, {address}, {phone_number}"
        )
        self._parent.client_id = client_id
        self._parent.update_width()

        self.close()
