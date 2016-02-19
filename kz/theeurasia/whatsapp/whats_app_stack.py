'''
@author: vadim.isaev
'''
import logging

from yowsup import env
from yowsup.common.constants import YowConstants
from yowsup.layers import YowParallelLayer, YowLayerEvent
from yowsup.layers.auth.autherror import AuthError
from yowsup.layers.auth.layer_authentication import YowAuthenticationProtocolLayer
from yowsup.layers.axolotl.layer import YowAxolotlLayer
from yowsup.layers.coder.layer import YowCoderLayer
from yowsup.layers.network.layer import YowNetworkLayer
from yowsup.layers.protocol_acks.layer import YowAckProtocolLayer
from yowsup.layers.protocol_iq.layer import YowIqProtocolLayer
from yowsup.layers.protocol_media.layer import YowMediaProtocolLayer
from yowsup.layers.protocol_messages.layer import YowMessagesProtocolLayer
from yowsup.layers.protocol_receipts.layer import YowReceiptProtocolLayer
from yowsup.stacks import YOWSUP_CORE_LAYERS

from kz.theeurasia.whatsapp.whats_app_layer import WhatsAppLayer
from yowsup.stacks.yowstack import YowStack


logger = logging.getLogger(__name__)


class WhatsAppException(object):
    _msg = None

    def __init__(self, msg):
        self._msg =  msg

    def getMessage(self):
        return self._msg

class WhatsAppStack(object):

    whatsAppPhone = None
    whatsAppPassword = None
    stompService = None
    autoReply = None
    replyUnsupported = None
    yowsupStack = None

    def __init__(self,
                 whatsAppPhone,
                 whatsAppPassword,
                 autoReply,
                 replyUnsupported,
                 stompService):
        self.whatsAppPhone = whatsAppPhone
        self.whatsAppPassword = whatsAppPassword
        self.autoReply = autoReply
        self.replyUnsupported = replyUnsupported
        self.stompService = stompService


    def findWhatsAppLayerInStack(self):
        self.layer = None
        for i in range(0, 100):
            self.layer = self.yowsupStack.getLayer(i)
            if self.layer != None and self.layer.__class__ == WhatsAppLayer:
                return
        raise WhatsAppException("Can't find WhatsAppLayer in Stack")

    def start(self):
        layers = (
                  WhatsAppLayer,
                  YowParallelLayer([
                                    YowAuthenticationProtocolLayer,
                                    YowMessagesProtocolLayer,
                                    YowMediaProtocolLayer,
                                    YowReceiptProtocolLayer,
                                    YowAckProtocolLayer,
                                    YowIqProtocolLayer
                                    ]),
                  YowAxolotlLayer
        ) + YOWSUP_CORE_LAYERS

        self.yowsupStack = YowStack(layers)
        self.yowsupStack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, (self.whatsAppPhone, self.whatsAppPassword))  # setting credentials
        self.yowsupStack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])  # whatsapp server address
        self.yowsupStack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
        self.yowsupStack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())  # info about us as WhatsApp client

        self.findWhatsAppLayerInStack()
        self.layer.setStompService(self.stompService)
        self.layer.setAutoReply(self.autoReply)
        self.layer.setReplyUnsupported(self.replyUnsupported)

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

