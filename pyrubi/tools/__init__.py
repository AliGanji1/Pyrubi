from random import randint
from requests import get
from base64 import b64encode as b64e
from PIL import Image
from io import BytesIO
from mutagen.mp3 import MP3
from tinytag import TinyTag
from re import findall

class tools:

    def get_file_name(file):
        return file if not 'http' in file else f'pyrubi {randint(1, 100)}.{format}'

    def get_file_size(file):
        return str(len(get(file).content if 'http' in file else open(file,'rb').read()))

    def get_thumbnail(image_bytes):
        image = Image.open(BytesIO(image_bytes))
        width, height = image.size
        if height > width:
            new_height = 40
            new_width  = round(new_height * width / height)
        else:
            new_width = 40
            new_height = round(new_width * height / width)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)
        changed_image = BytesIO()
        image.save(changed_image, format='PNG')
        return b64e(changed_image.getvalue())

    def get_image_size(image_bytes):
        width, height = Image.open(BytesIO(image_bytes)).size
        return width , height

    def get_voice_duration(voice_bytes):
        file = BytesIO()
        file.write(voice_bytes)
        file.seek(0)
        return MP3(file).info.length

    def get_video_duration(video):
        return round(TinyTag.get(video).duration * 1000)

    def get_music_artist(music):
        return str(TinyTag.get(music).artist)

    def get_mime_from_url(url):
        if '.' in url:
            mime = url.split('.')[-1]
            if len(mime) <= 4:
                return mime
        return 'pyrubi'

    def check_metadata(text):
        g = 0
        if text is None:
            return ([], text)
        results = []
        real_text = text.replace('**', '').replace('__', '').replace('``', '').replace('@@', '')
        bolds = findall(r'\*\*(.*?)\*\*' , text)
        italics = findall(r'\_\_(.*?)\_\_' , text)
        monos = findall(r'\`\`(.*?)\`\`' , text)
        mentions = findall(r'\@\@(.*?)\@\@' , text)
        mention_ids = findall(r'\@\@\((.*?)\)' , text)
        for bold_index , bold_word in zip([real_text.index(i) for i in bolds] , bolds):
            results.append(
                {
                    'from_index' : bold_index,
                    'length' : len(bold_word),
                    'type' : 'Bold'
                }
            )
        for italic_index , italic_word in zip([real_text.index(i) for i in italics] , italics):
            results.append(
                {
                    'from_index' : italic_index,
                    'length' : len(italic_word),
                    'type' : 'Italic'
                }
            )
        for mono_Index , mono_word in zip([real_text.index(i) for i in monos] , monos):
            results.append(
                {
                    'from_index' : mono_Index,
                    'length' : len(mono_word),
                    'type' : 'Mono'
                }
            )
        for mention_index , mention_word in zip([real_text.index(i) for i in mentions] , mentions):
            results.append(
                {
                    'type': 'MentionText',
                    'from_index': mention_index,
                    'length': len(mention_word),
                    'mention_text_object_guid': mention_ids[g] if '@(' in text else '@'
                }
            )
            if '@(' in text:
                real_text = real_text.replace(f'({mention_ids[g]})', '') 
            g += 1
        return (results, real_text)

    def get_chat_type_by_id(chat_id):
        if chat_id.startswith('u'): data = 'User'
        elif chat_id.startswith('g'): data = 'Group'
        elif chat_id.startswith('c'): data = 'Channel'
        elif chat_id.startswith('b'): data = 'Bot'
        elif chat_id.startswith('s'): data = 'Service'
        return data

    def parse_phone_number(phone_number):
        if str(phone_number).startswith('0'):
            phone_number = phone_number[1:]
        elif str(phone_number).startswith('98'):
            phone_number = phone_number[2:]
        elif str(phone_number).startswith('+98'):
            phone_number = phone_number[3:]
        return phone_number