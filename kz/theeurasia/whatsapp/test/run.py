# -*- coding: utf-8 -*-
'''
@author: vadim.isaev
'''

from kz.theeurasia.whatsapp.test.stomp_server import StompServer
from kz.theeurasia.whatsapp.test.whatsapp_server import WhatsAppServer
import time

class Run(object):
    whatsAppPhone = '77010359568'
    whatsAppPassword = 'dooVWTrlE5Ggtmg2NPp1hCpsPwY='

    stompServerHost = 'almaty-linuxapp01.theeurasia.local'
    stompServerPort = 61613
    stompServerLogin = 'admin'
    stompServerPassword = 'admin'
    stompServerWhatsappOutboxQueue = 'kz.theeurasia.whatsap.OUTBOX'
    stomServerWhatsappInboxQueuePrefix = 'kz.theeurasia.whatsap.INBOX'
    
    whatsAppServer = None
    stompServer = None

    def __init__(self):
        self.stompServer = StompServer(
                                       self.stompServerHost, 
                                       self.stompServerPort, 
                                       self.stompServerLogin, 
                                       self.stompServerPassword, 
                                       self.stompServerWhatsappOutboxQueue,
                                       self.stomServerWhatsappInboxQueuePrefix)
        self.whatsAppServer = WhatsAppServer(self.whatsAppPhone, self.whatsAppPassword)
        self.stompServer.setWhatsAppStack(self.whatsAppServer)
        self.whatsAppServer.setStompServer(self.stompServer)

    def start(self):
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
        if self.whatsAppServer:
            self.whatsAppServer.stop()
        if self.stompServer:
            self.stompServer.stop()

if __name__ == "__main__":
    run = Run()
    run.start()
    run.loop()
    run.stop()
