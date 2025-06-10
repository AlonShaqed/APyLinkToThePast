from peewee import fn
from datetime import datetime

from models import *

OUTPUT_PATH = "thread_output.txt"

start_date = datetime(2015, 5, 6)
end_date = datetime(2015, 5, 8, 23, 59, 59)

query = (
    Message
    .select(
        Message.datetime,
        Thread.title,
        Message.datetime,
        Participant.name,
        Message.content,
        Media.path
    )
    .join(Thread, on=(Message.thread == Thread.thread_id))
    .switch(Message)  # switch context back to Message to join Participant
    .join(Participant, on=(Message.sender == Participant.participant_id))
    .switch(Message)  # switch context again to join Media
    .join(Media, JOIN.LEFT_OUTER, on=(Media.message == Message.message_id))
    .where(
        #(Thread.title == 'Title') #&
        (Message.datetime.between(start_date, end_date))
    )
    .order_by(Thread.title, Message.datetime)
)

with open(OUTPUT_PATH, "w") as log:
    thread_title = None
    for message in query:
        dt = datetime.fromisoformat(message.datetime)
        content = message.content
        if content is None:
            content = "[media missing]"
            try:
                content = "[media: %s]," %(message.media.path)
            except AttributeError:
                pass
        #end if-try
        if message.thread.title != thread_title:
            thread_title = message.thread.title
            log.write("@%s\n" %thread_title)
        #end if 
        log.write(
            dt.strftime("%Y-%m-%d %H:%M:%S") +"| "+ message.sender.name.split(" ")[0] +"> "+ content +"\n"
        )
    #end for
#end with