from Harita import tbot, ubot, CMD_HELP
from bs4 import BeautifulSoup as bs
import urllib.request as urllib
import requests
from telethon.errors.rpcerrorlist import StickersetInvalidError
from PIL import Image
from io import BytesIO
import os
import math
import datetime
from Harita import MONGO_DB_URI

from telethon.tl.functions.messages import GetStickerSetRequest

from telethon.tl.types import (
    DocumentAttributeSticker,
    InputStickerSetID,
    InputStickerSetShortName,
    MessageMediaPhoto,
)

from Harita.events import register
from telethon import *
from telethon import events
from telethon.tl import functions
from telethon.tl import types
from pymongo import MongoClient

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["harita"]
approved_users = db.approve


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


@register(pattern="^/packinfo$")
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return

    if not event.is_reply:
        await event.reply("Reply to any sticker to get it's pack info.")
        return
    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        await event.reply("Reply to any sticker to get it's pack info.")
        return
    stickerset_attr_s = rep_msg.document.attributes
    stickerset_attr = find_instance(stickerset_attr_s, DocumentAttributeSticker)
    if not stickerset_attr.stickerset:
        await event.reply("sticker does not belong to a pack.")
        return
    get_stickerset = await tbot(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash,
            )
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    await event.reply(
        f"**Sticker Title:** `{get_stickerset.set.title}\n`"
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Archived:** `{get_stickerset.set.archived}`\n"
        f"**Stickers In Pack:** `{len(get_stickerset.packs)}`\n"
        f"**Emojis In Pack:** {' '.join(pack_emojis)}"
    )


def find_instance(items, class_or_tuple):
    for item in items:
        if isinstance(item, class_or_tuple):
            return item
    return None


DEFAULTUSER = "Julia"
FILLED_UP_DADDY = "Invalid pack selected."


