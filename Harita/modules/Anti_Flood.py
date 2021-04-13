  
import html
from typing import Optional, List
import re, time
from Harita.modules.sql import antiflood_sql as sql
from telethon.tl.functions.channels import EditBannedRequest
from telethon import *
from telethon.tl.types import *
from Harita import *

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

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


async def can_change_info(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.change_info
    )


async def extract_time(message, time_val):
    if any(time_val.endswith(unit) for unit in ("m", "h", "d")):
        unit = time_val[-1]
        time_num = time_val[:-1]  # type: str
        if not time_num.isdigit():
            await message.reply("Invalid time amount specified.")
            return ""

        if unit == "m":
            bantime = int(time.time() + int(time_num) * 60)
        elif unit == "h":
            bantime = int(time.time() + int(time_num) * 60 * 60)
        elif unit == "d":
            bantime = int(time.time() + int(time_num) * 24 * 60 * 60)
        else:
            return
        return bantime
    else:
        await message.reply(
            "Invalid time type specified. Expected m,h, or d, got: {}".format(
                time_val[-1]
            )
        )
        return


@tbot.on(events.NewMessage(pattern=None))
async def _(event):
    if event.is_private:
        return
    user = event.sender  # type: Optional[User]
    chat = event.chat_id  # type: Optional[Chat]

    # ignore admins and owner
    if await is_register_admin(chat, user.id) or user.id == OWNER_ID:
        sql.update_flood(chat, None)
        return

    should_ban = sql.update_flood(chat, user.id)
    if not should_ban:
        return

    try:
        getmode, getvalue = sql.get_flood_setting(chat)
        if getmode == 1:
            await tbot(EditBannedRequest(chat, user.id, BANNED_RIGHTS))
            execstrings = "Banned"

        elif getmode == 2:
            await tbot.kick_participant(chat, user.id)
            execstrings = "Kicked"

        elif getmode == 3:
            await tbot(EditBannedRequest(chat, user.id, MUTE_RIGHTS))
            execstrings = "Muted"

        elif getmode == 4:
            bantime = await extract_time(event, getvalue)
            NEW_RIGHTS = ChatBannedRights(
                until_date=bantime,
                view_messages=True,
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                embed_links=True,
            )
            await tbot(EditBannedRequest(chat, user.id, NEW_RIGHTS))
            execstrings = "Banned for {}".format(getvalue)

        elif getmode == 5:
            mutetime = await extract_time(event, getvalue)
            print(mutetime)
            NEW_RIGHTS = ChatBannedRights(until_date=mutetime, send_messages=True)
            await tbot(EditBannedRequest(chat, user.id, NEW_RIGHTS))
            execstrings = "Muted for {}".format(getvalue)

        await event.reply("Spammer Detected !\n{}!".format(execstrings))

    except Exception:
        await event.reply(
            "I can't restrict people here, give me permissions first! Until then, I'll disable anti-flood."
        )
        sql.set_flood(chat, 0)


@register(pattern="^/setfloodlimit ?(.*)")
async def _(event):
    if event.is_private:
        return
    if event.is_group:
        if not await can_change_info(message=event):
            return
    chat_id = event.chat_id
    args = event.pattern_match.group(1)
    if not args:
        await event.reply(
            (
                "Use `/setflood number` to enable anti-flood.\nOr use `/setflood off` to disable antiflood!."
            ),
            parse_mode="markdown",
        )
        return

    if args == "off":
        sql.set_flood(chat_id, 0)
        await event.reply("Antiflood has been disabled.")

    elif args.isdigit():
        amount = int(args)
        if amount <= 0:
            sql.set_flood(chat_id, 0)
            await event.reply("Antiflood has been disabled.")

        elif amount < 3:
            await event.reply(
                "Antiflood must be either 0 (disabled) or number greater than 2!",
            )
            return
        else:
            sql.set_flood(chat_id, amount)
            await event.reply(
                "Successfully updated anti-flood limit to {}!".format(amount)
            )
    else:
        await event.reply("Invalid argument please use a number or 'off'")


