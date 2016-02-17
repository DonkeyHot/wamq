'''
@author: vadim.isaev
'''

from kz.theeurasia.whatsapp.test.whatsapp_stack import WhatsAppStack


class WhatsAppServer(object):
    whatsAppPhone = None
    whatsAppPassword = None

    stompServer = None
    
    def __init__(self, whatsAppPhone, whatsAppPassword):
        self.whatsAppPhone = whatsAppPhone
        self.whatsAppPassword = whatsAppPassword

    def setStompServer(self, stompServer):
        self.stompServer = stompServer

    def start(self):
#        if not self.stompServer:
#            raise Exception("StompServer is not set")
        self.stack = WhatsAppStack(self.whatsAppPhone, self.whatsAppPassword, self.stompServer)
        self.stack.start()
#        self.proc = Process(target=self.stack.start)
#        self.proc.start()

    def stop(self):
#        if self.proc:
#            self.proc.terminate()
        self.stack.stop()
