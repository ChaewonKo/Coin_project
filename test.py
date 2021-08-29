from PyQt5.QtCore import *
from PyQt5.QtGui import QValidator 
from PyQt5.QtWidgets import * 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import time

class CoinBotGUI(QDialog): 
    def __init__(self, parent=None): 
        self.y = 1
        super().__init__(parent) 
        # self.qtxt1 = QTextEdit(self) 
        # self.btn1 = QPushButton("Start", self) 
        # self.btn2 = QPushButton("Stop", self) 
        # self.btn3 = QPushButton("add 100", self) 
        # self.btn4 = QPushButton("send instance", self) 
        
        
        layout = QVBoxLayout() 

        # 첫번째 줄 <그래프>
        hbox_1 = QHBoxLayout() 
        self.line_fig = plt.Figure()
        self.line_canvas = FigureCanvas(self.line_fig)

        self.bar_fig = plt.bar('오늘', self.y)
        self.bar_canvas = FigureCanvas()
        hbox_1.addWidget(self.line_canvas)
        hbox_1.addWidget(self.bar_canvas)
        
        # 두번째 줄 <설정>
        hbox_2 = QHBoxLayout() 
        self.get_cur_stick = QComboBox()
        self.get_cur_stick.addItem('1분')
        self.get_cur_stick.addItem('5분')
        self.get_cur_stick.addItem('10분')
        self.get_cur_stick.addItem('60분')
        self.get_cur_stick.addItem('240분')

        vbox2_1 = QVBoxLayout()
        self.crawling_website_1 = QCheckBox('코인 니스', self)
        self.crawling_website_2 = QCheckBox('블록 미디어', self)
        self.crawling_website_3 = QCheckBox('민티드랩', self)
        self.crawling_website_4 = QCheckBox('체인노드', self)
        self.crawling_website_5 = QCheckBox('톡큰', self)
        self.crawling_website_6 = QCheckBox('쟁글', self)
        vbox2_1.addWidget(self.crawling_website_1)
        vbox2_1.addWidget(self.crawling_website_2)
        vbox2_1.addWidget(self.crawling_website_3)
        vbox2_1.addWidget(self.crawling_website_4)
        vbox2_1.addWidget(self.crawling_website_5)
        vbox2_1.addWidget(self.crawling_website_6)

        vbox2_2 = QVBoxLayout()
        self.collect_peorid = QComboBox()
        for i in range(1,8):
            self.collect_peorid.addItem(str(i)+'일')
        vbox2_2.addWidget(QLabel('데이터 수집 기간', self))
        vbox2_2.addWidget(self.collect_peorid)

        self.graph_update_btn = QPushButton("그래프 업데이트", self) 
        self.start_btn = QPushButton("시작", self) 
        self.stop_btn = QPushButton("중지", self) 

        hbox_2.addWidget(self.get_cur_stick)
        hbox_2.addWidget(QLabel('봉', self))
        hbox_2.addLayout(vbox2_1)
        hbox_2.addLayout(vbox2_2)
        hbox_2.addWidget(self.graph_update_btn)
        hbox_2.addWidget(self.start_btn)
        hbox_2.addWidget(self.stop_btn)

        # 세번째 줄 <결과, 현재 시간>
        hbox_3 = QHBoxLayout() 
        result_text = QLabel('결과', self)
        result_text.setStyleSheet("color: red;")
        self.result = QLabel('다음에 상승 할 것으로 87.5% 예상됩니다.', self)
        self.cur_time = QLabel('현재 시간\n21-08-29\n 19:14:38', self)

        hbox_3.addWidget(result_text)
        hbox_3.addWidget(self.result)
        hbox_3.addWidget(self.cur_time)


        # vbox_1.addWidget(self.qtxt1) 
        # vbox_1.addWidget(self.btn1) 
        # vbox_1.addWidget(self.btn2) 
        # vbox_1.addWidget(self.btn3) 
        # vbox_1.addWidget(self.btn4) 

        layout.addLayout(hbox_1)
        layout.addLayout(hbox_2)
        layout.addLayout(hbox_3)

        self.setLayout(layout) 
        self.setGeometry(100, 100, 600, 600) 

    def doGraph1(self):
        x = np.arange(0, 10, 0.5)
        y1 = np.sin(x)
        y2 = np.cos(x)

        self.line_fig.clear()
        ax = self.line_fig.add_subplot(111)
        ax.plot(x, y1, label="sin(x)")
        ax.plot(x, y2, label="cos(x)", linestyle="--")
        
        # ax.set_xlabel("x")
        # ax.set_xlabel("y")
        
        # ax.set_title("sin & cos")
        ax.legend()
        
        self.line_canvas.draw()

    @pyqtSlot() 
    def prediction_start(self): 
        x = '오늘'
        self.y += 1
        print(self.y)

        # self.bar_fig.clear()
        ax = self.bar_fig       
        # ax.plot(x, self.y)

        # ax.legend()
        self.bar_canvas.draw()
    

