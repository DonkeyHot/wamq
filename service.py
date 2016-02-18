# -*- coding: utf-8 -*-
'''
@author: vadim.isaev
'''

import logging
import sys
import time

from kz.theeurasia.whatsapp.stomp_service import StompService
from kz.theeurasia.whatsapp.whats_app_service import WhatsAppService


logging.basicConfig(filename='service.log', level=logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(ch)

class Service(object):
    whatsAppPhone = '77010359568'
    whatsAppPassword = 'dooVWTrlE5Ggtmg2NPp1hCpsPwY='
    whatsAppAutoReply = True

    stompHost = 'almaty-linuxapp01.theeurasia.local'
    stompPort = 61613
    stompLogin = 'admin'
    stompPassword = 'admin'

    stompListeningDestinations = ['/queue/kz.theeurasia.whatsapp.OUTBOX', '/topic/kz.theeurasia.whatsapp.OUTBOX']
    stompWhatsAppDestinationInboxPrefix = '/topic/kz.theeurasia.whatsapp.INBOX'

    whatsAppService = None
    stompService = None

    def __init__(self):
        self.stompService = StompService(
                                       self.stompHost,
                                       self.stompPort,
                                       self.stompLogin,
                                       self.stompPassword,
                                       self.stompListeningDestinations,
                                       self.stompWhatsAppDestinationInboxPrefix,
                                       self.whatsAppPhone)
        self.whatsAppService = WhatsAppService(
                                               self.whatsAppPhone,
                                               self.whatsAppPassword,
                                               self.whatsAppAutoReply)
        self.stompService.setWhatsAppService(self.whatsAppService)
        self.whatsAppService.setStompService(self.stompService)

    def start(self):
        logger.info("Starting services...")
        if self.stompService:
            self.stompService.start()
        if self.whatsAppService:
            self.whatsAppService.start()

    def loop(self):
        while True:
            try:
                self.stompService.checkAlive()
                self.whatsAppService.checkAlive()
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                logger.info("CLIENT: Interrupted")
                break
            except SystemExit:
                logger.info("SYSTEM: Interrupted")
                break

    def stop(self):
        logger.info("Stopping services...")
        if self.whatsAppService:
            self.whatsAppService.stop()
        if self.stompService:
            self.stompService.stop()

if __name__ == "__main__":
    run = Service()
    run.start()
    run.loop()
    run.stop()
