
from random import choices, randint
from time import time
from re import finditer, sub
from base64 import b64encode
from io import BytesIO
from tempfile import TemporaryFile
from mutagen import mp3, File
from filetype import guess
from os import system

class Tools:

    def randomTmpSession() -> str:
        return "".join(choices("abcdefghijklmnopqrstuvwxyz", k=32))
    
    def randomDeviceHash() -> str:
        return "".join(choices("0123456789", k=26))
    
    def randomRnd() -> str:
        return str(randint(-99999999, 99999999))
    
    def privateParse(private:str) -> str:
        if not private.startswith("-----BEGIN RSA PRIVATE KEY-----\n"):
            private = "-----BEGIN RSA PRIVATE KEY-----\n" + private
        
        if not private.endswith("\n-----END RSA PRIVATE KEY-----"):
            private += "\n-----END RSA PRIVATE KEY-----"

        return private

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
            if objectGuid.startswith(chatType[0]): return chatType[1]
        return ""
    
    def getChatTypeByLink(link:str) -> str:
        if "rubika.ir/joing" in link: return "Group"
        elif "rubika.ir/joinc" in link: return "Channel"
    
    def checkMetadata(text):
        if text is None:
            return [], ""

        real_text = sub(r'``|\*\*|__|~~|--|@@|##|', '', text)
        metadata = []
        conflict = 0
        mentionObjectIndex = 0
        result = []

        patterns = {
            "Mono": r'\`\`([^``]*)\`\`',
            "Bold": r'\*\*([^**]*)\*\*',
            "Italic": r'\_\_([^__]*)\_\_',
            "Strike": r'\~\~([^~~]*)\~\~',
            "Underline": r'\-\-([^__]*)\-\-',
            "Mention": r'\@\@([^@@]*)\@\@',
            "Spoiler": r'\#\#([^##]*)\#\#',
        }

        for style, pattern in patterns.items():
            for match in finditer(pattern, text):
                metadata.append((match.start(), len(match.group(1)), style))

        metadata.sort()

        for start, length, style in metadata:
            if not style == "Mention":
                result.append({
                    'type': style,
                    'from_index': start - conflict,
                    'length': length,
                })
                conflict += 4
            else:
                mentionObjects = [i.group(1) for i in finditer(r'\@\(([^(]*)\)', text)]
                mentionType = Tools.getChatTypeByGuid(objectGuid=mentionObjects[mentionObjectIndex]) or 'Link'

                if mentionType == 'Link':
                    result.append(
                        {
                            'from_index': start - conflict,
                            'length': length,
                            'link': {
                                'hyperlink_data': {
                                    "url": mentionObjects[mentionObjectIndex]
                                },
                                'type': 'hyperlink',
                            },
                            'type': mentionType,
                        }
                    )
                else:
                    result.append(
                        {
                            'type': 'MentionText',
                            'from_index': start - conflict,
                            'length': length,
                            'mention_text_object_guid': mentionObjects[mentionObjectIndex],
                            'mention_text_object_type': mentionType
                        }
                    )
                real_text = real_text.replace(f'({mentionObjects[mentionObjectIndex]})', '')
                conflict += 6 + len(mentionObjects[mentionObjectIndex])
                mentionObjectIndex += 1
                
        return result, real_text
    
    def checkLink(url:str) -> dict:
        for i in ["http:/", "https://"]:
            if url.startswith(i): return True

    def getMimeFromByte(bytes:bytes) -> str:
        return (guess(bytes).extension or "pyrubi")
    
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
        image.save(changed_image, format='PNG')
        return b64encode(changed_image.getvalue()).decode('UTF-8')
    
    def getVideoData(bytes:bytes) -> list:
        try:
            try:
                import cv2
            except ImportError:
                system("pip install opencv-python")
                import cv2

            try:
                import numpy
            except ImportError:
                system("pip install numpy")
                import numpy

            with TemporaryFile(mode='wb+') as file:
                file.write(bytes)
                cap = cv2.VideoCapture(file.name)

                if not cap.isOpened():
                    return None, [1000, 1000], 1

                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
                frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                video_duration = int(frame_count / frame_rate) * 1000

                ret, thumbnail_frame = cap.read()
                if not ret:
                    return None, [1000, 1000], 1
                
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 1]
                _, buffer = cv2.imencode(".jpg", thumbnail_frame, encode_param)
                thumbnail_bytes = numpy.array(buffer).tobytes()

                cap.release()

                return b64encode(thumbnail_bytes).decode('UTF-8'), [frame_width, frame_height], video_duration
        except:
            return None, [1000, 1000], 1
        
    def getVoiceDuration(bytes:bytes) -> int:
        file = BytesIO()
        file.write(bytes)
        file.seek(0)
        print(mp3.MP3(file).info.length)
        return mp3.MP3(file).info.length
    
    def getMusicArtist(bytes:bytes) -> str:
        try:
            audio = File(BytesIO(bytes), easy=True)

            if audio and 'artist' in audio:
                return audio['artist'][0]
            
            return "pyrubi"
        except Exception:
            return "pyrubi"