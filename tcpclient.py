# -*- coding: utf-8 -*-

# Copyright (c) 2011 Filippenok Dmitriy <fil@fillis.nsk.ru>
# Version 1.0
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSignal, QDataStream, QFile, QTextStream
from tcpmessages import CanPacket
import timedthread

import logging


__author__ = 'Filin'

from PyQt4.QtNetwork import *

import struct, logging

logCAN = logging.getLogger('can')
log = logging.getLogger('main')

class TcpClient(timedthread.TimedThread):
    """
    TCP-клиент в отдельном потоке,
    """

    # Константы
    TCPP_CONNECTTIMEOUT = 5000                                      # таймаут подключения (ms)

    # Сигналы:
    connectionFailed = pyqtSignal(str)
    tcpClientError = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    incomingMessage = pyqtSignal()


    def __init__(self):
        super(TcpClient, self).__init__("tcp_client")

        # Mutex и буферы для приема и отправки сообщений из всех потоков

        log.debug("Создан TCP-клиент")
        # Введена ПОТЕНЦИАЛЬНАЯ возможность восстанавливать связь при разрыве

        # Параметры для подключения
        self._m_HostaAddr = QHostAddress()
        self._socket = None
        self._stream = None

        # Переменные состояния
        self.m_bConnected = False
        self.m_bShouldConnect = False
        self.m_bShouldDisconnect = False
        self.m_bError = False

        self.pingCounter = 0


    def connectToHost(self, addr, port=9110):
        # Функция подключения к принтеру.
        if self.m_bConnected:
            # Если уже подключены - ничего не делаем
            return 2

        if not self._m_HostaAddr.setAddress(addr):
            print('"{}"'.format(addr))
            # Если адрес указан неверно, выходим со знаком минус и выводим сообщение в лог
            print("Невенро указан адрес подключения!")
            return 0

        try:
            self._m_Port = int(port)
        except ValueError as e:
            print("Неверно задан номер порта (не числовое значение): {}!".format( e))

        self.m_bShouldConnect = True
        self.m_bConnected = False
        self.m_bShouldDisconnect = False
        self.m_bError = False

        if not self.isRunning():
            self.start()

        return 1

    def disconnectFromHost(self, waitTime):
        # Функция отключения от принтера. Время ожидания не обрабатывается, поэтому переменную состояния отключения выставляем сразу
        log.debug('Should disconnect')
        self.m_bShouldDisconnect = True

    def workThread(self):
        """
        Основная функция треда
        Не учитывается время с последней отправки и с последнего приема
        """
        super(TcpClient, self).workThread()

        if self._socket is not None and self.m_bConnected:
            if self._socket.error() != -1 and not self.m_bError:
                self.m_bError = True

        # Требуется отключение
        if self.m_bError:
            # Сообщаем, что произошла ошибка и в сигнале передаем описание
            self.onSocketError()
        elif self.m_bShouldDisconnect and self.m_bConnected:
            log.debug('try disconnect')
            if self._socket.isOpen():
                self._socket.disconnectFromHost()
                self._socket.close()
                self._socket.disconnected.disconnect(self.disconnected)
                self._socket.connected.disconnect(self.connected)
                self.m_bShouldDisconnect = False
                self.m_bConnected = False
                log.debug('Отключаемся от принтера по адресу {}:{}'.format(self._m_HostaAddr.toString(), self._m_Port))

        # Требуется подключение
        elif self.m_bShouldConnect and not self.m_bConnected:
            self.m_bShouldConnect = False
            # Если сокет уже открыт, а подключения нет, то лучше его убить и создать новый
            if self._socket is None:
                self._socket = QTcpSocket()
            elif self._socket.isOpen():
                self._socket.disconnectFromHost()
                self._socket.close()
                del self._socket
                self._socket = QTcpSocket()
            self._stream = QDataStream(self._socket)

            # Обрабатываем изменения состояния сокета и его ошибки.
            self._socket.disconnected.connect(self.disconnected)
            self._socket.connected.connect(self.connected)
            log.debug("Начинаем подключение к принтеру {}:{}".format(self._m_HostaAddr.toString(), self._m_Port))
            # Подключаемся к принтеру
            self._socket.connectToHost(self._m_HostaAddr, self._m_Port)
            # Если время ожидания истекло, то отправляем сигнал об этом
            if not self._socket.waitForConnected(self.TCPP_CONNECTTIMEOUT):
                self.m_bConnected = False
                self.m_bError = True
#                log.warning(self._langManager.getString(__name__, "timeout"))
                log.debug("Время ожидания истекло. Соединение не установлено!")
                self._socket.disconnected.disconnect(self.disconnected)
                self._socket.connected.disconnect(self.connected)
                self.connectionFailed.emit('TimeOut')
            else:
                self.m_bConnected = True
                self.m_bError = False
                log.debug('Установлено подключение с {}:{}'.format(self._m_HostaAddr.toString(), self._m_Port))
                #self.connected.emit('Установлено подключение с принтером по адресу {0}:{1}'.format(self._m_HostaAddr.toString(), self._m_Port))

        # Прием и отправка пакетов
        elif self.m_bConnected:
            packetCounter = 0
            # Получение пкаетов
            while self._socket.bytesAvailable()>16:
                if packetCounter > 255:
                    break # Если принято больше 255 пакетов, то приостанавливаем прием, чтоб другим дать возможность поработать ^_^
                # Распаковываем данные из сокета: тип, длина, 2байта время, 4байта ID, 8байт данных
                byteInfo = self._stream.readRawData(8)
                byteCommand = self._stream.readRawData(2)
                byteData = self._stream.readRawData(6)
                canPacket =  CanPacket()
                canPacket.unpackData(struct.unpack('<2BHL' ,byteInfo), struct.unpack('<2B', byteCommand), struct.unpack('<HBBBB', byteData), byteData)
                # запихиваем пакет в буфер
                logCan.info("{}".format(canPacket))
                packetCounter += 1


        return True

    def onSocketError(self):
        self.m_bConnected = False
        self.m_bShouldConnect = False
        self.m_bShouldDisconnect = False
        self.m_bError = False
        self.tcpClientError.emit('{}'.format(self._socket.errorString()))
        print('{}: [{}] {}'.format('Connection error', self._socket.error(), self._socket.errorString()))
#        log.error('При подключении произошла ошибка: [{}] {}'.format(self._socket.error(), self._socket.errorString()))






        


        
        
