import os
import logging
import random
import asyncio
import re
import json
import base64

from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from database.connections_mdb import active_connection

from info import (
    CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL,
    BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT
)

from utils import get_settings, get_size, is_subscribed, save_group_settings, temp

logger = logging.getLogger(__name__)

BATCH_FILES = {}

START_PICS = [
    "assets/start_1.jpg",
    "assets/start_2.jpg",
    "assets/start_3.jpg",
    "assets/start_4.jpg",
]

# --------------------------------------------------
# START COMMAND
# --------------------------------------------------
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):

    # ---------------- GROUP START ----------------
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [InlineKeyboardButton('🤖 Updates', url='https://t.me/+lRax6d2QVoJlNmMx')],
            [InlineKeyboardButton('ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help")]
        ]

        await message.reply(
            script.START_TXT.format(
                message.from_user.mention if message.from_user else message.chat.title,
                temp.U_NAME,
                temp.B_NAME
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

        await asyncio.sleep(2)

        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown")
            )
            await db.add_chat(message.chat.id, message.chat.title)
        return

    # ---------------- PRIVATE START ----------------
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention)
        )

    buttons = [
        [
            InlineKeyboardButton('🔍 Search', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🤖 Updates', url='https://t.me/+lRax6d2QVoJlNmMx')
        ],
        [
            InlineKeyboardButton('ℹ️ Help', callback_data='help'),
            InlineKeyboardButton('😊 About', callback_data='about')
        ]
    ]

    caption = script.START_TXT.format(
        message.from_user.mention,
        temp.U_NAME,
        temp.B_NAME
    )

    # ✅ SAFE IMAGE SEND (NO TELEGRAM CURL ERRORS)
photo = random.choice(START_PICS)

try:
    await message.reply_photo(
        photo=photo,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
except Exception as e:
    logger.warning(f"Start image failed: {e}")
    await message.reply_text(
        caption,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


# --------------------------------------------------
# ADMIN: CHANNEL LIST
# --------------------------------------------------
@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    channels = CHANNELS if isinstance(CHANNELS, list) else [CHANNELS]
    text = '📑 **Indexed channels/groups**\n'

    for channel in channels:
        chat = await bot.get_chat(channel)
        text += f"\n@{chat.username}" if chat.username else f"\n{chat.title}"

    text += f'\n\n**Total:** {len(channels)}'
    await message.reply(text)

# --------------------------------------------------
# ADMIN: LOGS
# --------------------------------------------------
@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

# --------------------------------------------------
# ADMIN: DELETE FILE
# --------------------------------------------------
@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await message.reply("Reply to a file with /delete")

    msg = await message.reply("Processing...")

    for t in ("document", "video", "audio"):
        media = getattr(reply, t, None)
        if media:
            break
    else:
        return await msg.edit("Unsupported file type")

    file_id, _ = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({'_id': file_id})
    if result.deleted_count:
        return await msg.edit("File deleted from database")

    await msg.edit("File not found")

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------
@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grp_id = await active_connection(str(userid))
        if not grp_id:
            return await message.reply("I'm not connected to any group.")
        chat = await client.get_chat(grp_id)
        title = chat.title
    else:
        grp_id = message.chat.id
        title = message.chat.title

    st = await client.get_chat_member(grp_id, userid)
    if st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and str(userid) not in ADMINS:
        return

    settings = await get_settings(grp_id)
    if not settings:
        return

    buttons = [
        [
            InlineKeyboardButton('Filter Button', callback_data=f'setgs#button#{settings["button"]}#{grp_id}'),
            InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                 callback_data=f'setgs#button#{settings["button"]}#{grp_id}')
        ]
    ]

    await message.reply_text(
        f"<b>Settings for {title}</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
