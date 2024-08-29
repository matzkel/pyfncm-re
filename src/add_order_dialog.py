import asyncio

import aiosqlite as sql
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from logger import get_logger
from select_client_dialog import SelectClientDialog
from select_food_dialog import SelectFoodDialog


class AddOrderDialog(QDialog):
    """A dialog to add a new order to the database."""

    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")
        self._parent = parent
        self._profile_name = parent._profile_name

        self.client_id = None
        self.client_label = QLabel("Client:")
        _select_client = QPushButton("Choisissez un client...")
        self.food_id = None
        self.food_label = QLabel("Nourriture:")
        _select_food = QPushButton("Choisir une nourriture...")

        date = QVBoxLayout()
        date_label = QLabel("Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        date.addWidget(date_label)
        date.addWidget(self.date_edit)

        quantity = QVBoxLayout()
        quantity_label = QLabel("Quantité:")
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setMinimum(1)
        quantity.addWidget(quantity_label)
        quantity.addWidget(self.quantity_spinbox)

        date_quantity_layout = QHBoxLayout()
        date_quantity_layout.addLayout(date)
        date_quantity_layout.addLayout(quantity)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout(self)
        layout.addWidget(self.client_label)
        layout.addWidget(_select_client)
        layout.addWidget(self.food_label)
        layout.addWidget(_select_food)
        layout.addLayout(date_quantity_layout)
        layout.addWidget(button_box)

        height = layout.totalMinimumSize().height()
        self.setFixedHeight(height)
        self.update_width()

        _select_client.clicked.connect(self.select_client)
        _select_food.clicked.connect(self.select_food)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def update_width(self):
        """Update dialog's width if client/food label exceeds certain width."""
        BASE_WIDTH = 512
        label_width = max(
            (self.client_label.minimumWidth(), self.food_label.minimumWidth())
        )
        if label_width > BASE_WIDTH:
            self.setFixedWidth(label_width)
        else:
            self.setFixedWidth(BASE_WIDTH)

    def select_client(self):
        select_client_dialog = SelectClientDialog(self)
        select_client_dialog.exec()

    def select_food(self):
        select_food_dialog = SelectFoodDialog(self)
        select_food_dialog.exec()

    async def add_order_to_database(self, logger, data):
        """Add order to the database."""
        async with sql.connect("data.db") as db:
            operation = f"""INSERT INTO {self._profile_name} (
                                client_id, food_id, food_quantity,
                                date
                            )
                            VALUES
                                (?, ?, ?, ?);"""
            await db.execute(operation, data)
            await db.commit()
        client = self.client_label.text().split(": ")[1]
        food = self.food_label.text().split(": ")[1]
        (client_id, food_id, food_quantity, date) = data
        QMessageBox.information(
            self,
            "Succès!",
            f"La commande de {client} pour {food_quantity}x {food} à {date} a été ajoutée au profil ({self._profile_name}).",
        )
        logger.info(
            f"Added values ({client_id}, {food_id}, {food_quantity}, {date}) into the '{self._profile_name}' table."
        )
        self.close()

    def accept(self):
        logger = get_logger("add_order_dialog.py")

        if None in (self.client_id, self.food_id):
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "Veuillez choisir client/nourriture pour créer une commande.",
            )
            logger.warn("The client/food has not been chosen; choose one.")
            return

        user_data = (
            self.client_id,
            self.food_id,
            self.quantity_spinbox.value(),
            self.date_edit.date().toString(Qt.DateFormat.ISODate),
        )

        asyncio.run(self.add_order_to_database(logger, user_data))
        self._parent.update_table()
