# -*- coding: utf-8 -*-
'''
@author: vadim.isaev
'''

from kz.theeurasia.whatsapp.stomp_server import StompService
from kz.theeurasia.whatsapp.whatsapp_server import WhatsAppServer
import time
import logging

logger = logging.getLogger(__name__)

class Run(object):
    whatsAppPhone = '77010359568'
    whatsAppPassword = 'dooVWTrlE5Ggtmg2NPp1hCpsPwY='

    stompHost = 'almaty-linuxapp01.theeurasia.local'
    stompPort = 61613
    stompLogin = 'admin'
    stompPassword = 'admin'
    stompWhatsAppDestinationOutbox = 'kz.theeurasia.whatsap.OUTBOX'
    stompWhatsAppDestinationInboxPrefix = 'kz.theeurasia.whatsap.INBOX'

    whatsAppServer = None
    stompServer = None

    def __init__(self):
        self.stompServer = StompService(
                                       self.stompHost,
                                       self.stompPort,
                                       self.stompLogin,
                                       self.stompPassword,
                                       self.stompWhatsAppDestinationOutbox,
                                       self.stompWhatsAppDestinationInboxPrefix)
        self.whatsAppServer = WhatsAppServer(self.whatsAppPhone, self.whatsAppPassword)
        self.stompServer.setWhatsAppStack(self.whatsAppServer)
        self.whatsAppServer.setStompServer(self.stompServer)

    def start(self):
        logger.info("Starting service")
        if self.stompServer:
            self.stompServer.start()
        if self.whatsAppServer:
            self.whatsAppServer.start()

    def loop(self):
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except SystemExit:
                break

    def stop(self):
        logger.info("Stopping service")
        if self.whatsAppServer:
            self.whatsAppServer.stop()
        if self.stompServer:
            self.stompServer.stop()

if __name__ == "__main__":
    run = Run()
    run.start()
    run.loop()
    run.stop()
