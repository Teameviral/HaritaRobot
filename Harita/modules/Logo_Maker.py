from Harita import CMD_HELP
from Harita.events import register
from Harita import tbot, OWNER_ID
import os
from PIL import Image, ImageDraw, ImageFont

@register(pattern="^/logo ?(.*)")
async def lego(event):
 quew = event.pattern_match.group(1)
 if event.sender_id == OWNER_ID:
     pass
 else:
     if event.is_group:
       await event.reply('Currently This Module Only Works in my [PM](tg://user?id=1624337697)')
       return
     else:
       pass
 if not quew:
       await event.reply('Provide Some Text To Draw!')
       return
 else:
       pass
 await event.reply('Drawing Text On Pic.Weit!')
 try:
    text = event.pattern_match.group(1)
    img = Image.open('./Harita/resources/Blankmeisnub.jpg')
    draw = ImageDraw.Draw(img)
    image_widthz, image_heightz = img.size
    pointsize = 500
    fillcolor = "gold"
    shadowcolor = "blue"
    font = ImageFont.truetype("./Harita/resources/Chopsic.otf", 160)
    w, h = draw.textsize(text, font=font)
    h += int(h*0.21)
    image_width, image_height = img.size
    draw.text(((image_widthz-w)/2, (image_heightz-h)/2), text, font=font, fill=(255, 255, 255))
    x = (image_widthz-w)/2
    y= ((image_heightz-h)/2+6)
    draw.text((x, y), text, font=font, fill="black", stroke_width=15, stroke_fill="yellow")
    fname2 = "LogoByAnie.png"
    img.save(fname2, "png")
    await tbot.send_file(event.chat_id, fname2, caption="Made By Harita")
    if os.path.exists(fname2):
            os.remove(fname2)
 except Exception as e:
   await event.reply(f'Error Report @HaritaSupport, {e}')

file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 In Beta!.
 - /logo <text>
Module Not Finished.!
Send Logo Bgs and Fonts to Bot DM! will add to module.
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
