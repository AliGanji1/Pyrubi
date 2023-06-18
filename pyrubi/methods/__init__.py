from ..cryption import cryption
from ..tools import tools
from ..message import message
from ..maker import maker
from ..handler import handler
from requests import session
from urllib3 import PoolManager
from random import choice, randint
from time import time
from pathlib import Path

class methods:

    def __init__(self, auth):
        self.auth = auth
        self.hs = handler(auth, self).hand_shake
        self.method = maker(auth, self).method
        self.crypto = cryption(auth)
        self.http = PoolManager()
        self.got_messages_update = []
        del auth


    def on_message(self, chat_filter=[], message_filter=[]):
        for recv in self.hs():
            if 'chat_updates' in recv and not message(recv).chat_type() in chat_filter and not message(recv).message_type() in message_filter:
                yield recv
            else:
                continue

    def get_chats_update(self, chat_filter=[], message_filter=[], save_message_ids=True):
        while True:
            try:
                chats_update = self.method('getChatsUpdates', {'state': round(time()) - 200})['chats'][0]
                if not message(chats_update).chat_type() in chat_filter and not message(chats_update).message_type() in message_filter:
                    if save_message_ids:
                        if not message(chats_update).message_id() in self.got_messages_update:
                            self.got_messages_update.append(message(chats_update).message_id())
                            yield chats_update
                    else:
                        yield chats_update
            except IndexError:
                continue

    def get_chats_update2(self):
        return self.method('getChatsUpdates', {'state': round(time()) - 200})['chats']

    def send_text(self, chat_id, text, message_id = None):
        metadata = tools.check_metadata(text)
        data = {
            'object_guid': chat_id,
            'rnd': str(randint(10000000, 999999999)),
            'text': metadata[1].strip() if metadata[1] != None else '????',
            'reply_to_message_id': message_id,
        }
        if metadata[0] != []:
            data['metadata'] = {'meta_data_parts': metadata[0]}
        return self.method('sendMessage', data)

    def reply(self, data, text):
        msg = message(data)
        return self.send_text(
            msg.chat_id(),
            text,
            msg.message_id(),
        )

    def send_image(self, chat_id, file, caption = None, message_id = None, thumbnail = None):
        req = self.upload_file(file)
        file_data = req[0]
        url_data = req[1]
        size = tools.get_image_size(file if str(type(file)) == "<class 'bytes'>" else open(file,'rb').read() if not url_data else url_data.data)
        metadata = tools.check_metadata(caption)
        data = {
            'file_inline': {
                'dc_id': file_data['dc_id'],
                'file_id': file_data['id'],
                'type':'Image',
                'file_name': f'Pyrubi {randint(1, 100)}.png' if url_data or str(type(file)) == "<class 'bytes'>" else file,
                'size': str(len(file)) if str(type(file)) == "<class 'bytes'>" else str(len(url_data.data)) if url_data else str(Path(file).stat().st_size),
                'mime': 'png',
                'access_hash_rec': req[2],
                'width': size[0],
                'height': size[1],
                'thumb_inline': tools.get_thumbnail(file if str(type(file)) == "<class 'bytes'>" else url_data.data if url_data else open(file or thumbnail, 'rb').read()).decode('utf-8')
            },
            'object_guid': chat_id,
            'rnd': str(randint(100000,999999999)),
            'reply_to_message_id': message_id,
            'text': metadata[1]
        }
        if metadata[0] != []:
            data['metadata'] = {'meta_data_parts': metadata[0]}
        return self.method('sendMessage', data)

    def send_video(self, chat_id, file, caption = None, message_id = None):
        req = self.upload_file(file)
        file_data = req[0]
        url_data = req[1]
        metadata = tools.check_metadata(caption)
        data = {
            'file_inline': {
                'file_id': file_data['id'],
                'mime': 'mp4',
                'dc_id': file_data['dc_id'],
                'access_hash_rec': req[2],
                'file_name': f'Pyrubi {randint(1, 100)}.mp4' if url_data or str(type(file)) == "<class 'bytes'>" else file,
                'thumb_inline': '/9j/4AAQSkZJRgABAQAAAQABAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYAAAAAAIQAABtbnRyUkdC\nIFhZWiAAAAAAAAAAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAA\nAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlk\nZXNjAAAA8AAAAHRyWFlaAAABZAAAABRnWFlaAAABeAAAABRiWFlaAAABjAAAABRyVFJDAAABoAAA\nAChnVFJDAAABoAAAAChiVFJDAAABoAAAACh3dHB0AAAByAAAABRjcHJ0AAAB3AAAADxtbHVjAAAA\nAAAAAAEAAAAMZW5VUwAAAFgAAAAcAHMAUgBHAEIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFhZWiAA\nAAAAAABvogAAOPUAAAOQWFlaIAAAAAAAAGKZAAC3hQAAGNpYWVogAAAAAAAAJKAAAA+EAAC2z3Bh\ncmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABYWVogAAAAAAAA9tYAAQAAAADT\nLW1sdWMAAAAAAAAAAQAAAAxlblVTAAAAIAAAABwARwBvAG8AZwBsAGUAIABJAG4AYwAuACAAMgAw\nADEANv/bAEMADQkKCwoIDQsKCw4ODQ8TIBUTEhITJxweFyAuKTEwLiktLDM6Sj4zNkY3LC1AV0FG\nTE5SU1IyPlphWlBgSlFST//bAEMBDg4OExETJhUVJk81LTVPT09PT09PT09PT09PT09PT09PT09P\nT09PT09PT09PT09PT09PT09PT09PT09PT09PT//AABEIAGQAOAMBIgACEQEDEQH/xAAWAAEBAQAA\nAAAAAAAAAAAAAAAAAQf/xAAXEAEBAQEAAAAAAAAAAAAAAAAAAREx/8QAFQEBAQAAAAAAAAAAAAAA\nAAAAAAH/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwDMFRRAwACiAACiwAAEQqKi\nqtEAU0QRQADqKBgCCKixVDgYIAIFCiqgAKAiBQqiACixFgACIFCqIAKLAAARCFBRABX/2Q==\n',
                'width': 240,
                'height': 240,
                'time': 1 if url_data or str(type(file)) == "<class 'bytes'>" else tools.get_video_duration(file),
                'size': str(len(file)) if str(type(file)) == "<class 'bytes'>" else str(len(url_data.data)) if url_data else str(Path(file).stat().st_size),
                'type': 'Video'
            },
            'object_guid': chat_id,
            'rnd': str(randint(100000,999999999)),
            'reply_to_message_id': message_id,
            'text': metadata[1]
        }
        if metadata[0] != []:
            data['metadata'] = {'meta_data_parts': metadata[0]}
        return self.method('sendMessage', data)

    def send_gif(self, chat_id, file, caption = None, message_id = None):
        req = self.upload_file(file)
        file_data = req[0]
        url_data = req[1]
        metadata = tools.check_metadata(caption)
        data = {
            'file_inline': {
                'file_id': file_data['id'],
                'mime': 'mp4',
                'dc_id': file_data['dc_id'],
                'access_hash_rec': req[2],
                'file_name': f'Pyrubi {randint(1, 100)}.mp4' if url_data or str(type(file)) == "<class 'bytes'>" else file,
                'width': 240,
                'height': 240,
                'time': 1 if url_data or str(type(file)) == "<class 'bytes'>" else tools.get_video_duration(file),
                'size': str(len(file)) if str(type(file)) == "<class 'bytes'>" else str(len(url_data.data)) if url_data else str(Path(file).stat().st_size),
                'type': 'Gif',
                'is_round': False,
            },
            'object_guid': chat_id,
            'rnd': str(randint(100000,999999999)),
            'reply_to_message_id': message_id,
            'text': metadata[1]
        }
        if metadata[0] != []:
            data['metadata'] = {'meta_data_parts': metadata[0]}
        return self.method('sendMessage',data)

    def send_voice(self, chat_id, file, caption = None, message_id = None, time = None):
        req = self.upload_file(file)
        file_data = req[0]
        url_data = req[1]
        metadata = tools.check_metadata(caption)
        data = {
            'file_inline': {
                'dc_id': file_data['dc_id'],
                'file_id': file_data['id'],
                'type': 'Voice',
                'file_name': f'Pyrubi {randint(1, 100)}.ogg' if url_data or str(type(file)) == "<class 'bytes'>" else file,
                'size': str(len(url_data.data)) if url_data else str(len(file)) if str(type(file)) == "<class 'bytes'>" else str(Path(file).stat().st_size),
                'time': 1 if url_data or str(type(file)) == "<class 'bytes'>" else int(tools.get_voice_duration(open(file,'rb').read()) if time == None else time) * 1000,
                'mime': 'ogg',
                'access_hash_rec': req[2],
            },
            'object_guid': chat_id,
            'rnd': str(randint(100000,999999999)),
            'reply_to_message_id': message_id,
            'text': metadata[1]
        }
        if metadata[0] != []:
            data['metadata'] = {'meta_data_parts': metadata[0]}
        return self.method('sendMessage', data)

    def send_music(self, chat_id, file, caption = None, message_id = None):
        req = self.upload_file(file)
        file_data = req[0]
        url_data = req[1]
        metadata = tools.check_metadata(caption)
        data = {
            'file_inline': {
                'file_id': file_data['id'],
                'mime': 'mp3',
                'dc_id': file_data['dc_id'],
                'access_hash_rec': req[2],
                'file_name': f'Pyrubi {randint(1, 100)}.mp3' if url_data or str(type(file)) == "<class 'bytes'>" else file,
                'width': 0,
                'height': 0,
                'time': 1 if url_data or str(type(file)) == "<class 'bytes'>" else int(tools.get_voice_duration(open(file,'rb').read()) if time == None else time),
                'size': str(len(file)) if str(type(file)) == "<class 'bytes'>" else str(len(url_data.data)) if url_data else str(Path(file).stat().st_size),
                'type': 'Music',
                'music_performer': tools.get_music_artist(url_data.data if url_data else file),
                'is_round': False
            },
            'is_mute': False,
            'object_guid': chat_id,
            'text': metadata[1],
            'rnd': str(randint(100000,999999999)),
            'reply_to_message_id': message_id
        }
        if metadata[0] != []:
            data['metadata'] = {'meta_data_parts': metadata[0]}
        return self.method('sendMessage', data)

    def send_file(self, chat_id, file, caption = None, message_id = None, file_name=None, mime=None):
        req = self.upload_file(file)
        file_data = req[0]
        url_data = req[1]
        metadata = tools.check_metadata(caption)
        data = {
            'file_inline': {
                'dc_id': file_data['dc_id'],
                'file_id': file_data['id'],
                'type': 'File',
                'file_name': file_name or f'Unknown {randint(1, 100)}.{mime or tools.get_mime_from_url(file)}' if url_data else file_name or file,
                'size': str(len(url_data.data)) if url_data else str(Path(file).stat().st_size),
                'mime': mime or tools.get_mime_from_url(file) if url_data else file.split('.')[-1] or file,
                'access_hash_rec': req[2]
            },
            'object_guid': chat_id,
            'rnd': str(randint(100000,999999999)),
            'reply_to_message_id': message_id,
            'text': metadata[1]
        }
        if metadata[0] != []:
            data['metadata'] = {'meta_data_parts': metadata[0]}
        return self.method('sendMessage', data)

    def send_sticker(self, chat_id, message_id = None):
        stickers = choice(self.method('getMyStickerSets', {})['sticker_sets'])
        return self.method(
            'sendMessage',
            {
                'sticker': choice(stickers['top_stickers']),
                'object_guid': chat_id,
                'rnd': str(randint(100000,999999999)),
                'reply_to_message_id': message_id
            }
        )

    def send_poll(self, chat_id, text_question = None, options = [], message_id = None, multiple_answers = False, anonymous = True,  quiz = False):
        return self.method(
            'createPoll',
            {
                'allows_multiple_answers': multiple_answers,
                'correct_option_index': None,
                'is_anonymous': anonymous,
                'object_guid': chat_id,
                'options': options if len(options) == 2 else ['This poll was created with "Pyrubi Library"', 'حداقل باید دو گزینه برای نظر سنجی بگزارید !'],
                'question': text_question if text_question != None else 'هیچ متنی تنظیم نشده است !',
                'reply_to_message_id': message_id,
                'rnd': randint(100000000, 999999999),
                'type': 'Quiz' if quiz else 'Regular'
            }
        )

    def vote_poll(self, poll_id, selection_index : str):
        return self.method(
            'votePoll',
            {
                'poll_id': poll_id,
                'selection_index': selection_index
            }
        )

    def get_poll_status(self, poll_id):
        return self.method('getPollStatus', {'poll_id': poll_id})

    def get_poll_option_voters(self, poll_id, selection_index : str, start_id = None):
        return self.method(
            'getPollOptionVoters',
            {
                'poll_id': poll_id,
                'selection_index': selection_index,
                'start_id': start_id
            }
        )

    def send_message_api_call(self, chat_id, text, message_id, button_id):
        return self.method(
            'sendMessageAPICall',
            {
                'text': text,
                'object_guid': chat_id,
                'message_id': message_id,
                'aux_data': {'button_id': button_id}
            }
        )

    def send_chat_activity(self, chat_id, action):
        return self.method(
            'sendChatActivity',
            {
                'object_guid': chat_id,
                'activity': action
            }
        )

    def edit_message(self, chat_id, new_text, message_id):
        metadata = tools.check_metadata(new_text)
        data = {
            'object_guid': chat_id,
            'text': metadata[1].strip(),
            'message_id': message_id,
        }
        if metadata[0] != []:
            data['metadata'] = {'meta_data_parts': metadata[0]}
        return self.method('editMessage', data)['message_update']

    def forward_message(self, from_chat_id, message_ids, to_chat_id):
        return self.method(
            'forwardMessages',
            {
                'from_object_guid': from_chat_id,
                'message_ids': message_ids,
                'rnd': str(randint(100000,999999999)),
                'to_object_guid': to_chat_id
            }
        )

    def resend_message(self, chat_id, file_inline, caption = None, message_id = None):
        metadata = tools.check_metadata(caption)
        data = {
            'file_inline': file_inline,
            'object_guid': chat_id,
            'rnd': str(randint(100000,999999999)),
            'reply_to_message_id': message_id,
            'text': metadata[1]
        }
        if metadata[0] != []:
            data['metadata'] = {'meta_data_parts': metadata[0]}
        return self.method(
            'sendMessage',
            data
        )

    def pin_message(self, chat_id, message_id):
        return self.method(
            'setPinMessage',
            {
                'object_guid': chat_id,
                'message_id': message_id,
                'action': 'Pin'
            }
        )

    def unpin_message(self, chat_id, message_id):
        return self.method(
            'setPinMessage',
            {
                'object_guid': chat_id,
                'message_id': message_id,
                'action': 'Unpin'
            }
        )

    def search_message(self, chat_id, text):
        return self.method(
            'searchChatMessages',
            {
                'object_guid': chat_id,
                'search_text': text,
                'type':'Text'
            }
        )['message_ids']

    def seen_message(self, chat_id, message_id):
        return self.method('seenChats', {'seen_list': {chat_id: int(message_id)}})

    def delete_message(self, chat_id, message_ids = [], type = 'Global'):
        return self.method(
            'deleteMessages',
            {
                'object_guid': chat_id,
                'message_ids': message_ids,
                'type': type
            }
        )['message_updates']

    def get_chat_messages(self, chat_id, middle_message_id):
        return self.method(
            'getMessagesInterval',
            {
                'object_guid':chat_id,
                'middle_message_id': middle_message_id
            }
        )['messages']
    
    def get_chat_last_messages(self, chat_id, min_id):
        return self.method(
            'getMessages',
            {
                "object_guid": chat_id,
                "sort":"FromMin",
                "min_id": min_id
            }
        )['messages']

    def get_messages_info(self, chat_id, messages_ids = []):
        return self.method(
            'getMessagesByID',
            {
                'object_guid': chat_id,
                'message_ids': messages_ids
            }
        )['messages']

    def get_link_info(self, url):
        return self.method('getLinkFromAppUrl', {'app_url': url})['link']['open_chat_data']

    def get_chats(self, start_id = None):
        return self.method('getChats', {'start_id': start_id})

    def search_chats(self, text):
        return self.method('searchGlobalObjects',{'search_text': text})['objects']

    def report_chat(self, chat_id, report_description, message_id = None):
        chat_type = tools.get_chat_type_by_id(chat_id)
        return self.method(
            'reportObject',
            {
                'object_guid': chat_id,
                'report_description': report_description, 
                'report_type_object': chat_type, 
                'report_type': 100,
                'meesage_id': message_id
            }
        )

    def get_chat_info(self, chat_id):
        data = tools.get_chat_type_by_id(chat_id)
        return self.method(f'get{data}Info',{f'{data.lower()}_guid': chat_id})
        
    def get_chat_preview_by_link(self, chat_link):
        return self.method(
            'groupPreviewByJoinLink' if 'joing' in chat_link else 'channelPreviewByJoinLink',
            {'hash_link': chat_link.split('/')[-1]}
        )

    def get_abs_chats(self, chat_ids = []):
        return self.method('getAbsObjects', {'objects': chat_ids})

    def get_chat_info_by_username(self, username):
        return self.method('getObjectByUsername', {'username': username.replace('@', '')})

    def get_chat_last_message(self, chat_id):
        return self.get_chat_info(chat_id)['chat'].get('last_message', None)

    def get_chat_last_message_id(self, chat_id):
        return self.get_chat_info(chat_id)['chat']['last_message_id']

    def delete_chat_history(self, chat_id):
        return self.method(
            'deleteChatHistory',
            {
                'object_guid': chat_id,
                'last_message_id': self.get_chat_last_message_id(chat_id)
            }
        )['chat_update']

    def delete_user_chat(self, user_id, last_deleted_message_id):
        return self.method(
            'deleteUserChat',
            {
                'user_guid': user_id,
                'last_deleted_message_id': last_deleted_message_id
            }
        )

    def add_chat_members(self, chat_id, member_ids = []):
        return self.method(
            f'add{tools.get_chat_type_by_id(chat_id)}Members',
            {
                f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id,
                'member_guids': member_ids
            }
        )

    def ban_chat_member(self, chat_id, member_id):
        return self.method(
            f'ban{tools.get_chat_type_by_id(chat_id)}Member',
            {
                f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id,
                'member_guid': member_id,
                'action': 'Set'
            }
        )

    def get_banned_members(self, chat_id, start_id = None):
        return self.method(
            f'getBanned{tools.get_chat_type_by_id(chat_id)}Members',
            {
                f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id,
                'start_id': start_id
            }
        )['in_chat_members']

    def set_group_access(self, group_id, view_members = False, view_admins = False ,send_message = False, add_member = False):
        access = []
        if view_members:
            access.append('ViewMembers')
        if view_admins:
            access.append('ViewAdmins')
        if send_message:
            access.append('SendMessages')
        if add_member:
            access.append('AddMember')
        return self.method(
            'setGroupDefaultAccess',
            {
                'access_list': access,
                'group_guid': group_id
            }
        )

    def get_chat_members(self, chat_id, only_ids = True, search = None):
        data = self.method(
            f'get{tools.get_chat_type_by_id(chat_id)}AllMembers',
            {
                f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id,
                'search_text': search
            }
        )['in_chat_members']
        return [i['member_guid'] for i in data] if only_ids else data
    
    def check_user_membership(self, chat_id, member_id):
        username = self.get_chat_info(member_id)['user']['username']
        return member_id in self.get_chat_members(chat_id, search=username)

    def get_chat_admins(self, chat_id, only_ids = True):
        data = self.method(f'get{tools.get_chat_type_by_id(chat_id)}AdminMembers', {f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id})['in_chat_members']
        return [i['member_guid'] for i in data] if only_ids else data

    def set_group_timer(self, group_id, time):
        return self.method(
            'editGroupInfo',
            {
                'group_guid': group_id,
                'slow_mode': int(time),
                'updated_parameters': ['slow_mode']
            }
        )['group']

    def set_chat_admin(self, chat_id, user_id, access = []):
        return self.method(
            f'set{tools.get_chat_type_by_id(chat_id)}Admin',
            {
                f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id,
                'member_guid': user_id,
                'access_list': access,
                'action': 'SetAdmin',
            }
        )['in_chat_member']
    
    def delete_chat_admin(self, chat_id, user_id):
        return self.method(
            f'set{tools.get_chat_type_by_id(chat_id)}Admin',
            {
                f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id,
                'member_guid': user_id,
                'action': 'UnsetAdmin',
            }
        )['in_chat_member']

    def edit_group_info(self, chat_id, title = None, bio = None, show_chat_history = None):
        data = self.get_chat_info(chat_id)['group']
        return self.method(
            'editGroupInfo',
            {
                'group_guid': chat_id,
                'title': title or data.get('group_title', None),
                'description': bio or data.get('description', None),
                'chat_history_for_new_members': 'Visible' if show_chat_history else 'Hidden'if show_chat_history != None else data['chat_history_for_new_members'],
                'updated_parameters': ['title', 'description', 'chat_history_for_new_members']
            }
        )

    def create_group(self, group_name, member_ids = []):
        return self.method(
            'addGroup',
            {
                'title': group_name,
                'member_guids': member_ids
            }
        )
    
    def join_group(self, group_link):
        return self.method('joinGroup', {'hash_link': group_link.split('/')[-1]})

    def leave_group(self, group_guid):
        return self.method('leaveGroup', {'group_guid': group_guid})

    def get_chat_link(self, chat_id):
        return self.method(f'get{tools.get_chat_type_by_id(chat_id)}Link', {f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id})['join_link']

    def set_chat_link(self, chat_id):
        return self.method(f'set{tools.get_chat_type_by_id(chat_id)}Link', {f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id})['join_link']

    def create_channel(self, channel_name, member_ids = [], channel_type = 'Public'):
        return self.method(
            'addChannel',
            {
                'channel_type': channel_type,
                'title': channel_name,
                'member_guids': member_ids
            }
        )

    def join_channel(self, channel_id):
        return self.method(
            'joinChannelAction',
            {
                'action': 'Join',
                'channel_guid': channel_id
            }
        )

    def join_channel_by_link(self, channel_link):
        return self.method('joinChannelByLink', {'hash_link': channel_link.split('/')[-1]})

    def leave_channel(self, channel_id):
        return self.method(
            'joinChannelAction',
            {
                'action': 'Leave',
                'channel_guid': channel_id
            }
        )

    def get_avatars(self, chat_id):
        return self.method('getAvatars', {'object_guid': chat_id})

    def upload_avatar(self, chat_id, file, thumbnai = None):
        main_id = self.upload_file(file)[0]['id']
        return self.method(
            'uploadAvatar',
            {
                'object_guid': chat_id,
                'thumbnail_file_id': self.upload_file(thumbnai)[0]['id'] if thumbnai != None else main_id,
                'main_file_id': main_id
            }
        )

    def delete_avatar(self, chat_id, avatar_id):
        return self.method(
            'deleteAvatar',
            {
                'object_guid': chat_id,
                'avatar_id': avatar_id
            }
        )

    def creat_voice_chat(self, chat_id):
        return self.method(
            f'create{tools.get_chat_type_by_id(chat_id)}VoiceChat',
            {f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id}
        )

    def join_voice_chat(self, chat_id, voice_chat_id, self_id, sdp_offer_data = None):
        return self.method(
            f'join{tools.get_chat_type_by_id(chat_id)}VoiceChat',
            {
                'chat_guid': chat_id,
                'voice_chat_id': voice_chat_id,
                'self_object_guid': self_id,
                'sdp_offer_data': sdp_offer_data or '''v=0\r\no=- 7025254686977085379 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0\r\na=extmap-allow-mixed\r\na=msid-semantic: WMS LjIerKYwibTOvR0Ewwk1PBsYYxTInaoXObBE\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111 63 103 104 9 0 8 106 105 13 110 112 113 126\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:6Hy7\r\na=ice-pwd:pyrxfUF+roBFRHDy6qgiKSAp\r\na=ice-options:trickle\r\na=fingerprint:sha-256 8C:90:E9:0C:E7:A4:79:7E:BF:78:81:ED:A7:19:82:64:71:F7:21:AB:43:4F:4B:3A:4C:EB:B5:3C:6A:01:CB:13\r\na=setup:actpass\r\na=mid:0\r\na=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level\r\na=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time\r\na=extmap:3 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01\r\na=extmap:4 urn:ietf:params:rtp-hdrext:sdes:mid\r\na=sendrecv\r\na=msid:LjIerKYwibTOvR0Ewwk1PBsYYxTInaoXObBE 00f6113c-f01a-447a-a72e-c989684b627a\r\na=rtcp-mux\r\na=rtpmap:111 opus/48000/2\r\na=rtcp-fb:111 transport-cc\r\na=fmtp:111 minptime=10;useinbandfec=1\r\na=rtpmap:63 red/48000/2\r\na=fmtp:63 111/111\r\na=rtpmap:103 ISAC/16000\r\na=rtpmap:104 ISAC/32000\r\na=rtpmap:9 G722/8000\r\na=rtpmap:0 PCMU/8000\r\na=rtpmap:8 PCMA/8000\r\na=rtpmap:106 CN/32000\r\na=rtpmap:105 CN/16000\r\na=rtpmap:13 CN/8000\r\na=rtpmap:110 telephone-event/48000\r\na=rtpmap:112 telephone-event/32000\r\na=rtpmap:113 telephone-event/16000\r\na=rtpmap:126 telephone-event/8000\r\na=ssrc:1614457217 cname:lYBnCNdQcW/DEUj9\r\na=ssrc:1614457217 msid:LjIerKYwibTOvR0Ewwk1PBsYYxTInaoXObBE 00f6113c-f01a-447a-a72e-c989684b627a\r\n''',
            }
        )

    def edit_voice_chat_setting(self, chat_id, voice_chat_id, custom_name):
        return self.method(
            f'set{tools.get_chat_type_by_id(chat_id)}VoiceChatSetting',
            {
                f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id,
                'voice_chat_id': voice_chat_id,
                'title': custom_name ,
                'updated_parameters': ['title']
            }
        )

    def discard_voice_chat(self, chat_id, voice_chat_id):
        return self.method(
            f'discard{tools.get_chat_type_by_id(chat_id)}VoiceChat',
            {
                f'{tools.get_chat_type_by_id(chat_id).lower()}_guid': chat_id,
                'voice_chat_id': voice_chat_id
            }
        )

    def set_pin_chat(self, chat_id):
        return self.method(
            'setActionChat',
            {
                'object_guid': chat_id,
                'action': 'Pin'
            }
        )

    def set_unpin_chat(self, chat_id):
        return self.method(
            'setActionChat',
            {
                'object_guid': chat_id,
                'action': 'Unpin'
            }
        )

    def set_mute_chat(self, chat_id):
        return self.method(
            'setActionChat',
            {
                'object_guid': chat_id,
                'action': 'Mute'
            }
        )

    def set_unmute_chat(self, chat_id):
        return self.method(
            'setActionChat',
            {
                'object_guid': chat_id,
                'action': 'Unmute'
            }
        )

    def block_user(self, user_id):
        return self.method(
            'setBlockUser',
            {
                'user_guid': user_id,
                'action': 'Block'
            }
        )['chat_update']

    def unblock_user(self, user_id):
        return self.method(
            'setBlockUser',
            {
                'user_guid': user_id,
                'action': 'Unblock'
            }
        )['chat_update']

    def get_block_users(self):
        return self.method('getBlockUsers', {})

    def get_contacts(self):
        return self.method('getContacts', {})

    def get_contacts_updates(self, state):
        return self.method('getContactsUpdates', {'state': state})

    def get_contacts_last_online(self, chat_ids : list = None):
        return self.method('getContactsLastOnline', {'user_guds': chat_ids})

    def add_contact(self, phone_number, first_name, last_name):
        return self.method(
            'addAddressBook',
            {
                'phone': f'98{tools.parse_phone_number(phone_number)}',
                'first_name': first_name,
                'last_name': last_name
            }
        )

    def get_folders(self):
        return self.method('getFolders', {})

    def get_suggested_folders(self):
        return self.method('getSuggestedFolders', {})

    def add_chat_folder(self, folder_name, exclude_chat_ids = [], exclude_chat_types = [], include_chat_ids = [], include_chat_types = [], add_to_top = True, folder_id = ''):
        data = dict(
            exclude_object_guids = exclude_chat_ids,
            include_object_guids = include_chat_ids,
            exclude_chat_types = exclude_chat_types,
            include_chat_types = include_chat_types,
            folder_id = folder_id, is_add_to_top = add_to_top,
            name = folder_name,
        )
        return self.make('addFolder', data)

    def get_privacy_setting(self):
        return self.method('getPrivacySetting', {})['privacy_setting']

    def get_my_sessions(self):
        return self.method('getMySessions', {})

    def get_two_passcode_status(self):
        return self.method('getTwoPasscodeStatus', {})['two_step_status']

    def check_two_step_passcode(self, password):
        if len(password) < 5:
            raise IndexError('Password vared shodeh bayad hadaghal 5 character bashad !')
        return self.method('checkTwoStepPasscode', {'password': password})['is_valid']

    def change_password(self, current_password, new_password, hint):
        return self.method(
            'changePassword',
            {
                'password': current_password,
                'new_password': new_password,
                'new_hint': hint
            }
        )

    def enable_two_step_verification(self, password, hint):
        return self.method(
            'setupTwoStepVerification',
            {
                'password': password,
                'hint': hint
            }
        )

    def disable_two_step_verification(self, current_password):
        return self.method('turnOffTwoStep', {'password': current_password})

    def request_recovery_email(self, current_password, email):
        return self.method(
            'requestRecoveryEmail',
            {
                'password': current_password,
                'recovery_email': email
            }
        )

    def verify_recovery_email(self, current_password, verification_code):
        return self.method(
            'verifyRecoveryEmail',
            {
                'password': current_password,
                'code': verification_code
            }            
        )
    
    def get_sticker_sets(self):
        return self.method('getMyStickerSets', {})

    def get_me(self):
        session().close()
        return session().post(
            'https://messengerg2c1.iranlms.ir',
            json={
                "data":{},
                "method":"getUser",
                "api_version":"2",
                "auth": self.auth,
                "Messenger":{
                    "app_name":"Main",
                    "package":"m.rubika.ir",
                    "app_version":"1.2.1",
                    "platform":"PWA"
                }
            },
            headers = {
                'referer': 'https://web.rubika.ir/',
            }
        ).json()
    
    def get_base_info(self):
        return session().post(
            'https://servicesbase.iranlms.ir/',
            json={
                'method':'getBaseInfo',
                'api_version':'0',
                'data':{},
                'auth': self.auth,
                'client':{
                    'app_name':'Main',
                    'app_version':'4.2.0',
                    'platform':'PWA',
                    'package':'web.rubika.ir'
                }
            }
        ).json()
    
    def get_tag_list(self):
        return session().post(
            'https://services3.iranlms.ir/',
            json={
                'method':'getTagList',
                'api_version':'0',
                'data':{'taglist_id': 'new_vod'},
                'auth': self.auth,
                'client':{
                    'app_name':'Main',
                    'app_version':'4.2.0',
                    'platform':'PWA',
                    'package':'web.rubika.ir'
                }
            }
        ).json()

    def edit_profile(self, **kwargs):
        """
        parameters : first_name, last_name, bio, username
        """
        if 'username' in list(kwargs.keys()):
            return self.method(
                'updateUsername',
                {
                    'username': kwargs.get('username'),
                    'updated_parameters': ['username']
                }
            )['user']
        else:
            return self.method(
                'updateProfile',
                {
                    'first_name': kwargs.get('first_name'),
                    'last_name': kwargs.get('last_name'),
                    'bio': kwargs.get('bio'),
                    'updated_parameters': list(kwargs.keys())
                }
            )['user']

    def set_setting(self, show_my_last_online = False, show_my_phone_number = False, show_my_profile_photo = False, link_forward_message = False, can_join_chat = False):
        return self.method(
            'setSetting',
            {
                'settings': {
                    'show_my_last_online': 'Everybody' if show_my_last_online else 'Nobody',
                    'show_my_phone_number': 'Everybody' if show_my_phone_number else 'Nobody',
                    'show_my_profile_photo': 'Everybody' if show_my_profile_photo else 'Nobody',
                    'link_forward_message': 'Everybody' if link_forward_message else 'Nobody',
                    'can_join_chat_by': 'Everybody' if can_join_chat else 'Nobody'
                },
                'update_parameters': [
                    'Everybody' if show_my_last_online else 'Nobody',
                    'Everybody' if show_my_phone_number else 'Nobody',
                    'Everybody' if show_my_profile_photo else 'Nobody',
                    'Everybody' if link_forward_message else 'Nobody',
                    'Everybody' if can_join_chat else 'Nobody'
                ]
            }
        )

    def send_code(self, phone_number, pass_key=None, send_internal=False):
        return self.method(
            'sendCode',
            {
                'phone_number': f'98{tools.parse_phone_number(phone_number)}',
                'send_type': 'Internal' if send_internal else 'SMS',
                'pass_key': pass_key
            }
        )

    def sing_in(self, phone_number, phone_code_hash, phone_code):
        return self.method(
            'signIn',
            {
                'phone_number': f'98{tools.parse_phone_number(phone_number)}',
                'phone_code_hash': phone_code_hash,
                'phone_code': phone_code
            }
        )

    def logout(self):
        return self.method('logout', {})
    
    def get_chat_ads(self):
        return self.method('getChatAds', {'state': str(round(time()) - 100)})

    def request_file(self, file):
        for link in ['http:/', 'https:/']:
            if link in str(file):
                url_data = self.http.request('GET', file)
                break
            else:
                url_data = None
        return self.method(
            'requestSendFile',
            {
                'file_name': f'pyrubi library {randint(1, 100)}',
                'mime': tools.get_mime_from_url(file) if url_data else 'pyrubi' if str(type(file)) == "<class 'bytes'>" else file.split('.')[-1],
                'size': len(url_data.data) if url_data else str(len(file)) if str(type(file)) == "<class 'bytes'>" else Path(file).stat().st_size
            }
        ), url_data

    def upload_file(self, file):
        req = self.request_file(file)
        file_data = req[0]
        url_data = req[1]
        upload = maker(self.auth, self)._upload
        bytef = url_data.data if url_data else file if str(type(file)) == "<class 'bytes'>" else open(file,'rb').read()
        size = str(len(url_data.data)) if url_data else str(len(file)) if str(type(file)) == "<class 'bytes'>" else str(Path(file).stat().st_size)
        url = file_data['upload_url']
        header = {
            'auth': self.auth,
            'Host': file_data['upload_url'].replace('https://','').replace('/UploadFile.ashx',''),
            'chunk-size': size,
            'data-length': size,
            'file-id': str(file_data['id']),
            'access-hash-send': file_data['access_hash_send'],
            'data-type': 'application/octet-stream',
        }
        while True:
            if len(bytef) <= 131072:
                header['part-number'], header['total-part'] = '1', '1'
                j = upload(url=url, data=bytef, headers=header)
                return file_data, url_data, j['data']['access_hash_rec']
            else:
                t = len(bytef) // 131072 + 1
                for i in range(1, t+1):
                    if i != t:
                        k = (i - 1) * 131072
                        header['chunk-size'], header['part-number'], header['total-part'] = '131072', str(i),str(t)
                        upload(url=url, data=bytef[k:k + 131072], headers=header)
                        print('\r' + f'{round(k / 1024) / 1000} MB /', sep='', end=f' {round(len(bytef) / 1024) / 1000} MB')  
                    else:
                        k = (i - 1) * 131072
                        header['chunk-size'], header['part-number'], header['total-part'] = str(len(bytef[k:])), str(i),str(t)
                        p = upload(url=url, data=bytef[k:], headers=header)
                        print('\r' + f'{round(len(bytef) / 1024) / 1000} MB /', sep='', end=f' {round(len(bytef) / 1024) / 1000} MB')
                return file_data, url_data, p['data']['access_hash_rec']
            
    def download_file(self, chat_id=None, message_id=None, save=False, file_inline=None):
        message_data = file_inline if file_inline else self.get_messages_info(chat_id, [message_id])[0].get('file_inline', None)
        if not message_data:
            raise FileExistsError(f'This ({message_id}) message is not a File !')
        file_name = message_data.get('file_name', f'pyrubi {time()}.{message_data.get("mime", "pyrubi")}')
        header = {
            'auth': self.auth,
            'file-id': str(message_data['file_id']),
            'access-hash-rec': message_data['access_hash_rec'],
            'client-app-version': '3.1.1',
            'client-platform': 'Android',
            'client-app-name': 'Main',
            'client-package': 'app.rbmain.a'
        }
        download = maker(self.auth)._download
        response = download(f'https://messenger{message_data["dc_id"]}.iranlms.ir/GetFile.ashx', header)
        chunk = b''
        for i in response.stream(524284):
            chunk += i
            print('\r' + f'{round(len(chunk) / 1024) / 1000} MB /', sep='', end=f' {message_data["size"] / 1000000} MB' if 'size' in message_data else None)
        if save:
            with open(file_name, 'wb+') as file:
                file.write(chunk)
                file.close()
                return {'file_name': file_name, 'size': message_data.get('size', None), 'file_inline': message_data}
        return chunk