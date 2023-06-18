from random import randint
from requests import get
from base64 import b64encode as b64e
from PIL import Image
from io import BytesIO
from mutagen.mp3 import MP3
from tinytag import TinyTag
from re import finditer

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
        if text is None:
            return [], text

        real_text = text.replace('``', '').replace('**', '').replace('__', '').replace('~~', '').replace('--', '').replace('@@', '')
        metadata = []
        conflict = 0
        mention_object_index = 0
        result = []

        for i in [(i.start(), len(i.group(1)), "mono") for i in finditer(r'\`\`([^``]*)\`\`', text)]:
            metadata.append(i)

        for i in [(i.start(), len(i.group(1)), "bold") for i in finditer(r'\*\*([^**]*)\*\*', text)]:
            metadata.append(i)

        for i in [(i.start(), len(i.group(1)), "italic") for i in finditer(r'\_\_([^__]*)\_\_', text)]:
            metadata.append(i)

        for i in [(i.start(), len(i.group(1)), "strike") for i in finditer(r'\~\~([^~~]*)\~\~', text)]:
            metadata.append(i)

        for i in [(i.start(), len(i.group(1)), "underline") for i in finditer(r'\-\-([^__]*)\-\-', text)]:
            metadata.append(i)

        for i in [(i.start(1) - 2, len(i.group(1)), "mention") for i in finditer(r'\@\@([^@@]*)\@\@', text)]:
            metadata.append(i)

        metadata.sort()
        for i in metadata:
            if i[2] == 'mono':
                result.append(
                    {
                        'type': 'Mono',
                        'from_index': i[0] - conflict,
                        'length': i[1]
                    }
                )
                conflict += 4

            elif i[2] == 'bold':
                result.append(
                    {
                        'type': 'Bold',
                        'from_index': i[0] - conflict,
                        'length': i[1]
                    }
                )
                conflict += 4

            elif i[2] == 'italic':
                result.append(
                    {
                        'type': 'Italic',
                        'from_index': i[0] - conflict,
                        'length': i[1]
                    }
                )
                conflict += 4

            elif i[2] == 'strike':
                result.append(
                    {
                        'type': 'Strike',
                        'from_index': i[0] - conflict,
                        'length': i[1]
                    }
                )
                conflict += 4

            elif i[2] == 'underline':
                result.append(
                    {
                        'type': 'Underline',
                        'from_index': i[0] - conflict,
                        'length': i[1]
                    }
                )
                conflict += 4

            else:
                mention_objects = [i.group(1) for i in finditer(r'\@\(([^(]*)\)', text)]
                mention_type = 'Link'
                if mention_objects[mention_object_index].startswith('u'): mention_type = 'User'
                elif mention_objects[mention_object_index].startswith('g'): mention_type = 'Group'
                elif mention_objects[mention_object_index].startswith('c'): mention_type = 'Channel'
                elif mention_objects[mention_object_index].startswith('b'): mention_type = 'Bot'
                elif mention_objects[mention_object_index].startswith('s'): mention_type = 'Service'
                if mention_type == 'Link':
                    result.append(
                        {
                            'from_index': i[0] - conflict,
                            'length': i[1],
                            'link': {
                                'hyperlink_data': {
                                    "url": mention_objects[mention_object_index]
                                },
                                'type': 'hyperlink',
                            },
                            'type': mention_type,
                        }
                    )

                else:
                    result.append(
                        {
                            'type': 'MentionText',
                            'from_index': i[0] - conflict,
                            'length': i[1],
                            'mention_text_object_guid': mention_objects[mention_object_index],
                            'mention_text_object_type': mention_type
                        }
                    )
                real_text = real_text.replace(f'({mention_objects[mention_object_index]})', '')
                conflict += 6 + len(mention_objects[mention_object_index])
                mention_object_index += 1
                
        return result, real_text

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