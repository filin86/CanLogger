# -*- coding: utf-8 -*-

# Copyright (c) 2011 Filippenok Dmitriy <fil@fillis.nsk.ru>
#
from PyQt4.QtCore import QThread, QTime, QEventLoop

__author__ = 'Filin'

import logging, logging.config

#logging.config.fileConfig('log/log.conf')
#log=logging.getLogger('main')
#logCAN=logging.getLogger('can')

class TimedThread(QThread):
    """
    Класс потока, который периодически засыпает и 
    """

    def __init__(self, name):
        super(TimedThread, self).__init__()
        self.m_bStop = False
        self.m_nTact = 100
        self.m_Name = name
        self.m_nTactCounter = 0

    def initThread(self):
        return True

    def workThread(self):
        return True

    def exitThread(self):
        pass

    def setTact(self, ms):
        if not self.isRunning():
            if ms < 10:
                ms = 10
            self.m_nTact = ms
        return self.m_nTact

    def getTact(self):
        return self.m_nTact

    def getName(self):
        return self.m_Name

    def Stop(self, waitTime):
        if self.m_bStop:
            return True

        self.m_bStop = True

        if waitTime < 0:
            return True

        while waitTime > 0:
            if self.isFinished() or not self.isRunning():
                break
            self.msleep(10)
            waitTime -= 10

        if waitTime <= 0:
            return False

        return True

    def run(self):
        time = QTime()
        eventLoop = QEventLoop()

        self.m_bStop = False

#        log.debug("Запускаем поток")
        #if not self.initThread():
            #return
        while not self.m_bStop:
            self.m_nTactCounter += 1 # Добавить обнуление при переполнении

            time.start()
            eventLoop.processEvents()

            if not self.workThread():
                self.m_bStop = True
                return
            workTime = time.elapsed()
            if 0 <= workTime < self.m_nTact:
                self.msleep(self.m_nTact - workTime)
            else:
                self.msleep(0)

        eventLoop.processEvents()

        self.exitThread()


    
        

