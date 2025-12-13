class script(object):

    # ───────────────────────────────────
    # START / HELP / ABOUT
    # ───────────────────────────────────

    START_TXT = (
        "<b>👋 Hey {},</b>\n"
        "<b>I'm P I X I E — your smart movie search companion 🎬</b>\n\n"
        "<i>Just send a movie name (correct spelling works best).</i>"
    )

    HELP_TXT = (
        "<b>🛠 Help Center</b>\n\n"
        "P I X I E helps you search movies, manage filters, "
        "connect chats, and more.\n\n"
        "👇 Select a category below to explore commands."
    )

    ABOUT_TXT = (
        "<b>📌 Bot Information</b>\n\n"
        "🤖 <b>Name:</b> {}\n"
        "👨‍💻 <b>Creator:</b> <a href='https://t.me/TitanBotUpdates'>Titan Bots</a>\n"
        "📚 <b>Library:</b> Pyrogram\n"
        "🐍 <b>Language:</b> Python 3\n"
        "🗄 <b>Database:</b> MongoDB\n"
        "🌐 <b>Server:</b> Koyeb\n"
        "🔖 <b>Version:</b> v1.0 • Beta\n\n"
        "<i>Built for speed, stability, and smooth movie searching 🚀</i>"
    )

    SOURCE_TXT = (
        "<b>📦 Open Source Notice</b>\n\n"
        "This bot is part of the <b>SPLAT</b> open-source project.\n\n"
        "🔗 <b>Source Code:</b>\n"
        "https://github.com/aidenhakimoff/Splat-Search-Bot\n\n"
        "<i>Feel free to fork or contribute 💡</i>"
    )

    # ───────────────────────────────────
    # FILTERS
    # ───────────────────────────────────

    MANUELFILTER_TXT = (
        "<b>🎛 Manual Filters — Guide</b>\n\n"
        "Filters allow automatic replies when a keyword is detected.\n\n"
        "<b>⚠ Important Notes</b>\n"
        "• Bot must be <b>admin</b>\n"
        "• Only <b>admins</b> can add filters\n"
        "• Alert button limit: <b>64 characters</b>\n\n"
        "<b>📝 Commands</b>\n"
        "• <code>/filter</code> — add a filter\n"
        "• <code>/filters</code> — list filters\n"
        "• <code>/del</code> — delete a filter\n"
        "• <code>/delall</code> — delete all filters (owner only)"
    )

    # ───────────────────────────────────
    # BUTTONS
    # ───────────────────────────────────

    BUTTON_TXT = (
        "<b>🔘 Inline Buttons — Guide</b>\n\n"
        "P I X I E supports <b>URL</b> and <b>Alert</b> buttons.\n\n"
        "<b>⚠ Notes</b>\n"
        "• Message text is mandatory\n"
        "• Works with all media types\n"
        "• Use correct markdown syntax\n\n"
        "<b>🔗 URL Button</b>\n"
        "<code>[Text](buttonurl:https://t.me/TitanBotUpdates)</code>\n\n"
        "<b>⚠ Alert Button</b>\n"
        "<code>[Text](buttonalert:This is an alert)</code>"
    )

    # ───────────────────────────────────
    # AUTO FILTER
    # ───────────────────────────────────

    AUTOFILTER_TXT = (
        "<b>🤖 Auto Filter — How It Works</b>\n\n"
        "Automatically indexes files from channels.\n\n"
        "<b>📌 Requirements</b>\n"
        "• Make me <b>admin</b> (private channels)\n"
        "• No camrips / porn / fake files\n"
        "• Forward last message <b>with quotes</b>\n\n"
        "<i>I’ll index everything automatically 🗂</i>"
    )

    # ───────────────────────────────────
    # CONNECTIONS
    # ───────────────────────────────────

    CONNECTION_TXT = (
        "<b>🔗 Connections — Guide</b>\n\n"
        "Manage group filters from PM to avoid spam.\n\n"
        "<b>📌 Notes</b>\n"
        "• Admins only\n"
        "• Use <code>/connect</code> in group\n\n"
        "<b>📝 Commands</b>\n"
        "• <code>/connect</code> — connect group\n"
        "• <code>/disconnect</code> — disconnect\n"
        "• <code>/connections</code> — list connections"
    )

    # ───────────────────────────────────
    # EXTRA MODULES
    # ───────────────────────────────────

    EXTRAMOD_TXT = (
        "<b>🧰 Extra Tools</b>\n\n"
        "Useful commands for quick information.\n\n"
        "<b>📝 Commands</b>\n"
        "• <code>/id</code> — user ID\n"
        "• <code>/info</code> — user info\n"
        "• <code>/imdb</code> — IMDb details\n"
        "• <code>/search</code> — movie search"
    )

    # ───────────────────────────────────
    # ADMIN MODULES
    # ───────────────────────────────────

    ADMIN_TXT = (
        "<b>🔐 Admin Controls</b>\n\n"
        "Restricted to bot admins only.\n\n"
        "<b>📝 Commands</b>\n"
        "• <code>/logs</code>\n"
        "• <code>/stats</code>\n"
        "• <code>/delete</code>\n"
        "• <code>/users</code>\n"
        "• <code>/chats</code>\n"
        "• <code>/leave</code>\n"
        "• <code>/disable</code>\n"
        "• <code>/ban</code> / <code>/unban</code>\n"
        "• <code>/channel</code>\n"
        "• <code>/broadcast</code>"
    )

    # ───────────────────────────────────
    # STATUS / LOGS
    # ───────────────────────────────────

    STATUS_TXT = (
        "<b>📊 Bot Status</b>\n\n"
        "📁 <b>Total Files:</b> <code>{}</code>\n"
        "👥 <b>Total Users:</b> <code>{}</code>\n"
        "💬 <b>Total Chats:</b> <code>{}</code>\n"
        "💾 <b>Used Storage:</b> <code>{}</code>\n"
        "🆓 <b>Free Storage:</b> <code>{}</code>"
    )

    LOG_TEXT_G = (
        "<b>🆕 New Group Added</b>\n\n"
        "🏷 <b>Group:</b> {} (<code>{}</code>)\n"
        "👥 <b>Members:</b> <code>{}</code>\n"
        "➕ <b>Added By:</b> {}"
    )

    LOG_TEXT_P = (
        "<b>🆕 New User Started Bot</b>\n\n"
        "🆔 <b>User ID:</b> <code>{}</code>\n"
        "👤 <b>Name:</b> {}"
    )
