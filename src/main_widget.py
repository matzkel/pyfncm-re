import asyncio

import aiosqlite as sql
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTabWidget, QToolButton

from actions_tab import ActionsTab
from add_profile_dialog import AddProfileDialog
from profile_tab import ProfileTab


class MainWidget(QTabWidget):
    """The central widget of the application."""

    def __init__(self):
        super().__init__()

        add_button = QToolButton()
        # Add spaces around "+" because otherwise the button will look weird
        add_button.setText(" + ")
        add_button.setToolTip("Ajouter un nouveau profil")
        self.setCornerWidget(add_button, Qt.TopLeftCorner)

        actions_tab = ActionsTab()
        self.addTab(actions_tab, "Actions principales")

        self._profiles = asyncio.run(self.get_profiles(), debug=False)
        for profile in self._profiles:
            self.add_profile_tab(profile)

        add_button.clicked.connect(self.add_profile)

    def add_profile_tab(self, profile):
        """Add new profile tab to the main widget."""
        profile_tab = ProfileTab()
        self.addTab(profile_tab, profile)

    async def get_profiles(self):
        """Return all profiles."""
        tables = []
        async with sql.connect("data.db") as db:
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ) as cursor:
                async for table in cursor:
                    tables.append(table[0])

        # All profiles start with uppercase letter, so we check against that and return only them
        return [profile for profile in filter(lambda table: table[0].isupper(), tables)]

    def add_profile(self):
        """Add new profile to the database"""
        add_profile_dialog = AddProfileDialog(self, self._profiles)
        add_profile_dialog.exec()
