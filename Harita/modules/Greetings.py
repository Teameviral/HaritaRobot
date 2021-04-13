from telethon import events
from Harita import tbot, BOT_ID, MONGO_DB_URI, CMD_HELP
from pymongo import MongoClient
from Harita.events import register
import os
from Harita.function import can_change_info, is_admin
from telethon import *
from telethon.tl import *
from telethon.utils import pack_bot_file_id

from Harita.modules.sql.welcome_sql import (
    add_welcome_setting,
    get_current_welcome_settings,
    rm_welcome_setting,
    update_previous_welcome,
)
from Harita.modules.sql.welcome_sql import (
    add_goodbye_setting,
    get_current_goodbye_settings,
    rm_goodbye_setting,
    update_previous_goodbye,
)
client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["harita"]
botcheck = db.checkbot
verified_user = db.user_verified

from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights


MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)


@tbot.on(events.ChatAction())  # pylint:disable=E0602
async def _(event):
    cws = get_current_welcome_settings(event.chat_id)
    if cws:
        if event.user_joined:
            
            a_user = await event.get_user()
            title = event.chat.title
            mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
            first = a_user.first_name
            last = a_user.last_name
            if last:
                fullname = f"{first} {last}"
            else:
                fullname = first
            userid = a_user.id
            current_saved_welcome_message = cws.custom_welcome_message
            chats = botcheck.find({})
            for c in chats:
                 if event.chat_id == c["id"]:
                        current_message = await event.reply(
                            current_saved_welcome_message.format(
                                mention=mention,
                                title=title,
                                first=first,
                                last=last,
                                fullname=fullname,
                                userid=userid,
                            ),
                            file=cws.media_file_id,
                            buttons=[
                                [
                                    Button.inline(
                                        "Click Here to prove you're Human", data=f"check-bot-{userid}"
                                    )
                                ]
                            ],
                        )
                        smex = verified_user.find({})
                        for c in smex:
                            if event.chat_id == c["id"] and userid == c["user"]:
                                return
                        await tbot(
                            EditBannedRequest(event.chat_id, userid, MUTE_RIGHTS)
                        )
                        return
            current_message = await event.reply(
                    current_saved_welcome_message.format(
                        mention=mention,
                        title=title,
                        first=first,
                        last=last,
                        fullname=fullname,
                        userid=userid,
                    ),
                    file=cws.media_file_id,
                )


@tbot.on(events.ChatAction())  # pylint:disable=E0602
async def _(event):
    cws = get_current_goodbye_settings(event.chat_id)
    if not cws:
      if event.user_left or event.user_kicked:
        if await is_admin(event, BOT_ID):
          await event.reply("Nice Knowing you!")
    if cws:
        if event.user_left or event.user_kicked:
            
            a_user = await event.get_user()
            title = event.chat.title
            mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
            first = a_user.first_name
            last = a_user.last_name
            if last:
                fullname = f"{first} {last}"
            else:
                fullname = first
            userid = a_user.id
            current_saved_goodbye_message = cws.custom_goodbye_message
            current_message = await event.reply(
                    current_saved_goodbye_message.format(
                        mention=mention,
                        title=title,
                        first=first,
                        last=last,
                        fullname=fullname,
                        userid=userid,
                    ),
                    file=cws.media_file_id,
                )

@tbot.on(events.CallbackQuery(pattern=r"check-bot-(\d+)"))
async def cbot(event):
    chats = verified_user.find({})
    user_id = int(event.pattern_match.group(1))
    chat_id = event.chat_id
    if not event.sender_id == user_id:
        await event.answer("You aren't the person whom should be verified.")
        return
    for c in chats:
        if chat_id == c["id"] and user_id == c["user"]:
            await event.answer("You are already verified !")
            await event.edit(buttons=None)
            return
    if event.sender_id == user_id:
      try:
            await tbot(EditBannedRequest(chat_id, user_id, UNMUTE_RIGHTS))
            verified_user.insert_one({"id": chat_id, "user": user_id})
            await event.answer("Yep you are verified as a human being")
            await event.edit(buttons=None)
      except Exception as e:
         print(e)


