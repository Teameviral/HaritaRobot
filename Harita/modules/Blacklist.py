#Written By Ayush Chatterjee And Avishek Bhattacharjee
#By Eviral (github.com/TeamEviral ; t.me/Eviral)
#Don't Forget to give credit and make your source public.

from Harita import CMD_HELP
import os
from Harita import tbot
import re
from telethon import events
import Harita.modules.sql.blacklist_sql as sql
import Harita.modules.sql.urlblacklist_sql as urlsql
from Harita.events import register
from telethon import types
from telethon.tl import functions
import html
import tldextract


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


@tbot.on(events.NewMessage(incoming=True))
async def on_new_message(event):
    # TODO: exempt admins from locks
    if event.is_private: 
        return
    if await is_register_admin(event.input_chat, event.message.sender_id):
        return

    name = event.text
    snips = sql.get_chat_blacklist(event.chat_id)
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        # print(re.search(pattern, name, flags=re.IGNORECASE))
        if re.search(pattern, name, flags=re.IGNORECASE):
            try:
                await event.delete()
            except Exception as e:
                print(e)


@register(pattern="^/addblacklist ((.|\n)*)")
async def on_add_black_list(event):
    if event.is_group:
        if not await can_change_info(message=event):
            return
    else:
        return
    text = event.pattern_match.group(1)
    to_blacklist = list(
        {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
    )
    for trigger in to_blacklist:
        sql.add_to_blacklist(event.chat_id, trigger.lower())
    await event.reply(
        "Added {} triggers to the blacklist in the current chat".format(
            len(to_blacklist)
        )
    )


@register(pattern="^/listblacklist$")
async def on_view_blacklist(event):
    all_blacklisted = sql.get_chat_blacklist(event.chat_id)
    OUT_STR = "**Blacklists in the Current Chat:\n**"
    if len(all_blacklisted) > 0:
        for trigger in all_blacklisted:
            OUT_STR += f"👉 {trigger} \n"
    else:
        OUT_STR = "No BlackLists. Start Adding using /addblacklist"
    if len(OUT_STR) > 4096:
        with io.BytesIO(str.encode(OUT_STR)) as out_file:
            out_file.name = "blacklist.text"
            await tbot.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="BlackLists in the Current Chat",
                reply_to=event,
            )
            await event.delete()
    else:
        await event.reply(OUT_STR)


@register(pattern="^/rmblacklist ((.|\n)*)")
async def on_delete_blacklist(event):
    if event.is_group:
        if not await can_change_info(message=event):
            return
    else:
        return
    text = event.pattern_match.group(1)
    to_unblacklist = list(
        {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
    )
    successful = 0
    for trigger in to_unblacklist:
        if sql.rm_from_blacklist(event.chat_id, trigger.lower()):
            successful += 1
    await event.reply(
        f"Removed {successful} / {len(to_unblacklist)} from the blacklist"
    )


@register(pattern="^/addurl")
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
    chat = event.chat
    urls = event.text.split(None, 1)
    if len(urls) > 1:
        urls = urls[1]
        to_blacklist = list({uri.strip() for uri in urls.split("\n") if uri.strip()})
        blacklisted = []

        for uri in to_blacklist:
            extract_url = tldextract.extract(uri)
            if extract_url.domain and extract_url.suffix:
                blacklisted.append(extract_url.domain + "." + extract_url.suffix)
                urlsql.blacklist_url(
                    chat.id, extract_url.domain + "." + extract_url.suffix
                )

        if len(to_blacklist) == 1:
            extract_url = tldextract.extract(to_blacklist[0])
            if extract_url.domain and extract_url.suffix:
                await event.reply(
                    "Added <code>{}</code> domain to the blacklist!".format(
                        html.escape(extract_url.domain + "." + extract_url.suffix)
                    ),
                    parse_mode="html",
                )
            else:
                await event.reply("You are trying to blacklist an invalid url")
        else:
            await event.reply(
                "Added <code>{}</code> domains to the blacklist.".format(
                    len(blacklisted)
                ),
                parse_mode="html",
            )
    else:
        await event.reply("Tell me which urls you would like to add to the blacklist.")


@register(pattern="^/delurl")
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
    chat = event.chat
    urls = event.text.split(None, 1)

    if len(urls) > 1:
        urls = urls[1]
        to_unblacklist = list({uri.strip() for uri in urls.split("\n") if uri.strip()})
        unblacklisted = 0
        for uri in to_unblacklist:
            extract_url = tldextract.extract(uri)
            success = urlsql.rm_url_from_blacklist(
                chat.id, extract_url.domain + "." + extract_url.suffix
            )
            if success:
                unblacklisted += 1

        if len(to_unblacklist) == 1:
            if unblacklisted:
                await event.reply(
                    "Removed <code>{}</code> from the blacklist!".format(
                        html.escape(to_unblacklist[0])
                    ),
                    parse_mode="html",
                )
            else:
                await event.reply("This isn't a blacklisted domain...!")
        elif unblacklisted == len(to_unblacklist):
            await event.reply(
                "Removed <code>{}</code> domains from the blacklist.".format(
                    unblacklisted
                ),
                parse_mode="html",
            )
        elif not unblacklisted:
            await event.reply("None of these domains exist, so they weren't removed.")
        else:
            await event.reply(
                "Removed <code>{}</code> domains from the blacklist. {} did not exist, so were not removed.".format(
                    unblacklisted, len(to_unblacklist) - unblacklisted
                ),
                parse_mode="html",
            )
    else:
        await event.reply(
            "Tell me which domains you would like to remove from the blacklist."
        )


@tbot.on(events.NewMessage(incoming=True))
async def on_url_message(event):
    if event.is_private: 
        return 
    chat = event.chat
    extracted_domains = []
    for (ent, txt) in event.get_entities_text():
        if ent.offset != 0:
            break
        if isinstance(ent, types.MessageEntityUrl):
            url = txt
            extract_url = tldextract.extract(url)
            extracted_domains.append(extract_url.domain + "." + extract_url.suffix)
    for url in urlsql.get_blacklisted_urls(chat.id):
        if url in extracted_domains:
            try:
                await event.delete()
            except:
                return


@register(pattern="^/geturl$")
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
    chat = event.chat
    base_string = "Current <b>blacklisted</b> domains:\n"
    blacklisted = urlsql.get_blacklisted_urls(chat.id)
    if not blacklisted:
        await event.reply("There are no blacklisted domains here!")
        return
    for domain in blacklisted:
        base_string += "- <code>{}</code>\n".format(domain)
    await event.reply(base_string, parse_mode="html")


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /addblacklist <trigger> : blacklists the trigger
 - /rmblacklist <trigger> : stop blacklisting a certain blacklist trigger
 - /listblacklist: list all active blacklist filters
 - /geturl: View the current blacklisted urls
 - /addurl <urls>: Add a domain to the blacklist. The bot will automatically parse the url.
 - /delurl <urls>: Remove urls from the blacklist.
**Example:**
 - /addblacklist the admins suck: This will remove "the admins suck" everytime some non-admin types it
 - /addurl bit.ly: This would delete any message containing url "bit.ly"
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
