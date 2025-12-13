import asyncio
import re
import ast
import math
import logging

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import (
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
from info import ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from utils import (
    get_size,
    is_subscribed,
    get_poster,
    search_gagala,
    temp,
    get_settings
)

from database.ia_filterdb import get_file_details, get_search_results
from database.filters_mdb import find_filter, get_filters

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

# ─────────────────────────────
# FILE CALLBACK HANDLER (FIXED)
# ─────────────────────────────
@Client.on_callback_query(filters.regex(r"^(file|filep)#"))
async def file_callback_handler(client, query: CallbackQuery):
    try:
        ident, file_id = query.data.split("#")
        files = await get_file_details(file_id)

        if not files:
            return await query.answer("File not found.", show_alert=True)

        file = files[0]
        settings = await get_settings(query.message.chat.id)

        caption = file.caption or file.file_name
        size = get_size(file.file_size)

        if CUSTOM_FILE_CAPTION:
            try:
                caption = CUSTOM_FILE_CAPTION.format(
                    file_name=file.file_name,
                    file_size=size,
                    file_caption=caption
                )
            except Exception:
                pass

        # ───── PRIVATE CHAT ─────
        if query.message.chat.type == enums.ChatType.PRIVATE:
            status = await query.message.reply("⏳ Sending your file...")

            await client.send_cached_media(
                chat_id=query.from_user.id,
                file_id=file.file_id,
                caption=caption,
                protect_content=True if ident == "filep" else False
            )

            await status.delete()
            await query.answer()

            try:
                await query.message.delete()
            except Exception:
                pass
            return

        # ───── GROUP CHAT ─────
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            return await query.answer(
                url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}"
            )

        if settings.get("botpm"):
            return await query.answer(
                url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}"
            )

        await query.answer("Check your PM 👇", show_alert=True)

    except UserIsBlocked:
        await query.answer("❌ Unblock the bot first.", show_alert=True)

    except PeerIdInvalid:
        await query.answer(
            url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}"
        )

    except Exception as e:
        logger.exception(e)
        await query.answer("Error occurred", show_alert=True)


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
        _, req, key, offset = query.data.split("_")
        if int(req) not in [query.from_user.id, 0]:
            return await query.answer("Not for you!", show_alert=True)

        offset = int(offset)
        search = BUTTONS.get(key)
        if not search:
            return await query.answer("Message expired", show_alert=True)

        files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
        settings = await get_settings(query.message.chat.id)
        pre = "filep" if settings["file_secure"] else "file"

        buttons = [[
            InlineKeyboardButton(
                text=f"[{get_size(f.file_size)}] {f.file_name}",
                callback_data=f"{pre}#{f.file_id}"
            )
        ] for f in files]

        if n_offset:
            buttons.append([
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{max(offset-10, 0)}"),
                InlineKeyboardButton(
                    f"📃 {math.ceil(offset/10)+1}/{math.ceil(total/10)}",
                    callback_data="pages"
                ),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ])

        try:
            await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
        except MessageNotModified:
            pass

        await query.answer()
    except Exception as e:
        logger.exception(e)
        await query.answer("Error")


# ─────────────────────────────
# AUTO FILTER (CORE SEARCH)
# ─────────────────────────────
async def auto_filter(client, message, spoll=False):
    settings = await get_settings(message.chat.id)
    search = message.text.strip()

    files, offset, total = await get_search_results(search.lower(), offset=0, filter=True)

    if not files:
        if settings["spell_check"]:
            return await advantage_spell_chok(message)
        return

    pre = "filep" if settings["file_secure"] else "file"

    buttons = [[
        InlineKeyboardButton(
            text=f"[{get_size(f.file_size)}] {f.file_name}",
            callback_data=f"{pre}#{f.file_id}"
        )
    ] for f in files]

    if offset:
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        buttons.append([
            InlineKeyboardButton("📃 Pages", callback_data="pages"),
            InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}")
        ])

    imdb = await get_poster(search, file=files[0].file_name) if settings["imdb"] else None
    caption = script.IMDB_TEMPLATE.format(**imdb, query=search) if imdb else f"Results for **{search}**"

    try:
        if imdb and imdb.get("poster"):
            await message.reply_photo(
                imdb["poster"],
                caption=caption[:1024],
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await message.reply_text(
                caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
        await message.reply_text(
            caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# ─────────────────────────────
# SPELL CHECK
# ─────────────────────────────
async def advantage_spell_chok(message):
    query = re.sub(r"(movie|film|pls|please|send)", "", message.text, flags=re.I).strip()
    results = await search_gagala(query)

    if not results:
        return await message.reply("No similar movies found.")

    buttons = [[
        InlineKeyboardButton(
            text=m,
            callback_data=f"spolling#0#{i}"
        )
    ] for i, m in enumerate(results[:5])]

    buttons.append([InlineKeyboardButton("Close", callback_data="close_data")])

    await message.reply(
        "Did you mean?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


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
            reply_text = reply_text.replace("\\n", "\n") if reply_text else ""

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
