from Evie import tbot, OWNER_ID, DEV_USERS
from Evie import MONGO_DB_URI, BOT_ID, GBAN_LOGS
from pymongo import MongoClient
from Evie.function import is_admin, sudo
from telethon import events
from Evie.events import register
from telethon.tl.functions.users import GetFullUserRequest
#RoseLoverX
from Evie.modules.sql.chats_sql import get_all_chat_id

from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest
BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["evie"]
gbanned = db.gban
gmuted = db.gmute #RoseloverX

def get_reason(id):
    return gbanned.find_one({"user": id})

GBAN_LOGS = int(GBAN_LOGS)
RoseLoverX = "e async def lamda -f"


@register(pattern="^/gban ?(.*)")
async def gban(event):
 sender = event.sender.first_name
 group = event.chat.title
 if event.fwd_from:
        return
 if event.sender_id == OWNER_ID:
  pass
 elif event.sender_id in DEV_USERS:
  pass
 elif sudo(id):
  pass
 else:
  return
 input = event.pattern_match.group(1)
 if input:
   arg = input.split(" ", 1)
 if not event.reply_to_msg_id:
  if len(arg) == 2:
    iid = arg[0]
    reason = arg[1]
  else:
    iid = arg[0]
    reason = "None"
  if not iid.isnumeric():
   username = iid.replace("@", "")
   entity = await tbot.get_input_entity(iid)
   try:
     r_sender_id = entity.user_id
   except Exception:
        await event.reply("Couldn't fetch that user.")
        return
  else:
   r_sender_id = int(iid)
  try:
   replied_user = await tbot(GetFullUserRequest(r_sender_id))
   fname = replied_user.user.first_name
  except Exception:
   fname = "User"
 else:
   reply_message = await event.get_reply_message()
   iid = reply_message.sender_id
   username = reply_message.sender.username
   fname = reply_message.sender.first_name
   if input:
     reason = input
   else:
     reason = "None"
   r_sender_id = iid
 if r_sender_id == OWNER_ID:
        await event.reply(f"Char Chavanni godhe pe\ngey Mere Lode Pe!.")
        return
 elif r_sender_id in DEV_USERS:
        await event.reply("This Person is a Dev, Sorry!")
        return
 elif r_sender_id == BOT_ID:
        await event.reply("Another one bits the dust! banned a betichod!")
        return
 elif sudo(r_sender_id):
        await event.reply("Yeah Nibba that's a Sudo User🤨")
        return
 chats = gbanned.find({})
 for c in chats:
      if r_sender_id == c["user"]:
          to_check = get_reason(id=r_sender_id)
          gbanned.update_one(
                {
                    "_id": to_check["_id"],
                    "bannerid": to_check["bannerid"],
                    "user": to_check["user"],
                    "reason": to_check["reason"],
                },
                {"$set": {"reason": reason, "bannerid": event.sender_id}},
            )
          await event.reply(
                "This user is already gbanned, I am updating the reason of the gban with your reason."
            )
          await tbot.send_message(GBAN_LOGS, "**Global Ban**\n#UPDATE\n**Originated From: {} {}**\n\n**Sudo Admin:** [{}](tg://user?id={})\n**User:** [{}](tg://user?id={})\n**ID:** `{}`\n**New Reason:** {}".format(
                                   group, event.chat_id, sender, event.sender_id, fname, r_sender_id, r_sender_id, reason))       
          return
 gbanned.insert_one(
        {"bannerid": event.sender_id, "user": r_sender_id, "reason": reason}
    )
 k = await event.reply("⚡Snaps the BanHammer⚡")
 cheater = get_all_chat_id()
 done = 0
 for i in cheater:
   try:
       chat = int(i.chat_id)
       await tbot(
                    EditBannedRequest(chat, f"{username}", BANNED_RIGHTS)
               )
       done = done + 1
   except Exception:
       pass
 await tbot.send_message(GBAN_LOGS, "**Global Ban**\n#NEW\n**Originated From: {} {}**\n\n**Sudo Admin:** [{}](tg://user?id={})\n**User:** [{}](tg://user?id={})\n**ID:** `{}`\n**Reason:** {}".format(
                                   group, event.chat_id, sender, event.sender_id, fname, r_sender_id, r_sender_id, reason))       
 await event.reply(f"GlobalBan Completed\n**Time Taken**: Soon!")

