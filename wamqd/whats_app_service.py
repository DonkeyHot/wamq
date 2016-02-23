'''
@author: vadim.isaev
'''
import logging
import threading

from wamqd.whats_app_stack import WhatsAppStack


logger = logging.getLogger(__name__)

class WhatsAppService(object):
    whatsAppPhone = None
    whatsAppPassword = None
    autoReply = None
    whatsAppReplyUnsupported = None

    stompService = None

    def __init__(self,
                 whatsAppPhone,
                 whatsAppPassword,
                 autoReply,
                 replyUnsupported,
                 stompService=None):
        self.whatsAppPhone = whatsAppPhone
        self.whatsAppPassword = whatsAppPassword
        self.autoReply = autoReply
        self.replyUnsupported = replyUnsupported
        self.stompService = stompService

    def setStompService(self, stompService):
        self.stompService = stompService

    def start(self):
        logger.info("Starting WhatsApp service...")
        self.stack = WhatsAppStack(
                                   self.whatsAppPhone,
                                   self.whatsAppPassword,
                                   self.autoReply,
                                   self.replyUnsupported,
                                   self.stompService)
        self.thread = threading.Thread(None, target=self.stack.start)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        logger.info("Stopping WhatsApp service...")
        self.stack.stop()

    def sendTextMessage(self, sendFrom, sendTo, text):
        self.stack.layer.sendTextMessage(sendTo, text)

    def checkAlive(self):
        if not self.thread.isAlive():
            logger.info("WhatsApp service is not alive. Restarting...")
            self.start()
