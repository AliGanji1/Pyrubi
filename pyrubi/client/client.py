from ..methods import Methods
from ..utils import checkUpdate
from threading import Thread

class Client(object):

    def __init__(
        self,
        session:str=None,
        auth:str=None,
        private:str=None,
        platform:str="web",
        proxy:str=None,
        time_out:int=10,
        show_progress_bar:bool=True
    ) -> None:
        
        self.session = session
        self.platform = platform
        self.proxy = proxy
        self.timeOut = time_out
        
        Thread(target=checkUpdate, daemon=True).start()
        
        if(session):
            from ..utils import Sessions
            self.sessions = Sessions(self)

            if(self.sessions.cheackSessionExists()):
                self.sessionData = self.sessions.loadSessionData()
            else:
                self.sessionData = self.sessions.createSession()
        else:
            if(not auth):
                print("Enter the session or auth and private!")
                exit()

            from ..utils import Tools
            self.sessionData = {
                "auth": auth,
                "private_key": Tools.privateParse(private=private)
            }

        self.methods = Methods(sessionData=self.sessionData, platform=platform, proxy=proxy, timeOut=time_out, showProgressBar=show_progress_bar)

    # Authentication methods
    
    def send_code(self, phone_number:str, pass_key:str=None) -> dict:
        return self.methods.sendCode(phoneNumber=phone_number, passKey=pass_key)
    
    def sign_in(self, phone_number:str, phone_code_hash:str, phone_code:str) -> dict:
        return self.methods.signIn(phoneNumber=phone_number, phoneCodeHash=phone_code_hash, phoneCode=phone_code)
    
    def register_device(self, system_version:str, device_model:str, device_hash:str) -> dict:
        return self.methods.registerDevice(systemVersion=system_version, deviceModel=device_model, deviceHash=device_hash)
    
    def logout(self) -> dict:
        return self.methods.logout()
    
    # Chats methods

    def get_chats(self, start_id:str=None) -> dict:
        return self.methods.getChats(startId=start_id)
    
    def get_top_users(self) -> dict:
        return self.methods.getTopChatUsers()
    
    def remove_from_top_users(self, object_guid:str) -> dict:
        return self.methods.removeFromTopChatUsers(objectGuid=object_guid)
    
    def get_chat_ads(self) -> dict:
        return self.methods.getChatAds()
    
    def get_chats_updates(self) -> dict:
        return self.methods.getChatsUpdates()
    
    def join_chat(self, guid_or_link:str) -> dict:
        return self.methods.joinChat(guidOrLink=guid_or_link)
    
    def leave_chat(self, object_guid:str) -> dict:
        return self.methods.leaveChat(objectGuid=object_guid)
    
    def remove_chat(self, object_guid:str) -> dict:
        return self.methods.removeChat(objectGuid=object_guid)
    
    def get_chat_info(self, object_guid:str) -> dict:
        return self.methods.getChatInfo(objectGuid=object_guid)
    
    def get_chat_info_by_username(self, username:str) -> dict:
        return self.methods.getChatInfoByUsername(username=username)

    def get_link(self, object_guid:str) -> dict:
        return self.methods.getChatLink(objectGuid=object_guid)
    
    def set_link(self, object_guid:str) -> dict:
        return self.methods.setChatLink(objectGuid=object_guid)
    
    def set_admin(self, object_guid:str, member_guid:str, access_list:list=None, custom_title:str=None) -> dict:
        return self.methods.setChatAdmin(objectGuid=object_guid, memberGuid=member_guid, accessList=access_list, customTitle=custom_title, action="SetAdmin")
    
    def unset_admin(self, object_guid:str, member_guid:str) -> dict:
        return self.methods.setChatAdmin(objectGuid=object_guid, memberGuid=member_guid, accessList=None, customTitle=None, action="UnsetAdmin")
    
    def add_member(self, object_guid:str, member_guids:list) -> dict:
        return self.methods.addChatMember(objectGuid=object_guid, memberGuids=member_guids)

    def ban_member(self, object_guid:str, member_guid:str) -> dict:
        return self.methods.banChatMember(objectGuid=object_guid, memberGuid=member_guid, action="Set")
    
    def unban_member(self, object_guid:str, member_guid:str) -> dict:
        return self.methods.banChatMember(objectGuid=object_guid, memberGuid=member_guid, action="Unset")
    
    def get_banned_members(self, object_guid:str, start_id:str=None) -> dict:
        return self.methods.getBannedChatMembers(objectGuid=object_guid, startId=start_id)

    def get_all_members(self, object_guid:str, search_text:str=None, start_id:str=None, just_get_guids:bool=False) -> dict:
        return self.methods.getChatAllMembers(objectGuid=object_guid, searchText=search_text, startId=start_id, justGetGuids=just_get_guids)
    
    def get_admin_members(self, object_guid:str, start_id:str=None, just_get_guids:bool=False) -> dict:
        return self.methods.getChatAdminMembers(objectGuid=object_guid, startId=start_id, justGetGuids=just_get_guids)
    
    def get_admin_access_list(self, object_guid:str, member_guid:str=None) -> dict:
        return self.methods.getChatAdminAccessList(objectGuid=object_guid, memberGuid=member_guid)
    
    def get_chat_preview(self, link:str) -> dict:
        return self.methods.chatPreviewByJoinLink(link=link)
    
    def create_voice_chat(self, object_guid:str) -> dict:
        return self.methods.createChatVoiceChat(objectGuid=object_guid)
    
    def join_voice_chat(self, object_guid:str, my_guid:str, voice_chat_id:str) -> dict:
        return self.methods.joinVoiceChat(objectGuid=object_guid, myGuid=my_guid, voiceChatId=voice_chat_id)
    
    def set_voice_chat_setting(self, object_guid:str, voice_chat_id:str, title:str=None, join_mute:bool=None) -> dict:
        return self.methods.setChatVoiceChatSetting(objectGuid=object_guid, voideChatId=voice_chat_id, title=title, joinMuted=join_mute)
    
    def get_voice_chat_updates(self, object_guid:str, voice_chat_id:str) -> dict:
        return self.methods.getChatVoiceChatUpdates(objectGuid=object_guid, voideChatId=voice_chat_id)
    
    def get_voice_chat_participants(self, object_guid:str, voice_chat_id:str) -> dict:
        return self.methods.getChatVoiceChatParticipants(objectGuid=object_guid, voideChatId=voice_chat_id)
    
    def set_voice_chat_state(self, object_guid:str, voice_chat_id:str, activity:str) -> dict:
        return self.methods.setChatVoiceChatState(objectGuid=object_guid, voideChatId=voice_chat_id, activity=activity)
    
    def send_voice_chat_activity(self, object_guid:str, voice_chat_id:str, activity:str, participant_object_guid:str) -> dict:
        return self.methods.sendChatVoiceChatActivity(objectGuid=object_guid, voideChatId=voice_chat_id, activity=activity, participantObjectGuid=participant_object_guid)    
    
    def leave_voice_chat(self, object_guid:str, voice_chat_id:str) -> dict:
        return self.methods.leaveChatVoiceChat(objectGuid=object_guid, voideChatId=voice_chat_id)
    
    def discard_voice_chat(self, object_guid:str, voice_chat_id:str) -> dict:
        return self.methods.discardChatVoiceChat(objectGuid=object_guid, voideChatId=voice_chat_id)
    
    def pin_chat(self, object_guid:str) -> dict:
        return self.methods.setActionChat(objectGuid=object_guid, action="Pin")
    
    def unpin_chat(self, object_guid:str) -> dict:
        return self.methods.setActionChat(objectGuid=object_guid, action="Unpin")
    
    def mute_chat(self, object_guid:str) -> dict:
        return self.methods.setActionChat(objectGuid=object_guid, action="Mute")
    
    def unmute_chat(self, object_guid:dict) -> dict:
        return self.methods.setActionChat(objectGuid=object_guid, action="Unmute")
    
    def seen_chats(self, seen_list:dict) -> dict:
        """
        ```python

        seen_list : dict = {"object_guid": "message_id", "object_guid": "message_id", ...}

        ```
        """
        return self.methods.seenChats(seenList=seen_list)
    
    def send_chat_activity(self, object_guid:str, activity:str) -> dict:
        return self.methods.sendChatActivity(objectGuid=object_guid, activity=activity)
    
    def search_chat_messages(self, object_guid:str, search_text:str) -> dict:
        return self.methods.searchChatMessages(objectGuid=object_guid, searchText=search_text)
    
    def upload_avatar(self, object_guid:str, main_file:str, thumbnail_file:str=None) -> dict:
        return self.methods.uploadAvatar(objectGuid=object_guid, mainFile=main_file, thumbnailFile=thumbnail_file)
    
    def getAvatars(self, object_guid:str) -> dict:
        return self.methods.getAvatars(objectGuid=object_guid)
    
    def delete_avatar(self, object_guid:str, avatar_id:str) -> dict:
        return self.methods.deleteAvatar(objectGuid=object_guid, avatarId=avatar_id)
    
    def delete_history(self, object_guid:str, last_message_id:str) -> dict:
        return self.methods.deleteChatHistory(objectGuid=object_guid, lastMessageId=last_message_id)
    
    def delete_user_chat(self, user_guid:str, last_deleted_message_id:str) -> dict:
        return self.methods.deleteUserChat(userGuid=user_guid, lastDeletedMessageId=last_deleted_message_id)
    
    def get_pending_owner(self, object_guid:str) -> dict:
        return self.methods.getPendingObjectOwner(objectGuid=object_guid)
    
    def request_change_owner(self, object_guid:str, member_guid:str) -> dict:
        return self.methods.requestChangeObjectOwner(objectGuid=object_guid, memberGuid=member_guid)
    
    def accept_request_owner(self, object_guid:str) -> dict:
        return self.methods.replyRequestObjectOwner(objectGuid=object_guid, action="Accept")
    
    def reject_request_owner(self, object_guid:str) -> dict:
        return self.methods.replyRequestObjectOwner(objectGuid=object_guid, action="Reject")
    
    def cancel_change_owner(self, object_guid:str) -> dict:
        return self.methods.cancelChangeObjectOwner(objectGuid=object_guid)
    
    def get_chat_reaction(self, object_guid:str, min_id:str, max_id:str) -> dict:
        return self.methods.getChatReaction(objectGuid=object_guid, minId=min_id, maxId=max_id)
    
    def report_chat(self, object_guid:str, description:str) -> dict:
        return self.methods.reportObject(objectGuid=object_guid, description=description)
    
    def set_chat_use_time(self, object_guid:str, time:int) -> dict:
        return self.methods.setChatUseTime(objectGuid=object_guid, time=time)
    
    # User methods
    
    def block_user(self, object_guid:str) -> dict:
        return self.methods.setBlockUser(objectGuid=object_guid, action="Block")
    
    def unblock_user(self, object_guid:str) -> dict:
        return self.methods.setBlockUser(objectGuid=object_guid, action="Unblock")
    
    def check_user_username(self, username:str) -> dict:
        return self.methods.checkUserUsername(username=username)
    
    # Group methods
    
    def add_group(self, title:str, member_guids:list) -> dict:
        return self.methods.addGroup(title=title, memberGuids=member_guids)
    
    def get_group_default_access(self, object_guid:str) -> dict:
        return self.methods.getGroupDefaultAccess(objectGuid=object_guid)
    
    def set_group_default_access(self, object_guid:str, access_list:list=[]) -> dict:
        return self.methods.setChatDefaultAccess(objectGuid=object_guid, accessList=access_list)

    def get_group_mention_list(self, object_guid:str, search_mention:str) -> dict:
        return self.methods.getGroupMentionList(objectGuid=object_guid, searchMention=search_mention)
    
    def edit_group_info(self, object_guid:str, title:str=None, description:str=None, slow_mode:int=None, event_messages:bool=None, chat_history_for_new_members:bool=None, reaction_type:str=None, selected_reactions:list=None) -> dict:
        return self.methods.editGroupInfo(objectGuid=object_guid, title=title, description=description, slowMode=slow_mode, eventMessages=event_messages, chatHistoryForNewMembers=chat_history_for_new_members, reactionType=reaction_type, selectedReactions=selected_reactions)
    
    # Channels methods
    
    def add_channel(self, title:str, description:str=None, member_guids:list=None, private:bool=False) -> dict:
        return self.methods.addChannel(title=title, description=description, memberGuids=member_guids, private=private)

    def edit_channel_info(self, object_guid:str, title:str=None, description:str=None, username:str=None, private:bool=None, sign_message:bool=None, reaction_type:str=None, selected_reactions:list=None) -> dict:
        return self.methods.editChannelInfo(objectGuid=object_guid, title=title, description=description, username=username, private=private, signMessages=sign_message, reactionType=reaction_type, selectedReactions=selected_reactions)
    
    def check_channel_username(self, username:str) -> dict:
        return self.methods.checkChannelUsername(username=username)
    
    def get_channel_seen_count(self, object_guid:str, min_id:str, max_id:str) -> dict:
        return self.methods.getChannelSeenCount(objectGuid=object_guid, minId=min_id, maxId=max_id)
    
    # Message methods
    
    def send_text(self, object_guid:str, text:str, message_id:str=None) -> dict:
        return self.methods.sendText(objectGuid=object_guid, text=text, messageId=message_id)
    
    def send_file(self, object_guid:str, file:str, message_id:str=None, text:str=None, file_name:str=None) -> dict:
        return self.methods.sendFile(objectGuid=object_guid, file=file, text=text, messageId=message_id, fileName=file_name)
    
    def send_image(self, object_guid:str, file:str, message_id:str=None, text:str=None, file_name:str=None) -> dict:
        return self.methods.sendImage(objectGuid=object_guid, file=file, text=text, messageId=message_id, fileName=file_name)
    
    def send_video(self, object_guid:str, file:str, message_id:str=None, text:str=None, file_name:str=None) -> dict:
        return self.methods.sendVideo(objectGuid=object_guid, file=file, text=text, messageId=message_id, fileName=file_name)
    
    def send_gif(self, object_guid:str, file:str, message_id:str=None, text:str=None, file_name:str=None) -> dict:
        return self.methods.sendGif(objectGuid=object_guid, file=file, text=text, messageId=message_id, fileName=file_name)
    
    def send_music(self, object_guid:str, file:str, message_id:str=None, text:str=None, file_name:str=None) -> dict:
        return self.methods.sendMusic(objectGuid=object_guid, file=file, text=text, messageId=message_id, fileName=file_name)
    
    def send_voice(self, object_guid:str, file:str, message_id:str=None, text:str=None, file_name:str=None) -> dict:
        return self.methods.sendVoice(objectGuid=object_guid, file=file, text=text, messageId=message_id, fileName=file_name)
    
    def send_location(self, object_guid:str, latitude:int, longitude:int, message_id:str=None) -> dict:
        return self.methods.sendLocation(objectGuid=object_guid, latitude=latitude, longitude=longitude, messageId=message_id)
    
    def send_message_api_call(self, objectGuid:str, text:str, message_id:str, button_id:str) -> dict:
        return self.methods.sendMessageAPICall(objectGuid=objectGuid, text=text, messageId=message_id, buttonId=button_id)
    
    def reaction_message(self, object_guid:str, message_id:str, reaction:int) -> dict:
        return self.methods.actionOnMessageReaction(objectGuid=object_guid, messageId=message_id, reactionId=reaction, action="Add")
    
    def unreaction_message(self, object_guid:str, message_id:str, reaction:int) -> dict:
        return self.methods.actionOnMessageReaction(objectGuid=object_guid, messageId=message_id, reactionId=reaction, action="Remove")
    
    def pin_message(self, object_guid:str, message_id:str) -> dict:
        return self.methods.setPinMessage(objectGuid=object_guid, messageId=message_id, action="Pin")
    
    def unpin_message(self, object_guid:str, message_id:str) -> dict:
        return self.methods.setPinMessage(objectGuid=object_guid, messageId=message_id, action="Unpin")
    
    def resend_message(self, object_guid:str, message_id:str, to_object_guid:str, reply_to_message_id:str=None, text:str=None) -> dict:
        return self.methods.resendMessage(objectGuid=object_guid, messageId=message_id, toObjectGuid=to_object_guid, replyToMessageId=reply_to_message_id, text=text)
    
    def forward_messages(self, object_guid:str, message_ids:list, to_object_guid:str) -> dict:
        return self.methods.forwardMessages(objectGuid=object_guid, messageIds=message_ids, toObjectGuid=to_object_guid)
    
    def edit_message(self, object_guid, text, message_id=None) -> dict:
        return self.methods.editMessage(object_guid, text=text, messageId=message_id)
    
    def delete_messages(self, object_guid:str, message_ids:list, delete_for_all:bool=True) -> dict:
        return self.methods.deleteMessages(objectGuid=object_guid, messageIds=message_ids, deleteForAll=delete_for_all)
    
    def seen_messages(self, object_guid:str, min_id:str, max_id:str) -> dict:
        return self.methods.seenChatMessages(objectGuid=object_guid, minId=min_id, maxId=max_id)
    
    def get_messages_interval(self, object_guid:str, middle_message_id:str) -> dict:
        return self.methods.getMessagesInterval(objectGuid=object_guid, middleMessageId=middle_message_id)
    
    def get_messages(self, object_guid:str, max_message_id:str, filter_type:str=None, limit:int=50) -> dict:
        return self.methods.getMessages(objectGuid=object_guid, maxId=max_message_id, filterType=filter_type, limit=limit)
    
    def get_last_message(self, object_guid:str) -> dict:
        return self.methods.getChatInfo(objectGuid=object_guid)["chat"].get("last_message")
    
    def get_messages_updates(self, object_guid:str) -> dict:
        return self.methods.getMessagesUpdates(objectGuid=object_guid)
    
    def get_messages_by_id(self, object_guid:str, message_ids:list) -> dict:
        return self.methods.getMessagesById(objectGuid=object_guid, messageIds=message_ids)
    
    def get_message_share_url(self, object_guid:str, message_id:str) -> dict:
        return self.methods.getMessageShareUrl(objectGuid=object_guid, messageId=message_id)
    
    def click_message_url(self, object_guid:str, message_id:str, link_url:str) -> dict:
        return self.methods.clickMessageUrl(objectGuid=object_guid, messageId=message_id, linkUrl=link_url)
    
    def request_send_file(self, file_name:str, mime:str, size:str) -> dict:
        return self.methods.requestSendFile()
    
    # Contact methods

    def send_contact(self, object_guid:str, first_name:str, last_name:str, phone_number:str, user_guid:str, message_id:str=None) -> dict:
        return self.methods.sendContact(objectGuid=object_guid, firstName=first_name, lastName=last_name, phoneNumber=phone_number, userGuid=user_guid, messageId=message_id)
    
    def get_contacts(self, start_id:str=None) -> dict:
        return self.methods.getContacts(startId=start_id)
    
    def get_contacts_last_online(self, user_guids:list) -> dict:
        return self.methods.getContactsLastOnline(userGuids=user_guids)
    
    def add_address_book(self, phone:str, first_name:str, last_name:str) -> dict:
        return self.methods.addAddressBook(phone=phone, firstName=first_name, lastName=last_name)
    
    def delete_contact(self, object_guid:str) -> dict:
        return self.methods.deleteContact(objectGuid=object_guid)
    
    def get_contacts_updates(self) -> dict:
        return self.methods.getContactsUpdates()
    
    # Sticker methods

    def send_sticker(self, object_guid:str, emoji:str=None, message_id:str=None, sticker_data:dict=None) -> dict:
        return self.methods.sendSticker(objectGuid=object_guid, emoji=emoji, messageId=message_id, stickerData=sticker_data)
    
    def get_my_sticker_sets(self) -> dict:
        return self.methods.getMyStickerSets()
    
    def get_trend_sticker_sets(self, start_id:str=None) -> dict:
        return self.methods.getTrendStickerSets(startId=start_id)
    
    def search_stickers(self, search_text:str, start_id:str=None) -> dict:
        return self.methods.searchStickers(searchText=search_text, startId=start_id)
    
    def add_sticker(self, sticker_set_id:str) -> dict:
        return self.methods.actionOnStickerSet(stickerSetId=sticker_set_id, action="Add")
    
    def remove_sticker(self, sticker_set_id:str) -> dict:
        return self.methods.actionOnStickerSet(stickerSetId=sticker_set_id, action="Remove")
    
    def get_stickers_by_emoji(self, emoji:str) -> dict:
        return self.methods.getStickersByEmoji(emoji=emoji)
    
    def get_stickers_by_set_ids(self, sticker_set_ids:list) -> dict:
        return self.methods.getStickersBySetIDs(stickerSetIds=sticker_set_ids)
    
    # Gif methods

    def get_my_gif_set(self) -> dict:
        return self.methods.getMyGifSet()
    
    def add_gif(self, object_guid:str, message_id:str) -> dict:
        return self.methods.addToMyGifSet(objectGuid=object_guid, messageId=message_id)
    
    def remove_gif(self, file_id:str) -> dict:
        return self.methods.removeFromMyGifSet(fileId=file_id)
    
    # Poll methods

    def send_poll(self, object_guid:str, question:str, options:list, message_id:str=None, multiple_answers:bool=None, anonymous:bool=None, quiz:bool=None) -> dict:
        return self.methods.sendPoll(objectGuid=object_guid, question=question, options=options, messageId=message_id, multipleAnswers=multiple_answers, anonymous=anonymous, quiz=quiz)
    
    def vote_poll(self, poll_id:str, selection_index:int) -> dict:
        return self.methods.votePoll(pollId=poll_id, selectionIndex=selection_index)
    
    def get_poll_status(self, poll_id:str) -> dict:
        return self.methods.getPollStatus(pollId=poll_id)
    
    def get_poll_option_voters(self, poll_id:str, selection_index:str, start_id:str=None) -> dict:
        return self.methods.getPollOptionVoters(pollId=poll_id, selectionIndex=selection_index, startId=start_id)
    
    # Live methods
    
    def send_live(self, object_guid:str, thumb_inline_file:str and bytes) -> dict:
        return self.methods.sendLive(objectGuid=object_guid, thumbInline=thumb_inline_file)
    
    def add_live_comment(self, access_token:str, live_id:str, text:str) -> dict:
        return self.methods.addLiveComment(accessToken=access_token, liveId=live_id, text=text)
    
    def get_live_status(self, access_token:str, live_id:str) -> dict:
        return self.methods.getLiveStatus(accessToken=access_token, liveId=live_id)
    
    def getLiveComments(self, access_token:str, live_id:str) -> dict:
        return self.methods.getLiveComments(accessToken=access_token, liveId=live_id)
    
    def getLivePlayUrl(self, access_token:str, live_id:str) -> dict:
        return self.methods.getLivePlayUrl(accessToken=access_token, liveId=live_id)
    
    # Call methods

    def requestCall(self, object_guid:str, call_type:str) -> dict:
        return self.methods.requestCall(objectGuid=object_guid, callType=call_type)
    
    def discardCall(self, call_id:str, duration:int, reason:str) -> dict:
        return self.methods.discardCall(callId=call_id, duration=duration, reason=reason)
    
    # Setting methods
    
    def set_setting(self, show_my_last_online:bool=None, show_my_phone_number:bool=None, show_my_profile_photo:bool=None, link_forward_message:bool=None, can_join_chat_by:bool=None) -> dict:
        return self.methods.setSetting(showMyLastOnline=show_my_last_online, showMyPhoneNumber=show_my_phone_number, showMyProfilePhoto=show_my_profile_photo, linkForwardMessage=link_forward_message, canJoinChatBy=can_join_chat_by)
    
    def add_folder(self, folder_name:str, folder_id:str, exclude_chat_ids:list, exclude_chat_types:list, include_chat_ids:list, include_chat_types:list) -> dict:
        return self.methods.addFolder(folderName=folder_name, folderId=folder_id, excludeChatIds=exclude_chat_ids, excludeChatTypes=exclude_chat_types, includeChatIds=include_chat_ids, includeChatTypes=include_chat_types)
    
    def get_folders(self, last_state:str=None) -> dict:
        return self.methods.getFolders(lastState=last_state)
    
    def get_suggested_folders(self) -> dict:
        return self.methods.getSuggestedFolders()
    
    def delete_folder(self, folder_id:str) -> dict:
        return self.methods.deleteFolder(folderId=folder_id)
    
    def update_profile(self, first_name:str, last_name:str, bio:str, username:str) -> dict:
        return self.methods.updateProfile(firstName=first_name, lastname=last_name, bio=bio, username=username)
    
    def get_my_sessions(self) -> dict:
        return self.methods.getMySessions()
    
    def terminate_session(self, session_key:str) -> dict:
        return self.methods.terminateSession(sessionKey=session_key)
    
    def check_two_step_passcode(self, password:str) -> dict:
        return self.methods.checkTwoStepPasscode(password=password)
    
    def setup_two_step_verification(self, password:str, hint:str, recovery_email:str) -> dict:
        return self.methods.setupTwoStepVerification(password=password, hint=hint, recoveryEmail=recovery_email)
    
    def request_recovery_email(self, password:str, recovery_email:str) -> dict:
        return self.methods.requestRecoveryEmail(password=password, recoveryEmail=recovery_email)
    
    def verify_recovery_email(self, password:str, code:str) -> dict:
        return self.methods.verifyRecoveryEmail(password=password, code=code)
    
    def turn_off_two_step(self, password:str) -> dict:
        return self.methods.turnOffTwoStep(password=password)
    
    def change_password(self, password:str, new_password:str, new_hint:str) -> dict:
        return self.methods.changePassword(password=password, newPassword=new_password, newHint=new_hint)
    
    def get_two_passcode_status(self) -> dict:
        return self.methods.getTwoPasscodeStatus()
    
    def get_privacy_setting(self) -> dict:
        return self.methods.getPrivacySetting()
    
    def get_blocked_users(self) -> dict:
        return self.methods.getBlockedUsers()
    
    # Other methods

    def get_me(self) -> dict:
        return self.methods.getMe()
    
    def get_time(self) -> dict:
        return self.methods.getTime()
    
    def get_abs_objects(self, object_guids:list) -> dict:
        return self.methods.getAbsObjects(objectGuids=object_guids)
    
    def get_link_from_app_url(self, url:str) -> dict:
        return self.methods.getLinkFromAppUrl(url=url)
    
    def search_global_objects(self, search_text:str, filters:list=None) -> dict:
        return self.methods.searchGlobalObjects(searchText=search_text, filters=filters)
    
    def search_global_messages(self, search_text:str) -> dict:
        return self.methods.searchGlobalMessages(searchText=search_text)
    
    def check_join(self, object_guid:str, user_guid:str) -> bool:
        return self.methods.checkJoin(objectGuid=object_guid, userGuid=user_guid)
    
    def get_download_link(self, object_guid:str=None, message_id:str=None, file_inline:dict=None) -> dict:
        return self.methods.getDownloadLink(objectGuid=object_guid, messageId=message_id, fileInline=file_inline)
    
    def download(self, object_guid:str=None, message_id:str=None, save:bool=False, file_inline:dict=None) -> dict:
        return self.methods.download(objectGuid=object_guid, messageId=message_id, save=save, fileInline=file_inline)
    
    def on_message(self, filters:list=[]):
        from ..utils import UpdateWrapper

        for update in self.methods.handler():
            filters = list(map(lambda x: x.lower(), filters))
            message:UpdateWrapper = UpdateWrapper(update, self)

            if(not(message.chat_type.lower() in filters or message.message_type.lower() in filters)):
                yield message