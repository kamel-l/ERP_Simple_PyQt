import sys
from PyQt6.QtWidgets import QApplication
import qdarktheme
from sales_history import SalesHistoryPage

from app import ERPApp


def main():
    app = QApplication(sys.argv)

    # Apply Dark Theme
    #qdarktheme.setup_theme("dark")

    window = ERPApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
