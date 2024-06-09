from urllib3 import PoolManager
from json import loads
from random import randint, choice

class Helper:

    @classmethod
    def getDcmess(self) -> dict:
        return loads(
            PoolManager().request(
                "GET",
                "https://getdcmess.iranlms.ir/"
            ).data.decode()
        )["data"]
        
    @classmethod
    def getApiServer(self) -> str:
        return f"https://messengerg2c{randint(2, 3)}.iranlms.ir"
    
    @classmethod
    def getSocketServer(self) -> str:
        return choice(list(self.getDcmess()["socket"].values()))