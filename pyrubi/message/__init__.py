class message:

    def __init__(self, data):
        self.data = data

    def chat_id(self):
        try:
            return self.data['message_updates'][0]['object_guid']
        except KeyError:
            try:
                return self.data['object_guid']
            except:
                return 'None'

    def author_id(self):
        try:
            return self.data['message_updates'][0]['message']['author_object_guid']
        except KeyError:
            try:
                return self.data['last_message']['author_object_guid']
            except:
                return 'None'

    def message_id(self):
        try:
            return self.data['message_updates'][0]['message_id']
        except KeyError:
            try:
                return self.data['last_message']['message_id']
            except:
                return 'None'

    def reply_to_message_id(self):
        try:
            return self.data['message_updates'][0]['message'].get('reply_to_message_id', 'None')
        except KeyError:
            return 'None'

    def text(self):
        try:
            return self.data['message_updates'][0]['message'].get('text', 'None')
        except KeyError:
            try:
                return self.data['last_message'].get('text', 'None')
            except:
                return 'None'

    def chat_type(self):
        try:
            return self.data['message_updates'][0]['type']
        except KeyError:
            try:
                return self.data['abs_object']['type']
            except:
                return 'None'

    def author_type(self):
        try:
            return self.data['message_updates'][0]['message']['author_type']
        except KeyError:
            try:
                return self.data['last_message']['author_type']
            except:
                return 'None'

    def message_type(self):
        try:
            res = self.data['message_updates'][0]['message']['type']
            return res
        except KeyError:
            return self.data['last_message']['type']
        except:
            return 'None'

    def is_forward(self):
        try:
            return 'forwarded_from' in self.data['message_updates'][0]['message'].keys()
        except KeyError:
            return 'None'
        
    def forward_type(self):
        try:
            return self.data['message_updates'][0]['message']['forwarded_from'].get('type_from', 'None')
        except KeyError:
            return 'None'
        
    def forward_id(self):
        try:
            return self.data['message_updates'][0]['message']['forwarded_from'].get('object_guid', 'None')
        except KeyError:
            return 'None'
        
    def forward_message_id(self):
        try:
            return self.data['message_updates'][0]['message']['forwarded_from'].get('message_id', 'None')
        except KeyError:
            return 'None'
        
    def is_event(self):
        try:
            return 'event_data' in self.data['message_updates'][0]['message']
        except KeyError:
            return self.message_type() == 'Other'
        except:
            return 'None'

    def is_user_chat(self):
        return self.chat_type() == "User"

    def is_group_chat(self):
        return self.chat_type() == "Group"

    def is_channel_chat(self):
        return self.chat_type() == "Channel"

    def chat_title(self):
        try:
            return self.data["show_notifications"][0].get("title", "None")
        except KeyError:
            try:
                return self.data['abs_object'].get("title", "None")
            except:
                return 'None'

    def author_title(self):
        try:
            return self.data["chat_updates"][0]['chat']['last_message'].get('author_title', self.chat_title())
        except KeyError:
            try:
                return self.data['last_message'].get('author_title', self.chat_title())
            except:
                return 'None'

    def event_type(self):
        try:
            return self.data['message_updates'][0]['message']['event_data']['type']
        except KeyError:
            return 'None'

    def event_id(self):
        try:
            return self.data["message_updates"][0]["message"]["event_data"]["performer_object"]["object_guid"]
        except KeyError:
            return 'None'
        
    def count_unseen(self):
        try:
            return self.data['chat_updates'][0]['chat'].get('count_unseen', '0')
        except KeyError:
            return 'None'