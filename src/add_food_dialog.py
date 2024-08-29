import asyncio

import aiosqlite as sql
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from logger import get_logger


class AddFoodDialog(QDialog):
    """A dialog to add a new food to the database."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")

        form_layout = QFormLayout()
        self._food_name_line_edit = QLineEdit()
        self._food_name_line_edit.setMaxLength(128)
        form_layout.addRow("&Nom de la nourriture:", self._food_name_line_edit)

        self.__color = None

        color_picker = QHBoxLayout()
        _choose_color = QPushButton("Choisissez la couleur...")
        self._color_indicator = QPushButton("")
        self._color_indicator.setDisabled(True)
        color_picker.addWidget(_choose_color, 14)
        color_picker.addWidget(self._color_indicator, 2)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addLayout(color_picker)
        layout.addWidget(button_box)

        height = layout.totalMinimumSize().height()
        self.setFixedHeight(height)
        self.setFixedWidth(512)

        _choose_color.clicked.connect(self.choose_color)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def set_color(self, color):
        """Set an RGB representation of a color."""
        self.__color = color

    def get_color(self):
        """Get an RGB representation of a color."""
        return self.__color

    async def add_food_to_database(self, logger, data):
        """Add food to the database."""
        (food_name, color) = data

        async with sql.connect("data.db") as db:
            # Check if food with the exact name already exists in the database
            operation = """
                        SELECT
                            food_name
                        FROM
                            food
                        WHERE
                            food_name = (?);"""

            # Try to find food with the same name
            async with db.execute(operation, (food_name,)) as cursor:
                async for row in cursor:
                    # When found, don't do anything
                    QMessageBox.warning(
                        self,
                        "Une erreur s'est produite!",
                        f"La nourriture portant le nom donné ({food_name}) existe déjà dans la base de données.",
                        QMessageBox.Ok,
                    )
                    logger.warn(
                        f"The food with given name ({food_name}) already exists in the database."
                    )
                    return

            if color is None:
                (operation, values) = (
                    """
                    INSERT INTO food (food_name)
                    VALUES
                        (?);""",
                    (food_name,),
                )
            else:
                # color[0] = red; color[1] = green; color[2] = blue
                (operation, values) = (
                    """
                    INSERT INTO food (
                        food_name, red_color, green_color,
                        blue_color
                    ) 
                    VALUES
                        (?, ?, ?, ?);""",
                    (food_name, color[0], color[1], color[2]),
                )

            await db.execute(operation, values)
            await db.commit()
        QMessageBox.information(
            self,
            "Succès!",
            f"La nourriture ({food_name}) a été ajoutée à la base de données.",
        )
        if color is None:
            logger.info(f"Added ({food_name}) values into the 'food' table.")
        else:
            # color[0] = red; color[1] = green; color[2] = blue
            logger.info(
                f"Added ({food_name}, {color[0]}, {color[1]}, {color[2]}) values into the 'food' table."
            )
        self.close()

    def choose_color(self):
        choose_color_dialog = ChooseColorDialog(self)
        choose_color_dialog.exec()

    def accept(self):
        logger = get_logger("add_food_dialog.py")

        food_name = self._food_name_line_edit.text().strip().title()
        if food_name == "":
            QMessageBox.warning(
                self,
                "Une erreur s'est produite!",
                "Le champ du nom de la nourriture est vide; veuillez le remplir.",
                QMessageBox.Ok,
            )
            logger.warn("Food name field is empty; please fill it.")
            return

        user_data = (food_name, self.get_color())
        asyncio.run(self.add_food_to_database(logger, user_data), debug=False)


class ChooseColorDialog(QColorDialog):
    """A dialog to help select a color."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")

    def accept(self):
        # Get RGB representation of color without alpha
        (red, green, blue) = self.currentColor().getRgb()[:-1]
        self.parent.set_color(self.currentColor().getRgb()[:-1])

        self.parent._color_indicator.setStyleSheet(
            f"background-color: rgb({red}, {green}, {blue})"
        )
        self.close()
