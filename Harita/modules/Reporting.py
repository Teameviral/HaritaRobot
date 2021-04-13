import html
import os
from Evie import tbot
from Evie import *
from telethon import events, Button
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import *
from telethon.errors import UserNotParticipantError
from pymongo import MongoClient
from Evie import MONGO_DB_URI
from Evie.events import register
from Evie.modules.sql import reporting_sql as sql

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


from Evie.function import is_admin, can_change_info


async def can_ban_users(chat, user):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            chat,
            user,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.ban_users
    )


async def can_del(chat, user):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            chat,
            user,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.delete_messages
    )


@register(pattern="^/reports ?(.*)")
async def _(event):
    if event.is_private:
        return
    if event.is_group:
        if not is_admin(event, event.sender_id):
            await event.reply("You need to be an admin to do this.")
            return
        if not await can_change_info(message=event):
            return
    chat = event.chat_id
    args = event.pattern_match.group(1)
    if args:
        if args == "on" or args == "yes":
            sql.set_chat_setting(chat, True)
            await event.reply(
                "Users will now be able to report messages."
            )

        elif args == "off" or args == "no":
            sql.set_chat_setting(chat, False)
            await event.reply(
                "Users will no longer be able to report via @admin or /report."
            )
        else:
            await event.reply("Your input was not recognised as one of: yes/no/on/off")
            return
    else:
        await event.reply(
            f"Reports are currently {sql.chat_should_report(chat)} in this chat. Users can use the /report command, or mention @admin, to tag all admins.\n\nTo change this setting, try this command again, with one of the following args: yes/no/on/off",
            parse_mode="markdown",
        )

from telethon import events
@tbot.on(events.NewMessage(pattern='/report'))
async def _(event):
    if event.is_private:
        return
    if await is_admin(event, event.sender_id):
        return

    chat = event.chat_id
    user = event.sender
    

    if not sql.chat_should_report(chat):
        return

    if event.reply_to_msg_id:
        c = await event.get_reply_message()
        reported_user = c.sender_id
        reported_user_first_name = c.sender.first_name
        if await is_admin(event, reported_user):
            return
        if user.id == BOT_ID:
            await event.reply("Why would I report myself?")
            return
        await tbot.send_message(event.chat_id, f"Reported [{reported_user_first_name}](tg://user?id={reported_user}) to admins.")

@tbot.on(events.NewMessage(pattern='@admins'))
async def _(event):
    if event.is_private:
        return
    if await is_admin(event, event.sender_id):
        return

    chat = event.chat_id
    user = event.sender
   

    if not sql.chat_should_report(chat):
        return

    if event.reply_to_msg_id:
        c = await event.get_reply_message()
        reported_user = c.sender_id
        reported_user_first_name = c.sender.first_name
        if await is_admin(event, reported_user):
            return
        if user.id == BOT_ID:
            await event.reply("Why would I report myself?")
            return
        await tbot.send_message(event.chat_id, f"Reported [{reported_user_first_name}](tg://user?id={reported_user}) to admins.")


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /report <reason>: reply to a message to report it to admins.
**NOTE:** This will not get triggered if used by admins.

**Admins only:**
 - /reports <on/yes/off/no>: change report setting, or view current status.
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
