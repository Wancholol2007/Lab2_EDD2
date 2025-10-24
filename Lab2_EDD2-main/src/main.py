import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication
from ui.interface import Interface

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Interface()
    sys.exit(app.exec_())
