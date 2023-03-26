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
                pass

    def author_id(self):
        try:
            return self.data['message_updates'][0]['message']['author_object_guid']
        except KeyError:
            try:
                return self.data['last_message']['author_object_guid']
            except:
                pass

    def message_id(self):
        try:
            return self.data['message_updates'][0]['message_id']
        except KeyError:
            try:
                return self.data['last_message']['message_id']
            except:
                pass

    def reply_to_message_id(self):
        try:
            return self.data['message_updates'][0]['message'].get('reply_to_message_id', 'None')
        except KeyError:
            pass

    def text(self):
        try:
            return self.data['message_updates'][0]['message'].get('text', 'None')
        except KeyError:
            try:
                return self.data['last_message'].get('text', 'None')
            except:
                pass

    def chat_type(self):
        try:
            return self.data['message_updates'][0]['type']
        except KeyError:
            try:
                return self.data['abs_object']['type']
            except:
                pass

    def author_type(self):
        try:
            return self.data['message_updates'][0]['message']['author_type']
        except KeyError:
            try:
                return self.data['last_message']['author_type']
            except:
                pass

    def message_type(self):
        try:
            return self.data['message_updates'][0]['message']['type']
        except KeyError:
            return self.data['last_message']['type']
        except:
            pass

    def is_forward(self):
        try:
            return 'forwarded_from' in self.data['message_updates'][0]['message']
        except KeyError:
            pass
    
    def is_event(self):
        try:
            return 'event_data' in self.data['message_updates'][0]['message']
        except KeyError:
            return self.message_type() == 'Other'
        except:
            pass

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
                return self.data['abs_object']['title']
            except:
                pass

    def author_title(self):
        try:
            return self.data["show_notifications"][0].get("text", "None:Text").split(":")[0] if self.is_group_chat() else self.chat_title()
        except KeyError:
            try:
                return self.data['last_message'].get('author_title', 'None')
            except:
                pass

    def event_type(self):
        try:
            return self.data['message_updates'][0]['message']['event_data']['type']
        except KeyError:
                pass

    def event_id(self):
        try:
            return self.data["message_updates"][0]["message"]["event_data"]["performer_object"]["object_guid"]
        except KeyError:
                pass