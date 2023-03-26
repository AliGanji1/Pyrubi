from random import choice
from urllib3 import PoolManager
from json import loads

def get_server(type):
    if type == 'api':
        return f'https://messengerg2c2.iranlms.ir/'
    else:
        return choice(list(loads(PoolManager().request('GET', 'https://getdcmess.iranlms.ir/').data.decode())['data']['socket'].values()))