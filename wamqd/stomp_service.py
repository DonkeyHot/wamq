'''
@author: vadim.isaev
'''
import logging

import stomp
from stomp.exception import ConnectFailedException

from wamqd import functions


logger = logging.getLogger(__name__)

class MessagesListener(object):

    recivedCount = 0;
    errorCount = 0
    whatsAppService = None

    def __init__(self, whatsAppService):
        self.whatsAppService = whatsAppService

    def on_error(self, headers, message):
        self.errorCount += 1
        logger.error('Received an error "%s"' % message)

    def on_message(self, headers, message):
        self.recivedCount += 1
        self.sendMessageToWhastapp(headers, message)

    def sendMessageToWhastapp(self, headers, message):
        msg = functions.safeJsonDecode(message)
        logger.info("Received message: %s" % msg)

        sendTo = msg['to']
        sendFrom = msg['from']
        msgType = msg['type']
        content = msg['content']
        if msgType == 'text':
            text = content['text']
            self.whatsAppService.sendTextMessage(sendFrom, sendTo, text)


class StompServiceException(object):
    __message = None

    def __init__(self, message):
        self.__message = message

    def getMessage(self):
        return self.__message

class StompService(object):
    stompHost = None
    stompPort = None
    stompLogin = None
    stompPassword = None
    stompReconnectionAttemps = None
    stompOutboxDestinations = None
    stompInboxDestinationPrefixes = None
    whatsAppPhone = None

    whatsAppService = None

    def __init__(self,
                 stompHost,
                 stompPort,
                 stompLogin,
                 stompPassword,
                 stompReconnectionAttemps,
                 stompOutboxDestinations,
                 stompInboxDestinationPrefixes,
                 whatsAppPhone):
        self.stompHost = stompHost
        self.stompPort = stompPort
        self.stompLogin = stompLogin
        self.stompPassword = stompPassword
        self.stompReconnectionAttemps = stompReconnectionAttemps
        self.stompOutboxDestinations = stompOutboxDestinations
        self.stompInboxDestinationPrefixes = stompInboxDestinationPrefixes
        self.whatsAppPhone = whatsAppPhone

    def setWhatsAppService(self, whatsAppService):
        self.whatsAppService = whatsAppService

    def start(self):
        logger.info("Starting Stomp service...")
        try:
            self.connection = stomp.Connection(
                                               [(self.stompHost, self.stompPort)],
                                               reconnect_attempts_max=self.stompReconnectionAttemps,
                                               auto_content_length=False)
            if not self.whatsAppService:
                raise StompServiceException("WhatsApp service is not set")
            listener = MessagesListener(self.whatsAppService)
            self.connection.set_listener('messages', listener)
            self.connection.start()
            self.connection.connect(self.stompLogin, self.stompPassword, wait=True)
            if self.stompOutboxDestinations:
                for dest in self.stompOutboxDestinations:
                    self.connection.subscribe(dest, dest)
                    logger.info("Stomp service is now listening '%s'" % dest)
        except ConnectFailedException:
            logger.error("Connection to Stomp server failed")
            raise

    def stop(self):
        logger.info("Stopping Stomp service...")
        if self.stompOutboxDestinations:
            for dest in self.stompOutboxDestinations:
                self.connection.unsubscribe(dest)
        self.connection.disconnect()
        self.connection.stop()

    def forwardTextMessage(self, messageFrom, text, timestamp):
        self._send(messageFrom, {
                                 'from' : messageFrom,
                                 'to': self.whatsAppPhone,
                                 'sent': functions.convertTimeStampToText(timestamp),
                                 'type': 'text',
                                 'content' : {'text': text}})

    def forwardImageURL(self, messageFrom, url, caption, fileName, mimeType, size, timestamp):
        self._send(messageFrom, {
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
                                              }})

    def _send(self, messageFrom, message):
        jsonCode = functions.safeJsonEncode(message)
        if self.stompInboxDestinationPrefixes:
            for d in self.stompInboxDestinationPrefixes:
                dest = "%s/%s" % (d, messageFrom)
                self.connection.send(dest, jsonCode)
                logger.info("Text message forwarded to ActiveMQ destination '%s'" % dest)

    def checkAlive(self):
        if not self.connection.is_connected():
            logger.info("Stomp service is not alive. Restarting...")
            self.start()
