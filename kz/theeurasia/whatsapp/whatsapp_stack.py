'''
@author: vadim.isaev
'''
from yowsup import env
from yowsup.common.constants import YowConstants
from yowsup.layers import YowParallelLayer, YowLayerEvent
from yowsup.layers.auth.autherror import AuthError
from yowsup.layers.auth.layer_authentication import YowAuthenticationProtocolLayer
from yowsup.layers.axolotl.layer import YowAxolotlLayer
from yowsup.layers.coder.layer import YowCoderLayer
from yowsup.layers.network.layer import YowNetworkLayer
from yowsup.layers.protocol_acks.layer import YowAckProtocolLayer
from yowsup.layers.protocol_messages.layer import YowMessagesProtocolLayer
from yowsup.layers.protocol_receipts.layer import YowReceiptProtocolLayer
from yowsup.stacks import YOWSUP_CORE_LAYERS
from yowsup.stacks.yowstack import YowStack

from kz.theeurasia.whatsapp.whatsapp_layer import WhatsAppLayer


class WhatsAppStack(object):
    whatsAppPhone = None
    whatsAppPassword = None
    stompService = None
    yowsupStack = None

    def __init__(self, whatsAppPhone, whatsAppPassword, stompService):
        self.whatsAppPhone = whatsAppPhone
        self.whatsAppPassword = whatsAppPassword
        self.stompService = stompService

    def start(self):
        layers = (
                  WhatsAppLayer,
                  YowParallelLayer([YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer]), YowAxolotlLayer
        ) + YOWSUP_CORE_LAYERS
        self.yowsupStack = YowStack(layers)
        self.yowsupStack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, (self.whatsAppPhone, self.whatsAppPassword))  # setting credentials
        self.yowsupStack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])  # whatsapp server address
        self.yowsupStack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
        self.yowsupStack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())  # info about us as WhatsApp client
        self.yowsupStack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))  # sending the connect signal

        for i in range(0, 50):
            layer = self.yowsupStack.getLayer(i)
            if layer.__class__ == WhatsAppLayer:
                layer.setStompService(self.stompService)
                break

        try:
            self.yowsupStack.loop()
        except AuthError as e:
            print("Authentication Error: %s" % e.message)

    def stop(self):
        self.yowsupStack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_DISCONNECT))

