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

from logger import get_logger


class SelectFoodDialog(QDialog):
    """A dialog to select a food from the database."""

    def __init__(self, parent):
        super().__init__()
        self._parent = parent
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

    def accept(self):
        logger = get_logger("select_food_dialog.py")

        row = self.get_food_idx()
        if row is None:
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "S'il vous plaît choisir la nourriture.",
            )
            logger.warn("The food has not been chosen; choose one.")
            return

        (food_id, food_name, _, _, _) = self._food[row]
        self._parent.food_label.setText(f"Nourriture: {food_name}")

        self._parent.food_id = food_id
        self._parent.update_width()

        self.close()
