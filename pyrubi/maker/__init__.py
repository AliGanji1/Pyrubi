from ..cryption import cryption
from ..servers import get_server
from urllib3 import PoolManager
from json import dumps, loads
from requests import  post

class maker:
    
    def __init__(self, auth, methods):
        self.auth = auth
        self.crypto = cryption(auth)
        self.http = PoolManager()
        self.server = get_server('api')
        self.methods = methods
        self.req_clients = {
            'web': {
                'app_name':'Main',
                'app_version':'4.2.0',
                'platform':'Web',
                'package':'web.rubika.ir',
                'lang_code':'fa'
            },
            'android': {
                'app_name': 'Main',
                'app_version': '3.0.9',
                'platform': 'Android',
                'package': 'ir.resaneh1.iptv',
                'lang_code': 'fa'
            }
        }
        del auth

    def method(self, method, data, api_version=5):
        data = {
            'api_version': str(api_version),
            'auth': self.auth,
            'data_enc': self.crypto.encrypt(
                dumps(
                    {
                        'method': method,
                        'input': data,
                        'client': self.req_clients['web']
                    }
                )
            )
        }
        trying = 0
        while True:
            result = self.http.request(
                'POST',
                self.server,
                body = dumps(data).encode(),
            )
            result = loads(self.crypto.decrypt(loads(result.data.decode('utf-8'))['data_enc']))
            if result['status'] == 'OK':
                return result['data']
            elif result['status'] in ['ERROR_GENERIC', 'ERROR_ACTION']:
                if result['status_det'] == 'INVALID_AUTH':
                    if trying < 3:
                        self.methods.get_me()
                        trying += 1
                        continue
                    raise ConnectionError('The Auth entered is invalid !')
                for i in [
                    ('NOT_REGISTERED', 'Method input is not registered !'),
                    ('INVALID_INPUT', 'Invalid method input !'),
                    ('TOO_REQUESTS', 'Too much request ! Your account has been suspended.')
                ]: 
                    if result['status_det'] == i[0]:
                        raise ConnectionError(i[1])
            continue

    def _upload(self, url, data, headers):
        while True:
            req = post(url=url, data=data, headers=headers)
            if req.status_code != 200:
                print('This file cannot be uploaded ! Trying to upload again ...')
                continue
            return req.json()
        
    def _download(self, url, headers):
        while True:
            try:
                return self.http.request(method='POST', url=url, headers=headers, preload_content=False)
            except:
                print('This file cannot be downloaded ! Trying to download again ...')
                continue