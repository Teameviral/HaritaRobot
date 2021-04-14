from Harita import CMD_HELP, tbot, BOT_ID
import html
import os
from telethon import *
from telethon.tl import *
from Harita.events import register
import Harita.modules.sql.warns_sql as sql
from telethon.tl.types import ChatBannedRights
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import *
import Harita.modules.sql.rules_sql as rulesql


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


@register(pattern="^/warn(?: |$)(.*)")
async def _(event):
    try:
        if event.fwd_from:
            return
        if event.is_private:
            return
        if event.is_group:
            if await is_register_admin(event.input_chat, event.message.sender_id):
                pass
            else:
                return
        quew = event.pattern_match.group(1)

        if event.reply_to_msg_id:
            warn_reason = event.text[len("/warn ") :]
            if not warn_reason:
                await event.reply("Please provide a reason for warning.")
                return
            reply_message = await event.get_reply_message()
            if not await is_register_admin(event.input_chat, reply_message.sender_id):
                pass
            else:
                await event.reply("I am not gonna warn an admin")
                return
            if reply_message.sender_id == BOT_ID:
                await event.reply("Why are you trying to warn me ?")
                return
            limit, soft_warn = sql.get_warn_setting(event.chat_id)
            num_warns, reasons = sql.warn_user(
                reply_message.sender_id, event.chat_id, warn_reason
            )
            if num_warns >= limit:
                sql.reset_warns(reply_message.sender_id, event.chat_id)
                if sql.get_warn_strength(event.chat_id) == "kick":
                    await tbot.kick_participant(event.chat_id, reply_message.sender_id)
                    reply = "{} warnings, <u><a href='tg://user?id={}'>{}</a></u> has been kicked!".format(
                        limit, reply_message.sender_id, reply_message.sender.first_name
                    )
                    await event.reply(reply, parse_mode="html")
                    return
                if sql.get_warn_strength(event.chat_id) == "ban":
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
                    await tbot(
                        EditBannedRequest(
                            event.chat_id, reply_message.sender_id, BANNED_RIGHTS
                        )
                    )
                    reply = "{} warnings, <u><a href='tg://user?id={}'>{}</a></u> has been banned!".format(
                        limit, reply_message.sender_id, reply_message.sender.first_name
                    )
                    await event.reply(reply, parse_mode="html")
                    return
                if sql.get_warn_strength(event.chat_id) == "mute":
                    MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
                    await tbot(
                        EditBannedRequest(
                            event.chat_id, reply_message.sender_id, MUTE_RIGHTS
                        )
                    )
                    reply = "{} warnings, <u><a href='tg://user?id={}'>{}</a></u> has been muted!".format(
                        limit, reply_message.sender_id, reply_message.sender.first_name
                    )
                    await event.reply(reply, parse_mode="html")
                    return
            else:
                reply = "<u><a href='tg://user?id={}'>{}</a></u> has {}/{} warnings... watch out!".format(
                    reply_message.sender_id,
                    reply_message.sender.first_name,
                    num_warns,
                    limit,
                )
                if warn_reason:
                    reply += "\nReason: {}".format(html.escape(warn_reason))
            chat_id = event.chat_id
            rules = rulesql.get_rules(chat_id)
            if rules:
                await event.reply(
                    reply,
                    buttons=[
                        [
                            Button.inline(
                                "Remove Warn ✖️",
                                data=f"rm_warn-{reply_message.sender_id}",
                            ),
                            Button.inline(
                                "Rules ✝️",
                                data=f"start-ruleswarn-{reply_message.sender_id}",
                            ),
                        ]
                    ],
                    parse_mode="html",
                )
            else:
                await event.reply(
                    reply,
                    buttons=[
                        [
                            Button.inline(
                                "Remove Warn ✖️",
                                data=f"rm_warn-{reply_message.sender_id}",
                            )
                        ]
                    ],
                    parse_mode="html",
                )
        if not event.reply_to_msg_id and quew:
            if "|" in quew:
                iid, reasonn = quew.split("|")
            cid = iid.strip()
            reason = reasonn.strip()
            if cid.isnumeric():
                cid = int(cid)
            entity = await tbot.get_entity(cid)
            try:
                r_sender_id = entity.id
                r_sender_fname = entity.first_name
            except Exception:
                await event.reply("Couldn't fetch that user.")
                return
            if not reason:
                await event.reply("Please provide a reason for warning.")
                return
            warn_reason = reason
            if not await is_register_admin(event.input_chat, r_sender_id):
                pass
            else:
                await event.reply("I am not gonna warn an admin")
                return
            if r_sender_id == BOT_ID:
                await event.reply("Why are you trying to warn me ?")
                return
            limit, soft_warn = sql.get_warn_setting(event.chat_id)
            num_warns, reasons = sql.warn_user(r_sender_id, event.chat_id, warn_reason)
            if num_warns >= limit:
                sql.reset_warns(r_sender_id, event.chat_id)
                if sql.get_warn_strength(event.chat_id) == "kick":
                    await tbot.kick_participant(event.chat_id, r_sender_id)
                    reply = "{} warnings, <u><a href='tg://user?id={}'>{}</a></u> has been kicked!".format(
                        limit, r_sender_id, r_sender_fname
                    )
                    await event.reply(reply, parse_mode="html")
                    return
                if sql.get_warn_strength(event.chat_id) == "ban":
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
                    await tbot(
                        EditBannedRequest(event.chat_id, r_sender_id, BANNED_RIGHTS)
                    )
                    reply = "{} warnings, <u><a href='tg://user?id={}'>{}</a></u> has been banned!".format(
                        limit, r_sender_id, r_sender_fname
                    )
                    await event.reply(reply, parse_mode="html")
                    return
                if sql.get_warn_strength(event.chat_id) == "mute":
                    MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
                    await tbot(
                        EditBannedRequest(event.chat_id, r_sender_id, MUTE_RIGHTS)
                    )
                    reply = "{} warnings, <u><a href='tg://user?id={}'>{}</a></u> has been muted!".format(
                        limit, r_sender_id, r_sender_fname
                    )
                    await event.reply(reply, parse_mode="html")
                    return
            else:
                reply = "<u><a href='tg://user?id={}'>{}</a></u> has {}/{} warnings... watch out!".format(
                    r_sender_id, r_sender_fname, num_warns, limit
                )
                if warn_reason:
                    reply += "\nReason: {}".format(html.escape(warn_reason))
            chat_id = event.chat_id
            rules = rulesql.get_rules(chat_id)
            if rules:
                await event.reply(
                    reply,
                    buttons=[
                        [
                            Button.inline(
                                "Remove Warn ✖️", data=f"rm_warn-{r_sender_id}"
                            ),
                            Button.inline(
                                "Rules ✝️", data=f"start-ruleswarn-{r_sender_id}"
                            ),
                        ]
                    ],
                    parse_mode="html",
                )
            else:
                await event.reply(
                    reply,
                    buttons=[
                        [Button.inline("Remove Warn ✖️", data=f"rm_warn-{r_sender_id}")]
                    ],
                    parse_mode="html",
                )
    except Exception as e:
        print(e)


