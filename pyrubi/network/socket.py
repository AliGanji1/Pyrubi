from websocket import WebSocketApp
from .helper import Helper
from json import dumps, loads
from threading import Thread
from ..types import Message
from ..exceptions import NotRegistered, TooRequests
from ..utils import Utils
from re import match
from time import sleep

class Socket:
    def __init__(self, methods) -> None:
        self.methods = methods
        self.handlers = {}

    def connect(self) -> None:
        print("Connecting to the webSocket...")
        ws = WebSocketApp(
            Helper.getSocketServer(),
            on_open=self.onOpen,
            on_message=self.onMessage
        )
        ws.run_forever()

    def handShake(self, ws, data=None) -> None:
        ws.send(
            data or dumps(
                {
                    "auth": self.methods.sessionData["auth"],
                    "api_version": self.methods.apiVersion,
                    "method": "handShake"
                }
            )
        )

    def keepAlive(self, ws) -> None:
        while True:
            try:
                self.methods.getChatsUpdates()
                self.handShake(ws, "{}")
                sleep(30)
            except NotRegistered:
                raise
            except TooRequests:
                break
            except:
                continue

    def onOpen(self, ws) -> None:
        Thread(target=self.keepAlive, args=[ws]).start()
        self.handShake(ws)
        print("Connected.")

    def onMessage(self, _, message:str) -> None:
        if not message:
            return
        
        message:dict = loads(message)

        if not message.get("type") == "messenger":
            return
        
        message:dict = loads(self.methods.crypto.decrypt(message["data_enc"]))

        if not message.get("message_updates"):
            return

        for handler in self.handlers:
            filters:list = self.handlers[handler]
            message:Message = Message(
                message,
                self.methods
            )

            if filters[0]:
                chatFilters:list = list(
                    map(
                        lambda x: x.lower() if Utils.isChatType(x) else x,
                        list(
                            filter(
                                lambda x: Utils.isChatType(x) or Utils.getChatTypeByGuid(x),
                                filters[0]
                            )
                        )
                    )
                )

                if chatFilters:
                    if message.object_guid in chatFilters:
                        pass

                    elif not message.chat_type.lower() in chatFilters:
                        return
                
                messageFilters:list = list(
                    map(
                        lambda x: x.lower(),
                        list(
                            filter(
                                lambda x: Utils.isMessageType(x),
                                filters[0]
                            )
                        )
                    )
                )
                
                if messageFilters and not message.message_type.lower() in messageFilters:
                    return
                
            if filters[1]:
                if not match(filters[1], message.text or ""):
                    return

            Thread(
                target=handler,
                args=[message]
            ).start()
                

    def addHandler(self, func, filters:list, regexp:str) -> None:
        self.handlers[func] = (filters, regexp)
        return func