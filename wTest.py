from PyQt5.QtWidgets import QApplication
import sys
from bankis import Bankis

if __name__ == '__main__':
    app = QApplication(sys.argv)
    bankis = Bankis()
    app.exec()