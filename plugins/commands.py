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
    CHANNELS,
    ADMINS,
    AUTH_CHANNEL,
    LOG_CHANNEL,
    BATCH_FILE_CAPTION,
    CUSTOM_FILE_CAPTION,
    PROTECT_CONTENT,
)

from utils import (
    get_settings,
    get_size,
    is_subscribed,
    save_group_settings,
    temp,
)

logger = logging.getLogger(__name__)

# ===============================
# START IMAGES (LOCAL FILES ONLY)
# ===============================
START_PICS = [
    "images/start_1.png",
    "images/start_2.png",
]

BATCH_FILES = {}


# ===============================
# /start COMMAND
# ===============================
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):

    # ---------- GROUP START ----------
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [InlineKeyboardButton("🤖 Updates", url="https://t.me/+lRax6d2QVoJlNmMx")],
            [InlineKeyboardButton("ℹ️ Help", url=f"https://t.me/{temp.U_NAME}?start=help")],
        ]
        await message.reply(
            script.START_TXT.format(
                message.from_user.mention if message.from_user else message.chat.title,
                temp.U_NAME,
                temp.B_NAME,
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
        )

        await asyncio.sleep(2)

        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(
                    message.chat.title, message.chat.id, total, "Unknown"
                ),
            )
            await db.add_chat(message.chat.id, message.chat.title)
        return

    # ---------- PRIVATE START ----------
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(
                message.from_user.id, message.from_user.mention
            ),
        )

    buttons = [
        [
            InlineKeyboardButton("🔍 Search", switch_inline_query_current_chat=""),
            InlineKeyboardButton("🤖 Updates", url="https://t.me/+lRax6d2QVoJlNmMx"),
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help"),
            InlineKeyboardButton("😊 About", callback_data="about"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    caption = script.START_TXT.format(
        message.from_user.mention,
        temp.U_NAME,
        temp.B_NAME,
    )

    # ---------- SAFE IMAGE SEND ----------
    photo = random.choice(START_PICS)

    try:
        if os.path.exists(photo):
            await message.reply_photo(
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML,
            )
        else:
            raise FileNotFoundError(photo)

    except Exception as e:
        logger.error(f"START IMAGE ERROR: {e}")
        await message.reply_text(
            caption,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )


# ===============================
# ADMIN: /channel
# ===============================
@Client.on_message(filters.command("channel") & filters.user(ADMINS))
async def channel_info(bot, message):
    channels = CHANNELS if isinstance(CHANNELS, list) else [CHANNELS]
    text = "📑 **Indexed channels/groups**\n"

    for channel in channels:
        chat = await bot.get_chat(channel)
        text += "\n@" + chat.username if chat.username else "\n" + chat.title

    text += f"\n\n**Total:** {len(channels)}"
    await message.reply(text)


# ===============================
# ADMIN: /logs
# ===============================
@Client.on_message(filters.command("logs") & filters.user(ADMINS))
async def log_file(bot, message):
    try:
        await message.reply_document("TelegramBot.log")
    except Exception as e:
        await message.reply(str(e))


# ===============================
# ADMIN: /delete
# ===============================
@Client.on_message(filters.command("delete") & filters.user(ADMINS))
async def delete(bot, message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await message.reply("Reply to a file with /delete")

    msg = await message.reply("Processing...⏳")

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media:
            break
    else:
        return await msg.edit("Unsupported file type")

    file_id, _ = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({"_id": file_id})
    await msg.edit(
        "File deleted successfully" if result.deleted_count else "File not found"
    )


# ===============================
# ADMIN: /deleteall
# ===============================
@Client.on_message(filters.command("deleteall") & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply(
        "This will delete all indexed files.\nContinue?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("YES", callback_data="autofilter_delete")],
                [InlineKeyboardButton("CANCEL", callback_data="close_data")],
            ]
        ),
    )


@Client.on_callback_query(filters.regex("^autofilter_delete"))
async def delete_all_index_confirm(bot, query):
    await Media.collection.drop()
    await query.answer("Done")
    await query.message.edit("✅ All indexed files deleted")


# ===============================
# SETTINGS
# ===============================
@Client.on_message(filters.command("settings"))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return

    if message.chat.type == enums.ChatType.PRIVATE:
        grp_id = await active_connection(str(userid))
        if not grp_id:
            return await message.reply("Not connected to any group")
        chat = await client.get_chat(grp_id)
        title = chat.title
    else:
        grp_id = message.chat.id
        title = message.chat.title

    st = await client.get_chat_member(grp_id, userid)
    if st.status not in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ):
        return

    settings = await get_settings(grp_id)
    if not settings:
        return

    await message.reply_text(
        f"<b>Settings for {title}</b>",
        parse_mode=enums.ParseMode.HTML,
    )


# ===============================
# TEMPLATE
# ===============================
@Client.on_message(filters.command("set_template"))
async def save_template(client, message):
    if len(message.command) < 2:
        return await message.reply("No template provided")

    template = message.text.split(" ", 1)[1]
    userid = message.from_user.id

    grp_id = (
        await active_connection(str(userid))
        if message.chat.type == enums.ChatType.PRIVATE
        else message.chat.id
    )

    await save_group_settings(grp_id, "template", template)
    await message.reply("✅ Template updated successfully")
