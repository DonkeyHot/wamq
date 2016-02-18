'''
@author: vadim.isaev
'''
import json
import logging

import stomp
from stomp.exception import ConnectFailedException

import functions


logger = logging.getLogger(__name__)

class MessagesListener(object):

    recivedCount = 0;
    errorCount = 0
    whatsAppService = None

    def __init__(self, whatsAppService):
        self.whatsAppService = whatsAppService

    def on_error(self, headers, message):
        self.errorCount += 1
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        self.recivedCount += 1
        self.sendMessageToWhastapp(headers, message)

#        messages = [
#                       {
#                        'message' : {
#                                         'from' : messageFrom,
#                                         'to': self.whatsAppPhone,
#                                         'sent': functions.convertTimeStampToText(timestamp),
#                                         'type': 'text',
#                                         'content' : {
#                                                      'text': text
#                                                      }
#                                     }
#                        }
#                    ]

    def sendMessageToWhastapp(self, headers, message):
        msg = json.loads(message)
        sendTo = msg['to']
        sendFrom = msg['from']
        msgType = msg['type']
        content = msg['content']
        if msgType == 'text':
            text = content['text']
            self.whatsAppService.sendTextMessage(sendFrom, sendTo, text)


class StompServiceException(object):
    __message = None

    def __init__(self,message):
        self.__message = message

    def getMessage(self):
        return self.__message

class StompService(object):
    stompHost = None
    stompPort = None
    stompLogin = None
    stompPassword = None
    stompListeningDestinations = None
    stompWhatsAppDestinationInboxPrefix = None
    whatsAppPhone = None

    whatsAppService = None

    def __init__(self,
                 stompHost,
                 stompPort,
                 stompLogin,
                 stompPassword,
                 stompListeningDestinations,
                 stompWhatsAppDestinationInboxPrefix,
                 whatsAppPhone):
        self.stompHost = stompHost
        self.stompPort = stompPort
        self.stompLogin = stompLogin
        self.stompPassword = stompPassword
        self.stompListeningDestinations = stompListeningDestinations
        self.stompWhatsAppDestinationInboxPrefix = stompWhatsAppDestinationInboxPrefix
        self.whatsAppPhone = whatsAppPhone

    def setWhatsAppService(self, whatsAppService):
        self.whatsAppService = whatsAppService

    def start(self):
        logger.info("    Starting Stomp service...")
        try:
            self.connection = stomp.Connection([(self.stompHost, self.stompPort)])
            if not self.whatsAppService:
                raise StompServiceException("WhatsApp service is not set")
            listener = MessagesListener(self.whatsAppService)
            self.connection.set_listener('messages', listener)
            self.connection.start()
            self.connection.connect(self.stompLogin, self.stompPassword, wait=True)
            if self.stompListeningDestinations:
                for dest in self.stompListeningDestinations:
                    logger.info("        Stomp service is listening '%s'" % dest)
                    self.connection.subscribe(dest, dest)
        except ConnectFailedException:
            logger.error("Connection to Stomp server failed")
            raise

    def stop(self):
        logger.info("    Stopping Stomp service...")
        if self.stompListeningDestinations:
            for dest in self.stompListeningDestinations:
                self.connection.unsubscribe(dest)
        self.connection.disconnect()
        self.connection.stop()

    def forwardTextMessage(self, messageFrom, text, timestamp):
        dest = self.stompWhatsAppDestinationInboxPrefix + '.' + messageFrom
        message = {
                    'from' : messageFrom,
                    'to': self.whatsAppPhone,
                    'sent': functions.convertTimeStampToText(timestamp),
                    'type': 'text',
                    'content' : {
                                 'text': text
                                 }
                    }
        jsonCode = json.dumps(message, indent=4)
        self.connection.send(dest, jsonCode)
        logger.debug("Forwared message to ActiveMQ queue: '" + dest + "' FROM: " + messageFrom + " TEXT: " + text)

    def forwardImageURL(self, messageFrom, url, caption, fileName, mimeType, size, timestamp):
        dest = self.stompWhatsAppDestinationInboxPrefix + '.' + messageFrom
        message =  {
                    'from' : messageFrom,
                    'to': self.whatsAppPhone,
                    'sent': functions.convertTimeStampToText(timestamp),
                    'type': 'image',
                    'content' : {
                                 'caption' : caption,
                                 'fileName': fileName,
                                 'mimeType' : mimeType,
                                 'fileSize' : size,
                                 'url': url,
                                 }
                    }

        jsonCode = json.dumps(message, indent=4)
        self.connection.send(dest, jsonCode)
        logger.debug("Forwared Image to ActiveMQ queue: %s FROM: %s URL %s CAPTION: %s FILENAME: %s MIME TYPE: %s SIZE: %s " % (dest, messageFrom, url, caption, fileName, mimeType, size))

    def checkAlive(self):
        if not self.connection.is_connected():
            logger.info("    Stomp service is not alive. Restarting...")
            self.start()