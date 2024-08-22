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
    """A dialog to add a new client to the database"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")

        form_layout = QFormLayout()
        self.first_name_line_edit = QLineEdit()
        self.first_name_line_edit.setMaxLength(128)
        form_layout.addRow("&Prénom:", self.first_name_line_edit)

        self.last_name_line_edit = QLineEdit()
        self.last_name_line_edit.setMaxLength(128)
        form_layout.addRow("&Nom de famille:", self.last_name_line_edit)

        self.address_line_edit = QLineEdit()
        self.address_line_edit.setMaxLength(128)
        form_layout.addRow("&Addresse:", self.address_line_edit)

        self.phone_number_line_edit = QLineEdit()
        self.phone_number_line_edit.setMaxLength(128)
        form_layout.addRow("&Numéro de téléphone:", self.phone_number_line_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        height = layout.totalMinimumSize().height()
        self.setFixedHeight(height)
        self.setMinimumWidth(512)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    async def add_client_to_database(self, logger, data):
        """Add client to the database."""
        async with sql.connect("data.db") as db:
            # Check if client with exact first name and last name already exists in the database
            operation = """
                        SELECT
                            first_name, last_name
                        FROM
                            clients
                        WHERE
                            first_name = (?)
                            AND last_name = (?);"""

            async with db.execute(operation, (data[0], data[1])) as cursor:
                async for row in cursor:
                    QMessageBox.warning(
                        self,
                        "Une erreur s'est produite!",
                        f"Le client avec le prénom ({data[0]}) et/ou le nom ({data[1]}) donné existe déjà dans la base de données.",
                        QMessageBox.Ok,
                    )
                    logger.warn(
                        f"Client with given first name ({data[0]}) and/or last name ({data[1]}) already exists in the database."
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
            f"Le client ({data[0]} {data[1]}, {data[2]}, {data[3]}) a été ajouté à la base de données.",
        )
        logger.info(
            f"Added ({data[0]}, {data[1]}, {data[2]}, {data[3]}) values into 'clients' table."
        )
        self.close()

    def accept(self):
        logger = getLogger("add_client_dialog.py")

        user_data = (
            self.first_name_line_edit.text().strip().title(),
            self.last_name_line_edit.text().strip().title(),
            self.address_line_edit.text().strip(),
            self.phone_number_line_edit.text().strip(),
        )

        if "" in user_data:
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "Un ou plusieurs champs sont vides, merci de les remplir.",
                QMessageBox.Ok,
            )
            logger.warn("One or more fields are empty, please fill them.")
            return

        asyncio.run(self.add_client_to_database(logger, user_data), debug=False)
