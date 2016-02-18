# -*- coding: utf-8 -*-
'''
@author: vadim.isaev
'''

import logging
import sys
import time

from kz.theeurasia.whatsapp.stomp_service import StompService, \
    StompServiceException
from kz.theeurasia.whatsapp.whats_app_service import WhatsAppService


#    filename='whatsapp_mq_service.log'
#    stream=sys.stdout
logging.basicConfig(filename='whatsapp_mq_service.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

logger = logging.getLogger(__name__)

class MainService(object):
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
        try:
            if self.stompService:
                self.stompService.start()
            if self.whatsAppService:
                self.whatsAppService.start()
            return True
        except StompServiceException as e:
            logger.error(e.getMessage())
            return False

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
    run = MainService()
    if not run.start():
        run.stop()
        sys.exit(1)
    run.loop()
    run.stop()
