# https://www.activestate.com/resources/quick-reads/how-to-install-python-packages-using-a-script/
DEPENDENCIES = [
    "pywin32",
    "clipboard",
    "global_hotkeys",
    "keyboard"
]


def main():
    import sys, subprocess
    for dependency in DEPENDENCIES:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", dependency])


if __name__ == "__main__":
    main()