class Test: 
    def __init__(self): 
        name = "" 

class CoinBot(CoinBotGUI): 
    add_sec_signal = pyqtSignal() 
    send_instance_singal = pyqtSignal("PyQt_PyObject") 

    def __init__(self, parent=None): 
        super().__init__(parent) 
        self.graph_update_btn.clicked.connect(self.doGraph1) 
        self.start_btn.clicked.connect(self.prediction_start) 


        # self.btn1.clicked.connect(self.time_start) 
        # self.btn2.clicked.connect(self.time_stop) 
        # self.btn3.clicked.connect(self.add_sec) 
        # self.btn4.clicked.connect(self.send_instance) 
        self.th = Worker(parent=self) 
        # self.th.sec_changed.connect(self.time_update) # custom signal from worker thread to main thread 
        # self.add_sec_signal.connect(self.th.add_sec) # custom signal from main thread to worker thread 
        # self.send_instance_singal.connect(self.th.recive_instance_singal) 
        self.show() 


    



    # @pyqtSlot() 
    # def time_start(self): 
    #     self.th.start() 
    #     self.th.working = True 
    
    # @pyqtSlot() 
    # def time_stop(self): 
    #     self.th.working = False
    
    # @pyqtSlot() 
    # def add_sec(self): 
    #     print(".... add singal emit....") 
    #     self.add_sec_signal.emit() 
    
    # @pyqtSlot(str) 
    # def time_update(self, msg): 
    #     self.qtxt1.append(msg)
        
    # @pyqtSlot() 
    # def send_instance(self): 
    #     t1 = Test() 
    #     t1.name = "SuperPower!!!" 
    #     self.send_instance_singal.emit(t1) 
    
class Worker(QThread): 
    sec_changed = pyqtSignal(str) 
    def __init__(self, sec=0, parent=None): 
        super().__init__() 
        self.main = parent 
        self.working = True 
        self.sec = sec 
        
        # self.main.add_sec_signal.connect(self.add_sec) # 이것도 작동함. # custom signal from main thread to worker thread 
            
    def __del__(self): 
        print(".... end thread.....") 
        self.wait() 

    def run(self): 
        while self.working: 
            print('이게 실행 되네')

            self.sleep(1) 
            self.sec += 1 


    # def run(self): 
    #     while self.working: 
    #         print('이게 실행 되네')
    #         self.sec_changed.emit('time (secs)：{}'.format(self.sec)) 
    #         self.sleep(1) 
    #         self.sec += 1 
    
    @pyqtSlot() 
    def add_sec(self): 
        print("add_sec....") 
        self.sec += 100 
        
    @pyqtSlot("PyQt_PyObject") # @pyqtSlot(object) 도 가능.. 
    def recive_instance_singal(self, inst): 
        print(inst.name) 

if __name__ == "__main__": 
    import sys 
    
    app = QApplication(sys.argv) 
    form = CoinBot() 
    app.exec_()
