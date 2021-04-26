import sys
import time

from PyQt6 import QtGui
from PyQt6 import QtWidgets
from PyQt6 import QtCore

from PromSensor import GetPromSensor

class WorkerSignals(QtCore.QObject):
    result = QtCore.pyqtSignal(dict)

class Worker(QtCore.QRunnable):
    def __init__(self, prom_sensor):
        super(Worker, self).__init__()
        self.prom_sensor = prom_sensor
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        while True:
            print("Thread start")
            self.signals.result.emit(self.prom_sensor.get_sensor_latest())
            time.sleep(30)
            print("Thread complete")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.threadpool = QtCore.QThreadPool()
        self.prom_sensor = GetPromSensor()
        self.sensor_locations = { "prologue" : "garage", "accurite" : "outside", "oregon" : "attic" }

        self.previous = None
        self.widgets = { }

        self.frame_main = QtWidgets.QFrame(self)

        self.layout_top = QtWidgets.QVBoxLayout(self.frame_main)
        self.layout_top.setObjectName("layout_top")

        self.frame_main.setStyleSheet("background-color:DarkSeaGreen")
        self.frame_main.setLayout(self.layout_top)

        self.setCentralWidget(self.frame_main)

        self.show()

        self.start_worker()

    def start_worker(self):
        worker = Worker(prom_sensor = self.prom_sensor)
        worker.signals.result.connect(self.process_result)

        self.threadpool.start(worker)

    def process_result(self, sensors):
        print("receiving:", sensors)

        for sensor in sensors.keys():
            if self.widgets.get(sensor):
                print("updating:", sensor)
                self.update_sensor(sensor, sensors.get(sensor))
            else:
                print("adding:", sensor)
                self.add_sensor(sensor, sensors.get(sensor))


    def update_sensor(self, sensor, value):
        label = self.widgets.get(sensor)
        label.setText("{:.1f}".format(float(value)))

    def add_sensor(self, sensor, value):
        location = self.sensor_locations.get(sensor)
        if location:
            label_title = QtWidgets.QLabel("{} ({})".format(location, sensor))
        else:
            label_title = QtWidgets.QLabel(sensor)

        label_title.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        label_title.setStyleSheet("border: 1px solid black; background-color:DarkKhaki; border-radius:2px")
        label_title.setAlignment(QtCore.Qt.Alignment.AlignCenter)
        label_title.setFont(QtGui.QFont("Cooper Lt BT", 12))

        label_value = QtWidgets.QLabel("{:.1f}".format(float(value)))

        label_value.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        label_value.setStyleSheet("border: 1px solid dimgrey; background-color:PaleTurquoise; border-radius:4px")
        label_value.setAlignment(QtCore.Qt.Alignment.AlignCenter)
        label_value.setFont(QtGui.QFont("Cooper Blk BT", 32))

        frame = QtWidgets.QFrame(self.frame_main)
        frame.setStyleSheet("border: 2px solid black; background-color:SkyBlue; border-radius:6px")

        self.layout_top.addWidget(frame)

        layout_vbox = QtWidgets.QVBoxLayout(frame)
        layout_vbox.setObjectName("layout_vbox")
    
        layout_vbox.addWidget(label_title)
        layout_vbox.addWidget(label_value)

        #self.layout_top.addLayout(layout_vbox)

        self.widgets.update({ sensor : label_value })

    def closeEvent(self, event):
        print("close event")
        sys.exit()
        event.accept()

app = QtWidgets.QApplication([])
window = MainWindow()
sys.exit(app.exec())
