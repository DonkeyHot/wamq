'''
@author: vadim.isaev
'''
import stomp
import logging

logger = logging.getLogger(__name__)

class MessagesListener(object):
    def __init__(self):
        self.recivedCount = 0;
        self.errorCount = 0

    def on_error(self, headers, message):
        self.errorCount += 1
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        self.recivedCount += 1
        self.sendMessageToWhastapp(headers, message)

    def sendMessageToWhastapp(self, headers, message):
        print('Sending message "%s"' % message)
        pass

    def setWhatsAppStack(self, whats_app_stack):
        self.whats_app_stack = whats_app_stack

class StompService(object):
    stompHost = None
    stompPort = None
    stompLogin = None
    stompPassword = None
    stompWhatsAppDestinationOutbox = None
    stompWhatsAppDestinationInboxPrefix = None
    whatsAppStack = None

    def __init__(self,
                 stompHost,
                 stompPort,
                 stompLogin,
                 stompPassword,
                 stompWhatsAppDestinationOutbox,
                 stompWhatsAppDestinationInboxPrefix):
        self.stompHost = stompHost
        self.stompPort = stompPort
        self.stompLogin = stompLogin
        self.stompPassword = stompPassword
        self.stompWhatsAppDestinationOutbox = stompWhatsAppDestinationOutbox
        self.stompWhatsAppDestinationInboxPrefix = stompWhatsAppDestinationInboxPrefix

    def setWhatsAppStack(self, whatsAppStack):
        self.whatsAppStack = whatsAppStack

    def start(self):
        self.connection = stomp.Connection([(self.stompHost, self.stompPort)])
        listener = MessagesListener()
        if self.whatsAppStack:
            listener.setWhatsAppStack(self.whatsAppStack)
        self.connection.set_listener('messages', MessagesListener())
        self.connection.start()
        self.connection.connect(self.stompLogin, self.stompPassword, wait=True)
        self.connection.subscribe(self.stompWhatsAppDestinationOutbox, self.stompWhatsAppDestinationOutbox)

    def stop(self):
        self.connection.unsubscribe(self.stompWhatsAppDestinationOutbox)
        self.connection.disconnect()
        self.connection.stop()

    def forwardTextMessage(self, messageFrom, messageBody):
        dest = self.stompWhatsAppDestinationInboxPrefix + '.' + messageFrom
        self.connection.send(dest, messageBody)
        logger.info("Forwared message to ActiveMQ queue: '" + dest + "' FROM: " + messageFrom + " TEXT: " + messageBody)

    def forwardImageURL(self, messageFrom, url, caption, fileName, mimeType, size):
        dest = self.stompWhatsAppDestinationInboxPrefix + '.' + messageFrom
        message = url
        if caption:
            message += " " + caption
        self.connection.send(dest, message)
        logger.info("Forwared Image to ActiveMQ queue: %s FROM: %s URL %s CAPTION: %s FILENAME: %s MIME TYPE: %s SIZE: %s " % (dest, messageFrom, url, caption, fileName, mimeType, size))
