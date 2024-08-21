# Nuitka specific compilation options
# nuitka-project-if: {OS} in ("Windows"):
#   nuitka-project: --onefile
#   nuitka-project: --mingw64
#   nuitka-project: --lto=yes
#   nuitka-project: --disable-console
#   nuitka-project: --output-dir=build\windows
#   nuitka-project: --output-filename=pyfncm
# nuitka-project-else:
#   nuitka-project: --onefile
#   nuitka-project: --lto=yes
#   nuitka-project: --output-dir=build/linux
#   nuitka-project: --output-filename=pyfncm

from PySide6.QtWidgets import QApplication, QMainWindow

from profile_widget import ProfileWidget


class MainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        self.setWindowTitle("pyfncm - Python Food and Clientèle Manager")
        self.setCentralWidget(widget)


if __name__ == "__main__":
    """ Run the application. """
    import sys

    app = QApplication([])
    main_window = MainWindow(ProfileWidget())
    main_window.show()
    sys.exit(app.exec())
