import sys

#from PyQt6.QtCore import *
#from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

app = QApplication(sys.argv)

w = QWidget()
b = QLabel(w)
b.setText("hello")
w.setGeometry(100, 100, 200, 50)
b.move(50, 20)
w.setWindowTitle("pyqt")
w.show()

sys.exit(app.exec())

#app.exec(); del app
