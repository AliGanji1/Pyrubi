from random import randint
from ..network import Network, Socket
from ..crypto import Cryption
from ..utils import Utils
from random import choice
from time import sleep
from pyrubi.exceptions import InvalidAuth, InvalidInput
import asyncio

class Methods:

    def __init__(self, sessionData:dict, platform:str, apiVersion:int, proxy:str, timeOut:int, showProgressBar:bool) -> None:
        self.platform = platform.lower()
        if not self.platform in ["android", "web", "rubx", "rubikax", "rubino"]:
            print("The \"{}\" is not a valid platform. Choose these one -> (web, android, rubx)".format(platform))
            exit()
        self.apiVersion = apiVersion
        self.proxy = proxy
        self.timeOut = timeOut
        self.showProgressBar = showProgressBar
        self.sessionData = sessionData
        self.crypto = Cryption(
            auth=sessionData["auth"],
            private_key=sessionData["private_key"]
        ) if sessionData else Cryption(auth=Utils.randomTmpSession())
        self.network = Network(methods=self)
        self.socket = Socket(methods=self)

    # Authentication methods

    def sendCode(self, phoneNumber:str, passKey:str=None, sendInternal:bool=False) -> dict:
        input:dict = {
            "phone_number": f"98{Utils.phoneNumberParse(phoneNumber)}",
            "send_type": "Internal" if sendInternal else "SMS",
        }

        if passKey:
            input["pass_key"] = passKey

        return self.network.request(
            method="sendCode",
            input=input,
            tmpSession=True
        )
    
    def signIn(self, phoneNumber, phoneCodeHash, phoneCode) -> dict:
        publicKey, privateKey = self.crypto.rsaKeyGenrate()

        data = self.network.request(
            method="signIn",
            input={
                "phone_number": f"98{Utils.phoneNumberParse(phoneNumber)}",
                "phone_code_hash": phoneCodeHash,
                "phone_code": phoneCode,
			    "public_key": publicKey
            },
            tmpSession=True
        )
        
        data["private_key"] = privateKey

        return data
    
    def registerDevice(self, deviceModel) -> dict:
        return self.network.request(
            method="registerDevice",
            input={
                "app_version": "WB_4.3.3" if self.platform == "web" else "MA_3.4.3",
                "device_hash": Utils.randomDeviceHash(),
                "device_model": deviceModel,
                "is_multi_account": False,
                "lang_code": "fa",
                "system_version": "Windows 11" if self.platform == "web" else "SDK 28",
                "token": "",
                "token_type": "Web" if self.platform == "web" else "Firebase"
            }
        )
    
    def logout(self) -> dict:
        return self.network.request(method="logout")
    
    # Chats methods
    
    def getChats(self, startId:str) -> dict:
        return self.network.request(method="getChats", input={"start_id": startId})
    
    def getTopChatUsers(self) -> dict:
        return self.network.request(method="getTopChatUsers")
    
    def removeFromTopChatUsers(self, objectGuid:str) -> dict:
        return self.network.request(method="removeFromTopChatUsers", input={"user_guid": objectGuid})
    
    def getChatAds(self) -> dict:
        return self.network.request(method="getChatAds", input={"state": Utils.getState()})

    def getChatsUpdates(self) -> dict:
        return self.network.request(method="getChatsUpdates", input={"state": Utils.getState()})
    
    def joinChat(self, guidOrLink:str) -> dict:
        if Utils.checkLink(guidOrLink):
            method:str = "joinGroup" if Utils.getChatTypeByLink(link=guidOrLink) == "Group" else "joinChannelByLink"
        else:
            method:str = "joinChannelAction"

        return self.network.request(
            method=method,
            input={"hash_link": guidOrLink.split("/")[-1]} if Utils.checkLink(guidOrLink) else {
                "channel_guid": guidOrLink,
                "action": "Join"
            }
        )
    
    def leaveChat(self, objectGuid:str) -> dict:
        input:dict = {f"{Utils.getChatTypeByGuid(objectGuid=objectGuid).lower()}_guid": objectGuid}

        if Utils.getChatTypeByGuid(objectGuid=objectGuid) == "Group": method:str = "leaveGroup"
        else:
            method:str = "joinChannelAction"
            input["action"] = "Leave"

        return self.network.request(
            method=method,
            input=input
        )
    
    def removeChat(self, objectGuid:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"remove{chatType}",
            input={f"{chatType.lower()}_guid": objectGuid}
        )
    
    def getChatInfo(self, objectGuid:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"get{chatType}Info",
            input={f"{chatType.lower()}_guid": objectGuid}
        )
    
    def getChatInfoByUsername(self, username:str) -> dict:
        return self.network.request(method="getObjectInfoByUsername", input={"username": username.replace("@", "")})
    
    def getChatLink(self, objectGuid:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"get{chatType}Link",
            input={f"{chatType.lower()}_guid": objectGuid}
        )
    
    def setChatLink(self, objectGuid:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"set{chatType}Link",
            input={f"{chatType.lower()}_guid": objectGuid}
        )
    
    def setChatAdmin(self, objectGuid:str, memberGuid:str, accessList:list, customTitle:str, action:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        input:dict = {
            f"{chatType.lower()}_guid": objectGuid,
            "member_guid": memberGuid,
            "action": action,
            "access_list": accessList or []
        }

        if customTitle: input["custom_title"] = customTitle

        return self.network.request(
            method=f"set{chatType}Admin",
            input=input
        )
    
    def addChatMember(self, objectGuid:str, memberGuids:list) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"add{chatType}Members",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "member_guids": memberGuids
            }
        )
    
    def banChatMember(self, objectGuid:str, memberGuid:str, action:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"ban{chatType}Member",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "member_guid": memberGuid,
                "action": action
            }
        )
    
    def getBannedChatMembers(self, objectGuid:str, startId:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"getBanned{chatType}Members",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "start_id": startId
            }
        )
    
    def getChatAllMembers(self, objectGuid:str, searchText:str, startId:str, justGetGuids:bool=False) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        data = self.network.request(
            method=f"get{chatType}AllMembers",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "search_text": searchText.replace("@", "") if searchText else searchText,
                "start_id": startId
            }
        )

        if justGetGuids: return [i["member_guid"] for i in data["in_chat_members"]]

        return data
    
    def getChatAdminMembers(self, objectGuid:str, startId:str, justGetGuids:bool) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        data = self.network.request(
            method=f"get{chatType}AdminMembers",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "start_id": startId
            }
        )
    
        if justGetGuids: return [i["member_guid"] for i in data["in_chat_members"]]

        return data

    
    def getChatAdminAccessList(self, objectGuid:str, memberGuid:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"get{chatType}AdminAccessList",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "member_guid": memberGuid
            }
        )
    
    def chatPreviewByJoinLink(self, link:str) -> dict:
        return self.network.request(
            method="groupPreviewByJoinLink" if "joing" in link else "channelPreviewByJoinLink",
            input={"hash_link": link.split("/")[-1]}
        )
    
    def createChatVoiceChat(self, objectGuid:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"create{chatType}VoiceChat",
            input={f"{chatType.lower()}_guid": objectGuid}
        )
    
    def joinVoiceChat(self, objectGuid:str, myGuid:str, voiceChatId:str, sdp_offer_data:str) -> dict:
        return self.network.request(
            method=f"join{Utils.getChatTypeByGuid(objectGuid=objectGuid)}VoiceChat",
            input={
                "chat_guid": objectGuid,
                "voice_chat_id": voiceChatId,
                "sdp_offer_data": sdp_offer_data,
                "self_object_guid": myGuid
            }
        )

    def setChatVoiceChatSetting(self, objectGuid:str, voideChatId:str, title:str, joinMuted:bool) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        input:dict = {
            f"{chatType.lower()}_guid": objectGuid,
            "voice_chat_id": voideChatId,
            "updated_parameters": []
        }

        if title:
            input["title"] = title
            input["updated_parameters"].append("title")
        
        if joinMuted:
            input["join_muted"] = joinMuted
            input["updated_parameters"].append("join_muted")

        return self.network.request(
            method=f"set{chatType}VoiceChatSetting",
            input=input
        )
    
    def getChatVoiceChatUpdates(self, objectGuid:str, voideChatId:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"get{chatType}VoiceChatUpdates",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "voice_chat_id": voideChatId,
                "state": Utils.getState()
            }
        )
    
    def getChatVoiceChatParticipants(self, objectGuid:str, voideChatId:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"get{chatType}VoiceChatParticipants",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "voice_chat_id": voideChatId,
            }
        )
    
    def setChatVoiceChatState(self, objectGuid:str, voideChatId:str, activity:str, participantObjectGuid:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"set{chatType}VoiceChatState",
            input={
                "chat_guid": objectGuid,
                "voice_chat_id": voideChatId,
                "action": activity,
                "participant_object_guid": participantObjectGuid
            }
        )
    
    def sendChatVoiceChatActivity(self, objectGuid:str, voideChatId:str, activity:str, participantObjectGuid:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"send{chatType}VoiceChatActivity",
            input={
                "chat_guid": objectGuid,
                "voice_chat_id": voideChatId,
                "activity": activity,
                "participant_object_guid": participantObjectGuid
            }
        )
    
    def leaveChatVoiceChat(self, objectGuid:str, voideChatId:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"leave{chatType}VoiceChat",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "voice_chat_id": voideChatId
            }
        )
    
    def discardChatVoiceChat(self, objectGuid:str, voideChatId:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"discard{chatType}VoiceChat",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "voice_chat_id": voideChatId
            }
        )
    
    def setActionChat(self, objectGuid:str, action:str) -> dict:
        return self.network.request(
            method="setActionChat",
            input={
                "object_guid": objectGuid,
                "action": action
            }
        )
    
    def seenChats(self, seenList:dict) -> dict:
        return self.network.request(method="seenChats", input={"seen_list": seenList})
    
    def seenChatMessages(self, objectGuid:str, minId:str, maxId:str) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"seen{chatType}Messages",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "min_id": minId,
                "max_id": maxId
            }
        )
    
    def sendChatActivity(self, objectGuid:str, activity:str) -> dict:
        return self.network.request(
            method="sendChatActivity",
            input={
                "object_guid": objectGuid,
                "activity": activity
            }
        )
    
    def searchChatMessages(self, objectGuid:str, searchText:str) -> dict:
        return self.network.request(
            method="searchChatMessages",
            input={
                "object_guid": objectGuid,
                "search_text": searchText,
                "type": "Hashtag" if searchText.startswith("#") else "Text"
            }
        )
    
    def uploadAvatar(self, objectGuid:str, mainFile:str, thumbnailFile:str) -> dict:
        uploadMainFileData = self.network.upload(file=mainFile)

        return self.network.request(
            method="uploadAvatar",
            input={
                "object_guid": objectGuid,
                "thumbnail_file_id": self.network.upload(file=thumbnailFile)["id"] if thumbnailFile else uploadMainFileData["id"],
                "main_file_id": uploadMainFileData["id"]
            }
        )
    
    def getAvatars(self, objectGuid:str) -> dict:
        return self.network.request(method="getAvatars", input={"object_guid": objectGuid})
    
    def deleteAvatar(self, objectGuid:str, avatarId:str) -> dict:
        return self.network.request(
            method="deleteAvatar",
            input={
                "object_guid": objectGuid,
                "avatar_id": avatarId
            }
        )
    
    def deleteChatHistory(self, objectGuid:str, lastMessageId:str) -> dict:
        return self.network.request(
            method="deleteChatHistory",
            input={
                "object_guid": objectGuid,
                "last_message_id": lastMessageId
            }
        )
    
    def deleteUserChat(self, userGuid:str, lastDeletedMessageId) -> dict:
        return self.network.request(
            method="deleteUserChat",
            input={
                "user_guid": userGuid,
                "last_deleted_message_id": lastDeletedMessageId
            }
        )
    
    def getPendingObjectOwner(self, objectGuid:str) -> dict:
        return self.network.request(method="getPendingObjectOwner", input={"object_guid": objectGuid})
    
    def requestChangeObjectOwner(self, objectGuid:str, memberGuid:str) -> dict:
        return self.network.request(
            method="requestChangeObjectOwner",
            input={
                "new_owner_user_guid": memberGuid,
                "object_guid": objectGuid
            }
        )
    
    def replyRequestObjectOwner(self, objectGuid:str, action:str) -> dict:
        return self.network.request(
            method="replyRequestObjectOwner",
            input={
                "action": action, #Accept Reject
                "object_guid": objectGuid
            }
        )
    
    def cancelChangeObjectOwner(self, objectGuid:str) -> dict:
        return self.network.request(method="cancelChangeObjectOwner", input={"object_guid": objectGuid})
    
    def getChatReaction(self, objectGuid:str, minId:str, maxId:str) -> dict:
        return self.network.request(
            method="getChatReaction",
            input={
                f"object_guid": objectGuid,
                "min_id": minId,
                "max_id": maxId
            }
        )
    
    def reportObject(self, objectGuid:str, description:str) -> dict:
        return self.network.request(
            method="reportObject",
            input={
                "object_guid": objectGuid,
                "report_description": description,
                "report_type": 100,
                "report_type_object": "Object"
            }
        )
    
    def setChatUseTime(self, objectGuid:str, time:int) -> dict:
        return self.network.request(
            method="setChatUseTime",
            input={
                "object_guid": objectGuid,
                "time": time
            }
        )
    
    # User methods

    def setBlockUser(self, objectGuid:str, action:str) -> dict:
        return self.network.request(
            method="setBlockUser",
            input={
                "user_guid": objectGuid,
                "action": action
            }
        )
    
    def checkUserUsername(self, username:str) -> dict:
        return self.network.request(
            method="checkUserUsername",
            input={
                "username": username,
            }
        )
    
    # Group methods

    def addGroup(self, title:str, memberGuids:str) -> dict:
        return self.network.request(
            method="addGroup",
            input={
                "title": title,
                "member_guids": memberGuids
            }
        )
    
    def getGroupDefaultAccess(self, objectGuid:str) -> dict:
        return self.network.request(
            method=f"getGroupDefaultAccess",
            input={"group_guid": objectGuid}
        )
    
    def setChatDefaultAccess(self, objectGuid:str, accessList:list) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)

        return self.network.request(
            method=f"setGroupDefaultAccess",
            input={
                f"group_guid": objectGuid,
                "access_list": accessList
            }
        )
    
    def getGroupMentionList(self, objectGuid:str, searchMention:str) -> dict:
        return self.network.request(
            method="getGroupMentionList",
            input={
                "group_guid": objectGuid,
                "search_mention": searchMention
            }
        )
    
    def editGroupInfo(
            self,
            objectGuid:str,
            title:str,
            description:str,
            slowMode:int,
            eventMessages:bool,
            chatHistoryForNewMembers:bool,
            reactionType:str, #Selected Disabled All
            selectedReactions:list
        ) -> dict:

        input:dict = {
            "group_guid": objectGuid,
            "updated_parameters": []
        }

        if title:
            input["title"] = title
            input["updated_parameters"].append("title")

        if description:
            input["description"] = description
            input["updated_parameters"].append("description")

        if slowMode:
            input["slow_mode"] = slowMode
            input["updated_parameters"].append("slow_mode")

        if not eventMessages is None:
            input["event_messages"] = eventMessages
            input["updated_parameters"].append("event_messages")

        if not chatHistoryForNewMembers is None:
            input["chat_history_for_new_members"] = "Visible" if chatHistoryForNewMembers else "Hidden"
            input["updated_parameters"].append("chat_history_for_new_members")

        if reactionType:
            input["chat_reaction_setting"] = {"reaction_type": reactionType}
            input["updated_parameters"].append("chat_reaction_setting")

            if selectedReactions: input["chat_reaction_setting"]["selected_reactions"] = selectedReactions


        return self.network.request(
            method="editGroupInfo",
            input=input
        )
    
    # Channel methods

    def addChannel(self, title:str, description:str, memberGuids:list, private:bool) -> dict:
        input:dict = {
            "title": title,
            "description": description,
            "member_guids": memberGuids or [],
            "channel_type": "Private" if private else "Public"
        }
        
        return self.network.request(
            method="addChannel",
            input=input
        )
    
    def editChannelInfo(
            self,
            objectGuid:str,
            title:str,
            description:str,
            username:str,
            private:bool,
            signMessages:bool,
            reactionType:str, #Selected Disabled All
            selectedReactions:list
        ) -> dict:

        input:dict = {
            "channel_guid": objectGuid,
            "updated_parameters": []
        }

        if selectedReactions: input["chat_reaction_setting"]["selected_reactions"] = selectedReactions

        if title:
            input["title"] = title
            input["updated_parameters"].append("title")

        if description:
            input["description"] = description
            input["updated_parameters"].append("description")

        if not private is None:
            input["channel_type"] = "Private" if private else "Public"
            input["updated_parameters"].append("channel_type")

        if not signMessages is None: 
            input["sign_messages"] = signMessages
            input["updated_parameters"].append("sign_messages")
        
        if reactionType:
            input["chat_reaction_setting"] = {"reaction_type": reactionType}
            input["updated_parameters"].append("chat_reaction_setting")

            if selectedReactions: input["chat_reaction_setting"]["selected_reactions"] = selectedReactions

        if username:
            self.updateChannelUsername(
                objectGuid=objectGuid,
                username=username
            )

        return self.network.request(
            method="editChannelInfo",
            input=input
        )
    
    def checkChannelUsername(self, username:str) -> dict:
        return self.network.request(
            method="checkChannelUsername",
            input={
                "username": username,
            }
        )
    
    def updateChannelUsername(self, objectGuid:str, username:str) -> dict:
        return self.network.request(
            method="updateChannelUsername",
            input={
                "channel_guid": objectGuid,
                "username": username
            }
        )
    
    def getChannelSeenCount(self, objectGuid:str, minId:str, maxId:str) -> dict:
        return self.network.request(
            method="getChannelSeenCount",
            input={
                "channel_guid": objectGuid,
                "min_id": minId,
                "max_id": maxId
            }
        )
    
    # Message methods
    
    def sendText(self, objectGuid:str, text:str, messageId:str) -> dict:
        metadata = Utils.checkMetadata(text)

        input = {
            "object_guid": objectGuid,
            "rnd": str(randint(10000000, 999999999)),
            "text": metadata[1],
            "reply_to_message_id": messageId,
        }

        if metadata[0] != []: input["metadata"] = {"meta_data_parts": metadata[0]}

        return self.network.request(method="sendMessage", input=input)
    
    def baseSendFileInline(
            self,
            objectGuid:str,
            file:str,
            text:str,
            messageId:str,
            fileName:str,
            type:dict,
            isSpoil:bool=False,
            customThumbInline:str=None,
            time:int=None,
            performer:str=None
    ) -> dict:
        uploadData:dict = self.network.upload(file=file, fileName=fileName)
        if not uploadData: return
        
        input:dict = {
            "file_inline": {
                "dc_id": uploadData["dc_id"],
                "file_id": uploadData["id"],
                "file_name": uploadData["file_name"],
                "size": uploadData["size"],
                "mime": uploadData["mime"],
                "access_hash_rec": uploadData["access_hash_rec"],
                "type": type,
                "is_spoil": isSpoil
            },
            "object_guid": objectGuid,
            "rnd": Utils.randomRnd(),
            "reply_to_message_id": messageId
        }

        if type in ["Image", "Video", "Gif", "VideoMessage"]:
            customThumbInline = Utils.getImageThumbnail(
                customThumbInline
                if isinstance(customThumbInline, bytes)
                else self.network.http.request("GET", customThumbInline).data
                if Utils.checkLink(customThumbInline)
                else open(customThumbInline, "rb").read()
            ) if customThumbInline else None

            if not type == "Image":
                videoData:list = Utils.getVideoData(uploadData["file"])
                input["file_inline"]["time"] = videoData[2] * 1000

            fileSize:list = Utils.getImageSize(uploadData["file"]) if type == "Image" else videoData[1]
            input["file_inline"]["width"] = fileSize[0]
            input["file_inline"]["height"] = fileSize[1]

            if type == "VideoMessage":
                input["file_inline"]["type"] = "Video"
                input["file_inline"]["is_round"] = True

            input["file_inline"]["thumb_inline"] = customThumbInline or (Utils.getImageThumbnail(uploadData["file"]) if type == "Image" else videoData[0])

        if type in ["Music", "Voice"]:
            input["file_inline"]["time"] = (time or Utils.getVoiceDuration(uploadData["file"])) * (1000 if type == "Voice" else 1)

            if type == "Music":
                input["file_inline"]["music_performer"] = performer or Utils.getMusicArtist(uploadData["file"])

        metadata:list = Utils.checkMetadata(text)
        if metadata[1]: input["text"] = metadata[1]
        if metadata[0]: input["metadata"] = {"meta_data_parts": metadata[0]}

        return self.network.request(
            method="sendMessage",
            input=input
        )

    
    def sendFile(self, objectGuid:str, file:str, messageId:str, text:str, fileName:str) -> dict:
        return self.baseSendFileInline(
            objectGuid=objectGuid,
            file=file,
            text=text,
            messageId=messageId,
            fileName=fileName,
            type="File"
        )
    
    def sendImage(self, objectGuid:str, file:str, messageId:str, text:str, isSpoil:bool, thumbInline:str, fileName:str) -> dict:
        return self.baseSendFileInline(
            objectGuid=objectGuid,
            file=file,
            text=text,
            messageId=messageId,
            fileName=fileName,
            type="Image",
            isSpoil=isSpoil,
            customThumbInline=thumbInline
        )
    
    def sendVideo(self, objectGuid:str, file:str, messageId:str, text:str, isSpoil:bool, thumbInline:str, fileName:str) -> dict:
        return self.baseSendFileInline(
            objectGuid=objectGuid,
            file=file,
            text=text,
            messageId=messageId,
            fileName=fileName,
            type="Video",
            isSpoil=isSpoil,
            customThumbInline=thumbInline
        )
    
    def sendVideoMessage(self, objectGuid:str, file:str, messageId:str, text:str, thumbInline:str, fileName:str) -> dict:
        return self.baseSendFileInline(
            objectGuid=objectGuid,
            file=file,
            text=text,
            messageId=messageId,
            fileName=fileName,
            type="VideoMessage",
            customThumbInline=thumbInline
        )
    
    def sendGif(self, objectGuid:str, file:str, messageId:str, text:str, thumbInline:str, fileName:str) -> dict:
        return self.baseSendFileInline(
            objectGuid=objectGuid,
            file=file,
            text=text,
            messageId=messageId,
            fileName=fileName,
            type="Gif",
            customThumbInline=thumbInline
        )
    
    def sendMusic(self, objectGuid:str, file:str, messageId:str, text:str, fileName:str, performer:str) -> dict:
        return self.baseSendFileInline(
            objectGuid=objectGuid,
            file=file,
            text=text,
            messageId=messageId,
            fileName=fileName,
            type="Music",
            performer=performer
        )
    
    def sendVoice(self, objectGuid:str, file:str, messageId:str, text:str, fileName:str, time:int) -> dict:
        return self.baseSendFileInline(
            objectGuid=objectGuid,
            file=file,
            text=text,
            messageId=messageId,
            fileName=fileName,
            type="Voice",
            time=time
        )
    
    def sendLocation(self, objectGuid:str, latitude:int, longitude:int, messageId:str) -> dict:
        return self.network.request(
            method="sendMessage",
            input={
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "object_guid":objectGuid,
                "rnd": Utils.randomRnd(),
                "reply_to_message_id": messageId
            }
        )
    
    def sendMessageAPICall(self, objectGuid:str, text:str, messageId:str, buttonId:str) -> dict:
        return self.network.request(
            method="sendMessageAPICall",
            input={
                "text": text,
                "object_guid": objectGuid,
                "message_id": messageId,
                "aux_data": {"button_id": buttonId}
            }
        )
    
    def editMessage(self, objectGuid, text, messageId) -> dict:
        metadata = Utils.checkMetadata(text)
        data = {
            "object_guid": objectGuid,
            "text": metadata[1],
            "message_id": messageId,
        }
        if metadata[0] != []:
            data["metadata"] = {"meta_data_parts": metadata[0]}
        return self.network.request("editMessage", data)
    
    def actionOnMessageReaction(self, objectGuid:str, messageId:str, reactionId:int, action:str) -> dict:
        return self.network.request(
            method="actionOnMessageReaction",
            input={
                "action": action, #Add OR Remove
                "object_guid": objectGuid,
                "message_id": messageId,
                "reaction_id": reactionId
            }
        )
    
    def setPinMessage(self, objectGuid:str, messageId:str, action:str) -> dict:
        return self.network.request(
            method="setPinMessage",
            input={
                "object_guid": objectGuid,
                "message_id": messageId,
                "action": action
            }
        )
    
    def resendMessage(self, objectGuid:str, messageId:str, toObjectGuid:str, replyToMessageId:str, text:str, fileInline:None) -> dict:
        if not fileInline:
            messageData:dict = self.getMessagesById(objectGuid=objectGuid, messageIds=[messageId])

        text:str = text or messageData["messages"][0].get("text")
        metadata = Utils.checkMetadata(text)
        input = {
            "is_mute": False,
            "object_guid": toObjectGuid,
            "rnd": Utils.randomRnd(),
            "reply_to_message_id": replyToMessageId,
            "text": metadata[1]
        }

        fileInline:dict = fileInline or messageData["messages"][0].get("file_inline")
        if fileInline:
            input["file_inline"] = fileInline

        if not fileInline:
            location:dict = messageData["messages"][0].get("location")
            if location:
                input["location"] = location
                del input["location"]["map_view"]
                del input["text"]

            contact:dict = messageData["messages"][0].get("message_contact")
            if contact:
                input["message_contact"] = contact
                del input["text"]

            sticker:dict = messageData["messages"][0].get("sticker")
            if sticker:
                input["sticker"] = sticker
                del input["text"]

            if messageData["messages"][0].get("metadata"):
                input["metadata"] = {"meta_data_parts": messageData["messages"][0]["metadata"]}
                
        elif metadata[0] != []:
            input["metadata"] = {"meta_data_parts": metadata[0]}

        return self.network.request(method="sendMessage", input=input)

    def forwardMessages(self, objectGuid:str, messageIds:list, toObjectGuid:str) -> dict:
        return self.network.request(
            method="forwardMessages",
            input={
                "from_object_guid": objectGuid,
                "message_ids": messageIds,
                "to_object_guid": toObjectGuid,
                "rnd": Utils.randomRnd(),
            }
        )
    
    def deleteMessages(self, objectGuid:str, messageIds:list, deleteForAll:bool) -> dict:
        return self.network.request(
            method="deleteMessages",
            input={
                "object_guid": objectGuid,
                "message_ids": messageIds,
                "type": "Global" if deleteForAll else "Local"
            }
        )
    
    def getMessagesInterval(self, objectGuid:str, middleMessageId:str) -> dict:
        return self.network.request(
            method="getMessagesInterval",
            input={
                "object_guid": objectGuid,
                "middle_message_id": middleMessageId
            }
        )
    
    def getMessages(self, objectGuid:str, maxId:str, filterType:str, limit:int) -> dict:
        input:dict = {
            "object_guid": objectGuid,
            "sort": "FromMax",
            "max_id": maxId,
            "limit": limit
        }
        
        if filterType: input["filter_type"] = filterType

        return self.network.request(
            method="getMessages",
            input=input
        )
    
    def getMessagesUpdates(self, objectGuid:str) -> dict:
        return self.network.request(
            method="getMessagesUpdates",
            input={
                "object_guid": objectGuid,
                "state": Utils.getState(),
            }
        )
    
    def getMessagesById(self, objectGuid:str, messageIds:list) -> dict:
        return self.network.request(
            method="getMessagesByID",
            input={
                "object_guid": objectGuid,
                "message_ids": messageIds,
            }
        )
    
    def getMessageShareUrl(self, objectGuid:str, messageId:str) -> dict:
        return self.network.request(
            method="getMessageShareUrl",
            input={
                "object_guid": objectGuid,
                "message_id": messageId,
            }
        )
    
    def clickMessageUrl(self, objectGuid:str, messageId:str, linkUrl:str) -> dict:
        return self.network.request(
            method="clickMessageUrl",
            input={
                "object_guid": objectGuid,
                "message_id": messageId,
                "link_url": linkUrl
            }
        )
    
    def searchGlobalMessages(self, searchText:str) -> dict:
        return self.network.request(
            method="search_text",
            input={
                "search_text": searchText,
                "type": "Text",
            }
        )
    
    def requestSendFile(self, fileName:str, mime:str, size:str) -> dict:
        return self.network.request(
            method="requestSendFile",
            input={
                "file_name": fileName,
                "mime": mime,
                "size": size
            }
        )
    
    # Contact methods
    
    def sendContact(self, objectGuid:str, firstName:str, lastName:str, phoneNumber:str, userGuid:str, messageId:str) -> dict:
        return self.network.request(
            method="sendMessage",
            input={
                "message_contact":{
                    "first_name": firstName,
                    "last_name": lastName or "",
                    "phone_number": phoneNumber,
                    "user_guid": userGuid
                },
                "object_guid":objectGuid,
                "rnd": Utils.randomRnd(),
                "reply_to_message_id": messageId
            }
        )

    def getContacts(self, startId:str) -> dict:
        return self.network.request(method="getContacts", input={"start_id": startId})
    
    def getContactsLastOnline(self, userGuids:list) -> dict:
        return self.network.request(method="getContactsLastOnline", input={"user_guids": userGuids})

    def addAddressBook(self, phone:str, firstName:str, lastName:str) -> dict:
        return self.network.request(
            method="addAddressBook",
            input={
                "phone": f"98{Utils.phoneNumberParse(phone)}",
                "first_name": firstName,
                "last_name": lastName
            }
        )
    
    def deleteContact(self, objectGuid:str) -> dict:
        return self.network.request(method="deleteContact", input={"user_guid": objectGuid})
    
    def getContactsUpdates(self) -> dict:
        return self.network.request(method="getContactsUpdates", input={"state": Utils.getState()})
    
    # Sticker methods

    def sendSticker(self, objectGuid:str, emoji:str, messageId:str, stickerData:str) -> dict:
        data = {
            "sticker": stickerData or choice(self.getStickersByEmoji(emoji)["stickers"]),
            "object_guid": objectGuid,
            "rnd": Utils.randomRnd(),
            "reply_to_message_id": messageId,
        }
        
        return self.network.request("sendMessage", data)

    def getMyStickerSets(self) -> dict:
        return self.network.request(method="getMyStickerSets")
    
    def getTrendStickerSets(self, startId:str) -> dict:
        return self.network.request(method="getTrendStickerSets", input={"start_id": startId})
    
    def searchStickers(self, searchText:str, startId:str) -> dict:
        return self.network.request(
            method="searchStickers",
            input={
                "search_text": searchText,
                "start_id": startId
            }
        )
    
    def actionOnStickerSet(self, stickerSetId:str, action:str) -> dict:
        return self.network.request(
            method="actionOnStickerSet",
            input={
                "sticker_set_id": stickerSetId,
                "action": action
            }
        )
    
    def getStickersByEmoji(self, emoji:str) -> dict:
        return self.network.request(
            method="getStickersByEmoji",
            input={
                "emoji_character": emoji,
                "suggest_by": "All"
            }
        )
    
    def getStickersBySetIDs(self, stickerSetIds:list) -> dict:
        return self.network.request(method="getStickersBySetIDs", input={"sticker_set_ids": stickerSetIds})
    
    # Gif methods

    def getMyGifSet(self) -> dict:
        return self.network.request(method="getMyGifSet")

    def addToMyGifSet(self, objectGuid:str, messageId:str) -> dict:
        return self.network.request(
            method="addToMyGifSet",
            input={
                "message_id": messageId,
                "object_guid": objectGuid
            }
        )
    
    def removeFromMyGifSet(self, fileId:str) -> dict:
        return self.network.request(method="removeFromMyGifSet", input={"file_id": fileId})
    
    # Poll methods

    def sendPoll(self, objectGuid:str, question:str, options:list, messageId:str = None, multipleAnswers:bool = False, anonymous:bool = True,  quiz:bool = False) -> dict:
        return self.network.request(
            method="createPoll",
            input={
                "allows_multiple_answers": multipleAnswers,
                "correct_option_index": None,
                "is_anonymous": anonymous,
                "object_guid": objectGuid,
                "options": options if len(options) >= 2 else ["This poll was created with Pyrubi Library", "حداقل باید دو گزینه برای نظر سنجی گزاشته شود!"],
                "question": question,
                "rnd": Utils.randomRnd(),
                "type": "Quiz" if quiz else "Regular",
                "reply_to_message_id": messageId
            }
        )
    
    def votePoll(self, pollId:str, selectionIndex:int) -> dict:
        return self.network.request(
            method="votePoll",
            input={
                "poll_id": pollId,
                "selection_index": selectionIndex
            }
        )
    
    def getPollStatus(self, pollId:str) -> dict:
        return self.network.request(method="getPollStatus", input={"poll_id": pollId})
    
    def getPollOptionVoters(self, pollId:str, selectionIndex:int, startId:str=None) -> dict:
        return self.network.request(
            method="getPollOptionVoters",
            input={
                "poll_id": pollId,
                "selection_index": selectionIndex,
                "start_id": startId
            }
        )
    
    # Live methods

    def sendLive(self, objectGuid:str, thumbInline:str) -> dict:
        return self.network.request(
            method="sendLive",
            input={
                "thumb_inline": Utils.getImageThumbnail(
                    thumbInline
                    if isinstance(thumbInline, bytes)
                    else self.network.http.request("GET", thumbInline)
                    if Utils.checkLink(thumbInline)
                    else open(thumbInline, "rb").read()
                ),
                "device_type": "Software",
                "object_guid": objectGuid,
                "rnd": Utils.randomRnd()
            }
        )
    
    def addLiveComment(self, accessToken:str, liveId:str, text:str) -> dict:
        return self.network.request(
            method="addLiveComment",
            input={
                "access_token": accessToken,
                "live_id": liveId,
                "text": text
            }
        )
    
    def getLiveStatus(self, accessToken:str, liveId:str) -> dict:
        return self.network.request(
            method="getLiveStatus",
            input={
                "access_token": accessToken,
                "live_id": liveId,
                "type": "LiveViewer"
            }
        )
    
    def getLiveComments(self, accessToken:str, liveId:str) -> dict:
        return self.network.request(
            method="getLiveComments",
            input={
                "access_token": accessToken,
                "live_id": liveId,
            }
        )
    
    def getLivePlayUrl(self, accessToken:str, liveId:str) -> dict:
        return self.network.request(
            method="getLivePlayUrl",
            input={
                "access_token": accessToken,
                "live_id": liveId
            }
        )
    
    # Call methods

    def requestCall(self, objectGuid:str, callType:str) -> dict:
        return self.network.request(
            method="requestCall",
            input={
                "call_type": callType,
                "library_versions": ["2.7.7","2.4.4"],
                "max_layer": 92,
                "min_layer": 65,
                "sip_version": 1,
                "support_call_out": True,
                "user_guid": objectGuid
            }
        )
    
    def discardCall(self, callId:str, duration:int, reason:str) -> dict:
        return self.network.request(
            method="discardCall",
            input={
                "call_id": callId,
                "duration": duration,
                "reason": reason #Missed OR Disconnect
            }
        )
    
    # Setting methods

    def setSetting(
            self,
            showMyLastOnline:bool,
            showMyPhoneNumber:bool,
            showMyProfilePhoto:bool,
            linkForwardMessage:bool,
            canJoinChatBy:bool
        ) -> dict:

        input:dict = {
            "settings": {},
            "update_parameters": []
        }

        if not showMyLastOnline is None:
            input["settings"]["show_my_last_online"] = "Everybody" if showMyLastOnline else "Nobody"
            input["update_parameters"].append("show_my_last_online")

        if not showMyPhoneNumber is None:
            input["settings"]["show_my_phone_number"] = "Everybody" if showMyPhoneNumber else "Nobody"
            input["update_parameters"].append("show_my_phone_number")

        if not showMyProfilePhoto is None:
            input["settings"]["show_my_profile_photo"] = "Everybody" if showMyProfilePhoto else "MyContacts"
            input["update_parameters"].append("show_my_profile_photo")

        if not linkForwardMessage is None:
            input["settings"]["link_forward_message"] = "Everybody" if linkForwardMessage else "Nobody"
            input["update_parameters"].append("link_forward_message")

        if not canJoinChatBy is None:
            input["settings"]["can_join_chat_by"] = "Everybody" if canJoinChatBy else "MyContacts"
            input["update_parameters"].append("can_join_chat_by")

        return self.network.request(
            method="setSetting",
            input=input
        )
    
    def addFolder(
            self,
            folderName:str,
            folderId:str,
            excludeChatIds:list,
            excludeChatTypes:list,
            includeChatIds:list,
            includeChatTypes:list
        ) -> dict:

        return self.network.request(
            method="addFolder",
            input={
                "exclude_object_guids": excludeChatIds,
                "include_object_guids": excludeChatTypes,
                "exclude_chat_types": includeChatIds,
                "include_chat_types": includeChatTypes,
                "folder_id": folderId,
                "is_add_to_top": True,
                "name": folderName
            }
        )
    
    def getFolders(self, lastState:str) -> dict:
        return self.network.request(method="getFolders", input={"last_state": lastState})
    
    def getSuggestedFolders(self) -> dict:
        return self.network.request(method="getSuggestedFolders")
    
    def deleteFolder(self, folderId:str) -> dict:
        return self.network.request(method="deleteFolder", input={"folder_id": folderId})
    
    def updateProfile(self, firstName:str, lastname:str, bio:str, username:str) -> dict:
        input:dict = {
            "first_name": firstName,
            "last_name": lastname,
            "bio": bio,
            "updated_parameters": []
        }

        if firstName:input["updated_parameters"].append("first_name")
        if lastname: input["updated_parameters"].append("last_name")
        if bio: input["updated_parameters"].append("bio")

        if username:
            response:dict = self.network.request(method="updateUsername", input={"username": username})
            if not input["updated_parameters"]:
                return response

        return self.network.request(
            method="updateProfile",
            input=input
        )
    
    def getMySessions(self) -> dict:
        return self.network.request(method="getMySessions")
    
    def terminateSession(self, sessionKey:str) -> dict:
        return self.network.request(method="terminateSession", input={"session_key": sessionKey})
    
    def terminateOtherSessions(self):
            return self.network.request("terminateOtherSessions")
    
    def checkTwoStepPasscode(self, password:str) -> dict:
        return self.network.request(method="checkTwoStepPasscode", input={"password": password})
    
    def setupTwoStepVerification(self, password:str, hint:str, recoveryEmail:str) -> dict:
        return self.network.request(
            method="setupTwoStepVerification",
            input={
                "password": password,
                "hint": hint,
                "recovery_email": recoveryEmail
            }
        )
    
    def requestRecoveryEmail(self, password:str, recoveryEmail:str) -> dict:
        return self.network.request(
            method="requestRecoveryEmail",
            input={
                "password": password,
                "recovery_email": recoveryEmail
            }
        )
    
    def verifyRecoveryEmail(self, password:str, code:str) -> dict:
        return self.network.request(
            method="verifyRecoveryEmail",
            input={
                "password": password,
                "code": code
            }
        )
    
    def turnOffTwoStep(self, password:str) -> dict:
        return self.network.request(method="turnOffTwoStep", input={"password": password})
    
    def changePassword(self, password:str, newPassword:str, newHint:str) -> dict:
        return self.network.request(
            method="changePassword",
            input={
                "password": password,
                "new_password": newPassword,
                "new_hint": newHint
            }
        )
    
    def getTwoPasscodeStatus(self) -> dict:
        return self.network.request(method="getTwoPasscodeStatus")
    
    def getPrivacySetting(self) -> dict:
        return self.network.request(method="getPrivacySetting")
    
    def getBlockedUsers(self, startId:str) -> dict:
        return self.network.request(method="getBlockedUsers", input={"start_id": startId})
    
    # Other methods

    def getMe(self) -> dict:
        data:dict = self.network.request(method="getUserInfo")
        data.update(self.sessionData)
        return data
    
    def transcribeVoice(self, objectGuid:str, messageId:str) -> dict:
        response = self.network.request(
            method="transcribeVoice",
            input={
                "object_guid": objectGuid,
                "message_id": messageId
            }
        )
        
        if response["status"] != "OK":
            return response
        
        while True:
            sleep(0.5)
            result = self.network.request(
                method="getTranscription",
                input={
                    "message_id": messageId,
                    "transcription_id": response["transcription_id"]
                }
            )
            
            if result["status"] != "OK":
                continue

            return result
    
    def resetContacts(self) -> dict:
        return self.network.request("resetContacts")
    
    def getTime(self) -> dict:
        return self.network.request("getTime")

    def getAbsObjects(self, objectGuids:list) -> dict:
        return self.network.request(method="getAbsObjects", input={"object_guids": objectGuids})
    
    def getLinkFromAppUrl(self, url:str) -> dict:
        return self.network.request(method="getLinkFromAppUrl", input={"app_url": url})
    
    def searchGlobalObjects(self, searchText:str, filters:list) -> dict:
        input:dict = {"search_text": searchText}
        if filters: input["filter_types"] = filters

        return self.network.request(method="searchGlobalObjects", input=input)
    
    def checkJoin(self, objectGuid:str, userGuid:str) -> bool:
        userUsername:dict = self.getChatInfo(userGuid)["user"].get("username")

        if userGuid in self.getChatAllMembers(objectGuid=objectGuid, searchText=userUsername, startId=None, justGetGuids=True):
            return True
        
        if userUsername:
            return False
        
        return None
    
    def getProfileLinkItems(self, objectGuid:str) -> dict:
        return self.network.request(method="getProfileLinkItems", input={"object_guid": objectGuid})
    
    def getDownloadLink(self, objectGuid:str, messageId:str, fileInline:dict) -> str:
        if not fileInline:
            fileInline = self.getMessagesById(objectGuid=objectGuid, messageIds=[messageId])["messages"][0]["file_inline"]
        
        return f'https://messenger{fileInline["dc_id"]}.iranlms.ir/InternFile.ashx?id={fileInline["file_id"]}&ach={fileInline["access_hash_rec"]}'
    
    def download(self, objectGuid:str, messageId:str, save:bool, saveAs:str, fileInline:dict) -> dict:
        if not fileInline:
            fileInline = self.getMessagesById(objectGuid=objectGuid, messageIds=[messageId])["messages"][0]["file_inline"]

        downloadedData:bytes = self.network.download(
            accessHashRec=fileInline["access_hash_rec"],
            fileId=fileInline["file_id"],
            dcId=fileInline["dc_id"],
            size=fileInline["size"], 
            fileName=fileInline["file_name"]
        )

        if save or saveAs:
            with open(saveAs or fileInline["file_name"], "wb") as file:
                file.write(downloadedData)

        fileInline["file"] = downloadedData

        return fileInline
    
    async def playVoice(self, objectGuid:str, file: str) -> None:
        try:
            from aiortc import RTCPeerConnection, RTCSessionDescription
            from aiortc.contrib.media import MediaPlayer
                
            voiceChatId: str = self.getChatInfo(objectGuid)["chat"].get("group_voice_chat_id")

            if not voiceChatId:
                voiceChatId:str = self.createChatVoiceChat(objectGuid=objectGuid)["group_voice_chat_update"]["voice_chat_id"]

            rtcConnection = RTCPeerConnection()
            player: MediaPlayer = MediaPlayer(file)
            rtcConnection.addTrack(player.audio)
            spdOffer = await rtcConnection.createOffer()
            await rtcConnection.setLocalDescription(spdOffer)

            answerSdp = self.joinVoiceChat(
                objectGuid=objectGuid,
                myGuid=self.sessionData["user"]["user_guid"],
                voiceChatId=voiceChatId,
                sdp_offer_data=spdOffer.sdp
            )["sdp_answer_data"]
            
            self.setChatVoiceChatState(
                objectGuid=objectGuid,
                voideChatId=voiceChatId,
                activity="Unmute",
                participantObjectGuid=self.sessionData["user"]["user_guid"]
            )

            remoteDescription = RTCSessionDescription(answerSdp, "answer")
            await rtcConnection.setRemoteDescription(remoteDescription)

            def onEnded():
                asyncio.ensure_future(rtcConnection.close())

            player.audio.on("ended", onEnded)

            def keepAlive():
                while rtcConnection.connectionState != "closed":
                    try:
                        if self.sendChatVoiceChatActivity(
                            objectGuid=objectGuid,
                            voideChatId=voiceChatId,
                            activity="Speaking",
                            participantObjectGuid=self.sessionData["user"]["user_guid"]
                        )["status"] != "OK":
                            break
                        
                        if self.getChatVoiceChatUpdates(
                            objectGuid=objectGuid,
                            voideChatId=voiceChatId
                        )["status"] != "OK":
                            break

                        sleep(8)
                    except (InvalidInput, InvalidAuth):
                        break
                    except:
                        continue
                
            from threading import Thread
            Thread(target=keepAlive, daemon=False).start()

            while rtcConnection.connectionState != "closed":
                await asyncio.sleep(1)

            asyncio.ensure_future(rtcConnection.close())

        except ImportError:
            print("The aiortc library is not installed!")

    def add_handler(self, func, filters:list, regexp:str) -> None:
        self.socket.addHandler(
            func=func,
            filters=filters,
            regexp=regexp
        )
        return func
    
    def run(self) -> None:
        self.socket.connect()