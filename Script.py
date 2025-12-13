class script(object):

    # ───────────────────────────────────
    # START / HELP / ABOUT
    # ───────────────────────────────────

    START_TXT = """
👋 Hey {},  
Welcome to **{}** — your smart movie search companion!

🎬 Send me your movie name with correct spelling and I’ll find it for you instantly.  
"""

    HELP_TXT = """
🛠 **Help Menu**

I’m here to help you search, manage filters, connect chats, and more.  
Choose a category below to explore commands 👇
"""

    ABOUT_TXT = """
📌 **Bot Information**

**🤖 Name:** {}  
**👨‍💻 Creator:** <a href='https://t.me/TitanBotUpdates'>Titan Bots</a>  
**📚 Library:** Pyrogram  
**🐍 Language:** Python 3  
**🗄 Database:** MongoDB  
**🌐 Server:** Koyeb  
**🔖 Version:** v1.0 • Beta  

I’m built for speed, stability, and smooth movie searching 🚀
"""

    SOURCE_TXT = """
📦 **Open Source Notice**

This bot is part of the SPLAT open-source project.

🔗 **Source Code:**  
https://github.com/aidenhakimoff/Splat-Search-Bot

Feel free to contribute or fork 💡
"""

    # ───────────────────────────────────
    # FILTERS
    # ───────────────────────────────────

    MANUELFILTER_TXT = """
🎛 **Manual Filters — Guide**

Filters allow the bot to automatically reply when a keyword is detected.

🔔 **Important Notes**
1. The bot must be **admin** in the chat.  
2. Only **admins** can create filters.  
3. Alert buttons support up to **64 characters**.

📝 **Commands**
• `/filter` — add a new filter  
• `/filters` — list active filters  
• `/del` — delete a filter  
• `/delall` — delete all filters (owner only)
"""

    # ───────────────────────────────────
    # BUTTONS
    # ───────────────────────────────────

    BUTTON_TXT = """
🔘 **Inline Buttons — Guide**

Splat supports both **URL buttons** and **Alert buttons**.

⚠️ **Notes**
1. Telegram requires a message body — buttons alone are not allowed.  
2. Buttons work with any media type.  
3. Follow proper Markdown formatting.

🔗 **URL Button Example**
`[Text](buttonurl:https://t.me/TitanBotUpdates)`

⚠️ **Alert Button Example**
`[Text](buttonalert:This is an alert message)`
"""

    # ───────────────────────────────────
    # AUTO FILTER
    # ───────────────────────────────────

    AUTOFILTER_TXT = """
🤖 **Auto Filter — How It Works**

Auto Filter automatically indexes files from a channel into the database.

📌 **Requirements**
1. Make me **admin** in your channel (if private).  
2. Your channel must not contain:
   • camrips  
   • porn  
   • fake files  
3. Forward the **last message** from the channel **with quotes**.  
   I’ll index all files automatically 🗂
"""

    # ───────────────────────────────────
    # CONNECTIONS
    # ───────────────────────────────────

    CONNECTION_TXT = """
🔗 **Connections — Guide**

Connections allow managing filters in PM instead of group chat,  
keeping the group clean from clutter.

📌 **Notes**
1. Only admins can create connections.  
2. Use `/connect` in a group to link it to your PM.

📝 **Commands**
• `/connect` — connect a group  
• `/disconnect` — disconnect a chat  
• `/connections` — list your connections
"""

    # ───────────────────────────────────
    # EXTRA MODULES
    # ───────────────────────────────────

    EXTRAMOD_TXT = """
🧰 **Extra Tools**

Useful commands for retrieving information.

📝 **Commands**
• `/id` — get user ID  
• `/info` — detailed user info  
• `/imdb` — movie details from IMDb  
• `/search` — search movies across sources
"""

    # ───────────────────────────────────
    # ADMIN MODULES
    # ───────────────────────────────────

    ADMIN_TXT = """
🔐 **Admin Controls**

These commands are only for bot admins.

📝 **Commands**
• `/logs` — recent error logs  
• `/stats` — file database stats  
• `/delete` — remove a file from DB  
• `/users` — list bot users  
• `/chats` — list connected chats  
• `/leave` — make bot leave a chat  
• `/disable` — disable chat  
• `/ban` — ban a user  
• `/unban` — unban a user  
• `/channel` — list connected channels  
• `/broadcast` — broadcast a message
"""

    # ───────────────────────────────────
    # STATUS / LOGS
    # ───────────────────────────────────

    STATUS_TXT = """
📊 **Bot Status**

• **Total Files:** `{}`  
• **Total Users:** `{}`  
• **Total Chats:** `{}`  
• **Used Storage:** `{}`  
• **Free Storage:** `{}`  
"""

    LOG_TEXT_G = """
🆕 **New Group Added**

🏷 Group: {} (`{}`)  
👥 Members: `{}`  
➕ Added By: {}
"""

    LOG_TEXT_P = """
🆕 **New User Started Bot**

🆔 User ID: `{}`  
👤 Name: {}
"""
