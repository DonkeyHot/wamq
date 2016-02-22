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
    stompListeningDestinations = None
    stompWhatsAppDestinationInboxPrefix = None
    whatsAppPhone = None

    whatsAppService = None

    def __init__(self,
                 stompHost,
                 stompPort,
                 stompLogin,
                 stompPassword,
                 stompReconnectionAttemps,
                 stompListeningDestinations,
                 stompWhatsAppDestinationInboxPrefix,
                 whatsAppPhone):
        self.stompHost = stompHost
        self.stompPort = stompPort
        self.stompLogin = stompLogin
        self.stompPassword = stompPassword
        self.stompReconnectionAttemps = stompReconnectionAttemps
        self.stompListeningDestinations = stompListeningDestinations
        self.stompWhatsAppDestinationInboxPrefix = stompWhatsAppDestinationInboxPrefix
        self.whatsAppPhone = whatsAppPhone

    def setWhatsAppService(self, whatsAppService):
        self.whatsAppService = whatsAppService



#                 host_and_ports=None,
#                 prefer_localhost=True,
#                 try_loopback_connect=True,
#                 reconnect_sleep_initial=0.1,
#                 reconnect_sleep_increase=0.5,
#                 reconnect_sleep_jitter=0.1,
#                 reconnect_sleep_max=60.0,
#                 reconnect_attempts_max=3,
#                 use_ssl=False,
#                 ssl_key_file=None,
#                 ssl_cert_file=None,
#                 ssl_ca_certs=None,
#                 ssl_cert_validator=None,
#                 wait_on_receipt=False,
#                 ssl_version=DEFAULT_SSL_VERSION,
#                 timeout=None,
#                 heartbeats=(0, 0),
#                 keepalive=None,
#                 vhost=None,
#                 auto_decode=True,
#                 auto_content_length=True):

    def start(self):
        logger.info("Starting Stomp service...")
        try:
            self.connection = stomp.Connection(
                                               [(self.stompHost, self.stompPort)],
                                               reconnect_attempts_max=self.stompReconnectionAttemps)
            if not self.whatsAppService:
                raise StompServiceException("WhatsApp service is not set")
            listener = MessagesListener(self.whatsAppService)
            self.connection.set_listener('messages', listener)
            self.connection.start()
            self.connection.connect(self.stompLogin, self.stompPassword, wait=True)
            if self.stompListeningDestinations:
                for dest in self.stompListeningDestinations:
                    logger.info("Stomp service is listening '%s'" % dest)
                    self.connection.subscribe(dest, dest)
        except ConnectFailedException:
            logger.error("Connection to Stomp server failed")
            raise

    def stop(self):
        logger.info("Stopping Stomp service...")
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
        jsonCode = functions.safeJsonEncode(message)
        self.connection.send(dest, jsonCode)
        logger.info("Text message forwarded to ActiveMQ destination '%s'" % dest)

    def forwardImageURL(self, messageFrom, url, caption, fileName, mimeType, size, timestamp):
        dest = self.stompWhatsAppDestinationInboxPrefix + '.' + messageFrom
        message = {
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

        jsonCode = functions.safeJsonEncode(message)
        self.connection.send(dest, jsonCode)
        logger.info("Image message forwarded to ActiveMQ destination '%s'" % dest)

    def checkAlive(self):
        if not self.connection.is_connected():
            logger.info("Stomp service is not alive. Restarting...")
            self.start()
