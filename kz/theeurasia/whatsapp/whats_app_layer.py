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

    @ProtocolEntityCallback("message")
    def onMessage(self, entity):
        self.sendReceipt(entity)
        if entity.getType() == 'text':
            self.onTextMessage(entity)

    def sendReceipt(self, entity):
        receipt = OutgoingReceiptProtocolEntity(entity.getId(), entity.getFrom(), 'read', entity.getParticipant())
        self.toLower(receipt)

    def onTextMessage(self, entity):
        autoReplyEntity = TextMessageProtocolEntity("RE: " + entity.getBody(),to=entity.getFrom())
        self.toLower(autoReplyEntity)
        if self.stompService:
            self.stompService.forwardTextMessage(entity.getFrom(False), entity.getBody())
        logger.info("Received TextMessage '" + entity.getBody() + "  " + entity.getFrom(False))

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)

    def setStompService(self, stompService):
        self.stompService = stompService
