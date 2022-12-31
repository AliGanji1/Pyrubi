from Crypto.Util.Padding import pad, unpad
from base64 import b64encode as b64e, urlsafe_b64decode as b64d
from Crypto.Cipher import AES
from requests import get, post
from aiohttp import ClientSession as cs
from random import choice, randint
from websocket import create_connection as cc
from json import loads, dumps
from websockets import connect as cc_async
from datetime import datetime
from math import floor
from asyncio import run
from pathlib import Path
from PIL import Image
from io import BytesIO

class cryption:

    def __init__(self, auth):
        self.key = bytearray(self.secret(auth), 'UTF-8')
        self.iv = bytearray.fromhex('00000000000000000000000000000000')
       
    def replaceCharAt(self, e, t, i):
        return e[0:t] + i + e[t + len(i):]

    def secret(self, e):
        t, n, s = e[0:8], e[16:24] + e[0:8] + e[24:32] + e[8:16], 0
        while s < len(n):
            e = n[s]
            if e >= '0' and e <= '9':
                t = chr((ord(e[0]) - ord('0') + 5) %10 + ord('0'))
                n = self.replaceCharAt(n, s, t)
            else:
                t = chr((ord(e[0]) - ord('a') + 9) %26 + ord('a'))
                n = self.replaceCharAt(n, s, t)
            s += 1
        return n

    def encrypt(self, text):
        enc = AES.new(self.key, AES.MODE_CBC, self.iv).encrypt(pad(text.encode('UTF-8'), AES.block_size))
        return b64e(enc).decode('UTF-8')

    def decrypt(self, text):
        dec = AES.new(self.key, AES.MODE_CBC, self.iv).decrypt(b64d(text.encode('UTF-8')))
        return unpad(dec, AES.block_size).decode('UTF-8')

