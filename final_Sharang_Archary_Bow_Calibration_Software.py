import sys
import os
from PyQt5 import QtWidgets, QtCore
import pyqtgraph
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
import serial
import threading
import csv
from zipfile import ZipFile
file_paths = [""]
portName = "COM5"
baudrate = "115200"
arduino = serial.Serial(portName,baudrate)
dist=[]

data = 0
event = threading.Event()
event.clear()
event2 = threading.Event()
event2.clear()

class MainWindow(QWidget):
    def __init__(self):
        self.dist = [0]
        self.li = [1]
        self.lo = [0]


        super(MainWindow,self).__init__()
        self.setGeometry(0, 0, 1100, 1000)
        self.setWindowTitle("Bow Calibration Software")
        self.VBL = QGridLayout()
        pixmap = QPixmap('sharang.jpeg').scaled(100,100)

        #self.win = pyqtgraph.PlotWidget()
        #self.p1 = win.addPlot(row=0, col=0)
        self.label1 = QLabel('Sharang Archery', self)
        self.label1.setFont(QFont('Arial', 20))
        self.label1.setAlignment(QtCore.Qt.AlignCenter)
        self.VBL.addWidget(self.label1, 0, 2, 1, 5)
        #self.label1.resize(400, 60)
        #self.label1.move(800, 0)

        self.label2 = QLabel('DATA ACQUISITION SYSTEM FOR BOW TESTING', self)
        self.label2.setFont(QFont('Arial', 20))
        self.label2.setAlignment(QtCore.Qt.AlignCenter)
        self.VBL.addWidget(self.label2, 1, 2, 1, 5)
        #self.label2.resize(1000, 60)
        #self.label2.move(550, 50)

        self.label3 = QLabel()
        self.label3.setPixmap(pixmap)
        self.VBL.addWidget(self.label3, 0, 1, 2,2)
        self.label4 = QLabel()
        self.label4.setPixmap(pixmap)
        self.VBL.addWidget(self.label4, 0, 7, 2, 2)


        self.graphWidget = pyqtgraph.PlotWidget()
        self.graphWidget.setTitle("Load(lbs) vs Displacement(inches)", color="b", size="10pt")
        #self.VBL.addWidget(self.graphWidget,0,4,8,8)
        self.VBL.addWidget(self.graphWidget, 9, 2,8,7)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setLabel(axis='left', text='Load(lbs)')
        self.graphWidget.setLabel(axis='bottom', text='Displacement(inches)')

        self.x = self.li
        self.y = self.dist
        self.d = self.lo


        self.graphWidget.setBackground('w')
        pen = pyqtgraph.mkPen(color=(255, 0, 0),width=10,style=QtCore.Qt.DotLine)
        pen2 = pyqtgraph.mkPen(color=(5, 57, 119),width=3)
        self.graphWidget.setXRange(0, 30)
        self.graphWidget.setYRange(-10, 40)
        self.data_line = self.graphWidget.plot(self.d, self.y, pen=None, symbol='o', symbolPen=None, symbolBrush=('r'), PointVisible=True, name='Axial Load (lbs)')
        self.data_line2 = self.graphWidget.plot(self.d, self.x, pen=None, symbol='o', symbolPen=None, symbolBrush=('b'),PointVisible=True, name='Axial Load 2 (lbs)')
        #self.data_line2 = self.graphWidget.plot(self.x, self.d, pen=pen2)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.get_val)
        # self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()



        self.FeedLabel = QLabel()
        #self.VBL.addWidget(self.FeedLabel,0,0,4,4)
        self.VBL.addWidget(self.FeedLabel, 3, 1, 4, 4)

        self.FeedLabel2 = QLabel()
        #self.VBL.addWidget(self.FeedLabel2,4,0,4,4)
        self.VBL.addWidget(self.FeedLabel2,3,5,4,4)

        #self.FeedLabel3 = pyqtgraph.GraphicsWindow()
        #self.VBL.addWidget(self.FeedLabel3)

        self.CancelBTN = QPushButton("Quit")
        self.CancelBTN.clicked.connect(QCoreApplication.instance().quit)
        self.VBL.addWidget(self.CancelBTN,13,1,1,1)
        self.StartBTN = QPushButton("Start Recording")
        self.StartBTN.clicked.connect(self.start_rec)
        self.VBL.addWidget(self.StartBTN, 9, 1, 1, 1)
        self.StopBTN = QPushButton("Stop recording")
        self.StopBTN.clicked.connect(self.stop_rec)
        self.VBL.addWidget(self.StopBTN, 11, 1, 1, 1)

        self.SaveBTN = QPushButton("Save")
        self.SaveBTN.clicked.connect(self.savezip)
        self.VBL.addWidget(self.SaveBTN, 15, 1, 1, 1)
        self.SnapBTN = QPushButton("Snap Shot")
        self.SnapBTN.clicked.connect(self.snapshot)
        self.VBL.addWidget(self.SnapBTN, 17, 1, 1, 1)

        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

        self.Worker2 = Worker2()
        self.Worker2.start()
        self.Worker2.ImageUpdate.connect(self.ImageUpdateSlot2)




        #self.graphWidget = pyqtgraph.PlotWidget()


        self.setLayout(self.VBL)
    def ImageUpdateSlot(self,Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))



    def ImageUpdateSlot2(self,Image):
        self.FeedLabel2.setPixmap(QPixmap.fromImage(Image))

    def start_rec(self):
        # printing pressed
        event.set()
        event2.clear()

    def stop_rec(self):
        # printing pressed
        event.clear()
        event2.set()
        print("recording saved as right.avi and left.avi")

    def snapshot(self):
        screenshot = screen.grabWindow(Root.winId())
        screenshot.save(r'F:\Work\November\data log\shot.jpg', 'jpg')
        print("snap shot saved as shot.jpg")

    def get_val(self):
        arduino_data = arduino.readline()
        string = arduino_data.decode()
        striped_string = string.rstrip().split(',')

        dista = (float(striped_string[0])+240-140)/25.4
        data = float(striped_string[2])* 2.20462
        data2 = float(striped_string[1]) * 2.20462
        row=[]
        self.d.append(dista)
        self.y.append(data)
        self.x.append(data2)
        #self.x.append(self.x[-1] + 1)

        #print(self.x, self.y, self.d,striped_string)
        self.data_line.setData(self.d, self.y)
        self.data_line2.setData(self.d, self.x)

        #self.x.append(self.x[-1] + 1)
        #self.x = self.x[1:]  # Remove the first y element.
        # Add a new value 1 higher than the last.


        self.y.append(data)
        self.x.append(data2)
        self.d.append(dista)
        self.y = self.y[1:]
        self.x = self.x[1:]
        self.d = self.d[1:]
        if len(self.y) > 2000:
            self.x = self.x[1:]
            self.y = self.y[1:]
            self.d = self.d[1:]
        #filename = "limb_info.csv"
        filename = r"F:\Work\November\data log\limb_info.csv"
        fields = ['Distance', 'Load 1', 'Load 2']
        row.clear()
        row = [dista,data,data2]
        if event.is_set():
            with open(filename, 'a+') as csvfile:
                # creating a csv writer object
                csvwriter = csv.writer(csvfile)
                # writing the fields
                # writing the data rows
                csvwriter.writerow(row)



    def savezip(self):
        file_paths = ["right.avi","left.avi","shot.jpg","limb_info.csv"]
        zippath = r"F:\Work\November\data log\limb_info.zip"
        with ZipFile(zippath, 'w') as zip: #'limb_info.zip'
            # writing each file one by one
            for file in file_paths:
                zip.write(file)
        print('All files zipped successfully!')
    def CancelFeed(self):
        self.Worker1.Stop()
        self.Worker1_rec.Stop()
        self.Worker2.stop()



