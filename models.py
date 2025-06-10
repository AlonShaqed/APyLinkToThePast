from enum import Enum

from peewee import *

db = SqliteDatabase("fb_messages_data.db")

class BaseModel(Model):
    class Meta:
        database = db
#end class-class

class Thread(BaseModel):
    thread_id = AutoField()
    title = TextField()
    path = CharField()
class Participant(BaseModel):
    participant_id = AutoField()
    name = TextField()
class Message(BaseModel):
    message_id = AutoField()
    thread = ForeignKeyField(Thread, backref="messages")
    sender = ForeignKeyField(Participant, backref="messages")
    content = TextField(null=True)
    timestamp = TimestampField()
    datetime = DateTimeField()
class Media(BaseModel):
    class TYPES:
        AUDIO = "audio_files"
        FILES = "files"
        GIFS = "gifs" # puede no tener timestamp
        PHOTOS = "photos"
        VIDEOS = "videos"
        STICKER = "sticker"
    #end class
    def types():
        return [
            Media.TYPES.AUDIO,
            Media.TYPES.FILES,
            Media.TYPES.PHOTOS,
            Media.TYPES.VIDEOS,
            Media.TYPES.STICKER,
        ]
    #end def
    media_id = AutoField()
    type = CharField()
    path = CharField()
    timestamp = TimestampField(null=True)
    message = ForeignKeyField(Message, backref="media")
#end class