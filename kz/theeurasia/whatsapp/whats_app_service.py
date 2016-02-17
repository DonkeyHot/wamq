'''
@author: vadim.isaev
'''
from kz.theeurasia.whatsapp.whats_app_stack import WhatsAppStack



class WhatsAppService(object):
    whatsAppPhone = None
    whatsAppPassword = None

    stompService = None
    
    def __init__(self, whatsAppPhone, whatsAppPassword):
        self.whatsAppPhone = whatsAppPhone
        self.whatsAppPassword = whatsAppPassword

    def setStompService(self, stompService):
        self.stompService = stompService

    def start(self):
#        if not self.stompService:
#            raise Exception("StompService is not set")
        self.stack = WhatsAppStack(self.whatsAppPhone, self.whatsAppPassword, self.stompService)
        self.stack.start()
#        self.proc = Process(target=self.stack.start)
#        self.proc.start()

    def stop(self):
#        if self.proc:
#            self.proc.terminate()
        self.stack.stop()
