import sys, requests
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QWidget


URL = "https://kr.coinness.com/news/"
max_num = 1004924
last_num = 1000106

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Coin Transaction')
        self.move(300, 300)
        self.resize(400, 200)

        
        hbox1 = QHBoxLayout()



        start_btn = QPushButton('Start', self)
        stop_btn = QPushButton('Stop', self)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(start_btn)
        hbox2.addWidget(stop_btn)


        self.setLayout(hbox2)
        self.show()


    def mainloop(self):
        pass



if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())