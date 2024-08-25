import asyncio

import aiosqlite as sql
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from logger import getLogger


class AddClientDialog(QDialog):
    """A dialog to add a new client to the database."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")

        form_layout = QFormLayout()
        self._first_name_line_edit = QLineEdit()
        self._first_name_line_edit.setMaxLength(128)
        form_layout.addRow("&Prénom:", self._first_name_line_edit)

        self._last_name_line_edit = QLineEdit()
        self._last_name_line_edit.setMaxLength(128)
        form_layout.addRow("&Nom de famille:", self._last_name_line_edit)

        self._address_line_edit = QLineEdit()
        self._address_line_edit.setMaxLength(128)
        form_layout.addRow("&Addresse:", self._address_line_edit)

        self._phone_number_line_edit = QLineEdit()
        self._phone_number_line_edit.setMaxLength(128)
        form_layout.addRow("&Numéro de téléphone:", self._phone_number_line_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        height = layout.totalMinimumSize().height()
        self.setFixedHeight(height)
        self.setFixedWidth(512)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    async def add_client_to_database(self, logger, data):
        """Add client to the database."""
        (first_name, last_name, address, phone_number) = data

        async with sql.connect("data.db") as db:
            # Check if a client with the exact first and last name already exists in the database
            operation = """
                        SELECT
                            first_name, last_name
                        FROM
                            clients
                        WHERE
                            first_name = (?)
                            AND last_name = (?);"""

            # Try to find client with the same first and last name
            async with db.execute(operation, (first_name, last_name)) as cursor:
                async for row in cursor:
                    # When found, don't do anything
                    QMessageBox.warning(
                        self,
                        "Une erreur s'est produite!",
                        f"Le client avec le prénom ({first_name}) et/ou le nom ({last_name}) donné existe déjà dans la base de données.",
                        QMessageBox.Ok,
                    )
                    logger.warn(
                        f"A client with the given first ({first_name}) and/or last name ({last_name}) already exists in the database."
                    )
                    return

            operation = """
                        INSERT INTO clients (
                            first_name, last_name, address, phone_number
                        )
                        VALUES
                            (?, ?, ?, ?);"""
            await db.execute(operation, data)
            await db.commit()
        QMessageBox.information(
            self,
            "Succès!",
            f"Le client ({first_name} {last_name}, {address}, {phone_number}) a été ajouté à la base de données.",
        )
        logger.info(
            f"Added ({first_name}, {last_name}, {address}, {phone_number}) values into the 'clients' table."
        )
        self.close()

    def accept(self):
        logger = getLogger("add_client_dialog.py")

        user_data = (
            self._first_name_line_edit.text().strip().title(),
            self._last_name_line_edit.text().strip().title(),
            self._address_line_edit.text().strip(),
            self._phone_number_line_edit.text().strip(),
        )

        if "" in user_data:
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "Un ou plusieurs champs sont vides; merci de les remplir.",
                QMessageBox.Ok,
            )
            logger.warn("One or more fields are empty; please fill them.")
            return

        asyncio.run(self.add_client_to_database(logger, user_data), debug=False)
