class script(object):
    START_TXT = """Hello {},
My name is <a href=https://t.me/{}>{}</a>, I can provide movies, Just search and enjoy. 😍"""
    HELP_TXT = """Hey {},
Here is the help for my commands."""
    ABOUT_TXT = """✯ My Name: {}
✯ Creator: <a href=https://t.me/TitanBotUpdates>Titan Bots</a>
✯ Library: Pyrogram
✯ Language: Python 3
✯ Database: MongoDB
✯ Bot Server: Koyeb
✯ Build Status: v1.0 [ Beta ]"""
    SOURCE_TXT = """<b>NOTE:</b>
- SplatSearchBot is a open source project. 
- Source - https://github.com/aidenhakimoff/Splat-Search-Bot

<b>DEVS:</b>
- <a href=https://t.me/TitanBotUpdates>Titan Bots</a>"""
    MANUELFILTER_TXT = """<b>Help for Filters:</b>

- Filter is the feature were users can set automated replies for a particular keyword and Splat will respond whenever a keyword is found the message.

<b>NOTE:</b>
1. Splat should have admin privillage.
2. only admins can add filters in a chat.
3. alert buttons have a limit of 64 characters.

<b>Commands and Usage:</b>
• /filter - <code>add a filter in chat</code>
• /filters - <code>list all the filters of a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>delete the whole filters in a chat (chat owner only)</code>"""
    BUTTON_TXT = """<b>Help for Buttons:</b>

- Splat supports both url and alert inline buttons.

<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. Splat supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format.

<b>URL Buttons:</b>
<code>[Button Text](buttonurl:https://t.me/TitanBotUpdates)</code>

<b>Alert Buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""
    AUTOFILTER_TXT = """<b>Help for Auto Filter:</b>

<b>NOTE:</b>
1. Make me the admin of your channel if it's private.
2. make sure that your channel does not contains camrips, porn and fake files.
3. Forward the last message to me with quotes.
 I'll add all the files in that channel to my db."""
    CONNECTION_TXT = """<b>Help for Connections:</b>

- Used to connect bot to PM for managing filters. 
- it helps to avoid spamming in groups.

<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM.

<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""
    EXTRAMOD_TXT = """<b>Help for Extra Modules:</b>

<b>NOTE:</b>
These are the extra features of Splat.

<b>Commands and Usage:</b>
• /id - <code>get id of a specified user.</code>
• /info  - <code>get information about a user.</code>
• /imdb  - <code>get the film information from IMDb source.</code>
• /search  - <code>get the film information from various sources.</code>"""
    ADMIN_TXT = """<b>Help for Admins:</b>

<b>NOTE:</b>
This module only works for my admins.

<b>Commands and Usage:</b>
• /logs - <code>to get the rescent errors</code>
• /stats - <code>to get status of files in db.</code>
• /delete - <code>to delete a specific file from db.</code>
• /users - <code>to get list of my users and ids.</code>
• /chats - <code>to get list of the my chats and ids </code>
• /leave  - <code>to leave from a chat.</code>
• /disable  -  <code>do disable a chat.</code>
• /ban  - <code>to ban a user.</code>
• /unban  - <code>to unban a user.</code>
• /channel - <code>to get list of total connected channels</code>
• /broadcast - <code>to broadcast a message to all users</code>"""
    STATUS_TXT = """★ Total Files: <code>{}</code>
★ Total Users: <code>{}</code>
★ Total Chats: <code>{}</code>
★ Used Storage: <code>{}</code>
★ Free Storage: <code>{}</code>"""
    LOG_TEXT_G = """#NewGroup
Group = {}(<code>{}</code>)
Total Members = <code>{}</code>
Added By - {}
"""
    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}
"""
