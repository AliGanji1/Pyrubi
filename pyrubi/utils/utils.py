
from random import choices, randint
from time import time
from re import finditer, sub
from base64 import b64encode
from io import BytesIO
from tempfile import NamedTemporaryFile
from mutagen import mp3, File
from filetype import guess
from os import system, chmod, remove
from .configs import Configs

class Utils:

    def randomTmpSession() -> str:
        return "".join(choices("abcdefghijklmnopqrstuvwxyz", k=32))
    
    def randomDeviceHash() -> str:
        return "".join(choices("0123456789", k=26))
    
    def randomRnd() -> str:
        return str(randint(-99999999, 99999999))
    
    def privateParse(private:str) -> str:
        if private:
            if not private.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                private = "-----BEGIN RSA PRIVATE KEY-----\\n" + private
            
            if not private.endswith("-----END RSA PRIVATE KEY-----"):
                private += "\\n-----END RSA PRIVATE KEY-----"

            return private.replace("\\n", "\n").strip()

    def getState() -> int:
        return int(time()) - 150
    
    def phoneNumberParse(phoneNumber:str) -> str:
        if str(phoneNumber).startswith("0"):
            phoneNumber = phoneNumber[1:]

        elif str(phoneNumber).startswith("98"):
            phoneNumber = phoneNumber[2:]

        elif str(phoneNumber).startswith("+98"):
            phoneNumber = phoneNumber[3:]

        return phoneNumber
    
    def getChatTypeByGuid(objectGuid:str) -> str:
        for chatType in [("u0", "User"), ("g0", "Group"), ("c0", "Channel"), ("s0", "Service"), ("b0", "Bot")]:
            if objectGuid.startswith(chatType[0]):
                return chatType[1]
    
    def isChatType(chatType:str) -> bool:
        chatType = chatType.lower()
        for type in ["user", "group", "channel", "service", "bot"]:
            if type == chatType:
                return True
            
    def isMessageType(messageType:str) -> bool:
        messageType = messageType.lower()
        for type in ["text", "image", "video", "gif", "video message", "voice", "music", "file"]:
            if type == messageType:
                return True

    
    def getChatTypeByLink(link:str) -> str:
        if "rubika.ir/joing" in link: return "Group"
        elif "rubika.ir/joinc" in link: return "Channel"
    
    def checkMetadata(text):
        if text is None:
            return [], ""

        real_text = sub(r"``|\*\*|__|~~|--|@@|##|", "", text)
        metadata = []
        conflict = 0
        mentionObjectIndex = 0
        result = []

        patterns = {
            "Mono": r"\`\`([^``]*)\`\`",
            "Bold": r"\*\*([^**]*)\*\*",
            "Italic": r"\_\_([^__]*)\_\_",
            "Strike": r"\~\~([^~~]*)\~\~",
            "Underline": r"\-\-([^__]*)\-\-",
            "Mention": r"\@\@([^@@]*)\@\@",
            "Spoiler": r"\#\#([^##]*)\#\#",
        }

        for style, pattern in patterns.items():
            for match in finditer(pattern, text):
                metadata.append((match.start(), len(match.group(1)), style))

        metadata.sort()

        for start, length, style in metadata:
            if not style == "Mention":
                result.append({
                    "type": style,
                    "from_index": start - conflict,
                    "length": length,
                })
                conflict += 4
            else:
                mentionObjects = [i.group(1) for i in finditer(r"\@\(([^(]*)\)", text)]
                mentionType = Utils.getChatTypeByGuid(objectGuid=mentionObjects[mentionObjectIndex]) or "Link"

                if mentionType == "Link":
                    result.append(
                        {
                            "from_index": start - conflict,
                            "length": length,
                            "link": {
                                "hyperlink_data": {
                                    "url": mentionObjects[mentionObjectIndex]
                                },
                                "type": "hyperlink",
                            },
                            "type": mentionType,
                        }
                    )
                else:
                    result.append(
                        {
                            "type": "MentionText",
                            "from_index": start - conflict,
                            "length": length,
                            "mention_text_object_guid": mentionObjects[mentionObjectIndex],
                            "mention_text_object_type": mentionType
                        }
                    )
                real_text = real_text.replace(f"({mentionObjects[mentionObjectIndex]})", "")
                conflict += 6 + len(mentionObjects[mentionObjectIndex])
                mentionObjectIndex += 1
                
        return result, real_text
    
    def checkLink(url:str) -> dict:
        for i in ["http:/", "https://"]:
            if url.startswith(i): return True

    def getMimeFromByte(bytes:bytes) -> str:
        mime = guess(bytes)
        return "pyrubi" if mime is None else mime.extension
    
    def generateFileName(mime:str) -> str:
        return "Pyrubi Library {}.{}".format(randint(1, 1000), mime)
    
    def getImageSize(bytes:bytes) -> str:
        try:
            from PIL import Image
        except ImportError:
            system("pip install pillow")
            from PIL import Image

        width, height = Image.open(BytesIO(bytes)).size
        return width , height
    
    def getImageThumbnail(bytes:bytes) -> str:
        try:
            from PIL import Image
        except ImportError:
            system("pip install pillow")
            from PIL import Image
            
        image = Image.open(BytesIO(bytes))
        width, height = image.size
        if height > width:
            new_height = 40
            new_width  = round(new_height * width / height)
        else:
            new_width = 40
            new_height = round(new_width * height / width)
        image = image.resize((new_width, new_height), Image.LANCZOS)
        changed_image = BytesIO()
        image.save(changed_image, format="PNG")
        return b64encode(changed_image.getvalue()).decode("UTF-8")
    
    def getVideoData(bytes:bytes) -> list:
        try:
            from moviepy.editor import VideoFileClip

            with NamedTemporaryFile(delete=False, dir=".") as temp_video:
                temp_video.write(bytes)
                temp_path = temp_video.name

            chmod(temp_path, 0o777)

            try:
                from PIL import Image
            except ImportError:
                system("pip install pillow")
                from PIL import Image

            with VideoFileClip(temp_path) as clip:
                duration = clip.duration
                resolution = clip.size
                thumbnail = clip.get_frame(0)
                thumbnail_image = Image.fromarray(thumbnail)
                thumbnail_buffer = BytesIO()
                thumbnail_image.save(thumbnail_buffer, format="JPEG")
                thumbnail_b64 = b64encode(thumbnail_buffer.getvalue()).decode("UTF-8")
                clip.close()

            remove(temp_path)

            return thumbnail_b64, resolution, duration
        except ImportError:
            print(Colors.YELLOW + "Can't get video data! Please install the moviepy library by following command:\npip install moviepy" + Colors.RESET)
            return Configs.defaultTumbInline, [900, 720], 1
        except:
            return Configs.defaultTumbInline, [900, 720], 1
        
    def getVoiceDuration(bytes:bytes) -> int:
        file = BytesIO()
        file.write(bytes)
        file.seek(0)
        return mp3.MP3(file).info.length
    
    def getMusicArtist(bytes:bytes) -> str:
        try:
            audio = File(BytesIO(bytes), easy=True)

            if audio and "artist" in audio:
                return audio["artist"][0]
            
            return "pyrubi"
        except Exception:
            return "pyrubi"
        
class Colors:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_RESET = "\033[49m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"