class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        Capture = cv2.VideoCapture(1)
        frame_width = int(Capture.get(3))
        frame_height = int(Capture.get(4))
        size = (frame_width, frame_height)
        name= r"F:\Work\November\data log\right.avi"
        result = cv2.VideoWriter(name,
                                 cv2.VideoWriter_fourcc(*'MJPG'),
                                 30, size)

        while self.ThreadActive:
            ret,frame = Capture.read()

            if ret:

                image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(image,1)
                ConvertToQtFormat = QImage(FlippedImage.data,FlippedImage.shape[1],FlippedImage.shape[0],QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(480,480,Qt.KeepAspectRatio)

                self.ImageUpdate.emit(Pic)
                if event.is_set():
                    result.write(frame)
                    print("recording....")
                    i = 0
                if event2.is_set():
                    result.release()




class Worker2(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def run(self):
        self.ThreadActive = True
        Capture = cv2.VideoCapture(0)
        frame_width = int(Capture.get(3))
        frame_height = int(Capture.get(4))
        size = (frame_width, frame_height)
        name1 = r"F:\Work\November\data log\left.avi"
        result = cv2.VideoWriter(name1,
                                 cv2.VideoWriter_fourcc(*'MJPG'),
                                 30, size)

        while self.ThreadActive:
            ret, frame = Capture.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0],QImage.Format_RGB888)
                Pic2 = ConvertToQtFormat.scaled(480, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic2)
                if event.is_set():
                    result.write(frame)
                    print("recording....")
                if event2.is_set():
                    result.release()



    def stop(self):
        self.ThreadActive = False
        self.quit()



if __name__ == "__main__":
    App = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    Root = MainWindow()

    Root.show()
    #limb_no=input("Enter Limb NO.")
    sys.exit(App.exec())
