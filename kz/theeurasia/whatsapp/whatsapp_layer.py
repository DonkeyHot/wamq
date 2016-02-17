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

    stompServer = None

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        # send receipt otherwise we keep receiving the same message over and over
        if True:
            receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom(), 'read', messageProtocolEntity.getParticipant())
            self.toLower(receipt)
            outgoingMessageProtocolEntity = TextMessageProtocolEntity(
                                                                      "RE: " + messageProtocolEntity.getBody(),
                                                                      to=messageProtocolEntity.getFrom()
                                                                      )
            self.toLower(outgoingMessageProtocolEntity)
            if messageProtocolEntity.getType() == 'text':
                self.onTextMessage(messageProtocolEntity)

    def onTextMessage(self, messageProtocolEntity):
        if self.stompServer:
            self.stompServer.forwardTextMessage(messageProtocolEntity.getFrom(False), messageProtocolEntity.getBody())
        logger.info("Received TextMessage '" + messageProtocolEntity.getBody() + "  " + messageProtocolEntity.getFrom(False))

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)

    def setStompServer(self, stompServer):
        self.stompServer = stompServer
