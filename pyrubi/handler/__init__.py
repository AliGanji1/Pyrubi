from websocket import create_connection
from json import dumps, loads
from ..servers import get_server
from ..cryption import cryption
class handler:

    def __init__(self, auth, methods):
        self.server = get_server('socket')
        self.crypto = cryption(auth)
        self.auth = auth
        self.methods = methods
        self.hs_data = {
            'api_version': '5',
            'auth': auth,
            'method': 'handShake'
        }
        del auth
        del methods
    
    def hand_shake(self):
        print('connecting to the web socket...')
        ws = create_connection(self.server)
        self.methods.get_me()
        ws.send(dumps(self.hs_data))
        print('connected !')
        while True:
            try:
                recv = loads(ws.recv())
                if recv != {"status":"OK", "status_det":"OK"}:
                    if recv['type'] == 'messenger':
                        yield loads(self.crypto.decrypt(recv['data_enc']))
            except:
                ws.close()
                del ws
                ws = create_connection(self.server)
                self.methods.get_me()
                ws.send(dumps(self.hs_data))
                continue