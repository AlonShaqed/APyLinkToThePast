import glob
import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from models import *

TIMEZONE = "America/Denver"
CODE = "Latin-1"

def datetime_from_timestamp_ms(ms, tz_str):
    return datetime.fromtimestamp(ms / 1000, ZoneInfo(tz_str))
def decode_to_unicode(text, code):
    return text.encode(code).decode("utf8")
#end def

db.connect()
db.create_tables([Message, Participant, Thread, Media])
ROOT_PATH = ROOT_PATH = "your_facebook_activity\messages"
for file in glob.glob(os.path.join(ROOT_PATH, "**", "*.json"), recursive=True):
    if os.path.dirname(file) != ROOT_PATH:
        people = dict()
        with open(file, "r") as json_data:
            data = json.load(json_data)
            thread_title = decode_to_unicode(data["title"], CODE)
            thread = Thread(
                title=thread_title, 
                path=data["thread_path"]
            )
            thread.save()
            for p_raw in data["participants"]:
                name = decode_to_unicode(p_raw["name"], CODE)
                participant, created = Participant.get_or_create(name=name)
                if created:
                    participant.save()
                people[participant.name] = participant
            #end for-if
            for m_raw in data["messages"]:
                keys = m_raw.keys()
                sender_name = decode_to_unicode(m_raw["sender_name"], CODE)
                message = Message(
                    thread=thread,
                    timestamp=m_raw["timestamp_ms"]/ 1000,
                    datetime=datetime_from_timestamp_ms(m_raw["timestamp_ms"], TIMEZONE)
                )
                if sender_name not in people.keys():
                    participant, created = Participant.get_or_create(name=sender_name)
                    people[participant.name] = participant
                message.sender=people[sender_name]
                message.save()
                if "content" in keys:
                    unicode_content = decode_to_unicode(m_raw["content"], CODE)
                    message.content = unicode_content
                    message.save()
                elif Media.TYPES.STICKER in keys:
                    media = Media(
                        type = Media.TYPES.STICKER,
                        path = m_raw[Media.TYPES.STICKER]["uri"],
                        message = message
                    )
                    media.save()
                else:
                    for t in Media.types():
                        if t in keys:
                            for e in m_raw[t]:
                                media = Media(
                                type = t,
                                path = e["uri"],
                                timestamp = e["creation_timestamp"],
                                message = message
                            )
                            media.save()
                        #end if
                    #end for
                #end if
            #end for "messages"
        #end with
    #end if
#end for