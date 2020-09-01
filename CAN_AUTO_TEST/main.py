from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from mainwindow import MainWindow
import sys

if __name__ == "__main__":
    # 高分屏屏幕自适应
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
