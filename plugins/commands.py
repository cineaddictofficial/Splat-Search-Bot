import logging
import asyncio
import secrets

from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.ia_filterdb import Media, unpack_new_file_id
from database.users_chats_db import db
from database.connections_mdb import active_connection

from info import (
    CHANNELS,
    ADMINS,
    LOG_CHANNEL,
)

from utils import (
    get_settings,
    save_group_settings,
    temp,
)

logger = logging.getLogger(__name__)

# =====================================================
# 🚀 START IMAGES — TELEGRAM CACHED FILE_IDS (FASTEST)
# =====================================================
# Replace these with YOUR real file_ids
START_IMAGE_FILE_IDS = [
    "AgACAgUAAxkBAAIBQ2XYZ1111111111111111111",
    "AgACAgUAAxkBAAIBQ2XYZ2222222222222222222",
]

# =====================================================
# /start COMMAND (ZERO DELAY)
# =====================================================
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):

    caption = script.START_TXT.format(
        message.from_user.mention if message.from_user else message.chat.title,
        temp.U_NAME,
        temp.B_NAME,
    )

    # ---------------- GROUP ----------------
    if message.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
        await message.reply(
            caption,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🤖 Updates", url="https://t.me/+lRax6d2QVoJlNmMx")],
                    [InlineKeyboardButton("ℹ️ Help", url=f"https://t.me/{temp.U_NAME}?start=help")],
                ]
            ),
            parse_mode=enums.ParseMode.HTML,
        )

        # background logging (NO WAIT)
        asyncio.create_task(_log_group(client, message))
        return

    # ---------------- PRIVATE ----------------
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔍 Search", switch_inline_query_current_chat=""),
                InlineKeyboardButton("🤖 Updates", url="https://t.me/+lRax6d2QVoJlNmMx"),
            ],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                InlineKeyboardButton("😊 About", callback_data="about"),
            ],
        ]
    )

    # ⚡ INSTANT IMAGE SEND (CACHED)
    try:
        file_id = secrets.choice(START_IMAGE_FILE_IDS)
        await client.send_cached_media(
            chat_id=message.chat.id,
            file_id=file_id,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as e:
        logger.error(f"START CACHED IMAGE ERROR: {e}")
        await message.reply_text(
            caption,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )

    # 🚀 background user logging (NO DELAY)
    asyncio.create_task(_log_user(client, message))


# =====================================================
# BACKGROUND TASKS (NON-BLOCKING)
# =====================================================
async def _log_user(client, message):
    try:
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_P.format(
                    message.from_user.id, message.from_user.mention
                ),
            )
    except Exception as e:
        logger.error(f"USER LOG ERROR: {e}")


async def _log_group(client, message):
    try:
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(
                    message.chat.title, message.chat.id, total, "Unknown"
                ),
            )
            await db.add_chat(message.chat.id, message.chat.title)
    except Exception as e:
        logger.error(f"GROUP LOG ERROR: {e}")


# =====================================================
# ADMIN COMMANDS
# =====================================================
@Client.on_message(filters.command("channel") & filters.user(ADMINS))
async def channel_info(bot, message):
    channels = CHANNELS if isinstance(CHANNELS, list) else [CHANNELS]
    text = "📑 **Indexed channels/groups**\n"
    for channel in channels:
        chat = await bot.get_chat(channel)
        text += "\n@" + chat.username if chat.username else "\n" + chat.title
    text += f"\n\n**Total:** {len(channels)}"
    await message.reply(text)


@Client.on_message(filters.command("logs") & filters.user(ADMINS))
async def log_file(bot, message):
    await message.reply_document("TelegramBot.log")


@Client.on_message(filters.command("delete") & filters.user(ADMINS))
async def delete(bot, message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await message.reply("Reply to a file with /delete")

    msg = await message.reply("Processing...")
    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media:
            break
    else:
        return await msg.edit("Unsupported file type")

    file_id, _ = unpack_new_file_id(media.file_id)
    result = await Media.collection.delete_one({"_id": file_id})
    await msg.edit("✅ Deleted" if result.deleted_count else "❌ Not found")


@Client.on_message(filters.command("deleteall") & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply(
        "Delete all indexed files?",
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


@Client.on_message(filters.command("settings"))
async def settings(client, message):
    userid = message.from_user.id
    grp_id = (
        await active_connection(str(userid))
        if message.chat.type == enums.ChatType.PRIVATE
        else message.chat.id
    )
    settings = await get_settings(grp_id)
    if settings:
        await message.reply("⚙ Settings loaded")


@Client.on_message(filters.command("set_template"))
async def save_template(client, message):
    if len(message.command) < 2:
        return await message.reply("No template provided")

    template = message.text.split(" ", 1)[1]
    grp_id = (
        await active_connection(str(message.from_user.id))
        if message.chat.type == enums.ChatType.PRIVATE
        else message.chat.id
    )
    await save_group_settings(grp_id, "template", template)
    await message.reply("✅ Template updated")
