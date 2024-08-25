import asyncio

import aiosqlite as sql
from PySide6.QtGui import QColor
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


class DeleteFoodDialog(QDialog):
    """A dialog to delete a food from the database."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")

        table = QTableWidget()
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self._food = asyncio.run(self.get_food())
        self.__food_idx = None

        # Populate a table if there is any food
        if self._food:
            table.setColumnCount(1)
            table.setRowCount(len(self._food))
            table.setHorizontalHeaderLabels(["Nom de la nourriture"])

            for row, (_, food_name, red_color, green_color, blue_color) in enumerate(
                self._food
            ):
                item = QTableWidgetItem(food_name)
                if None not in (red_color, green_color, blue_color):
                    item.setBackground(QColor(red_color, green_color, blue_color))
                    item.setForeground(
                        QColor(
                            self.get_foreground_color(
                                (red_color, green_color, blue_color)
                            )
                        )
                    )
                table.setItem(row, 0, item)

            table.cellClicked.connect(lambda row, _: self.set_food_idx(row))

            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
            # Add 35, lest part of the section gets swallowed
            self.setMinimumWidth(header.length() + 35)

            header.setSectionResizeMode(QHeaderView.Stretch)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout(self)
        layout.addWidget(table)
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def set_food_idx(self, row):
        """Set food row index (through clicking table item)."""
        self.__food_idx = row

    def get_food_idx(self):
        """Return chosen client row index (through clicking table item)."""
        return self.__food_idx

    def get_foreground_color(self, color):
        """Return black/white color depending on calculated luminance."""
        (red_color, green_color, blue_color) = color
        luminance = 0.2126 * red_color + 0.7152 * green_color + 0.0722 * blue_color
        return QColor(255, 255, 255) if luminance < 140 else QColor(0, 0, 0)

    async def get_food(self):
        """Return a list containing food from the database."""
        food = []
        async with sql.connect("data.db") as db:
            async with db.execute(
                "SELECT id, food_name, red_color, green_color, blue_color FROM food;"
            ) as cursor:
                async for row in cursor:
                    food.append(row)
        return food

    async def delete_food_from_database(self, logger, data):
        """Delete food from the database."""
        # TODO: Delete also orders from all profiles when implemented.
        (food_id, food_name, red_color, green_color, blue_color) = data

        async with sql.connect("data.db") as db:
            operation = "DELETE FROM food WHERE id = (?);"
            await db.execute(operation, (food_id,))
            await db.commit()
        QMessageBox.information(
            self,
            "Succès!",
            f"La nourriture ({food_name}) a été supprimée de la base de données.",
        )
        if None not in (red_color, green_color, blue_color):
            logger.info(
                f"Deleted ({food_name}, {red_color}, {green_color}, {blue_color}) values from the 'food' table."
            )
        else:
            logger.info(f"Deleted ({food_name}) values from the 'food' table.")
        self.close()

    def accept(self):
        logger = getLogger("delete_food_dialog.py")

        row = self.get_food_idx()
        if row is None:
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "Veuillez choisir de la nourriture que vous souhaitez supprimer de la base de données.",
            )
            logger.warn("The food for deletion has not been chosen; choose one.")
            return

        (_, food_name, _, _, _) = self._food[row]
        question = QMessageBox.question(
            self,
            "Es-tu sûr?",
            f"Êtes-vous sûr de vouloir supprimer la nourriture ({food_name}) de la base de données?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if question == QMessageBox.No:
            return

        asyncio.run(self.delete_food_from_database(logger, self._food[row]))
