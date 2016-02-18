# -*- coding: utf-8 -*-
'''
@author: vadim.isaev
'''
import logging

from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_acks.protocolentities.ack_outgoing import OutgoingAckProtocolEntity
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities.receipt_outgoing import OutgoingReceiptProtocolEntity


logger = logging.getLogger(__name__)

class WhatsAppLayer(YowInterfaceLayer):

    stompService = None
    autoReply = False

    @ProtocolEntityCallback("message")
    def onMessage(self, entity):
        self.sendReceipt(entity)
        if self.autoReply:
            self.sendAutoRepy(entity)
        if entity.getType() == 'text':
            self.onTextMessage(entity)
        elif entity.getType() == 'media':
            if entity.getMediaType() == 'image':
                self.onImageMessage(entity)
            elif entity.getMediaType() == 'audio':
                self.onAudioMessage(entity)
            elif entity.getMediaType() == 'video':
                self.onVideoMessage(entity)
            elif entity.getMediaType() == 'vcard':
                self.onVCardMessage(entity)
            elif entity.getMediaType() == 'location':
                self.onLocationMessage(entity)
            else:
                self.sendUnsupported(entity)
        else:
            self.sendUnsupported(entity)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)

    def setStompService(self, stompService):
        self.stompService = stompService

    def setAutoReply(self, autoReply):
        self.autoReply = autoReply

    def sendReceipt(self, entity):
        receipt = OutgoingReceiptProtocolEntity(entity.getId(), entity.getFrom(), 'read', entity.getParticipant())
        self.toLower(receipt)

    def sendUnsupported(self, entity, message="Данные виды сообщений не поддерживаются"):
        replyEntity = TextMessageProtocolEntity(message, to=entity.getFrom())
        self.toLower(replyEntity)

    def sendAutoRepy(self, entity):
        self.toLower(entity.forward(entity.getFrom()))

    def onTextMessage(self, entity):
        if self.stompService:
            self.stompService.forwardTextMessage(
                                                 entity.getFrom(False),
                                                 entity.getBody(),
                                                 entity.getTimestamp())

    def onImageMessage(self, entity):
        if self.stompService:
            self.stompService.forwardImageURL(
                                              entity.getFrom(False),
                                              entity.url,
                                              entity.caption,
                                              entity.fileName,
                                              entity.mimeType,
                                              entity.size,
                                              entity.getTimestamp())

    def onAudioMessage(self, entity):
        self.sendUnsupported(entity, "Аудио сообщения не поддерживаются")

    def onVideoMessage(self, entity):
        self.sendUnsupported(entity, "Видео сообщения не поддерживаются")

    def onVCardMessage(self, entity):
        self.sendUnsupported(entity, "Визитки не поддерживаются")

    def onLocationMessage(self, entity):
        self.sendUnsupported(entity, "Точки местоположения не поддерживаются")

    def sendTextMessage(self, msgTo, text):
        phone = self.normalizeJid(msgTo)
        entity = TextMessageProtocolEntity(text, to=phone)
        self.toLower(entity)

    def normalizeJid(self, phone):
        if '@' in phone:
            return phone
        elif '-' in phone:
            return "%s@g.us" % phone
        else:
            return "%s@s.whatsapp.net" % phone
