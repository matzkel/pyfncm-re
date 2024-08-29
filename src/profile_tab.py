import asyncio

import aiosqlite as sql
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
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

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        bottom_bar = QHBoxLayout()
        _add_order = QPushButton("Ajouter une commande")
        _delete_order = QPushButton("Supprimer la commande")
        bottom_bar.addWidget(_add_order)
        bottom_bar.addWidget(_delete_order)

        layout = QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(self.table)
        layout.addLayout(bottom_bar)

        self.setLayout(layout)

        _delete_profile.clicked.connect(self.delete_profile)

        _add_order.clicked.connect(self.add_order)
        _delete_order.clicked.connect(self.delete_order)

        self.update_table()

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

    def update_table(self):
        self.table.clear()
        self._orders = asyncio.run(self.get_orders(), debug=False)
        # Populate a table if there are any orders
        if self._orders:
            # Do not account for order id and food colors
            self.table.setColumnCount(len(self._orders[0]) - 4)
            self.table.setRowCount(len(self._orders))
            self.table.setHorizontalHeaderLabels(
                [
                    "Prénom",
                    "Nom de famille",
                    "Addresse",
                    "Numéro de téléphone",
                    "Nom de la nourriture",
                    "Quantité",
                    "Date",
                ]
            )

            for row, (
                _,
                first_name,
                last_name,
                address,
                phone_number,
                food_name,
                red_color,
                green_color,
                blue_color,
                food_quantity,
                date,
            ) in enumerate(self._orders):
                self.table.setItem(row, 0, QTableWidgetItem(first_name))
                self.table.setItem(row, 1, QTableWidgetItem(last_name))
                self.table.setItem(row, 2, QTableWidgetItem(address))
                self.table.setItem(row, 3, QTableWidgetItem(phone_number))
                self.table.setItem(row, 4, QTableWidgetItem(food_name))
                if None not in (red_color, green_color, blue_color):
                    rgb = (red_color, green_color, blue_color)
                    self.table.item(row, 4).setBackground(
                        QColor(red_color, green_color, blue_color)
                    )
                    self.table.item(row, 4).setForeground(
                        self.get_foreground_color(rgb)
                    )
                self.table.setItem(row, 5, QTableWidgetItem(str(food_quantity)))
                self.table.setItem(row, 6, QTableWidgetItem(date))

            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
            # Add 35, lest part of the last section gets swallowed
            self.setMinimumWidth(header.length() + 35)

            header.setSectionResizeMode(2, QHeaderView.Stretch)

    async def get_orders(self):
        """Return a list containing 1000 last orders for current profile."""
        orders = []
        async with sql.connect("data.db") as db:
            operation = f"""SELECT 
                                {self._profile_name}.id,
                                first_name,
                                last_name,
                                address,
                                phone_number,
                                food_name,
                                red_color,
                                green_color,
                                blue_color,
                                food_quantity,
                                date
                            FROM
                                {self._profile_name}
                                INNER JOIN clients ON {self._profile_name}.client_id = clients.id
                                INNER JOIN food ON {self._profile_name}.food_id = food.id
                            ORDER BY
                                date DESC,
                                first_name,
                                last_name
                            LIMIT
                                1000;"""
            async with db.execute(operation) as cursor:
                async for row in cursor:
                    orders.append(row)
        # Return reversed list so it actually shows the early dates first
        return orders[-1::-1]

    def get_foreground_color(self, color):
        """Return black/white color depending on calculated luminance."""
        (red_color, green_color, blue_color) = color
        luminance = 0.2126 * red_color + 0.7152 * green_color + 0.0722 * blue_color
        return QColor(255, 255, 255) if luminance < 140 else QColor(0, 0, 0)

    def add_order(self):
        add_order_dialog = AddOrderDialog(self)
        add_order_dialog.exec()

    def delete_order(self):
        raise NotImplementedError()
