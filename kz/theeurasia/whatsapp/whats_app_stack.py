'''
@author: vadim.isaev
'''
import logging
import sys

from yowsup import env
from yowsup.common.constants import YowConstants
from yowsup.layers import YowParallelLayer, YowLayerEvent
from yowsup.layers.auth.autherror import AuthError
from yowsup.layers.auth.layer_authentication import YowAuthenticationProtocolLayer
from yowsup.layers.axolotl.layer import YowAxolotlLayer
from yowsup.layers.coder.layer import YowCoderLayer
from yowsup.layers.network.layer import YowNetworkLayer
from yowsup.layers.protocol_acks.layer import YowAckProtocolLayer
from yowsup.layers.protocol_media.layer import YowMediaProtocolLayer
from yowsup.layers.protocol_messages.layer import YowMessagesProtocolLayer
from yowsup.layers.protocol_receipts.layer import YowReceiptProtocolLayer
from yowsup.stacks import YOWSUP_CORE_LAYERS
from yowsup.stacks.yowstack import YowStack

from kz.theeurasia.whatsapp.whats_app_layer import WhatsAppLayer


ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(ch)

class WhatsAppStack(object):

    whatsAppPhone = None
    whatsAppPassword = None
    stompService = None
    autoReply = False
    yowsupStack = None

    def __init__(self,
                 whatsAppPhone,
                 whatsAppPassword,
                 autoReply,
                 stompService):
        self.whatsAppPhone = whatsAppPhone
        self.whatsAppPassword = whatsAppPassword
        self.autoReply = autoReply
        self.stompService = stompService


    def findWhatsAppLayerInStack(self):
        layer = None
        i = 0
        while (True):
            layer = self.yowsupStack.getLayer(i)
            if layer != None and layer.__class__ == WhatsAppLayer:
                return layer
            i += 1
        return None

    def setupWhatsAppLayer(self, layer):
        layer.setStompService(self.stompService)
        layer.setAutoReply(self.autoReply)

    def start(self):
        layers = (
                  WhatsAppLayer,
                  YowParallelLayer([
                                    YowAuthenticationProtocolLayer,
                                    YowMessagesProtocolLayer,
                                    YowMediaProtocolLayer,
                                    YowReceiptProtocolLayer,
                                    YowAckProtocolLayer
                                    ]),
                  YowAxolotlLayer
        ) + YOWSUP_CORE_LAYERS

        self.yowsupStack = YowStack(layers)
        self.yowsupStack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, (self.whatsAppPhone, self.whatsAppPassword))  # setting credentials
        self.yowsupStack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])  # whatsapp server address
        self.yowsupStack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
        self.yowsupStack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())  # info about us as WhatsApp client

        self.setupWhatsAppLayer(self.findWhatsAppLayerInStack())

        self.yowsupStack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))  # sending the connect signal
        try:
            self.yowsupStack.loop()
        except (KeyboardInterrupt, SystemExit):
            logger.error("CLIENT: Interrupted")
            return False
        except AuthError as e:
            logger.error("Authentication Error: %s" % e.message)
            return False

    def stop(self):
        self.yowsupStack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_DISCONNECT))