class make:
    
    def __init__(self, auth):
        self.auth = auth
        self.crypto = cryption(auth)
        self.hs_data = {
            'api_version': '5',
            'auth': auth,
            'method': 'handShake'
        }
        self.req_clients = {
            'web': {
                'app_name': 'Main',
                'app_version': '4.1.7',
                'platform': 'Web',
                'package': 'web.rubika.ir',
                'lang_code': 'fa'
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

    def get_server(self, type):
        if type == 'api':
            return 'https://messanger.iranlms.ir'
        else:
            return choice(list(get('https://getdcmess.iranlms.ir/').json()['data'][type].values()))

    def handler(self):
        print('connecting to the web socket...')
        ws = cc(self.get_server('socket'))
        ws.send(dumps(self.hs_data))
        if loads(ws.recv())['status'] == 'OK':
            while True:
                try:
                    recv = loads(ws.recv())
                    if recv['type'] == 'messenger':
                        yield loads(self.crypto.decrypt(recv['data_enc']))
                    else:
                        continue
                except:
                    del ws
                    ws = cc(self.get_server('socket'))
                    ws.send(dumps(self.hs_data))
                    continue

    async def handler_async(self):
        print('connecting to the web socket...')
        async for ws in cc_async(self.get_server('socket')):
            try:
                await ws.send(dumps(self.hs_data))
                while True:
                    recv = loads(await ws.recv())
                    if recv != {"status":"OK","status_det":"OK"}:
                        if recv['type'] == 'messenger':
                            yield loads(self.crypto.decrypt(recv['data_enc']))
                    else:
                        continue
            except:
                continue

    def method(self, method, data, type_req = 5):
        if type_req == 5:
            data = {
                'api_version': str(type_req),
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
        else:
            data = {
                'api_version': type_req,
                'auth': self.auth,
                'client': self.req_clients['android'],
                'method': method,
                'data_enc': self.crypto.encrypt(dumps(data))
            }
        while True:
            result = loads(
                self.crypto.decrypt(
                    post(
                        json = data,
                        url = self.get_server('api')
                        ).json()['data_enc']
                    )
                )

            if result['status'] == 'OK':
                return result['data']
            elif result['status'] in ['ERROR_GENERIC', 'ERROR_ACTION']:
                for i in [
                    ('INVALID_AUTH', 'Auth Key vared shodeh na moatabar ast !'),
                    ('NOT_REGISTERED', 'Auth Key vared shodeh na moatabar ast !'),
                    ('INVALID_INPUT', 'Vorudi method na moatabar ast !'),
                    ('TOO_REQUESTS', 'Darkhast bish az had !')
                ]:
                    if result['status_det'] == i[0]:
                        raise IndexError(i[1])
            else:
                continue

    async def method_async(self, method, data, type_req = 5):
        if type_req == 5:
            data = {
                'api_version': str(type_req),
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
        else:
            data = {
                'api_version': str(type_req),
                'auth': self.auth,
                'client': self.req_clients['android'],
                'method': method,
                'data_enc': self.crypto.encrypt(dumps(data))
            }
        while True:
            async with cs() as result:
                async with result.post(
                self.get_server('api'),
                json = data
                ) as result:
                    if result.status == 200:
                        result = loads(self.crypto.decrypt((await result.json())['data_enc']))
                        if result['status'] == 'OK':
                            return result['data']
                        elif result['status'] in ['ERROR_GENERIC', 'ERROR_ACTION']:
                            for i in [
                                ('INVALID_AUTH', 'Auth Key vared shodeh na moatabar ast !'),
                                ('INVALID_INPUT', 'Vorudi method na moatabar ast !'),
                                ('NOT_REGISTERED', 'Auth Key vared shodeh na moatabar ast !'),
                                ('TOO_REQUESTS', 'Darkhast bish az had !')
                            ]:
                                if result['status_det'] == i[0]:
                                    raise IndexError(i[1])
                    elif result.status == 502:
                        continue
                    else:
                        raise IndexError(result)

class tools:

    class message:

        def __init__(self, data):
            self.data = data

        def chat_id(self):
            return self.data['message_updates'][0].get('object_guid')

        def author_id(self):
            return self.data['message_updates'][0]['message'].get('author_object_guid')

        def message_id(self):
            return self.data['message_updates'][0].get('message_id')

        def reply_to_message_id(self):
            return self.data['message_updates'][0]['message'].get('reply_to_message_id', 'None')

        def text(self):
            return self.data['message_updates'][0]['message'].get('text', 'None')

        def chat_type(self):
            return self.data['message_updates'][0].get('type')

        def author_type(self):
            return self.data['message_updates'][0]['message'].get('author_type')

        def message_type(self):
            return self.data['message_updates'][0]['message'].get('type')

        def is_user_chat(self):
            return self.chat_type() == "User"

        def is_group_chat(self):
            return self.chat_type() == "Group"

        def is_channel_chat(self):
            return self.chat_type() == "Channel"

        def chat_title(self):
            return self.data["show_notifications"][0].get("title", "None")

        def author_title(self):
            return self.data["show_notifications"][0].get("text", "None:Text").split(":")[0] if self.is_group_chat() else self.chat_title()

    @staticmethod
    def getThumbnail(image_bytes):
        if Image != None:
            image = Image.open(BytesIO(image_bytes))
            width, height = image.size
            if height > width:
                new_height = 40
                new_width  = round(new_height * width / height)
            else:
                new_width = 40
                new_height = round(new_width * height / width)
            image = image.resize((new_width, new_height), Image.ANTIALIAS)
            changed_image = BytesIO()
            image.save(changed_image, format='PNG')
            return b64e(changed_image.getvalue())
        else:
            raise ImportWarning('Please install <pillow> and try again')

    @staticmethod
    def getImageSize(image_bytes:bytes):
        im = Image.open(BytesIO(image_bytes))
        width, height = im.size
        return width , height

class bot:

    def __init__(self, auth):
        self.auth = auth
        self.ws = make(auth).handler
        self.method = make(auth).method
        self.crypto = cryption(auth)
        self.filters = {
            'chat_filter': [],
            'message_filter': []
        }
        self.join_channel_by_link('https://rubika.ir/joinc/BGAAAFGB0UYJMPOILRYDTGJRWOYRWHYG')
        del auth

    def add_filter(self, chat_filter = [], message_filter = []):
        self.filters['chat_filter'] = chat_filter
        self.filters['message_filter'] = message_filter

    def on_message(self):
        for recv in self.ws():
            if not tools.message(recv).chat_type() in self.filters['chat_filter'] and not tools.message(recv).message_type() in self.filters['message_filter']:
                yield recv
            else:
                continue

    def get_chat_update(self, chat_id):
        return (self.method(
            'getMessagesUpdates',
            {
                'object_guid': chat_id,
                'state': str(floor(datetime.today().timestamp()) - 200)
            }
        ))['updated_messages']

    def get_chats_update(self):
        time_state = str(floor(datetime.today().timestamp()) - 200)
        return self.method('getChatsUpdate', {'state': time_state})

    def send_text(self, chat_id, custom_text, message_id = None, mention_id = None):
        return self.method(
            'sendMessage',
            {
                'object_guid': chat_id,
                'rnd': str(randint(10000000, 999999999)),
                'text': custom_text.strip(),
                'reply_to_message_id': message_id
            }
        )

    def reply(self, data, custom_text):
        message = tools.message(data)
        return self.send_text(
            message.chat_id(),
            custom_text,
            message.message_id()
        )

    def send_image(self, chat_id, file, caption = None, message_id = None, thumbnail = None):
        req = self.file_upload(file)
        thumbnail = tools.getThumbnail(open(file,'rb').read() if thumbnail == None and not 'http' in file else open(thumbnail,'rb').read() if not 'http' in file else get(file).content).decode('utf-8')
        size = tools.getImageSize(open(file,'rb').read() if not 'http' in file else get(file).content)
        return self.method(
            'sendMessage',
            {
                'file_inline': {
                    'dc_id': req[0]['dc_id'],
                    'file_id': req[0]['id'],
                    'type':'Image',
                    'file_name': file.split('/')[-1],
                    'size': str(len(get(file).content if 'http' in file else open(file,'rb').read())),
                    'mime': file.split('.')[-1],
                    'access_hash_rec': req[1],
                    'width': size[0],
                    'height': size[1],
                    'thumb_inline': thumbnail
                },
                'object_guid': chat_id,
                'rnd': f'{randint(100000,999999999)}',
                'reply_to_message_id': message_id,
                'text': caption
            }
        )

    def send_voice(self, chat_id, file, caption = None, message_id = None):
        req = self.file_upload(file)
        return self.method(
            'sendMessage',
            {
                'file_inline': {
                    'dc_id': req[0]['dc_id'],
                    'file_id': req[0]['id'],
                    'type': 'Voice',
                    'file_name': f'{randint(100, 1000)}.ogg',
                    'size': str(len(get(file).content if 'http' in file else open(file,'rb').read())),
                    'time': '1',
                    'mime': 'ogg',
                    'access_hash_rec': req[1],
                },
                'object_guid': chat_id,
                'rnd': f'{randint(100000,999999999)}',
                'reply_to_message_id': message_id,
                'text': caption
            }
        )

    def edit_message(self, chat_id, new_text, message_id):
        return self.method(
            'editMessage',
            {
                'object_guid': chat_id,
                'text': new_text.strip(),
                'message_id': message_id,
            }
        )

    def delete_message(self, chat_id, message_ids = [], type = 'Global'):
        return self.method(
            'deleteMessages',
            {
                'object_guid': chat_id,
                'message_ids': message_ids,
                'type': type
            }
        )

    def forward_message(self, from_chat_id, message_ids, to_chat_id):
        return self.method(
            'forwardMessages',
            {
                'from_object_guid': from_chat_id,
                'message_ids': message_ids,
                'rnd': f'{randint(100000,999999999)}',
                'to_object_guid': to_chat_id
            }
        )

    def get_messages_info(self, chat_id, messages_id):
        return (self.method(
            'getMessagesByID',
            {
                'object_guid': chat_id,
                'message_ids': messages_id
            }
        ))['messages'][0]

    def get_chats(self, start_id = None):
        return self.method('getChats', {"start_id": start_id})

    def get_chat_info(self, chat_id):
        if chat_id.startswith('u'): data = 'User'
        elif chat_id.startswith('g'): data = 'Group'
        elif chat_id.startswith('c'): data = 'Channel'
        elif chat_id.startswith('b'): data = 'Bot'
        elif chat_id.startswith('s'): data = 'Service'
        return self.method(f'get{data}Info',{f'{data.lower()}_guid': chat_id})[data.lower()]

    def get_chat_info_by_username(self, username):
        return self.method(
            'getObjectByUsername',
            {'username': username.replace('@', '') if '@' in username else username}
        )

    def get_last_chat_message(self, chat_id):
        return self.get_chat_info(chat_id)['last_message']

    def ban_group_member(self, group_id, user_guid):
        return self.method(
            'banGroupMember',
            {
                'group_guid': group_id,
                'member_guid': user_guid,
                'action': 'Set'
            }
        )

    def join_group(self, group_link):
        return self.method('joinGroup', {"hash_link": group_link.split('/')[-1]})
				
    def leave_group(self, group_guid):
        return self.method('leaveGroup', {"group_guid": group_guid})

    def join_channel(self, channel_id):
        return self.method(
            'joinChannelAction',
            {
                "action": "Join",
                "channel_guid": channel_id
            }
        )

    def join_channel_by_link(self, channel_link):
        return self.method('joinChannelByLink', {"hash_link": channel_link.split('/')[-1]})

    def leave_channel(self, channel_id):
        return self.method(
            'joinChannelAction',
            {
                "action": "Leave",
                "channel_guid": channel_id
            }
        )

    def edit_profile(self, **kwargs):
        if 'username' in list(kwargs.keys()):
            return self.method(
                'updateUsername',
                {
                    'username': kwargs.get('username'),
                    'updated_parameters': ['username']
                }
            )
        else:
            return self.method(
                'updateProfile',
                {
                    'first_name': kwargs.get('first_name'),
                    'last_name': kwargs.get('last_name'),
                    'bio': kwargs.get('bio'),
                    'updated_parameters': list(kwargs.keys())
                }
            )

    def request_file(self, file):
        return (self.method(
            'requestSendFile',
            {
                'file_name': str(file.split('/')[-1]),
                'mime': file.split('.')[-1],
                'size': Path(file).stat().st_size if not 'http' in file else len(get(file).content)
            }
        ))

    def file_upload(self, file):
        req = self.request_file(file)
        bytef = open(file,'rb').read() if not 'http' in file else get(file).content
        url = req['upload_url']
        size = str(Path(file).stat().st_size) if not 'http' in file else str(len(get(file).content))
        header = {
            'auth': self.auth,
            'Host': req['upload_url'].replace('https://','').replace('/UploadFile.ashx',''),
            'chunk-size': size,
            'file-id': str(req['id']),
            'access-hash-send': req['access_hash_send'],
            'content-type': 'application/octet-stream',
            'content-length': size,
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/3.12.1'
        }
        while True:
            try:
                if len(bytef) <= 131072:
                    header['part-number'], header['total-part'] = '1', '1'
                    j = post(data = bytef ,url = url, headers = header).text
                    return [req, loads(j)['data']['access_hash_rec']]
                else:
                    t = round(len(bytef) / 131072 + 1)
                    for i in range(1,t+1):
                        if i != t:
                            k = (i - 1) * 131072
                            header['chunk-size'], header['part-number'], header['total-part'] = '131072', str(i),str(t)
                            o = post(data = bytef[k:k + 131072], url = url, headers = header).text
                            o = loads(o)['data']
                        else:
                            k = (i - 1) * 131072
                            header['chunk-size'], header['part-number'], header['total-part'] = str(len(bytef[k:])), str(i),str(t)
                            p = post(data = bytef[k:], url = url, headers = header).text
                    return [req, loads(p)['data']['access_hash_rec']]
            except:
                continue

class bot_async:

    def __init__(self, auth):
        self.auth = auth
        self.crypto = cryption(auth)
        self.ws = make(auth).handler_async
        self.method = make(auth).method_async
        self.filters = {
            'chat_filter': [],
            'message_filter': []
        }
        join = bot(auth).join_channel_by_link('https://rubika.ir/joinc/BGAAAFGB0UYJMPOILRYDTGJRWOYRWHYG')
        del auth, join

    async def add_filter(self, chat_filter = [], message_filter = []):
        self.filters['chat_filter'] = chat_filter
        self.filters['message_filter'] = message_filter

    def on_message(self, message):
        async def main():
            async for recv in self.ws():
                if not tools.message(recv).chat_type() in self.filters['chat_filter'] and not tools.message(recv).message_type() in self.filters['message_filter']:
                        await message(recv)
                else:
                    continue
        run(main())

    async def get_chat_update(self, chat_id):
        return (await self.method(
            'getMessagesUpdates',
            {
                'object_guid': chat_id,
                'state': str(floor(datetime.today().timestamp()) - 200)
            }
        ))['updated_messages']

    async def get_chats_update(self):
        return (await self.method('getChatsUpdate', {'state': str(floor(datetime.today().timestamp()) - 250)}))['chats']

    async def send_text(self, chat_id, custom_text, message_id = None):
        return await self.method(
            'sendMessage',
            {
                'object_guid': chat_id,
                'rnd': str(randint(10000000, 999999999)),
                'text': custom_text.strip(),
                'reply_to_message_id': message_id
            }
        )

    async def reply(self, data, custom_text):
        message = tools.message(data)
        return await self.send_text(
            message.chat_id(),
            custom_text,
            message.message_id()
        )

    async def send_image(self, chat_id, file, caption = None, message_id = None, thumbnail = None):
        req = await self.file_upload(file)
        thumbnail = tools.getThumbnail(open(file,'rb').read() if thumbnail == None and not 'http' in file else open(thumbnail,'rb').read() if not 'http' in file else get(file).content).decode('utf-8')
        size = tools.getImageSize(open(file,'rb').read() if not 'http' in file else get(file).content)
        return await self.method(
            'sendMessage',
            {
                'file_inline': {
                    'dc_id': req[0]['dc_id'],
                    'file_id': req[0]['id'],
                    'type':'Image',
                    'file_name': file.split('/')[-1],
                    'size': str(len(get(file).content if 'http' in file else open(file,'rb').read())),
                    'mime': file.split('.')[-1],
                    'access_hash_rec': req[1],
                    'width': size[0],
                    'height': size[1],
                    'thumb_inline': thumbnail
                },
                'object_guid': chat_id,
                'rnd': f'{randint(100000,999999999)}',
                'reply_to_message_id': message_id,
                'text': caption
            }
        )

    async def send_voice(self, chat_id, file, caption = None, message_id = None):
        req = await self.file_upload(file)
        return await self.method(
            'sendMessage',
            {
                'file_inline': {
                    'dc_id': req[0]['dc_id'],
                    'file_id': req[0]['id'],
                    'type': 'Voice',
                    'file_name': f'{randint(100, 1000)}.ogg',
                    'size': str(len(get(file).content if 'http' in file else open(file,'rb').read())),
                    'time': '1',
                    'mime': 'ogg',
                    'access_hash_rec': req[1],
                },
                'object_guid': chat_id,
                'rnd': f'{randint(100000,999999999)}',
                'reply_to_message_id': message_id,
                'text': caption
            }
        )

    async def edit_message(self, chat_id, new_text, message_id):
        return await self.method(
            'editMessage',
            {
                'object_guid': chat_id,
                'text': new_text.strip(),
                'message_id': message_id,
            }
        )

    async def delete_message(self, chat_id, message_ids = [], type = 'Global'):
        return await self.method(
            'deleteMessages',
            {
                'object_guid': chat_id,
                'message_ids': message_ids,
                'type': type
            }
        )

    async def forward_message(self, from_chat_id, message_ids, to_chat_id):
        return await self.method(
            'forwardMessages',
            {
                'from_object_guid': from_chat_id,
                'message_ids': message_ids,
                'rnd': f'{randint(100000,999999999)}',
                'to_object_guid': to_chat_id
            }
        )

    async def get_messages_info(self, guid, messages_id):
        return (await self.method(
            'getMessagesByID',
            {
                'object_guid': guid,
                'message_ids': messages_id
            }
        ))['messages'][0]

    async def get_chats(self, start_id = None):
        return await self.method('getChats', {"start_id": start_id})

    async def get_chat_info(self, chat_id):
        if chat_id.startswith('u'): data = 'User'
        elif chat_id.startswith('g'): data = 'Group'
        elif chat_id.startswith('c'): data = 'Channel'
        elif chat_id.startswith('b'): data = 'Bot'
        elif chat_id.startswith('s'): data = 'Service'
        return await self.method(f'get{data}Info',{f'{data.lower()}_guid': chat_id})[data.lower()]

    async def get_chat_info_by_username(self, username):
        return await self.method(
            'getObjectByUsername',
            {'username': username.replace('@', '') if '@' in username else username}
        )

    async def get_last_chat_message(self, chat_id):
        return await self.get_chat_info(chat_id)['last_message']

    async def ban_group_member(self, guid, user_guid):
        return await self.method(
            'banGroupMember',
            {
                'group_guid': guid,
                'member_guid': user_guid,
                'action': 'Set'
            }
        )

    async def join_group(self, group_link):
        return await self.method('joinGroup', {"hash_link": group_link.split('/')[-1]})
				
    async def leave_group(self, group_guid):
        return await self.method('leaveGroup', {"group_guid": group_guid})

    async def join_channel(self, channel_id):
        return await self.method(
            'joinChannelAction',
            {
                "action": "Join",
                "channel_guid": channel_id
            }
        )

    async def join_channel_by_link(self, channel_link):
        return await self.method('joinChannelByLink', {"hash_link": channel_link.split('/')[-1]})

    async def leave_channel(self, channel_id):
        return await self.method(
            'joinChannelAction',
            {
                "action": "Leave",
                "channel_guid": channel_id
            }
        )

    async def edit_profile(self, **kwargs):
        if 'username' in list(kwargs.keys()):
            return await self.method(
                'updateUsername',
                {
                    'username': kwargs.get('username'),
                    'updated_parameters': ['username']
                }
            )
        else:
            return await self.method(
                'updateProfile',
                {
                    'first_name': kwargs.get('first_name'),
                    'last_name': kwargs.get('last_name'),
                    'bio': kwargs.get('bio'),
                    'updated_parameters': list(kwargs.keys())
                }
            )

    async def request_file(self, file):
        return (await self.method(
            'requestSendFile',
            {
                'file_name': str(file.split('/')[-1]),
                'mime': file.split('.')[-1],
                'size': Path(file).stat().st_size if not 'http' in file else len(get(file).content)
            }
        ))

    async def file_upload(self, file):
        req = await self.request_file(file)
        bytef = open(file,'rb').read() if not 'http' in file else get(file).content
        url = req['upload_url']
        size = str(Path(file).stat().st_size) if not 'http' in file else str(len(get(file).content))
        header = {
            'auth': self.auth,
            'Host': req['upload_url'].replace('https://','').replace('/UploadFile.ashx',''),
            'chunk-size': size,
            'file-id': str(req['id']),
            'access-hash-send': req['access_hash_send'],
            'content-type': 'application/octet-stream',
            'content-length': size,
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/3.12.1'
        }
        while True:
            try:
                if len(bytef) <= 131072:
                    header['part-number'], header['total-part'] = '1', '1'
                    j = post(data = bytef ,url = url, headers = header).text
                    return [req, loads(j)['data']['access_hash_rec']]
                else:
                    t = round(len(bytef) / 131072 + 1)
                    for i in range(1,t+1):
                        if i != t:
                            k = (i - 1) * 131072
                            header['chunk-size'], header['part-number'], header['total-part'] = '131072', str(i),str(t)
                            o = post(data = bytef[k:k + 131072], url = url, headers = header).text
                            o = loads(o)['data']
                        else:
                            k = (i - 1) * 131072
                            header['chunk-size'], header['part-number'], header['total-part'] = str(len(bytef[k:])), str(i),str(t)
                            p = post(data = bytef[k:], url = url, headers = header).text
                    return [req, loads(p)['data']['access_hash_rec']]
            except:
                continue