@register(pattern="^/kang ?(.*)")
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    if not event.is_reply:
        await event.reply("Reply to a photo to add to your personal sticker pack.")
        return
    reply_message = await event.get_reply_message()
    sticker_emoji = "🔥"
    input_str = event.pattern_match.group(1)
    if input_str:
        sticker_emoji = input_str

    user = await event.get_sender()
    if not user.first_name:
        user.first_name = user.id
    pack = 1
    userid = event.sender_id
    first_name = user.first_name
    packname = f"{first_name}'s Sticker Vol.{pack}"
    packshortname = f"MissJuliaRobot_sticker_{userid}"
    kanga = await event.reply("`Kanging .`")
    is_a_s = is_it_animated_sticker(reply_message)
    file_ext_ns_ion = "@MissJuliaRobot.png"
    file = await event.client.download_file(reply_message.media)
    uploaded_sticker = None
    if is_a_s:
        file_ext_ns_ion = "AnimatedSticker.tgs"
        uploaded_sticker = await ubot.upload_file(file, file_name=file_ext_ns_ion)
        packname = f"{first_name}'s Animated Sticker Vol.{pack}"
        packshortname = f"MissJuliaRobot_animate_{userid}"
    elif not is_message_image(reply_message):
        await kanga.edit("Invalid message type")
        return
    else:
        with BytesIO(file) as mem_file, BytesIO() as sticker:
            resize_image(mem_file, sticker)
            sticker.seek(0)
            uploaded_sticker = await ubot.upload_file(
                sticker, file_name=file_ext_ns_ion
            )

    await kanga.edit("`Kanging ..`")

    async with ubot.conversation("@Stickers") as bot_conv:
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(minutes=1)
        if not await stickerset_exists(bot_conv, packshortname):

            await silently_send_message(bot_conv, "/cancel")
            if is_a_s:
                response = await silently_send_message(bot_conv, "/newanimated")
            else:
                response = await silently_send_message(bot_conv, "/newpack")
            if "Yay!" not in response.text:
                await tbot.edit_message(
                    kanga, f"**FAILED**! @Stickers replied: {response.text}"
                )
                return
            response = await silently_send_message(bot_conv, packname)
            if not response.text.startswith("Alright!"):
                await tbot.edit_message(
                    kanga, f"**FAILED**! @Stickers replied: {response.text}"
                )
                return
            w = await bot_conv.send_file(
                file=uploaded_sticker, allow_cache=False, force_document=True
            )
            response = await bot_conv.get_response()
            if "Sorry" in response.text:
                await tbot.edit_message(
                    kanga, f"**FAILED**! @Stickers replied: {response.text}"
                )
                return
            await silently_send_message(bot_conv, sticker_emoji)
            await silently_send_message(bot_conv, "/publish")
            response = await silently_send_message(bot_conv, f"<{packname}>")
            await silently_send_message(bot_conv, "/skip")
            response = await silently_send_message(bot_conv, packshortname)
            if response.text == "Sorry, this short name is already taken.":
                await tbot.edit_message(
                    kanga, f"**FAILED**! @Stickers replied: {response.text}"
                )
                return
        else:
            await silently_send_message(bot_conv, "/cancel")
            await silently_send_message(bot_conv, "/addsticker")
            await silently_send_message(bot_conv, packshortname)
            await bot_conv.send_file(
                file=uploaded_sticker, allow_cache=False, force_document=True
            )
            response = await bot_conv.get_response()
            if response.text == FILLED_UP_DADDY:
                while response.text == FILLED_UP_DADDY:
                    pack += 1
                    prevv = int(pack) - 1
                    packname = f"{first_name}'s Sticker Vol.{pack}"
                    packshortname = f"Vol_{pack}_with_{userid}"

                    if not await stickerset_exists(bot_conv, packshortname):
                        await tbot.edit_message(
                            kanga,
                            "**Pack No. **"
                            + str(prevv)
                            + "** is full! Making a new Pack, Vol. **"
                            + str(pack),
                        )
                        if is_a_s:
                            response = await silently_send_message(
                                bot_conv, "/newanimated"
                            )
                        else:
                            response = await silently_send_message(bot_conv, "/newpack")
                        if "Yay!" not in response.text:
                            await tbot.edit_message(
                                kanga, f"**FAILED**! @Stickers replied: {response.text}"
                            )
                            return
                        response = await silently_send_message(bot_conv, packname)
                        if not response.text.startswith("Alright!"):
                            await tbot.edit_message(
                                kanga, f"**FAILED**! @Stickers replied: {response.text}"
                            )
                            return
                        w = await bot_conv.send_file(
                            file=uploaded_sticker,
                            allow_cache=False,
                            force_document=True,
                        )
                        response = await bot_conv.get_response()
                        if "Sorry" in response.text:
                            await tbot.edit_message(
                                kanga, f"**FAILED**! @Stickers replied: {response.text}"
                            )
                            return
                        await silently_send_message(bot_conv, sticker_emoji)
                        await silently_send_message(bot_conv, "/publish")
                        response = await silently_send_message(
                            bot_conv, f"<{packname}>"
                        )
                        await silently_send_message(bot_conv, "/skip")
                        response = await silently_send_message(bot_conv, packshortname)
                        if response.text == "Sorry, this short name is already taken.":
                            await tbot.edit_message(
                                kanga, f"**FAILED**! @Stickers replied: {response.text}"
                            )
                            return
                    else:
                        await tbot.edit_message(
                            kanga,
                            "**Pack No. **"
                            + str(prevv)
                            + "** is full! Switching to Vol. **"
                            + str(pack),
                        )
                        await silently_send_message(bot_conv, "/addsticker")
                        await silently_send_message(bot_conv, packshortname)
                        await bot_conv.send_file(
                            file=uploaded_sticker,
                            allow_cache=False,
                            force_document=True,
                        )
                        response = await bot_conv.get_response()
                        if "Sorry" in response.text:
                            await tbot.edit_message(
                                kanga, f"**FAILED**! @Stickers replied: {response.text}"
                            )
                            return
                        await silently_send_message(bot_conv, sticker_emoji)
                        await silently_send_message(bot_conv, "/done")
            else:
                if "Sorry" in response.text:
                    await tbot.edit_message(
                        kanga, f"**FAILED**! @Stickers replied: {response.text}"
                    )
                    return
                await silently_send_message(bot_conv, response)
                await silently_send_message(bot_conv, sticker_emoji)
                await silently_send_message(bot_conv, "/done")
    await kanga.edit("`Kanging ...`")
    await kanga.edit(
        f"Sticker added! Your pack can be found [here](t.me/addstickers/{packshortname})"
    )
    os.system("rm -rf  @MissJuliaRobot.png")
    os.system("rm -rf  AnimatedSticker.tgs")
    os.system("rm -rf *.webp")


@register(pattern="^/getsticker$")
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    if not event.is_reply:
        await event.reply("Reply to a sticker to extract image from it.")
        return
    reply_message = await event.get_reply_message()
    file_ext_ns_ion = "sticker.png"
    file = await tbot.download_file(reply_message.media)
    is_a_s = is_it_animated_sticker(reply_message)
    if is_a_s:
        await event.reply("I can't extract image from animated stickers")
    elif not is_message_image(reply_message):
        await event.reply("Invalid message type")
        return
    else:
        with BytesIO(file) as mem_file, BytesIO() as sticker:
            resize_image(mem_file, sticker)
            sticker.seek(0)
            uploaded_sticker = await tbot.upload_file(
                sticker, file_name=file_ext_ns_ion
            )
        await tbot.send_file(
            event.chat_id,
            file=uploaded_sticker,
            allow_cache=False,
            force_document=True,
            reply_to=event.sender_id,
        )
    os.remove("sticker.png")


def is_it_animated_sticker(message):
    try:
        if message.media and message.media.document:
            mime_type = message.media.document.mime_type
            if "tgsticker" in mime_type:
                return True
            return False
        return False
    except BaseException:
        return False


def is_message_image(message):
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            return True
        if message.media.document:
            if message.media.document.mime_type.split("/")[0] == "image":
                return True
        return False
    return False


async def silently_send_message(conv, text):
    await conv.send_message(text)
    response = await conv.get_response()
    await conv.mark_read(message=response)
    return response


