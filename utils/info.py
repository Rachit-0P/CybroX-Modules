#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import datetime
import platform
import sys
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix, python_version, userbot_version, gitrepo
from utils.scripts import edit_or_reply


@Client.on_message(filters.command(["about", "info"], prefix) & filters.me)
async def about(client: Client, message: Message):
    """Show information about the userbot"""
    await message.edit(
        f"<b>🔥 CybroX-UserBot</b>\n\n"
        f"<b>• Version:</b> <code>{userbot_version}</code>\n"
        f"<b>• Python:</b> <code>{python_version}</code>\n"
        f"<b>• Pyrogram:</b> <code>{'.'.join(str(x) for x in client.pyrogram_version)}</code>\n"
        f"<b>• Platform:</b> <code>{sys.platform}</code>\n"
        f"<b>• System:</b> <code>{platform.version()}</code>\n"
        f"<b>• Architecture:</b> <code>{platform.machine()}</code>\n\n"
        f"<b>• Repository:</b> <a href='https://github.com/YOUR-USERNAME/CybroX-UserBot'>GitHub</a>\n"
        f"<b>• Channel:</b> <a href='https://t.me/YOUR-CHANNEL'>Telegram</a>\n\n"
        f"<b>📅 Current date:</b> <code>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>"
    )


@Client.on_message(filters.command("botinfo", prefix) & filters.me)
async def botinfo(client: Client, message: Message):
    """Show technical information about the userbot"""
    # Get git info
    try:
        last_commit = gitrepo.head.commit
        commit_time = datetime.datetime.fromtimestamp(last_commit.committed_date)
        commit_time_str = commit_time.strftime("%Y-%m-%d %H:%M:%S")
        branch_name = gitrepo.active_branch.name
        
        git_info = (
            f"<b>• Branch:</b> <code>{branch_name}</code>\n"
            f"<b>• Last commit:</b> <code>{last_commit.hexsha[:7]}</code>\n"
            f"<b>• Commit date:</b> <code>{commit_time_str}</code>\n"
            f"<b>• Commit msg:</b> <code>{last_commit.message.strip()}</code>\n"
        )
    except Exception:
        git_info = "<b>• Git info:</b> <code>Not available</code>\n"
    
    await message.edit(
        f"<b>🔧 CybroX-UserBot Technical Info</b>\n\n"
        f"<b>• Python version:</b> <code>{sys.version}</code>\n"
        f"<b>• Executable:</b> <code>{sys.executable}</code>\n"
        f"<b>• Process ID:</b> <code>{os.getpid()}</code>\n\n"
        f"{git_info}\n"
        f"<b>• Device model:</b> <code>{client.device_model}</code>\n"
        f"<b>• System version:</b> <code>{client.system_version}</code>\n"
        f"<b>• App version:</b> <code>{client.app_version}</code>"
    )


@Client.on_message(filters.command("id", prefix) & filters.me)
async def get_id(client: Client, message: Message):
    """Get user/chat ID information"""
    text = f"<b>💬 Chat ID:</b> <code>{message.chat.id}</code>\n"
    
    if message.reply_to_message:
        text += f"<b>🙋‍♂️ Replied User ID:</b> <code>{message.reply_to_message.from_user.id}</code>\n"
        if message.reply_to_message.forward_from:
            text += f"<b>↩️ Forwarded From:</b> <code>{message.reply_to_message.forward_from.id}</code>\n"
    
    text += f"<b>👤 Your ID:</b> <code>{message.from_user.id}</code>"
    
    await edit_or_reply(message, text)


modules_help["info"] = {
    "about": "Show information about userbot",
    "info": "Alias for about command",
    "botinfo": "Show detailed technical information",
    "id": "Get user and chat ID information",
    "__category__": "utils"
}
