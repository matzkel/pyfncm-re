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

from PySide6.QtWidgets import QApplication, QMainWindow

from logger import getLogger
from profile_widget import ProfileWidget


class MainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")
        self.setCentralWidget(widget)


if __name__ == "__main__":
    """ Run the application. """
    import sys

    logger = getLogger("main.py")

    app = QApplication([])
    logger.info("Application started...")

    main_window = MainWindow(ProfileWidget())
    main_window.show()
    sys.exit(app.exec())