@register(pattern="^/setwelcome")  # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    if not await can_change_info(message=event):
        return
    msg = await event.get_reply_message()
    if msg and msg.media:
        cws = get_current_welcome_settings(event.chat_id)
        if cws:
          rm_welcome_setting(event.chat_id)
        tbot_api_file_id = pack_bot_file_id(msg.media)
        add_welcome_setting(event.chat_id, msg.message, False, 0, tbot_api_file_id)
        await event.reply("Welcome message saved. ")
    else:
        cws = get_current_welcome_settings(event.chat_id)
        if cws:
          rm_welcome_setting(event.chat_id)
        input_str = event.text.split(None, 1)
        add_welcome_setting(event.chat_id, input_str[1], False, 0, None)
        await event.reply("Welcome message saved. ")


@register(pattern="^/clearwelcome$")  # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    if not await can_change_info(message=event):
        return
    cws = get_current_welcome_settings(event.chat_id)
    rm_welcome_setting(event.chat_id)
    await event.reply(
        "Welcome message cleared. "
        + "The previous welcome message was `{}`".format(cws.custom_welcome_message)
    )

@register(pattern="^/setgoodbye$")  # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    if not await can_change_info(message=event):
        return
    msg = await event.get_reply_message()
    if msg and msg.media:
        cws = get_current_goodbye_settings(event.chat_id)
        if cws:
          rm_goodbye_setting(event.chat_id)
        tbot_api_file_id = pack_bot_file_id(msg.media)
        add_goodbye_setting(event.chat_id, msg.text, False, 0, tbot_api_file_id)
        await event.reply("Goodbye message saved. ")
    else:
        input_str = msg.text
        cws = get_current_goodbye_settings(event.chat_id)
        if cws:
          rm_goodbye_setting(event.chat_id)
        add_goodbye_setting(event.chat_id, input_str, False, 0, None)
        await event.reply("Goodbye message saved. ")


@register(pattern="^/cleargoodbye$")  # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    if not await can_change_info(message=event):
        return
    cws = get_current_goodbye_settings(event.chat_id)
    rm_goodbye_setting(event.chat_id)
    await event.reply(
        "Goodbye message cleared. "
        + "The previous goodbye message was `{}`".format(cws.custom_goodbye_message)
    )


@register(pattern="^/welcomecaptcha(?: |$)(.*)")
async def welcome_verify(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if not await can_change_info(message=event):
        return
    input = event.pattern_match.group(1)
    chats = botcheck.find({})
    if not input:
        for c in chats:
            if event.chat_id == c["id"]:
                await event.reply(
                    "Please provide some input yes or no.\n\nCurrent setting is : **on**"
                )
                return
        await event.reply(
            "Please provide some input yes or no.\n\nCurrent setting is : **off**"
        )
        return
    if input in "on":
        if event.is_group:
            chats = botcheck.find({})
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply(
                        "Welcome Captcha is already enabled for this chat."
                    )
                    return
            botcheck.insert_one({"id": event.chat_id})
            await event.reply("Welcome Captcha enabled for this chat.")
    if input in "off":
        if event.is_group:
            chats = botcheck.find({})
            for c in chats:
                if event.chat_id == c["id"]:
                    botcheck.delete_one({"id": event.chat_id})
                    await event.reply("Welcome Captcha disabled for this chat.")
                    return
        await event.reply("Welcome Captcha enabled for this chat.")

    if not input == "on" and not input == "off":
        await event.reply("I only understand by on or off")
        return

file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
**Welcome**
 - /setwelcome <reply to a text>: Saves the message as a welcome note in the chat.
 - /checkwelcome: Check whether you have a welcome note in the chat.
 - /clearwelcome: Deletes the welcome note for the current chat.
 - /welcomecaptcha <on/off>: Mutes a user on joining and unmutes as he/she solves a image captcha.
 - /cleanwelcome <on/off>: Clean previous welcome message before welcoming a new user.

**Goodbye**
 - /setgoodbye <reply to a text>: Saves the message as a goodbye note in the chat.
 - /checkgoodbye: Check whether you have a goodbye note in the chat.
 - /cleargoodbye: Deletes the goodbye note for the current chat.
 - /cleangoodbye <on/off>: Clean previous goodbye message before farewelling a user.

**Available variables for formatting greeting message:**
`{mention}, {title}, {count}, {first}, {last}, {fullname}, {userid}, {username}, {my_first}, {my_fullname}, {my_last}, {my_mention}, {my_username}`

You can also include buttons in the welcome message
For eg: type /setwelcome in reply to `Welcome\nHere Are Some Cool Search Engines| [button('Google', 'google.com')] • [button('Yahoo', 'yahoo.com')] • [button('Bing', 'bing.com')]`

**Note**: __You can't set new welcome/goodbye message before deleting the previous one.__
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
