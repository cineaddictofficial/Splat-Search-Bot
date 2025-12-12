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
    ADMINS,
    AUTH_CHANNEL,
    CUSTOM_FILE_CAPTION,
)
from utils import (
    get_size,
    is_subscribed,
    get_poster,
    search_gagala,
    temp,
    get_settings,
    save_group_settings
)

from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import del_all, find_filter, get_filters
from database.connections_mdb import (
    active_connection,
    all_connections,
    delete_connection,
    if_active,
    make_active,
    make_inactive
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

# ─────────────────────────────
# GROUP MESSAGE HANDLER
# ─────────────────────────────
@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if await manual_filters(client, message) is False:
        await auto_filter(client, message)

# ─────────────────────────────
# PRIVATE MESSAGE SEARCH
# ─────────────────────────────
@Client.on_message(filters.private & filters.text & filters.incoming)
async def private_search(client, message):
    if message.text.startswith("/"):
        return
    await auto_filter(client, message)

# ─────────────────────────────
# PAGINATION
# ─────────────────────────────
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(client, query):
    try:
        ident, req, key, offset = query.data.split("_")
        if int(req) not in [query.from_user.id, 0]:
            return await query.answer("Not for you!", show_alert=True)

        offset = int(offset)
        search = BUTTONS.get(key)
        if not search:
            return await query.answer("Old message expired", show_alert=True)

        files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
        settings = await get_settings(query.message.chat.id)

        btn = []
        for file in files:
            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}"
                    if settings["button"]
                    else file.file_name,
                    callback_data=f"file#{file.file_id}"
                )
            ])

        if n_offset:
            btn.append([
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{offset-10 if offset else 0}"),
                InlineKeyboardButton(
                    f"📃 {math.ceil(offset/10)+1}/{math.ceil(total/10)}",
                    callback_data="pages"
                ),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ])

        try:
            await query.message.edit_reply_markup(InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass

        await query.answer()
    except Exception as e:
        logger.exception(e)
        await query.answer("Error")

# ─────────────────────────────
# AUTO FILTER (CORE SEARCH LOGIC)
# ─────────────────────────────
async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)

        if message.text.startswith("/"):
            return

        search = message.text.strip()
        files, offset, total = await get_search_results(search.lower(), offset=0, filter=True)

        if not files:
            if settings["spell_check"]:
                return await advantage_spell_chok(message)
            return
    else:
        message = msg.message.reply_to_message
        search, files, offset, total = spoll
        settings = await get_settings(message.chat.id)

    pre = "filep" if settings["file_secure"] else "file"

    buttons = [
        [InlineKeyboardButton(
            f"[{get_size(f.file_size)}] {f.file_name}",
            callback_data=f"{pre}#{f.file_id}"
        )] for f in files
    ]

    if offset:
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        buttons.append([
            InlineKeyboardButton("📃 Pages", callback_data="pages"),
            InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}")
        ])

    imdb = await get_poster(search, file=files[0].file_name) if settings["imdb"] else None
    cap = script.IMDB_TEMPLATE.format(**imdb, query=search) if imdb else f"Results for **{search}**"

    try:
        if imdb and imdb.get("poster"):
            await message.reply_photo(imdb["poster"], caption=cap[:1024],
                                      reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(buttons))
    except Exception:
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(buttons))

    if spoll:
        await msg.message.delete()

# ─────────────────────────────
# SPELL CHECK
# ─────────────────────────────
async def advantage_spell_chok(msg):
    query = re.sub(r"(movie|film|please|pls|send)", "", msg.text, flags=re.I).strip()
    results = await search_gagala(query)

    if not results:
        return await msg.reply("No similar movies found.")

    SPELL_CHECK[msg.id] = results[:5]
    buttons = [[
        InlineKeyboardButton(m, callback_data=f"spolling#0#{i}")
    ] for i, m in enumerate(results[:5])]

    buttons.append([InlineKeyboardButton("Close", callback_data="close_data")])

    await msg.reply("Did you mean?", reply_markup=InlineKeyboardMarkup(buttons))

# ─────────────────────────────
# MANUAL FILTERS
# ─────────────────────────────
async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    keywords = await get_filters(group_id)

    for keyword in sorted(keywords, key=len, reverse=True):
        if re.search(rf"\b{re.escape(keyword)}\b", name, re.I):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)
            if reply_text:
                reply_text = reply_text.replace("\\n", "\n")

            try:
                if fileid and fileid != "None":
                    await message.reply_cached_media(
                        fileid,
                        caption=reply_text,
                        reply_markup=InlineKeyboardMarkup(eval(btn)) if btn else None
                    )
                else:
                    await message.reply(
                        reply_text,
                        reply_markup=InlineKeyboardMarkup(eval(btn)) if btn else None
                    )
            except Exception as e:
                logger.exception(e)
            return True
    return False
