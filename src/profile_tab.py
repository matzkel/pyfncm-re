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

        asyncio.run(self.delete_old_orders(), debug=False)

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

        self.table.cellClicked.connect(lambda row, _: self.set_order_idx(row))
        self.update_table()

    def set_order_idx(self, row):
        """Set order row index (through clicking table item)."""
        self.__order_idx = row

    def get_order_idx(self):
        """Return chosen order row index (through clicking table item)."""
        return self.__order_idx

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
        self._parent.actions_tab._profiles.pop(idx)

    def update_table(self):
        self.table.clear()
        self._orders = asyncio.run(self.get_orders(), debug=False)
        self.__order_idx = None
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
        else:
            self.table.setColumnCount(0)
            self.table.setRowCount(0)
            self.table.setHorizontalHeaderLabels([])

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

    async def delete_old_orders(self):
        """Delete old orders (i.e., 1 year old)."""
        logger = get_logger("profile_tab.py")
        async with sql.connect("data.db") as db:
            operation = f"DELETE FROM {self._profile_name} WHERE date <= date('now', '-1 year');"
            await db.execute(operation)
            await db.commit()
        logger.info(
            f"Deleted 1 year old orders from the database for table '{self._profile_name}'."
        )

    async def delete_order_from_database(self, logger, data):
        """Delete order from the database."""
        (
            order_id,
            first_name,
            last_name,
            address,
            phone_number,
            food_name,
            food_quantity,
            date,
        ) = data

        async with sql.connect("data.db") as db:
            operation = f"DELETE FROM {self._profile_name} WHERE id = (?);"
            await db.execute(operation, (order_id,))
            await db.commit()
        QMessageBox.information(
            self,
            "Succès!",
            f"La commande ({first_name} {last_name}, {address}, {phone_number}, {food_quantity}x {food_name}, {date}) a été supprimée du profil ({self._profile_name}).",
        )
        logger.info(
            f"Deleted values associated with order ({first_name}, {last_name}, {address}, {phone_number}, {food_name}, {food_quantity}, {date}) from the '{self._profile_name}' table."
        )

    def delete_order(self):
        logger = get_logger("profile_tab.py")

        row = self.get_order_idx()
        if row is None:
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "Veuillez choisir la commande que vous souhaitez supprimer de la base de données.",
            )
            logger.warn("The order for deletion has not been chosen; choose one.")
            return

        (
            order_id,
            first_name,
            last_name,
            address,
            phone_number,
            food_name,
            _,
            _,
            _,
            food_quantity,
            date,
        ) = self._orders[row]

        question = QMessageBox.question(
            self,
            "Es-tu sûr?",
            f"Êtes-vous sûr de vouloir supprimer la commande ({first_name} {last_name}, {address}, {phone_number}, {food_quantity}x {food_name}, {date}) ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if question == QMessageBox.No:
            return

        user_data = (
            order_id,
            first_name,
            last_name,
            address,
            phone_number,
            food_name,
            food_quantity,
            date,
        )
        asyncio.run(self.delete_order_from_database(logger, user_data), debug=False)
        self.update_table()
