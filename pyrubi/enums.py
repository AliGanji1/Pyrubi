class SetAdminAccessList:
    set_admin:str = "SetAdmin"
    ban_member:str = "BanMember"
    change_info:str = "ChangeInfo"
    pin_messages:str = "PinMessages"
    delete_messages:str = "DeleteGlobalAllMessages"
    edit_messages:str = "EditMessages"
    set_join_link:str = "SetJoinLink"
    set_member_access:str = "SetMemberAccess"
    delete_global_all_messages:str = "DeleteGlobalAllMessages"

class SetGroupDefaultAccessList:
    send_messages:str = "SendMessages"
    add_member:str = "AddMember"
    view_admins:str = "ViewAdmins"
    view_members:str = "ViewMembers"

class ChatActivities:
    typing:str = "Typing"
    recording:str = "Recording"
    uploading:str = "Uploading"

class Filters:
    user:str = "User"
    group:str = "Group"
    channel:str = "Channel"
    bot:str = "Bot"
    service:str = "Service"
    media:str = "Media"
    file:str = "File"
    image:str = "Image"
    video:str = "Video"
    gif:str = "Gif"
    music:str = "Music"
    voice:str = "Voice"
    sticker:str = "Sticker"