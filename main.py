# -*- coding: utf-8 -*-

# Copyright (c) 2011 Filippenok Dmitriy <fil@fillis.nsk.ru>
#
import logging, logging.config

__author__ = 'Filin'

from PyQt4.QtGui import *
import sys
from tcpclient import TcpClient

log = logging.getLogger('main')

class MainWindow(QWidget):

    version = '1.1'
    stDisconnected = 0
    stConnected = 1

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.address = QLineEdit()
        self.address.setInputMask("\A\d\dress: 000.000.000.000")
        self.address.setText('192.168.001.069')
        self.port = QLineEdit()
        self.port.setInputMask("Port: 9000")
        self.port.setText('9110')
        self.btnConnect = QPushButton()
        self.btnConnect.clicked.connect(self.btnConnectClicked)

        self.statusBar = QStatusBar()

        self.layout.addWidget(self.address)
        self.layout.addWidget(self.port)
        self.layout.addWidget(self.btnConnect)
        self.layout.addWidget(self.statusBar)

        self.tcpClient = TcpClient()

        self.setWindowTitle('CAN Printer Logger v.{}'.format(self.version))
        self.setWindowIcon(QIcon('icons/icon.png'))


        self.tcpClient.connectionFailed.connect(self.connectionFailed)
        self.tcpClient.tcpClientError.connect(self.connectionFailed)
        self.tcpClient.connected.connect(self.connected)
        self.tcpClient.disconnected.connect(self.disconnected)
        self.changeState(self.stDisconnected)

    def closeEvent(self, event):
        self.disconnectFromPrinter()
        event.accept()

    def btnConnectClicked(self):
        if self._state == self.stConnected:
            self.disconnectFromPrinter()
            self.statusBar.showMessage("Disconnecting...")
            log.debug('Start disconnecting')
        else:
            self.statusBar.showMessage("Connecting...")
            self.connectToPrinter()

    def disconnectFromPrinter(self):
        self.tcpClient.disconnectFromHost(0)

    def connectionFailed(self, text):
        self.statusBar.showMessage(text)

    def connectToPrinter(self):
        if self.address.hasAcceptableInput():
            ip = self.address.text()
            ip = self.address.text().strip('Address: ')
        else:
            QMessageBox.warning('Error', 'Incorrect ip-addres!')
            ip = None
        if self.port.hasAcceptableInput():
            port = int(self.port.text().strip('Port: '))
        else:
            QMessageBox.warning('Error', 'Incorrect port!')
            port = None
        if ip is not None and port is not None:
            self.tcpClient.connectToHost(ip, port)
            log.debug("Connect to {}:{}".format(ip, port))

    def changeState(self, state):
        if state == self.stConnected:
            self.btnConnect.setIcon(QIcon("icons/disconnect.png"))
            self.btnConnect.setText('Disconnect')
            self.btnConnect.setToolTip('Stop logging')
            self.statusBar.showMessage("Logging...")
            self._state = self.stConnected
        else:
            self.btnConnect.setIcon(QIcon("icons/connect.png"))
            self.btnConnect.setText('Сonnect')
            self.btnConnect.setToolTip('Start logging')
            self.statusBar.showMessage("Disconnected", 5000)
            self._state = self.stDisconnected

    def disconnected(self):
        self.changeState(self.stDisconnected)

    def connected(self):
        self.changeState(self.stConnected)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()