@tbot.on(events.CallbackQuery(pattern=r"start-ruleswarn-(\d+)"))
async def rm_warn(event):
    rules = rulesql.get_rules(event.chat_id)
    if not rules:
        rules = "The group admins haven't set any rules for that chat yet.\nThis probably doesn't mean it's lawless though...!"
    user_id = int(event.pattern_match.group(1))
    if not event.sender_id == user_id:
        await event.answer("You haven't been warned !")
        return
    text = f"The rules for **{event.chat.title}** are:\n\n{rules}"
    try:
        await tbot.send_message(
            user_id, text, parse_mode="markdown", link_preview=False
        )
    except Exception:
        await event.answer(
            "I can't send you the rules as you haven't started me in PM, first start me !",
            alert=True,
        )


@tbot.on(events.CallbackQuery(pattern=r"rm_warn-(\d+)"))
async def rm_warn(event):
    try:
        if event.is_group:
            if await is_register_admin(event.input_chat, event.sender_id):
                pass
            else:
                await event.answer("You need to be an admin to do this", alert=False)
                return
            sender = await event.get_sender()
            sid = sender.id
            user_id = int(event.pattern_match.group(1))
            result = sql.get_warns(user_id, event.chat_id)
            if not result and result[0] != 0:
                await event.answer("This user hasn't got any warnings!", alert=False)
                return
            sql.remove_warn(user_id, event.chat_id)
            await event.edit(
                f"Warn removed by <u><a href='tg://user?id={sid}'>user</a></u> ",
                parse_mode="html",
            )
        else:
            return
    except:
        await event.answer(
            "Sorry the button link has expired, pls use /removelastwarn to manually remove warns",
            alert=True,
        )


@register(pattern="^/getwarns$")
async def _(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass

        else:
            return
    reply_message = await event.get_reply_message()
    if not await is_register_admin(event.input_chat, reply_message.sender_id):
        pass
    else:
        await event.reply("I am not gonna get warns of an admin")
        return
    result = sql.get_warns(reply_message.sender_id, event.chat_id)
    if result and result[0] != 0:
        num_warns, reasons = result
        limit, soft_warn = sql.get_warn_setting(event.chat_id)
        if reasons:
            text = "This user has {}/{} warnings, for the following reasons:".format(
                num_warns, limit
            )
            text += "\r\n"
            text += reasons
            await event.reply(text)
        else:
            await event.reply(
                "This user has {} / {} warning, but no reasons for any of them.".format(
                    num_warns, limit
                )
            )
    else:
        await event.reply("This user hasn't got any warnings!")


@register(pattern="^/removelastwarn$")
async def _(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        else:
            return
    reply_message = await event.get_reply_message()
    if not await is_register_admin(event.input_chat, reply_message.sender_id):
        pass
    else:
        await event.reply("I am not gonna remove warn of an admin")
        return
    result = sql.get_warns(reply_message.sender_id, event.chat_id)
    if not result and result[0] != 0:
        await event.reply("This user hasn't got any warnings!")
        return
    sql.remove_warn(reply_message.sender_id, event.chat_id)
    await event.reply("Removed last warn of that user.")


@register(pattern="^/resetwarns$")
async def _(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass

        else:
            return
    reply_message = await event.get_reply_message()
    if not await is_register_admin(event.input_chat, reply_message.sender_id):
        pass
    else:
        await event.reply("I am not gonna reset warn of an admin")
        return
    sql.reset_warns(reply_message.sender_id, event.chat_id)
    await event.reply("Warns for this user have been reset!")


@register(pattern="^/setwarnmode (.*)")
async def _(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if event.is_group:
        if await can_change_info(message=event):
            pass
        else:
            return
    input = event.pattern_match.group(1)
    if not input == "kick" and not input == "mute" and not input == "ban":
        await event.reply("I only understand by kick/ban/mute")
        return
    sql.set_warn_strength(event.chat_id, input)
    await event.reply(f"Too many warns will now result in **{input}**")


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /warn <userid> | <reason> or /warn <reason> in reply to a message: warn a user
 - /removelastwarn: remove the last warn that a user has received
 - /getwarns: list the warns that a user has received
 - /resetwarns: reset all warns that a user has received
 - /setwarnmode <kick/ban/mute>: set the warn mode for the chat
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
