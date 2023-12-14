from json import dumps, loads
from tqdm import tqdm
from urllib3 import PoolManager
from websocket import create_connection, _exceptions as wsExceptions
from ..utils import Configs
from time import sleep
from threading import Thread
from ..utils import Exceptions

class Network:

    def __init__(self, methods:object) -> None:
        self.methods = methods
        self.sessionData = methods.sessionData
        self.crypto = methods.crypto
        self.http = PoolManager(proxy_url=methods.proxy) if methods.proxy else PoolManager()

    def getServer(self, type):
        if type == "api":
            from random import randint
            return f"https://messengerg2c{randint(2, 3)}.iranlms.ir"
        else:
            from random import choice
            return choice(list(loads(self.http.request("GET", "https://getdcmess.iranlms.ir/").data.decode())["data"]["socket"].values()))

    def request(self, method:str, input:dict={}, tmpSession:bool=False, apiVersion:int=6):
        url:str = self.getServer("api")

        data = {
            "api_version": apiVersion,
            "tmp_session" if tmpSession else "auth": self.crypto.auth if tmpSession else self.crypto.changeAuthType(self.sessionData["auth"]),
            "data_enc": self.crypto.encrypt(
                dumps({
                    "method": method,
                    "input": input,
                    "client": Configs.clients[self.methods.platform.lower()]
                })
            )
        }

        headers:dict = {
            "Referer": "https://web.rubika.ir/",
            "Content-Type": "application/json; charset=utf-8"
        }

        if self.sessionData:
            data["sign"] = self.crypto.makeSignFromData(data["data_enc"])

        while True:
            try:
                result = self.http.request(
                    method="POST",
                    url=url,
                    headers=headers,
                    body = dumps(data).encode(),
                    timeout=self.methods.timeOut
                )

                result = loads(self.crypto.decrypt(loads(result.data.decode("UTF-8"))["data_enc"]))

                if result["status"] == "OK":
                    if not self.sessionData:
                        result["data"]["tmp_session"] = self.crypto.auth

                    return result["data"]
                
                elif result["status"] in ["ERROR_GENERIC", "ERROR_ACTION"]:
                    raise self.raise_info[result["status_det"]]
                
                continue
            except:
                continue

    def handShake(self):
        global ws

        def sendData():
            ws.send(dumps(
                {
                    "api_version": "5",
                    "auth": self.sessionData["auth"],
                    "method": "handShake"
                }
            ))

        def keepAlive():
            while True:
                try:
                    sendData()
                    self.methods.getChatsUpdates()
                    sleep(60)
                except Exceptions.NotRegistered or Exceptions.InvalidAuth:
                    print("Invalid session data! Please enter a valid data of your account.")
                    exit()
                except Exceptions.TooRequests:
                    break
                except:
                    continue

        print("Connecting to the web socket...")
        wsServer:str = self.getServer("socket")

        while True:
            try:
                ws = create_connection(url=wsServer)

                sendData()
                if loads(ws.recv()).get("status") == "OK":
                    print("Connected.")

                    Thread(target=keepAlive, daemon=True).start()

                    while True:
                        recv:dict = loads(ws.recv())

                        if recv.get("type") == "messenger":
                            yield loads(self.crypto.decrypt(recv.get("data_enc")))

            except wsExceptions.WebSocketConnectionClosedException or wsExceptions.WebSocketAddressException:
                print("The websocket connection was disconnected! Reconnecting...")
                continue

    def upload(self, file:str and bytes, fileName:str=None, chunkSize:int=131072):
        from ..utils import Tools

        if isinstance(file, str):
            if Tools.checkLink(url=file):
                file:bytes = self.http.request(method="GET", url=file).data
                mime:str = Tools.getMimeFromByte(bytes=file)
                fileName = fileName or Tools.generateFileName(mime=mime)
            else:
                fileName = fileName or file
                mime = file.split(".")[-1]
                file = open(file, "rb").read()

        elif not isinstance(file, bytes):
            raise FileNotFoundError("Enter a valid path or url or bytes of file.")
        else:
            mime = Tools.getMimeFromByte(bytes=file)
            fileName = fileName or Tools.generateFileName(mime=mime)

        def send_chunk(data, maxAttempts=2):
            for attempt in range(maxAttempts):
                try:
                    response = self.http.request(
                        "POST",
                        url=requestSendFileData["upload_url"],
                        headers=header,
                        body=data
                    )
                    return loads(response.data.decode("UTF-8"))
                except Exception:
                    print(f"\nError uploading file! (Attempt {attempt + 1}/{maxAttempts})")
            
            print("\nFailed to upload the file!")

        requestSendFileData:dict = self.methods.requestSendFile(
            fileName = fileName,
            mime = mime,
            size = len(file)
        )

        header = {
            "auth": self.sessionData["auth"],
            "access-hash-send": requestSendFileData["access_hash_send"],
            "file-id": requestSendFileData["id"],
        }

        totalParts = (len(file) + chunkSize - 1) // chunkSize

        if self.methods.showProgressBar:
            processBar = tqdm(
                desc=f"Uploading {fileName}",
                total=len(file),
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            )

        for partNumber in range(1, totalParts + 1):
            startIdx = (partNumber - 1) * chunkSize
            endIdx = min(startIdx + chunkSize, len(file))
            header["chunk-size"] = str(endIdx - startIdx)
            header["part-number"] = str(partNumber)
            header["total-part"] = str(totalParts)
            data = file[startIdx:endIdx]
            hashFileReceive = send_chunk(data)
            if self.methods.showProgressBar:
                processBar.update(len(data))
            if not hashFileReceive: return
            if partNumber == totalParts:
                if not hashFileReceive["data"]: return
                requestSendFileData["file"] = file
                requestSendFileData["access_hash_rec"] = hashFileReceive["data"]["access_hash_rec"]
                requestSendFileData["file_name"] = fileName
                requestSendFileData["mime"] = mime
                requestSendFileData["size"] = len(file)
                return requestSendFileData
            
    def download(self, accessHashRec:str, fileId:str, dcId:str, size:int, fileName:str, chunkSize:int=131072):

        header:dict = {
            "Connection": "Keep-Alive",
            "Content-Type": "application/json",
            "User-Agent": "okhttp/3.12.1",
            "client-app-name": "Main",
            "client-app-version": "3.5.4",
            "app.rbmain.a": "app.rbmain.a",
            "client-platform": "Android",
            "auth": self.sessionData["auth"],
            "access-hash-rec": accessHashRec,
            "file-id": fileId,
            "start-index": "0"
        }

        data:bytes = b""

        def downloadChunk(maxAttempts=2) -> bytes:
            for attempt in range(maxAttempts):
                try:
                    return self.http.request(
                        "GET",
                        url=f"https://messenger{dcId}.iranlms.ir/GetFile.ashx",
                        headers=header,
                    ).data
                except Exception:
                    print(f"\nError downloading file! (Attempt {attempt + 1}/{maxAttempts})")
            
            print("\nFailed to download the file!")

        if self.methods.showProgressBar:
            processBar = tqdm(
                desc=f"Downloading {fileName}",
                total=size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            )

        while True:
            lastIndex = int(header["start-index"]) + chunkSize - 1 if int(header["start-index"]) + chunkSize < size else size - 1
            header["last-index"] = str(lastIndex)

            downloadedData = downloadChunk()
            if downloadedData:
                data += downloadedData
                if self.methods.showProgressBar:
                    processBar.update(len(downloadedData))

            if len(data) >= size:
                return data

            header["start-index"] = lastIndex + 1