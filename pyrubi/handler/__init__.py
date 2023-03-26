from websocket import create_connection
from json import dumps, loads
from ..servers import get_server
from ..cryption import cryption

class handler:

    def __init__(self, auth):
        self.server = get_server('socket')
        self.crypto = cryption(auth)
        self.auth = auth
        del auth
    
    def hand_shake(self):
        print('connecting to the web socket...')
        ws = create_connection(self.server)
        ws.send(
            dumps(
                {
                    'api_version': '5',
                    'auth': self.auth,
                    'method': 'handShake'
                }
            )
        )
        print('connected !')
        while True:
            try:
                recv = loads(ws.recv())
                if recv != {"status":"OK","status_det":"OK"}:
                    if recv['type'] == 'messenger':
                        yield loads(self.crypto.decrypt(recv['data_enc']))
            except:
                print('There was a problem connecting to the web socket. Reconnecting...')
                del ws
                ws = create_connection(self.server)
                ws.send(
                    dumps(
                        {
                            'api_version': '5',
                            'auth': self.auth,
                            'method': 'handShake'
                        }
                    )
                )
                print('connected !')
                continue