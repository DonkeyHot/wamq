'''
@author: vadim.isaev
'''
import logging
import sys
import threading

from kz.theeurasia.whatsapp.whats_app_stack import WhatsAppStack


ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(ch)

class WhatsAppService(object):
    whatsAppPhone = None
    whatsAppPassword = None
    autoReply = None

    stompService = None
    
    def __init__(self,
                 whatsAppPhone,
                 whatsAppPassword,
                 autoReply,
                 stompService=None):
        self.whatsAppPhone = whatsAppPhone
        self.whatsAppPassword = whatsAppPassword
        self.autoReply = autoReply
        self.stompService = stompService

    def setStompService(self, stompService):
        self.stompService = stompService

    def start(self):
        logger.info("    Starting WhatsApp service...")
        self.stack = WhatsAppStack(self.whatsAppPhone, self.whatsAppPassword, self.autoReply, self.stompService)
        self.thread = threading.Thread(None, target=self.stack.start)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        logger.info("    Stopping WhatsApp service...")
        self.stack.stop()

    def checkAlive(self):
        if not self.thread.isAlive():
            logger.info("    WhatsApp service is not alive. Restarting...")
            self.start()
