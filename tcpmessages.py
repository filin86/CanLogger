# -*- coding: utf-8 -*-

# Copyright (c) 2011 Filippenok Dmitriy <fil@fillis.nsk.ru>
#
from datetime import datetime, date, time
from time import timezone

__author__ = 'Filin'

from PyQt4.QtCore import *
import struct

class CanId(QObject):
    """
    Класс для работы с четырехбайтным ID CAN посылки:
    Идентификатор расширенного протокола (1 бит), Приоритет посылки (3 бита), ID отправителя (13 бит), ID получателя (13 бит)
    """
    def __init__(self):
        super(CanId, self).__init__()
        # Инициализируем для пустого пакета на отправку. Если будет прием - перезатрутся автоматом
        self._priority = 4
        self._sourceID = 0x12
        self._targetID = 0

    def fromCanID(self, id):
        """
        Распаковываем адрес из CAN-пакета в структуру
        """
        self._priority = (id >> 26) & 0x07
        self._sourceID = (id >> 13) & 0x1FFF
        self._targetID = id & 0x1FFF

    def toCANID(self):
        """
        Функция упаковки CAN идентификаторов в 4х-байтное число.
        """
        return 1<<29 | (self._priority << 26) | (self._sourceID << 13 ) | self._targetID

    def getTargetID(self):
        return self._targetID

    def getSourceID(self):
        return self._sourceID

    def setCanID(self, target, source=0x12, priority=4):
        self._targetID = target
        self._sourceID = source
        self._priority = priority

    def __str__(self):
        return "{0:X} S:0x{1:0>2X} T:0x{2:0>2X}".format(self._priority, self._sourceID, self._targetID)


class CanPacket(QObject):
    """
    Структура для хранения всего CAN-пакета.
    Сохраняем, на всякий, все поля: Тип, ID CAN посылки, временнАя метка, длина, номер команды, номер канала и данные
    """
    def __init__(self):
        """
        Просто инициализируем структуру
        """
        super(CanPacket, self).__init__()
        self._type = 0
        self._length = 0
        self._timeStamp = 0
        self._canID = CanId()
        self._command = 0
        self._channel = 0
        self._bytes = None

    def getCanID(self):
        return self._canID

    def setCanID(self, targetID, sourceID=0x12, priority=4):
        self._canID.setCanID(targetID, sourceID, priority)
        return

    def getCommand(self):
        return self._command

    def setCommand(self, command):
        self._command = command

    def getChannel(self):
        return self._channel

    def setChannel(self, channel):
        self._channel = channel

    def setLength(self, length):
        self._length = length

    def getData(self):
        return self._bytes

    def setData(self, bytes):
        self._bytes = bytes

    def unpackData(self, tupleInfo, tupleCommand, tupleData, packed):
        """
        Распаковывает данные из CAN-пакета в структуру.
        Данные (16 байт) приходят в формате ((Тип, Длина, ВременнАя метка, CAN ID), (Номер команды, Номер канала), 6 байт данных)
        """
        self._type = tupleInfo[0]
        self._length = tupleInfo[1]
        self._timeStamp = tupleInfo[2]
        self._canID = CanId()
        self._canID.fromCanID(tupleInfo[3])
        self._command = tupleCommand[0]
        self._channel = tupleCommand[1]
        self._bytes = tupleData
        self._packed = packed

    def __str__(self):
        return '{4} {0} Cmd:{1:0>2X} Ch:{2:0>2X} ID:{5:0>4X}   {6:0>2X} {7:0>2X} {8:0>2X} {9:0>2X}\tPackedData:{3} \n'.format(self._canID, self._command, self._channel, self._packed, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), *self._bytes)
