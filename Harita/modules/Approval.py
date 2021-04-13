#Written it on go lang by Paul Larsen
#Written it on Telethon By Ayush Chatterjee And Avishek Bhattacharjee
#By Eviral (github.com/TeamEviral ; t.me/Eviral)
#Don't Forget to give credit and make your source public.

from Harita import CMD_HELP, BOT_ID, tbot
import os
from pymongo import MongoClient
from Harita import MONGO_DB_URI
from Harita.events import register
from telethon import types
from telethon.tl import functions

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["Harita"]
approved_users = db.approve

from Evie.function import is_register_admin, can_approve_users


async def get_user_from_event(event):
    """ Get the user from argument or replied message. """
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await tbot.get_entity(previous_message.sender_id)
    else:
        user = event.pattern_match.group(1)

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.reply("Pass the user's username, id or reply!")
            return

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await tbot.get_entity(user_id)
                return user_obj
        try:
            user_obj = await tbot.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.reply(str(err))
            return None

    return user_obj


@register(pattern="^/approve(?: |$)(.*)")
async def approve(event):
    if event.fwd_from:
        return
    chat_id = event.chat.id
    sender = event.sender_id
    reply_msg = await event.get_reply_message()
    approved_userss = approved_users.find({})

    if event.is_group:
        if not await can_approve_users(message=event):
            await event.reply("You are missing the following rights to use this command:CanChangeInfo")
            return
    else:
        return

    userr = await get_user_from_event(event)
    if userr:
        pass
    else:
        return
    iid = userr.id


    if await is_register_admin(event.input_chat, iid):
        await event.reply("User is already admin - locks, blocklists, and antiflood already don't apply to them.")
        return

    

    if event.sender_id == BOT_ID or int(iid) == int(BOT_ID):
        await event.reply("There's not much point in approving myself.")
        return

    chats = approved_users.find({})
    for c in chats:
        if event.chat_id == c["id"] and iid == c["user"]:
            await event.reply(f"[{userr.first_name}](tg://user?id={iid}) has been approved in {event.chat.title}! They will now be ignored by automated admin actions like locks, blocklists, and antiflood.")
            return

    approved_users.insert_one({"id": event.chat_id, "user": iid})
    await event.reply(f"[{userr.first_name}](tg://user?id={iid}) has been approved in {event.chat.title}! They will now be ignored by automated admin actions like locks, blocklists, and antiflood.")


@register(pattern="^/disapprove(?: |$)(.*)")
async def disapprove(event):
    if event.fwd_from:
        return
    chat_id = event.chat.id
    sender = event.sender_id
    reply_msg = await event.get_reply_message()
    if event.is_group:
        if not await can_approve_users(message=event):
            await event.reply("You are missing the following rights to use this command:CanChangeInfo")
            return
    else:
        return

    userr = await get_user_from_event(event)
    if userr:
        pass
    else:
        return
    iid = userr.id

    if await is_register_admin(event.input_chat, iid):
        await event.reply("This user is an admin, they can't be unapproved.")
        return

    chats = approved_users.find({})
    for c in chats:
        if event.chat_id == c["id"] and iid == c["user"]:
            approved_users.delete_one({"id": event.chat_id, "user": iid})
            await event.reply(f"{userr.first_name} is no longer approved in {event.chat.title}.")
            return
    await event.reply(f"{userr.first_name} isn't approved yet!")


@register(pattern="^/checkstatus(?: |$)(.*)")
async def checkst(event):
    if event.fwd_from:
        return
    if MONGO_DB_URI is None:
        return
    chat_id = event.chat.id
    sender = event.sender_id
    reply_msg = await event.get_reply_message()
    approved_userss = approved_users.find({})

    if event.is_group:
        if not await can_approve_users(message=event):
            return
    else:
        return

    userr = await get_user_from_event(event)
    if userr:
        pass
    else:
        return
    iid = userr.id

    if await is_register_admin(event.input_chat, iid):
        await event.reply("Why will check status of an admin ?")
        return

    if event.sender_id == BOT_ID or int(iid) == int(BOT_ID):
        await event.reply("I am not gonna check my status")
        print("7")
        return

    chats = approved_users.find({})
    for c in chats:
        if event.chat_id == c["id"] and iid == c["user"]:
            await event.reply("This User is Approved")
            return
    await event.reply("This user isn't Approved")


@register(pattern="^/listapproved$")
async def apprlst(event):
    if event.fwd_from:
        return
    if MONGO_DB_URI is None:
        return
    chat_id = event.chat.id
    sender = event.sender_id
    reply_msg = await event.get_reply_message()

    if event.is_group:
        if not await can_approve_users(message=event):
            return
    else:
        return

    autos = approved_users.find({})
    pp = ""
    for i in autos:
        if event.chat_id == i["id"]:
            try:
                h = await tbot.get_entity(i["user"])
                getmyass = ""
                if not h.username:
                    getmyass += f"- [{h.first_name}](tg://user?id={h.id})\n"
                else:
                    getmyass += "- @" + h.username + "\n"
                pp += str(getmyass)
            except ValueError:
                pass
    try:
        await event.reply(pp)
    except Exception:
        await event.reply("No one is approved in this chat.")


@register(pattern="^/disapproveall$")
async def disapprlst(event):
    if event.fwd_from:
        return
    if MONGO_DB_URI is None:
        return
    chat_id = event.chat.id
    sender = event.sender_id
    reply_msg = await event.get_reply_message()

    if event.is_group:
        if not await can_approve_users(message=event):
            return
    else:
        return
    autos = approved_users.find({})
    for i in autos:
        if event.chat_id == i["id"]:
            approved_users.delete_one({"id": event.chat_id})
            await event.reply("Successfully disapproved everyone in the chat.")
            return
    await event.reply("No one is approved in this chat.")


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /approve: Approves a user so that they can use all non-admin commands in group
 - /disapprove: Disapproves a user so that they can't use non-admin commands in group
 - /checkstatus: Check the approve status of an admin
 - /listapproved: List all the Approved users in the chat
 - /disapproveall: Disapproves all users who were approved in the chat
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
