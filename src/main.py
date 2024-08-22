# Nuitka specific compilation options
# nuitka-project-if: {OS} in ("Windows"):
#   nuitka-project: --onefile
#   nuitka-project: --mingw64
#   nuitka-project: --enable-plugin=pyside6
#   nuitka-project: --lto=yes
#   nuitka-project: --disable-console
#   nuitka-project: --output-dir=build\windows
#   nuitka-project: --output-filename=pyfncm
# nuitka-project-else:
#   nuitka-project: --onefile
#   nuitka-project: --enable-plugin=pyside6
#   nuitka-project: --lto=yes
#   nuitka-project: --output-dir=build/linux
#   nuitka-project: --output-filename=pyfncm

import aiosqlite as sql
from PySide6.QtWidgets import QApplication, QMainWindow

from logger import getLogger
from main_widget import MainWidget


class MainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")
        self.setCentralWidget(widget)


async def initialize_database(logger):
    """Initialize database if it doesn't exist."""
    async with sql.connect("data.db") as db:
        # Create clients table if it doesn't exist
        operation = """
                    CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY, first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL, address TEXT NOT NULL,
                        phone_number TEXT NOT NULL
                    );"""
        await db.execute(operation)
        await db.commit()

        # Create index for clients table on first name, last name and phone number
        operation = "CREATE INDEX IF NOT EXISTS first_name_idx ON clients(first_name);"
        await db.execute(operation)
        await db.commit()

        operation = "CREATE INDEX IF NOT EXISTS last_name_idx ON clients(last_name);"
        await db.execute(operation)
        await db.commit()

        operation = (
            "CREATE INDEX IF NOT EXISTS phone_number_idx ON clients(phone_number);"
        )
        await db.execute(operation)
        await db.commit()

        # Create food table if it doesn't exist
        operation = """
                    CREATE TABLE IF NOT EXISTS food (
                        id INTEGER PRIMARY KEY, food_name TEXT UNIQUE NOT NULL,
                        red_color INTEGER, green_color INTEGER,
                        blue_color INTEGER
                    );"""
        await db.execute(operation)
        await db.commit()
    logger.info("Database initialized...")


if __name__ == "__main__":
    """Run the application."""
    import asyncio
    import sys

    logger = getLogger("main.py")

    asyncio.run(initialize_database(logger), debug=False)

    app = QApplication([])
    logger.info("Application started...")

    main_window = MainWindow(MainWidget())
    main_window.show()
    sys.exit(app.exec())
