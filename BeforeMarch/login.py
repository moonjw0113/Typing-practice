import sys
from PyQt6.QtWidgets import *
from PyQt6 import uic
from 타자연습 import MainClass

long = False
form_class = uic.loadUiType("login.ui")[0]
class loginWindow(QMainWindow, form_class) :
    
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.Long.released.connect(self.longTyping)
        self.Short.released.connect(self.shortTyping)
        
    def longTyping(self):
        self.w = MainClass()
        self.w.flag = 'LONG'
        self.w.SetTypingMode()
        self.w.show()
    
    def shortTyping(self):
        self.w = MainClass()
        self.w.flag = 'SHORT'
        self.w.SetTypingMode()
        self.w.show()

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    Window = loginWindow()
    Window.show()
    app.exec()