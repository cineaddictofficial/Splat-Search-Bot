import logging
import asyncio
import secrets

from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

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
# 🚀 START IMAGES — TELEGRAM CACHED FILE_IDS
# =====================================================
START_IMAGE_FILE_IDS = [
    "AgACAgUAAxkDAAMHaT6P0G7EJhDGhB-C6r3Ck2KOtE8AAvILaxuWBPlVou9Yvd6lKlMACAEAAwIAA3cABx4E",
]

@Client.on_message(filters.command("genid") & filters.private)
async def gen_file_id(client, message):
    msg = await message.reply_photo("images/start_4.jpg")
    await message.reply_text(f"FILE_ID:\n<code>{msg.photo.file_id}</code>",
                             parse_mode=enums.ParseMode.HTML)
    
# =====================================================
# /start COMMAND
# =====================================================
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):

    caption = script.START_TXT.format(
        message.from_user.mention if message.from_user else message.chat.title
    )

    # -------- GROUP --------
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
        asyncio.create_task(_log_group(client, message))
        return

    # -------- PRIVATE --------
    reply_markup = _start_buttons()

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
        logger.error(f"START IMAGE ERROR: {e}")
        await message.reply_text(
            caption,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )

    asyncio.create_task(_log_user(client, message))


# =====================================================
# CALLBACKS — START / HELP / ABOUT
# =====================================================
@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client, query: CallbackQuery):
    await query.answer()
    await query.message.edit_caption(
        script.HELP_TXT,
        reply_markup=_help_buttons(),
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client, query: CallbackQuery):
    await query.answer()
    await query.message.edit_caption(
        script.ABOUT_TXT.format(temp.B_NAME),
        reply_markup=_back_to_start(),
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_callback_query(filters.regex("^back_start$"))
async def back_start(client, query: CallbackQuery):
    await query.answer()
    await query.message.edit_caption(
        script.START_TXT.format(query.from_user.mention),
        reply_markup=_start_buttons(),
        parse_mode=enums.ParseMode.HTML,
    )


# =====================================================
# HELP CATEGORIES
# =====================================================
@Client.on_callback_query(filters.regex("^help_filters$"))
async def help_filters(client, query):
    await query.answer()
    await query.message.edit_caption(
        script.MANUELFILTER_TXT,
        reply_markup=_back_to_help(),
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_callback_query(filters.regex("^help_buttons$"))
async def help_buttons(client, query):
    await query.answer()
    await query.message.edit_caption(
        script.BUTTON_TXT,
        reply_markup=_back_to_help(),
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_callback_query(filters.regex("^help_autofilter$"))
async def help_autofilter(client, query):
    await query.answer()
    await query.message.edit_caption(
        script.AUTOFILTER_TXT,
        reply_markup=_back_to_help(),
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_callback_query(filters.regex("^help_connections$"))
async def help_connections(client, query):
    await query.answer()
    await query.message.edit_caption(
        script.CONNECTION_TXT,
        reply_markup=_back_to_help(),
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_callback_query(filters.regex("^help_extra$"))
async def help_extra(client, query):
    await query.answer()
    await query.message.edit_caption(
        script.EXTRAMOD_TXT,
        reply_markup=_back_to_help(),
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_callback_query(filters.regex("^help_admin$"))
async def help_admin(client, query):
    await query.answer()
    await query.message.edit_caption(
        script.ADMIN_TXT,
        reply_markup=_back_to_help(),
        parse_mode=enums.ParseMode.HTML,
    )


# =====================================================
# BUTTON BUILDERS
# =====================================================
def _start_buttons():
    return InlineKeyboardMarkup(
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


def _help_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎛 Filters", callback_data="help_filters"),
                InlineKeyboardButton("🔘 Buttons", callback_data="help_buttons"),
            ],
            [
                InlineKeyboardButton("🤖 Auto Filter", callback_data="help_autofilter"),
                InlineKeyboardButton("🔗 Connections", callback_data="help_connections"),
            ],
            [
                InlineKeyboardButton("🧰 Extra", callback_data="help_extra"),
                InlineKeyboardButton("🔐 Admin", callback_data="help_admin"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_start"),
            ],
        ]
    )


def _back_to_help():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back to Help", callback_data="help")]]
    )


def _back_to_start():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]
    )


# =====================================================
# BACKGROUND LOGGING
# =====================================================
async def _log_user(client, message):
    try:
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_P.format(
                    message.from_user.id,
                    message.from_user.mention,
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
                    message.chat.title,
                    message.chat.id,
                    total,
                    "Unknown",
                ),
            )
            await db.add_chat(message.chat.id, message.chat.title)
    except Exception as e:
        logger.error(f"GROUP LOG ERROR: {e}")
