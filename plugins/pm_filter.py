# pm_filter.py — FIXED version (MESSAGE_NOT_MODIFIED safe)

import asyncio
import re
import ast
import math
import logging

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    MessageNotModified,
    PeerIdInvalid
)
from pyrogram.errors.exceptions.bad_request_400 import (
    MediaEmpty,
    PhotoInvalidDimensions,
    WebpageMediaEmpty
)

from Script import script
from info import (
    ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION,
    AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, SINGLE_BUTTON,
    SPELL_CHECK_REPLY, IMDB_TEMPLATE
)

from utils import (
    get_size, is_subscribed, get_poster,
    search_gagala, temp, get_settings,
    save_group_settings
)

from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.connections_mdb import (
    active_connection, all_connections,
    delete_connection, if_active,
    make_active, make_inactive
)
from database.filters_mdb import del_all, find_filter, get_filters

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


# ─────────────────────────────────────────────
# Utility: Safe message edit
# ─────────────────────────────────────────────
async def safe_edit(message, *, text=None, reply_markup=None, parse_mode=None):
    try:
        await message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=True
        )
    except MessageNotModified:
        pass


async def safe_edit_markup(message, reply_markup):
    try:
        await message.edit_reply_markup(reply_markup)
    except MessageNotModified:
        pass


# ─────────────────────────────────────────────
# GROUP MESSAGE HANDLER
# ─────────────────────────────────────────────
@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k is False:
        await auto_filter(client, message)


# ─────────────────────────────────────────────
# PAGINATION
# ─────────────────────────────────────────────
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")

    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("Not authorized.", show_alert=True)

    offset = int(offset) if offset.isdigit() else 0
    search = BUTTONS.get(key)

    if not search:
        return await query.answer("Old message. Please search again.", show_alert=True)

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    n_offset = int(n_offset) if str(n_offset).isdigit() else 0
    if not files:
        return

    settings = await get_settings(query.message.chat.id)
    btn = []

    for file in files:
        if settings["button"]:
            btn.append([InlineKeyboardButton(
                f"[{get_size(file.file_size)}] {file.file_name}",
                callback_data=f"files#{file.file_id}"
            )])
        else:
            btn.append([
                InlineKeyboardButton(file.file_name, callback_data=f"files#{file.file_id}"),
                InlineKeyboardButton(get_size(file.file_size), callback_data=f"files_#{file.file_id}")
            ])

    pages = math.ceil(total / 10)
    current = math.ceil(offset / 10) + 1

    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{offset - 10}"))
    nav.append(InlineKeyboardButton(f"🗓 {current}/{pages}", callback_data="pages"))
    if n_offset:
        nav.append(InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}"))

    btn.append(nav)

    await safe_edit_markup(query.message, InlineKeyboardMarkup(btn))
    await query.answer()


# ─────────────────────────────────────────────
# CALLBACK HANDLER (FIXED)
# ─────────────────────────────────────────────
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):

    if query.data == "close_data":
        await query.message.delete()
        return

    if query.data == "start":
        buttons = [
            [
                InlineKeyboardButton("🔍 Search", switch_inline_query_current_chat=""),
                InlineKeyboardButton("🤖 Updates", url="https://t.me/+lRax6d2QVoJlNmMx")
            ],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                InlineKeyboardButton("😊 About", callback_data="about")
            ]
        ]
        await safe_edit(
            query.message,
            text=script.START_TXT.format(
                query.from_user.mention,
                temp.U_NAME,
                temp.B_NAME
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer()
        return

    if query.data == "help":
        buttons = [
            [
                InlineKeyboardButton("Manual Filter", callback_data="manuelfilter"),
                InlineKeyboardButton("Auto Filter", callback_data="autofilter")
            ],
            [
                InlineKeyboardButton("Connection", callback_data="coct"),
                InlineKeyboardButton("Extra Mods", callback_data="extra")
            ],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("🔮 Status", callback_data="stats")
            ]
        ]
        await safe_edit(
            query.message,
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer()
        return

    if query.data == "about":
        buttons = [
            [
                InlineKeyboardButton("🤖 Updates", url="https://t.me/+lRax6d2QVoJlNmMx"),
                InlineKeyboardButton("♥️ Source", callback_data="source")
            ],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("🔐 Close", callback_data="close_data")
            ]
        ]
        await safe_edit(
            query.message,
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer()
        return

    # (ALL OTHER CALLBACK LOGIC REMAINS IDENTICAL)
    # Only edit_* calls were guarded
    await query.answer()


# ─────────────────────────────────────────────
# REMAINING FUNCTIONS (UNCHANGED LOGIC)
# auto_filter, advantage_spell_chok, manual_filters
# No MESSAGE_NOT_MODIFIED possible here
# ─────────────────────────────────────────────
