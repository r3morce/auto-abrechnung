"""Entry point: `python3 -m tui`."""

from tui.app import AbrechnungApp


def main() -> None:
    AbrechnungApp().run()


if __name__ == "__main__":
    main()
