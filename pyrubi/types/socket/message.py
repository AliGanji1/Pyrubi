class ReplyInfo:
    def __init__(self, text, author_guid) -> None:
        self.text = text
        self.author_guid = author_guid
        pass

    @classmethod
    def from_json(cls, json: dict):
        return cls(json["text"], json["author_object_guid"])

class Message:
    def __init__(self, data:dict, methods:object) -> None:
        self.data = data
        self.methods = methods

    @property
    def object_guid(self) -> str:
        return self.data["chat_updates"][0].get("object_guid")
    
    @property
    def chat_type(self) -> str:
        return self.data["chat_updates"][0].get("type")
    
    @property
    def count_unseen(self) -> int:
        return int(self.data["chat_updates"][0]["chat"].get("count_unseen", 0))
    
    @property
    def last_seen_peer_mid(self) -> str:
        return self.data["chat_updates"][0]["chat"].get("last_seen_peer_mid")
    
    @property
    def time_string(self) -> str:
        return self.data["chat_updates"][0]["chat"].get("time_string")
    
    @property
    def is_mine(self) -> bool:
        return self.data["chat_updates"][0]["chat"]["last_message"].get("is_mine")
    
    @property
    def time(self) -> str:
        return self.data["chat_updates"][0]["chat"]["last_message"].get("time")
    
    @property
    def status(self) -> str:
        return self.data["chat_updates"][0]["chat"].get("status")
    
    @property
    def last_message_id(self) -> str:
        return self.data["chat_updates"][0]["chat"].get("last_message_id")
    
    @property
    def action(self) -> str:
        return self.data["message_updates"][0].get("action")
    
    @property
    def message_id(self) -> str:
        return self.data["message_updates"][0].get("message_id")
    
    @property
    def reply_message_id(self) -> str:
        return self.data["message_updates"][0]["message"].get("reply_to_message_id")
    
    @property
    def text(self) -> str:
        return str(self.data["message_updates"][0]["message"].get("text"))
    
    @property
    def is_edited(self) -> bool:
        return self.data["message_updates"][0]["message"].get("is_edited")
    
    @property
    def message_type(self) -> str:
        if self.file_inline:
            return self.file_inline["type"]
        
        return self.data["message_updates"][0]["message"].get("type")
    
    @property
    def author_type(self) -> str:
        return self.data["message_updates"][0]["message"].get("author_type")
    
    @property
    def author_guid(self) -> str:
        return self.data["message_updates"][0]["message"].get("author_object_guid")
    
    @property
    def prev_message_id(self) -> str:
        return self.data["message_updates"][0].get("prev_message_id")
    
    @property
    def state(self) -> str:
        return self.data["message_updates"][0].get("state")
    
    @property
    def title(self) -> str:
        if self.data['show_notifications']:
            return self.data['show_notifications'][0].get('title')
    
    @property
    def author_title(self) -> str:
        return self.data['chat_updates'][0]['chat']['last_message'].get('author_title', self.title)
    
    @property
    def is_user(self) -> bool:
        return self.chat_type == "User"
    
    @property
    def is_group(self) -> bool:
        return self.chat_type == "Group"
    
    @property
    def is_forward(self) -> bool:
        return "forwarded_from" in self.data["message_updates"][0]["message"].keys()
    
    @property
    def forward_from(self) -> str:
        return self.data["message_updates"][0]["message"]["forwarded_from"].get("type_from") if self.is_forward else None
    
    @property
    def forward_object_guid(self) -> str:
        return self.data["message_updates"][0]["message"]["forwarded_from"].get("object_guid") if self.is_forward else None
    
    @property
    def forward_message_id(self) -> str:
        return self.data["message_updates"][0]["message"]["forwarded_from"].get("message_id") if self.is_forward else None

    @property
    def is_event(self) -> bool:
        return 'event_data' in self.data['message_updates'][0]['message'].keys()
    
    @property
    def event_type(self) -> str:
        return self.data['message_updates'][0]['message']['event_data'].get('type') if self.is_event else None
    
    @property
    def event_object_guid(self) -> str:
        return self.data['message_updates'][0]['message']['event_data']['performer_object'].get('object_guid') if self.is_event else None
    
    @property
    def pinned_message_id(self) -> str:
        return self.data['message_updates'][0]['message']['event_data'].get('pinned_message_id') if self.is_event else None
    
    @property
    def file_inline(self) -> dict:
        return self.data["message_updates"][0]["message"].get("file_inline")

    @property
    def has_link(self) -> bool:
        for link in ["http:/", "https:/", "www.", ".ir", ".com", ".net" "@"]:
            if link in self.text.lower():
                return True
        return False
    
    @property
    def reply_info(self) -> ReplyInfo:
        if not self.reply_message_id:
            return
        
        return ReplyInfo.from_json(self.methods.getMessagesById(self.object_guid, [self.reply_message_id])["messages"][0])
    
    def reply(self, text:str) -> dict:
        return self.methods.sendText(objectGuid=self.object_guid, text=text, messageId=self.message_id)
    
    def seen(self) -> dict:
        return self.methods.seenChats(seenList={self.object_guid: self.message_id})
    
    def reaction(self, reaction:int) -> dict:
        return self.methods.actionOnMessageReaction(objectGuid=self.object_guid, messageId=self.message_id, reactionId=reaction, action="Add")
    
    def delete(self, delete_for_all:bool=True) -> dict:
        return self.methods.deleteMessages(objectGuid=self.object_guid, messageIds=[self.message_id], deleteForAll=delete_for_all)
    
    def pin(self) -> dict:
        return self.methods.pinMessage(objectGuid=self.object_guid, messageId=self.message_id)
    
    def forward(self, to_object_guid:str) -> dict:
        return self.methods.forwardMessages(objectGuid=self.object_guid, message_ids=[self.message_id], toObjectGuid=to_object_guid)
    
    def ban(self) -> dict:
        return self.methods.banMember(objectGuid=self.object_guid, memberGuid=self.author_guid)
    
    def check_join(self, object_guid:str) -> bool:
        return self.methods.checkJoin(objectGuid=object_guid, userGuid=self.author_guid)
    
    def download(self, save:bool=False, save_as:str=None) -> dict:
        return self.methods.download(save=save, saveAs=save_as, fileInline=self.file_inline)