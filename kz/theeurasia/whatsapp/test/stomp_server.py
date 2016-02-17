'''
@author: vadim.isaev
'''
import stomp

class MessagesListener(object):
    def __init__(self):
        self.recivedCount = 0;
        self.errorCount = 0

    def on_error(self, headers, message):
        self.errorCount += 1
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        self.recivedCount += 1
        self.sendMessageToWhastapp(headers, message)

    def sendMessageToWhastapp(self, headers, message):
        print('Sending message "%s"' % message)
        pass

    def setWhatsAppStack(self, whats_app_stack):
        self.whats_app_stack = whats_app_stack

class StompServer(object):
    def __init__(self, stompServerHost, stompServerPort, stompServerLogin, stompServerPassword, stompServerWhatsappOutboxQueue, stomServerWhatsappInboxQueuePrefix):
        self.stompServerHost = stompServerHost
        self.stompServerPort = stompServerPort
        self.stompServerLogin = stompServerLogin
        self.stompServerPassword = stompServerPassword
        self.stompServerWhatsappOutboxQueue = stompServerWhatsappOutboxQueue
        self.stomServerWhatsappInboxQueuePrefix = stomServerWhatsappInboxQueuePrefix
        self.whatsAppStack = None
        
    def setWhatsAppStack(self, whatsAppStack):
        self.whatsAppStack = whatsAppStack
        
    def start(self):
        self.connection = stomp.Connection([(self.stompServerHost, self.stompServerPort)])
        listener = MessagesListener()
        if self.whatsAppStack:
            listener.setWhatsAppStack(self.whatsAppStack)
        self.connection.set_listener('messages', MessagesListener())
        self.connection.start()
        self.connection.connect(self.stompServerLogin, self.stompServerPassword, wait=True)
        self.connection.subscribe(self.stompServerWhatsappOutboxQueue, self.stompServerWhatsappOutboxQueue)

    def stop(self):
        self.connection.unsubscribe(self.stompServerWhatsappOutboxQueue)
        self.connection.disconnect()
        self.connection.stop()

    def forwardTextMessage(self, messageFrom, messageBody):
        dest = self.stomServerWhatsappInboxQueuePrefix + '.' + messageFrom
        self.connection.send(dest, messageBody)
        print("Message sent to queue: '" + dest + "' ActiveMQ " + messageFrom + " to ActiveMQ. Message body is " + messageBody)
    