@register(pattern="^/flood$")
async def _(event):
    if event.is_private:
        return
    if event.is_group:
        if not await can_change_info(message=event):
            return
    chat_id = event.chat_id
    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        await event.reply("I'm not enforcing any flood control here!")
    else:
        await event.reply(
            "I'm currently restricting members after {} consecutive messages.".format(
                limit
            )
        )


@register(pattern="^/setfloodmode ?(.*)")
async def _(event):
    try:
        if event.is_private:
            return
        if event.is_group:
            if not await can_change_info(message=event):
                return
        chat_id = event.chat_id
        args = event.pattern_match.group(1)
        time = args.split()
        if time[0]:
            if time[0] == "ban":
                settypeflood = "ban"
                sql.set_flood_strength(chat_id, 1, "0")
            elif time[0] == "kick":
                settypeflood = "kick"
                sql.set_flood_strength(chat_id, 2, "0")
            elif time[0] == "mute":
                settypeflood = "mute"
                sql.set_flood_strength(chat_id, 3, "0")
            elif time[0] == "tban":
                try:
                    ttime = time[1]
                except:
                    await event.reply("Please provide the tban time interval.")
                    return
                if len(ttime) == 1:
                    teks = """It looks like you tried to set time value for antiflood but you didn't specified time; Try, `/setfloodmode tban <timevalue>`.
Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                    await event.reply(teks, parse_mode="markdown")
                    return
                if not any(ttime.endswith(unit) for unit in ("m", "h", "d")):
                    await event.reply(
                        "Invalid time type specified. Expected m,h, or d, got: {}".format(
                            ttime
                        )
                    )
                    return
                settypeflood = "tban for {}".format(ttime)
                sql.set_flood_strength(chat_id, 4, str(ttime))
            elif time[0] == "tmute":
                try:
                    ttime = time[1]
                except:
                    await event.reply("Please provide the tmute time interval.")
                    return
                if len(ttime) == 1:
                    teks = """It looks like you tried to set time value for antiflood but you didn't specified time; Try, `/setfloodmode tmute <timevalue>`.
Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                    await event.reply(teks, parse_mode="markdown")
                    return
                if not any(ttime.endswith(unit) for unit in ("m", "h", "d")):
                    await event.reply(
                        "Invalid time type specified. Expected m,h, or d, got: {}".format(
                            ttime
                        )
                    )
                    return
                settypeflood = "tmute for {}".format(ttime)
                sql.set_flood_strength(chat_id, 5, str(ttime))
            else:
                await event.reply("I only understand ban/kick/mute/tban/tmute!")
                return

            await event.reply(
                "Exceeding consecutive flood limit will result in {}!".format(
                    settypeflood
                )
            )
        else:
            getmode, getvalue = sql.get_flood_setting(chat_id)
            if getmode == 1:
                settypeflood = "ban"
            elif getmode == 2:
                settypeflood = "kick"
            elif getmode == 3:
                settypeflood = "mute"
            elif getmode == 4:
                settypeflood = "tban for {}".format(getvalue)
            elif getmode == 5:
                settypeflood = "tmute for {}".format(getvalue)

            await event.reply(
                "Sending more message than flood limit will result in {}.".format(
                    settypeflood
                )
            )
    except Exception as e:
        print(e)


__help__ = """
Antiflood allows you to take action on users that send more than x messages in a row.
Exceeding the set flood will result in restricting that user.
This will mute users if they send more than 10 messages in a row, bots are ignored.
 - /flood: Get the current flood control setting
**Admins only:**
 - /setfloodlimit <int/'off'>: enables or disables flood control
Example: /setflood 10
 - /setfloodmode <ban/kick/mute/tban/tmute> <value>: Action to perform when user have exceeded flood limit. ban/kick/mute/tmute/tban
**Note:**
Value must be filled for tban and tmute
It can be:
5m = 5 minutes
6h = 6 hours
3d = 3 days
1w = 1 week
"""

file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