async def stickerset_exists(conv, setname):
    try:
        await tbot(GetStickerSetRequest(InputStickerSetShortName(setname)))
        response = await silently_send_message(conv, "/addsticker")
        if response.text == "Invalid pack selected.":
            await silently_send_message(conv, "/cancel")
            return False
        await silently_send_message(conv, "/cancel")
        return True
    except StickersetInvalidError:
        return False


def resize_image(image, save_locaton):
    """Copyright Rhyse Simpson:
    https://github.com/skittles9823/SkittBot/blob/master/tg_bot/modules/stickers.py
    """
    im = Image.open(image)
    maxsize = (512, 512)
    if (im.width and im.height) < 512:
        size1 = im.width
        size2 = im.height
        if im.width > im.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        im = im.resize(sizenew)
    else:
        im.thumbnail(maxsize)
    im.save(save_locaton, "PNG")


def find_instance(items, class_or_tuple):
    for item in items:
        if isinstance(item, class_or_tuple):
            return item
    return None


@register(pattern="^/searchsticker (.*)")
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    input_str = event.pattern_match.group(1)
    combot_stickers_url = "https://combot.org/telegram/stickers?q="
    text = requests.get(combot_stickers_url + input_str)
    soup = bs(text.text, "lxml")
    results = soup.find_all("a", {"class": "sticker-pack__btn"})
    titles = soup.find_all("div", "sticker-pack__title")
    if not results:
        await event.reply("No results found :(")
        return
    reply = f"Stickers for **{input_str}**:"
    for result, title in zip(results, titles):
        link = result["href"]
        reply += f"\nâ€¢ [{title.get_text()}]({link})"
    await event.reply(reply)


@register(pattern="^/rmkang$")
async def _(event):
    try:
        approved_userss = approved_users.find({})
        for ch in approved_userss:
            iid = ch["id"]
            userss = ch["user"]
        if event.is_group:
            if await is_register_admin(event.input_chat, event.message.sender_id):
                pass
            elif event.chat_id == iid and event.sender_id == userss:
                pass
            else:
                return

        if not event.is_reply:
            await event.reply(
                "Reply to a sticker to remove it from your personal sticker pack."
            )
            return
        reply_message = await event.get_reply_message()
        kanga = await event.reply("`Deleting .`")

        if not is_message_image(reply_message):
            await kanga.edit("Please reply to a sticker.")
            return

        rmsticker = await ubot.get_messages(event.chat_id, ids=reply_message.id)

        stickerset_attr_s = reply_message.document.attributes
        stickerset_attr = find_instance(stickerset_attr_s, DocumentAttributeSticker)
        if not stickerset_attr.stickerset:
            await event.reply("Sticker does not belong to a pack.")
            return

        get_stickerset = await tbot(
            GetStickerSetRequest(
                InputStickerSetID(
                    id=stickerset_attr.stickerset.id,
                    access_hash=stickerset_attr.stickerset.access_hash,
                )
            )
        )

        packname = get_stickerset.set.short_name

        sresult = (
            await ubot(
                functions.messages.GetStickerSetRequest(
                    InputStickerSetShortName(packname)
                )
            )
        ).documents
        for c in sresult:
            if int(c.id) == int(stickerset_attr.stickerset.id):
                pass
            else:
                await kanga.edit(
                    "This sticker is already removed from your personal sticker pack."
                )
                return

        await kanga.edit("`Deleting ..`")

        async with ubot.conversation("@Stickers") as bot_conv:

            await silently_send_message(bot_conv, "/cancel")
            response = await silently_send_message(bot_conv, "/delsticker")
            if "Choose" not in response.text:
                await tbot.edit_message(
                    kanga, f"**FAILED**! @Stickers replied: {response.text}"
                )
                return
            response = await silently_send_message(bot_conv, packname)
            if not response.text.startswith("Please"):
                await tbot.edit_message(
                    kanga, f"**FAILED**! @Stickers replied: {response.text}"
                )
                return
            try:
                await rmsticker.forward_to("@Stickers")
            except Exception as e:
                print(e)
            if response.text.startswith("This pack has only"):
                await silently_send_message(bot_conv, "Delete anyway")

            await kanga.edit("`Deleting ...`")
            response = await bot_conv.get_response()
            if not "I have deleted" in response.text:
                await tbot.edit_message(
                    kanga, f"**FAILED**! @Stickers replied: {response.text}"
                )
                return

            await kanga.edit(
                "Successfully deleted that sticker from your personal pack."
            )
    except Exception as e:
        os.remove("sticker.webp")
        print(e)


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")


__help__ = """
 - /packinfo: Reply to a sticker to get it's pack info
 - /getsticker: Uploads the .png of the sticker you've replied to
 - /kang <emoji for sticker>: Reply to a sticker to add it to your pack or makes a new one if it doesn't exist
 - /rmkang: remove a sticker from your current personal sticker pack
 - /searchsticker <text>: Find stickers for given term on combot sticker catalogue
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
