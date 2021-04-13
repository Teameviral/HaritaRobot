import os
from Harita import tbot, CMD_HELP
from Harita.modules.sql import afk_sql as sql
from telethon.tl.functions.users import GetFullUserRequest
from telethon import types
from telethon.tl import functions
from Harita.events import register
from telethon import events
import random
options = [
                "{} is here!",
                "{} is back!",
                "{} is now in the chat!",
                "{} is awake!",
                "{} is back online!",
                "{} is finally here!",
                "Welcome back! {}",
                "Where is {}?\nIn the chat!",
                "Pro {}, is back alive!",
            ]
nub = random.choice(options)

@register(pattern=r"(.*?)")
async def _(event):
    sender = await event.get_sender()
    if event.text.startswith("/afk"):
     cmd = event.text[len("/afk ") :]
     if cmd is not None:
        reason = cmd
     else:
        reason = ""
     fname = sender.first_name   
     start_time = fname
     sql.set_afk(sender.id, reason, start_time)
     await event.reply(
           "{} is now AFK!".format(fname),
           parse_mode="markdown")
     return
    if event.text.startswith("Brb"):
     cmd = event.text[len("Brb ") :]
     if cmd is not None:
        reason = cmd
     else:
        reason = ""
     fname = sender.first_name
     start_time = fname
     sql.set_afk(sender.id, reason, start_time)
     await event.reply(
           "{} is now AFK!".format(fname),
           parse_mode="markdown")
     return
    if event.text.startswith("brb"):
     cmd = event.text[len("brb ") :]
     if cmd is not None:
        reason = cmd
     else:
        reason = ""
     fname = sender.first_name
     start_time = fname
     sql.set_afk(sender.id, reason, start_time)
     await event.reply(
           "{} is now AFK!".format(fname),
           parse_mode="markdown")
     return

    if sql.is_afk(sender.id):
       res = sql.rm_afk(sender.id)
       if res:
          firstname = sender.first_name
          loda = nub.format(firstname)
          await event.reply(loda, parse_mode="markdown")


@tbot.on(events.NewMessage(pattern=None))
async def _(event):
    sender = event.sender_id
    msg = str(event.text)
    global let
    global userid
    userid = None
    let = None
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        userid = reply.sender_id
    else:
        try:
            for (ent, txt) in event.get_entities_text():
                if ent.offset != 0:
                    break
                if isinstance(ent, types.MessageEntityMention):
                    pass
                elif isinstance(ent, types.MessageEntityMentionName):
                    pass
                else:
                    return
                c = txt
                a = c.split()[0]
                let = await tbot.get_input_entity(a)
                userid = let.user_id
        except Exception:
            return

    if not userid:
        return
    if sender == userid:
        return

    if event.is_group:
        pass
    else:
        return

    if sql.is_afk(userid):
        user = sql.check_afk_status(userid)
        if not user.reason:
            final = user.start_time
            res = "{} is AFK!".format(final)
            await event.reply(res, parse_mode="markdown")
        else:
            final = user.start_time
            res = "{} is AFK!\n**Reason:** {}".format(
                final, user.reason
            )
            await event.reply(res, parse_mode="markdown")
    userid = ""
    let = ""


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /afk <reason>: mark yourself as AFK(Away From Keyboard)
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
