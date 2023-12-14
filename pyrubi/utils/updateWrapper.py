class UpdateWrapper:
    def __init__(self, update:dict, methods:object) -> None:
        self.update = update
        self.client = methods

    @property
    def object_guid(self) -> str:
        return self.update["chat_updates"][0].get("object_guid")
    
    @property
    def action(self) -> str:
        return self.update["chat_updates"][0].get("action")
    
    @property
    def chat_type(self) -> str:
        return self.update["chat_updates"][0].get("type")
    
    @property
    def count_unseen(self) -> int:
        return int(self.update["chat_updates"][0]["chat"].get("count_unseen", 0))
    
    @property
    def last_seen_peer_mid(self) -> str:
        return self.update["chat_updates"][0]["chat"].get("last_seen_peer_mid")
    
    @property
    def time_string(self) -> str:
        return self.update["chat_updates"][0]["chat"].get("time_string")
    
    @property
    def is_mine(self) -> bool:
        return self.update["chat_updates"][0]["chat"]["last_message"].get("is_mine")
    
    @property
    def time(self) -> str:
        return self.update["chat_updates"][0].get("object_guid")
    
    @property
    def status(self) -> str:
        return self.update["chat_updates"][0]["chat"].get("status")
    
    @property
    def last_message_id(self) -> str:
        return self.update["chat_updates"][0]["chat"].get("last_message_id")
    
    @property
    def message_id(self) -> str:
        return self.update["message_updates"][0].get("message_id")
    
    @property
    def reply_message_id(self) -> str:
        return self.update["message_updates"][0]["message"].get("reply_to_message_id")
    
    @property
    def text(self) -> str:
        return str(self.update["message_updates"][0]["message"].get("text"))
    
    @property
    def is_edited(self) -> bool:
        return self.update["message_updates"][0]["message"].get("is_edited")
    
    @property
    def message_type(self) -> str:
        if self.file_inline:
            return self.file_inline["type"]
        
        return self.update["message_updates"][0]["message"].get("type")
    
    @property
    def author_type(self) -> str:
        return self.update["message_updates"][0]["message"].get("author_type")
    
    @property
    def author_guid(self) -> str:
        return self.update["message_updates"][0]["message"].get("author_object_guid")
    
    @property
    def prev_message_id(self) -> str:
        return self.update["message_updates"][0].get("prev_message_id")
    
    @property
    def state(self) -> str:
        return self.update["message_updates"][0].get("state")
    
    @property
    def title(self) -> str:
        if self.update['show_notifications']:
            return self.update['show_notifications'][0].get('title')
    
    @property
    def author_title(self) -> str:
        return self.update['chat_updates'][0]['chat']['last_message'].get('author_title', self.title)
    
    @property
    def is_user(self) -> bool:
        return self.chat_type == "User"
    
    @property
    def is_group(self) -> bool:
        return self.chat_type == "Group"
    
    @property
    def is_forward(self) -> bool:
        return "forwarded_from" in self.update["message_updates"][0]["message"].keys()
    
    @property
    def forward_from(self) -> str:
        return self.update["message_updates"][0]["message"]["forwarded_from"].get("type_from") if self.is_forward else None
    
    @property
    def forward_object_guid(self) -> str:
        return self.update["message_updates"][0]["message"]["forwarded_from"].get("object_guid") if self.is_forward else None
    
    @property
    def forward_message_id(self) -> str:
        return self.update["message_updates"][0]["message"]["forwarded_from"].get("message_id") if self.is_forward else None

    @property
    def is_event(self) -> bool:
        return 'event_data' in self.update['message_updates'][0]['message'].keys()
    
    @property
    def event_type(self) -> str:
        return self.update['message_updates'][0]['message']['event_data'].get('type') if self.is_event else None
    
    @property
    def event_object_guid(self) -> str:
        return self.update['message_updates'][0]['message']['event_data']['performer_object'].get('object_guid') if self.is_event else None
    
    @property
    def pinned_message_id(self) -> str:
        return self.update['message_updates'][0]['message']['event_data'].get('pinned_message_id') if self.is_event else None
    
    @property
    def file_inline(self) -> dict:
        return self.update["message_updates"][0]["message"].get("file_inline")

    @property
    def has_link(self) -> bool:
        for link in ["http:/", "https:/", "www.", ".ir", ".com"]:
            if link in self.text.lower():
                return True
        return False
    
    def reply(self, text:str) -> dict:
        return self.client.send_text(object_guid=self.object_guid, text=text, message_id=self.message_id)
    
    def seen(self) -> dict:
        return self.client.seen_chats(seen_list={self.object_guid: self.message_id})
    
    def reaction(self, reaction:int) -> dict:
        return self.client.reaction_message(object_guid=self.object_guid, message_id=self.message_id, reaction=reaction)
    
    def delete(self, deleteForAll:bool=True) -> dict:
        return self.client.delete_messages(object_guid=self.object_guid, message_ids=[self.message_id], delete_for_all=deleteForAll)
    
    def pin(self) -> dict:
        return self.client.pin_message(object_guid=self.object_guid, message_id=self.message_id)
    
    def forward(self, to_object_guid:str) -> dict:
        return self.client.forward_messages(object_guid=self.object_guid, message_ids=[self.message_id], toObject_guid=to_object_guid)
    
    def ban(self) -> dict:
        return self.client.ban_member(object_guid=self.object_guid, member_guid=self.author_guid)
    
    def check_join(self, object_guid:str) -> bool:
        return self.client.check_join(object_guid=object_guid, user_guid=self.author_guid)
    
    def download(self, save:bool=False) -> dict:
        return self.client.download(save=save, file_inline=self.file_inline)