@register(pattern="^/ungban ?(.*)")
async def ugban(event):
 sender = event.sender.first_name
 group = event.chat.title
 id = event.sender_id
 if event.fwd_from:
        return
 if event.sender_id == OWNER_ID:
  pass
 elif event.sender_id in DEV_USERS:
  pass
 elif sudo(id):
  pass
 else:
  return
 input = event.pattern_match.group(1)
 if input:
   arg = input.split(" ", 1)
 if not event.reply_to_msg_id:
  if len(arg) == 2:
    iid = arg[0]
    reason = arg[1]
  else:
    iid = arg[0]
    reason = None
  if not iid.isnumeric():
   username = iid.replace("@", "")
   entity = await tbot.get_input_entity(iid)
   try:
     r_sender_id = entity.user_id
   except Exception:
        await event.reply("Couldn't fetch that user.")
        return
  else:
   r_sender_id = int(iid)
  try:
   replied_user = await tbot(GetFullUserRequest(r_sender_id))
   fname = replied_user.user.first_name
  except Exception:
   fname = "User"
 else:
   reply_message = await event.get_reply_message()
   iid = reply_message.sender_id
   username = reply_message.sender.username
   fname = reply_message.sender.first_name
   if input:
     reason = input
   else:
     reason = None
   r_sender_id = iid
 if r_sender_id == OWNER_ID:
        await event.reply(f"Yeah FuckOff!")
        return
 elif r_sender_id in DEV_USERS:
        await event.reply("No!")
        return
 elif r_sender_id == BOT_ID:
        await event.reply("Who Dafaq Made You Sudo?!")
        return
 elif sudo(r_sender_id):
        await event.reply("Yeah Nibba that's a Sudo User🤨")
        return
 chats = gbanned.find({})
 for c in chats:
        if r_sender_id == c["user"]:
            to_check = get_reason(id=r_sender_id)
            gbanned.delete_one({"user": r_sender_id})
            await event.reply("Globally Pardoned This User.!🏳️")
            await tbot.send_message(GBAN_LOGS, "**Global Unban**\n#UNGBAN\n**Originated From: {} {}**\n\n**Sudo Admin:** [{}](tg://user?id={})\n**User:** [{}](tg://user?id={})\n**ID:** `{}`\n**Reason:** {}".format(
                                   group, event.chat_id, sender, event.sender_id, fname, r_sender_id, r_sender_id, reason))
            return
 await event.reply("Yeah that user is not in my Gbanned list.!?")

@register(pattern="^/gmute ?(.*)")
async def gban(event):
 sender = event.sender.first_name
 group = event.chat.title
 if event.fwd_from:
        return
 if event.sender_id == OWNER_ID:
  pass
 elif event.sender_id in DEV_USERS:
  pass
 elif sudo(id):
  pass
 else:
  return
 input = event.pattern_match.group(1)
 if input:
   arg = input.split(" ", 1)
 if not event.reply_to_msg_id:
  if len(arg) == 2:
    iid = arg[0]
    reason = arg[1]
  else:
    iid = arg[0]
    reason = "None"
  if not iid.isnumeric():
   username = iid.replace("@", "")
   entity = await tbot.get_input_entity(iid)
   try:
     r_sender_id = entity.user_id
   except Exception:
        await event.reply("Couldn't fetch that user.")
        return
  else:
   r_sender_id = int(iid)
  try:
   replied_user = await tbot(GetFullUserRequest(r_sender_id))
   fname = replied_user.user.first_name
  except Exception:
   fname = "User"
 else:
   reply_message = await event.get_reply_message()
   iid = reply_message.sender_id
   username = reply_message.sender.username
   fname = reply_message.sender.first_name
   if input:
     reason = input
   else:
     reason = "None"
   r_sender_id = iid
 if r_sender_id == OWNER_ID:
        await event.reply(f"Char Chavanni godhe pe\ngey Mere Lode Pe!.")
        return
 elif r_sender_id in DEV_USERS:
        await event.reply("This Person is a Dev, Sorry!")
        return
 elif r_sender_id == BOT_ID:
        await event.reply("Another one bits the dust! banned a betichod!")
        return
 elif sudo(r_sender_id):
        await event.reply("Yeah Nibba that's a Sudo User🤨")
        return
 chats = gmuted.find({})
 for c in chats:
      if r_sender_id == c["user"]:
          to_check = get_reason(id=r_sender_id)
          gmuted.update_one(
                {
                    "_id": to_check["_id"],
                    "bannerid": to_check["bannerid"],
                    "user": to_check["user"],
                    "reason": to_check["reason"],
                },
                {"$set": {"reason": reason, "bannerid": event.sender_id}},
            )
          await event.reply(
                "This user is already gmuted, I am updating the reason of the gmute with your reason."
            )
          await tbot.send_message(GBAN_LOGS, "**Global Mute**\n#UPDATE\n**ID:** `{}`".format(r_sender_id))

 gmuted.insert_one(
        {"bannerid": event.sender_id, "user": r_sender_id, "reason": reason}
    )
 await tbot.send_message(GBAN_LOGS, "**Global Mute**\n**Sudo Admin:** {}\n**User:** {}\n**ID:** `{}`".format(sender, fname, r_sender_id))
 await event.reply("Sucessfully Added user to Gmute List!")
 
