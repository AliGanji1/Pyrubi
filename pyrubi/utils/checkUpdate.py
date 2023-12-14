from urllib3 import PoolManager
from json import loads

__version__ = "3.1.2"

def checkUpdate(appVersion:str=__version__) -> None:
    try:
        url:str = "https://aliganji1.github.io/api.pyrubi/checkUpdate.json"
        updateData = loads(PoolManager().request(method="GET", url=url).data.decode('UTF-8'))

        if updateData["version"] != appVersion:
            newUpdateText:str = '\u001b[33m' + f'\n{updateData["title"]}\nVersion: {updateData["version"]}\n\n{updateData["description"]}\n\nInstall: {updateData["update_command"]}\n' + '\u001b[37m'
            print(newUpdateText)
    except:
        pass