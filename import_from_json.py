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


ROOT_PATH = "/home/alonso/Downloads/your_instagram_activity/messages"

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
            existing_messages = set()
            for m_raw in data["messages"]:
                keys = m_raw.keys()
                # checking for dups
                media_paths = list()
                sender_name = decode_to_unicode(m_raw["sender_name"], CODE)
                timestamp = m_raw["timestamp_ms"]/ 1000
                if "content" in keys:
                    unicode_content = decode_to_unicode(m_raw["content"], CODE)
                else:
                    unicode_content = None
                    for t in Media.types():
                        if t in keys:
                            media_paths = [m.get("uri") for m in m_raw[t]]
                #end if-for-if
                exist_key = (sender_name, timestamp, unicode_content, tuple(sorted(media_paths)))
                if exist_key in existing_messages:
                    continue
                existing_messages.add(exist_key)

                message = Message(
                    thread=thread,
                    timestamp=timestamp,
                    datetime=datetime_from_timestamp_ms(m_raw["timestamp_ms"], TIMEZONE)
                )
                message.content = unicode_content
                if sender_name not in people.keys():
                    participant, created = Participant.get_or_create(name=sender_name)
                    people[participant.name] = participant
                message.sender=people[sender_name]
                message.save()
                
                if Media.TYPES.STICKER in keys:
                    media = Media(
                        type = Media.TYPES.STICKER,
                        path = m_raw[Media.TYPES.STICKER]["uri"],
                        message = message
                    )
                    media.save()
                elif Media.TYPES.STORY in keys:
                    if "link" in m_raw[Media.TYPES.STORY].keys():
                        path_ = ["link"]
                    else:
                        path_ = "missing shared story"
                    media = Media(
                        type = Media.TYPES.STORY,
                        path = path_,
                        message = message
                    )
                    media.save()
                else:
                    for t in Media.types():
                        if t in keys:
                            for e in m_raw[t]:
                                if "creation_timestamp" in e.keys():
                                    timestamp = e["creation_timestamp"]
                                else:
                                    timestamp = message.timestamp
                                media = Media(
                                type = t,
                                path = e["uri"],
                                timestamp = timestamp,
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