@register(pattern="^/ungmute ?(.*)")
async def ugban(event):
 sender = event.sender.first_name
 group = event.chat.title
 id = event.sender_id
 if event.fwd_from:
        return
 if event.sender_id == OWNER_ID:
  pass
 elif event.sender_id in DEV_USERS:
  pass
 elif sudo(id):
  pass
 else:
  return
 input = event.pattern_match.group(1)
 if input:
   arg = input.split(" ", 1)
 if not event.reply_to_msg_id:
  if len(arg) == 2:
    iid = arg[0]
    reason = arg[1]
  else:
    iid = arg[0]
    reason = None
  if not iid.isnumeric():
   username = iid.replace("@", "")
   entity = await tbot.get_input_entity(iid)
   try:
     r_sender_id = entity.user_id
   except Exception:
        await event.reply("Couldn't fetch that user.")
        return
  else:
   r_sender_id = int(iid)
  try:
   replied_user = await tbot(GetFullUserRequest(r_sender_id))
   fname = replied_user.user.first_name
  except Exception:
   fname = "User"
 else:
   reply_message = await event.get_reply_message()
   iid = reply_message.sender_id
   username = reply_message.sender.username
   fname = reply_message.sender.first_name
   if input:
     reason = input
   else:
     reason = None
   r_sender_id = iid
 if r_sender_id == OWNER_ID:
        await event.reply(f"Yeah FuckOff!")
        return
 elif r_sender_id in DEV_USERS:
        await event.reply("No!")
        return
 elif r_sender_id == BOT_ID:
        await event.reply("Who Dafaq Made You Sudo?!")
        return
 elif sudo(r_sender_id):
        await event.reply("Yeah Nibba that's a Sudo User🤨")
        return
 chats = gmuted.find({})
 for c in chats:
        if r_sender_id == c["user"]:
            to_check = get_reason(id=r_sender_id)
            gmuted.delete_one({"user": r_sender_id})
            await event.reply("Globally Pardoned This User.!🏳️")
            await tbot.send_message(GBAN_LOGS, "**Global Unmute**\n**ID:** `{}`".format(
                                   r_sender_id))
            return
 await event.reply("Yeah that user is not in my Gmute list.!?")


@tbot.on(events.ChatAction)
async def joinban(event):
    if event.user_joined:
      if is_admin(event, BOT_ID):
        chats = gbanned.find({})
        for c in chats:
          if event.user_id == c["user"]:
              try:
               chat = event.chat_id
               await tbot(
                    EditBannedRequest(chat, event.user_id, BANNED_RIGHTS)
                 )
               await tbot.send_message(event.chat_id, f"Gbanned User Joined\n**ID:** `{event.user_id}`\n\n**Quick Action:** Banned")
              except Exception:
                   pass
              
@tbot.on(events.NewMessage(pattern=None))
async def gmute(event):
    chats = gmuted.find({})
    for c in chats:
        if event.sender_id == c["user"]: 
            await event.delete()
