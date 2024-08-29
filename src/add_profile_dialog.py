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

from logger import get_logger


class AddProfileDialog(QDialog):
    """A dialog to add a new profile to the database."""

    def __init__(self, parent, profiles):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")
        self._parent = parent
        self._profiles = profiles

        form_layout = QFormLayout()
        self._profile_name_line_edit = QLineEdit()
        self._profile_name_line_edit.setMaxLength(128)
        form_layout.addRow("&Nom du profil:", self._profile_name_line_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        height = layout.totalMinimumSize().height()
        self.setFixedHeight(height)
        self.setFixedWidth(512)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def scrub(self, text):
        """Return a string with only alphanumerics, stripped of all punctuation (except underscores) and whitespace."""
        sanitized_text = ""
        for ch in text:
            if not ch.isalnum() and ch != "_":
                raise ValueError
            sanitized_text += ch
        return sanitized_text

    async def add_profile_to_database(self, logger, profile_name):
        """Add new profile to the database."""
        async with sql.connect("data.db") as db:
            operation = f"""
                        CREATE TABLE IF NOT EXISTS {profile_name} (
                            id INTEGER PRIMARY KEY,
                            client_id INTEGER NOT NULL,
                            food_id INTEGER NOT NULL,
                            food_quantity INTEGER NOT NULL,
                            date TEXT NOT NULL,
                            FOREIGN KEY (client_id) REFERENCES clients(id),
                            FOREIGN KEY (food_id) REFERENCES food(id)
                        );"""
            await db.execute(operation)
        QMessageBox.information(
            self,
            "Succès!",
            f"Le profil ({profile_name}) a été ajouté à la base de données.",
        )
        logger.info(f"Added '{profile_name}' table to the database.")
        self.close()

    def accept(self):
        logger = get_logger("add_profile_dialog.py")

        profile_name = self._profile_name_line_edit.text().strip().title()
        if profile_name == "":
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "Le champ du nom du profil est vide; veuillez le remplir.",
                QMessageBox.Ok,
            )
            logger.warn("Profile name field is empty; please fill it.")
            return

        if profile_name in self._profiles:
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                f"Un profil avec le nom donné ({profile_name}) existe déjà dans la base de données.",
            )
            logger.warn(
                f"A profile with the given name ({profile_name}) already exists in the database."
            )
            return

        try:
            sanitized_profile_name = self.scrub(profile_name).title()
        except ValueError:
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                f"Le nom de profil de votre choix ({profile_name}) contient des caractères interdits et n'a pas pu être créé. Veuillez supprimer tous les caractères d'espacement ou les remplacer par des caractères de soulignement et supprimer toute la ponctuation.",
            )
            logger.warn(
                f"The profile name ({profile_name}) has forbidden character and couldn't be created."
            )
            return

        asyncio.run(
            self.add_profile_to_database(logger, sanitized_profile_name), debug=False
        )

        # Add new tab in the main widget and update _profiles variable
        self._parent.add_profile_tab(sanitized_profile_name)
        self._parent._profiles = asyncio.run(self._parent.get_profiles(), debug=False)
