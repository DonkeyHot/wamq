# -*- coding: utf-8 -*-
'''
@author: vadim.isaev
'''
import logging

import stomp
from stomp.constants import HDR_CONTENT_TYPE, HDR_CONTENT_LENGTH
from stomp.exception import ConnectFailedException

from wamqd import functions
from wamqd.constants import *


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
        whatsappMessageType = headers[HDR_WHATSAPP_MESSAGE_TYPE]
        whatsappRecipient = headers[HDR_WHATSAPP_RECIPIENT]
        whatsappSender = headers[HDR_WHATSAPP_SENDER]
        if whatsappMessageType == MESSAGE_TYPE_TEXT:
            self.whatsAppService.sendTextMessage(whatsappSender, whatsappRecipient, message)
            logger.info("Sending message to WhatsApp number '%s'" % whatsappRecipient)
        elif whatsappMessageType == MESSAGE_TYPE_IMAGE:
            logger.error("Message type '%s' is not supported" % whatsappMessageType)
        else:
            logger.error("Message type '%s' is not supported" % whatsappMessageType)

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
    stompInboxDestinations = None
    whatsAppPhone = None

    whatsAppService = None

    def __init__(self,
                 stompHost,
                 stompPort,
                 stompLogin,
                 stompPassword,
                 stompReconnectionAttemps,
                 stompOutboxDestinations,
                 stompInboxDestinations,
                 whatsAppPhone):
        self.stompHost = stompHost
        self.stompPort = stompPort
        self.stompLogin = stompLogin
        self.stompPassword = stompPassword
        self.stompReconnectionAttemps = stompReconnectionAttemps
        self.stompOutboxDestinations = stompOutboxDestinations
        self.stompInboxDestinations = stompInboxDestinations
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

    def forwardTextMessage(self, msgId, msgSender, msgText, msgSentTimestamp):
        if self.stompInboxDestinations:
            for dest in self.stompInboxDestinations:
                self.connection.send(dest,
                                     msgText,
                                     headers={
                                              HDR_CONTENT_TYPE: CONTENT_TYPE_TEXT_MESSAGE,
                                              HDR_CONTENT_LENGTH: None,
                                              HDR_WHATSAPP_MESSAGE_TYPE: MESSAGE_TYPE_TEXT,
                                              HDR_WHATSAPP_ID: msgId,
                                              HDR_WHATSAPP_SENDER: msgSender,
                                              HDR_WHATSAPP_RECIPIENT: self.whatsAppPhone,
                                              HDR_WHATSAPP_SENT: functions.convertTimeStampToText(msgSentTimestamp)
                                              }
                                     )
                logger.info("TEXT forwarded to ActiveMQ destination '%s'" % dest)

    def forwardImageURL(self, msgId, msgSender, url, caption, fileName, mimeType, msgSentTimestamp):
        import urllib2
        response = urllib2.urlopen(url)
        image = response.read()

        if self.stompInboxDestinations:
            for dest in self.stompInboxDestinations:
                self.connection.send(dest,
                                     image,
                                     headers={
                                              HDR_CONTENT_TYPE: mimeType,
                                              HDR_CONTENT_LENGTH: len(image),
                                              HDR_WHATSAPP_MESSAGE_TYPE: MESSAGE_TYPE_IMAGE,
                                              HDR_WHATSAPP_ID: msgId,
                                              HDR_WHATSAPP_SENDER: msgSender,
                                              HDR_WHATSAPP_RECIPIENT: self.whatsAppPhone,
                                              HDR_WHATSAPP_SENT: functions.convertTimeStampToText(msgSentTimestamp),
                                              HDR_WHATSAPP_FILE_NAME: fileName,
                                              HDR_WHATSAPP_IMAGE_TEXT: caption
                                              }
                                     )
                logger.info("IMAGE message forwarded to ActiveMQ destination '%s'" % dest)

    def checkAlive(self):
        if not self.connection.is_connected():
            logger.info("Stomp service is not alive. Restarting...")
            self.start()
