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


def main():
    print("Hello, world!")


if __name__ == "__main__":
    main()
