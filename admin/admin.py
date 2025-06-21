#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Union

from pyrogram import Client, filters, errors
from pyrogram.types import Message, ChatPermissions, ChatPrivileges
from pyrogram.enums import ChatMemberStatus, ChatType

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply, with_reply


async def get_user(client: Client, message: Message) -> Optional[dict]:
    """Get user from message"""
    user_id = None
    user_first_name = None
    
    # If command has arguments
    if len(message.command) > 1:
        # Handle user by username or user ID
        arg = message.command[1]
        
        # Check if arg is a user mention
        if len(message.entities) > 1 and message.entities[1].type == "text_mention":
            return {
                "user_id": message.entities[1].user.id,
                "user_first_name": message.entities[1].user.first_name
            }
            
        # Check if arg is a user ID
        if arg.isdigit():
            user = await client.get_users(int(arg))
            return {
                "user_id": user.id,
                "user_first_name": user.first_name
            }
            
        # Check if arg is a username
        if arg.startswith("@"):
            arg = arg[1:]  # Remove @ symbol
            
        try:
            user = await client.get_users(arg)
            return {
                "user_id": user.id,
                "user_first_name": user.first_name
            }
        except (errors.UsernameNotOccupied, errors.UsernameInvalid):
            return None
    
    # If command is in reply to another message
    if message.reply_to_message and message.reply_to_message.from_user:
        return {
            "user_id": message.reply_to_message.from_user.id,
            "user_first_name": message.reply_to_message.from_user.first_name
        }
        
    return None


async def check_privileges(client: Client, message: Message, privileges: list) -> bool:
    """Check bot and user privileges in chat"""
    chat = message.chat
    
    # Check if command used in a group/supergroup
    if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await edit_or_reply(message, "❌ <b>This command can only be used in groups!</b>")
        return False
    
    # Check if bot has required privileges
    try:
        bot_member = await chat.get_member(client.me.id)
    except errors.ChatAdminRequired:
        await edit_or_reply(message, "❌ <b>I'm not an admin in this chat!</b>")
        return False
    
    missing_privileges = []
    for privilege in privileges:
        if not getattr(bot_member.privileges, privilege):
            missing_privileges.append(privilege.replace("_", " ").title())
    
    if missing_privileges:
        await edit_or_reply(
            message, 
            f"❌ <b>I don't have the required privileges:</b> {', '.join(missing_privileges)}"
        )
        return False
    
    # Check if user has required privileges
    try:
        user_member = await chat.get_member(message.from_user.id)
    except errors.UserNotParticipant:
        await edit_or_reply(message, "❌ <b>You're not even in this chat!</b>")
        return False
    
    if user_member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        await edit_or_reply(message, "❌ <b>You must be an admin to use this command!</b>")
        return False
        
    return True


@Client.on_message(filters.command("ban", prefix) & filters.me)
async def ban_cmd(client: Client, message: Message):
    """Ban user from chat"""
    if not await check_privileges(client, message, ["can_restrict_members"]):
        return
        
    user_dict = await get_user(client, message)
    if not user_dict:
        await edit_or_reply(message, "❌ <b>User not found!</b>")
        return
    
    user_id = user_dict["user_id"]
    user_first_name = user_dict["user_first_name"]
    
    # Check for ban duration and reason
    ban_time = 0
    reason = ""
    
    if len(message.command) > 1:
        if len(message.command) > 2 and message.command[1][0].isdigit():
            time_str = message.command[1].lower()
            
            if time_str[-1] == 'm':
                ban_time = int(time_str[:-1]) * 60
            elif time_str[-1] == 'h':
                ban_time = int(time_str[:-1]) * 3600
            elif time_str[-1] == 'd':
                ban_time = int(time_str[:-1]) * 86400
            else:
                ban_time = int(time_str)
                
            if len(message.command) > 2:
                reason = " ".join(message.command[2:])
        else:
            reason = " ".join(message.command[1:])
    
    # Try to ban user
    try:
        # Notify about the ban
        msg = await edit_or_reply(message, "<b>🔨 Banning user...</b>")
        
        if ban_time > 0:
            ban_until_date = datetime.now() + timedelta(seconds=ban_time)
            await client.ban_chat_member(
                chat_id=message.chat.id, 
                user_id=user_id,
                until_date=ban_until_date
            )
            
            # Format time
            time_text = ""
            if ban_time >= 86400:
                time_text = f"{ban_time // 86400} days"
            elif ban_time >= 3600:
                time_text = f"{ban_time // 3600} hours"
            else:
                time_text = f"{ban_time // 60} minutes"
                
            ban_text = f"<b>🔨 User banned for {time_text}!</b>"
        else:
            await client.ban_chat_member(
                chat_id=message.chat.id, 
                user_id=user_id
            )
            ban_text = "<b>🔨 User banned permanently!</b>"
        
        # Success message
        text = f"{ban_text}\n\n"
        text += f"<b>Chat:</b> {message.chat.title}\n"
        text += f"<b>User:</b> {user_first_name}\n"
        text += f"<b>ID:</b> <code>{user_id}</code>"
        
        if reason:
            text += f"\n<b>Reason:</b> {reason}"
            
        await msg.edit(text)
        
    except errors.ChatAdminRequired:
        await msg.edit("❌ <b>I don't have permission to ban users!</b>")
    except errors.UserAdminInvalid:
        await msg.edit("❌ <b>I can't ban an admin!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> {e}")


@Client.on_message(filters.command("unban", prefix) & filters.me)
async def unban_cmd(client: Client, message: Message):
    """Unban user from chat"""
    if not await check_privileges(client, message, ["can_restrict_members"]):
        return
    
    user_dict = await get_user(client, message)
    if not user_dict:
        await edit_or_reply(message, "❌ <b>User not found!</b>")
        return
    
    user_id = user_dict["user_id"]
    user_first_name = user_dict["user_first_name"]
    
    try:
        msg = await edit_or_reply(message, "<b>🔓 Unbanning user...</b>")
        
        await client.unban_chat_member(
            chat_id=message.chat.id,
            user_id=user_id
        )
        
        # Success message
        text = f"<b>🔓 User unbanned!</b>\n\n"
        text += f"<b>Chat:</b> {message.chat.title}\n"
        text += f"<b>User:</b> {user_first_name}\n"
        text += f"<b>ID:</b> <code>{user_id}</code>"
            
        await msg.edit(text)
        
    except errors.ChatAdminRequired:
        await msg.edit("❌ <b>I don't have permission to unban users!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> {e}")


@Client.on_message(filters.command("kick", prefix) & filters.me)
async def kick_cmd(client: Client, message: Message):
    """Kick user from chat"""
    if not await check_privileges(client, message, ["can_restrict_members"]):
        return
    
    user_dict = await get_user(client, message)
    if not user_dict:
        await edit_or_reply(message, "❌ <b>User not found!</b>")
        return
    
    user_id = user_dict["user_id"]
    user_first_name = user_dict["user_first_name"]
    
    # Check for reason
    reason = ""
    if len(message.command) > 1:
        if len(message.command) > 2 and message.command[1][0].isdigit():
            reason = " ".join(message.command[2:])
        else:
            reason = " ".join(message.command[1:])
    
    try:
        msg = await edit_or_reply(message, "<b>👢 Kicking user...</b>")
        
        # Ban and unban to kick
        await client.ban_chat_member(
            chat_id=message.chat.id, 
            user_id=user_id
        )
        await client.unban_chat_member(
            chat_id=message.chat.id, 
            user_id=user_id
        )
        
        # Success message
        text = f"<b>👢 User kicked!</b>\n\n"
        text += f"<b>Chat:</b> {message.chat.title}\n"
        text += f"<b>User:</b> {user_first_name}\n"
        text += f"<b>ID:</b> <code>{user_id}</code>"
        
        if reason:
            text += f"\n<b>Reason:</b> {reason}"
            
        await msg.edit(text)
        
    except errors.ChatAdminRequired:
        await msg.edit("❌ <b>I don't have permission to kick users!</b>")
    except errors.UserAdminInvalid:
        await msg.edit("❌ <b>I can't kick an admin!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> {e}")


@Client.on_message(filters.command("mute", prefix) & filters.me)
async def mute_cmd(client: Client, message: Message):
    """Mute user in chat"""
    if not await check_privileges(client, message, ["can_restrict_members"]):
        return
    
    user_dict = await get_user(client, message)
    if not user_dict:
        await edit_or_reply(message, "❌ <b>User not found!</b>")
        return
    
    user_id = user_dict["user_id"]
    user_first_name = user_dict["user_first_name"]
    
    # Check for mute duration and reason
    mute_time = 0
    reason = ""
    
    if len(message.command) > 1:
        if len(message.command) > 2 and message.command[1][0].isdigit():
            time_str = message.command[1].lower()
            
            if time_str[-1] == 'm':
                mute_time = int(time_str[:-1]) * 60
            elif time_str[-1] == 'h':
                mute_time = int(time_str[:-1]) * 3600
            elif time_str[-1] == 'd':
                mute_time = int(time_str[:-1]) * 86400
            else:
                mute_time = int(time_str)
                
            if len(message.command) > 2:
                reason = " ".join(message.command[2:])
        else:
            reason = " ".join(message.command[1:])
    
    try:
        msg = await edit_or_reply(message, "<b>🔇 Muting user...</b>")
        
        # Permissions for muted user
        mute_permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False
        )
        
        if mute_time > 0:
            mute_until_date = datetime.now() + timedelta(seconds=mute_time)
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=mute_permissions,
                until_date=mute_until_date
            )
            
            # Format time
            time_text = ""
            if mute_time >= 86400:
                time_text = f"{mute_time // 86400} days"
            elif mute_time >= 3600:
                time_text = f"{mute_time // 3600} hours"
            else:
                time_text = f"{mute_time // 60} minutes"
                
            mute_text = f"<b>🔇 User muted for {time_text}!</b>"
        else:
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=mute_permissions
            )
            mute_text = "<b>🔇 User muted permanently!</b>"
        
        # Success message
        text = f"{mute_text}\n\n"
        text += f"<b>Chat:</b> {message.chat.title}\n"
        text += f"<b>User:</b> {user_first_name}\n"
        text += f"<b>ID:</b> <code>{user_id}</code>"
        
        if reason:
            text += f"\n<b>Reason:</b> {reason}"
            
        await msg.edit(text)
        
    except errors.ChatAdminRequired:
        await msg.edit("❌ <b>I don't have permission to mute users!</b>")
    except errors.UserAdminInvalid:
        await msg.edit("❌ <b>I can't mute an admin!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> {e}")


@Client.on_message(filters.command("unmute", prefix) & filters.me)
async def unmute_cmd(client: Client, message: Message):
    """Unmute user in chat"""
    if not await check_privileges(client, message, ["can_restrict_members"]):
        return
    
    user_dict = await get_user(client, message)
    if not user_dict:
        await edit_or_reply(message, "❌ <b>User not found!</b>")
        return
    
    user_id = user_dict["user_id"]
    user_first_name = user_dict["user_first_name"]
    
    try:
        msg = await edit_or_reply(message, "<b>🔊 Unmuting user...</b>")
        
        # Default chat permissions
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=message.chat.permissions
        )
        
        # Success message
        text = f"<b>🔊 User unmuted!</b>\n\n"
        text += f"<b>Chat:</b> {message.chat.title}\n"
        text += f"<b>User:</b> {user_first_name}\n"
        text += f"<b>ID:</b> <code>{user_id}</code>"
            
        await msg.edit(text)
        
    except errors.ChatAdminRequired:
        await msg.edit("❌ <b>I don't have permission to unmute users!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> {e}")


@Client.on_message(filters.command("pin", prefix) & filters.me)
async def pin_cmd(client: Client, message: Message):
    """Pin message in chat"""
    if not await check_privileges(client, message, ["can_pin_messages"]):
        return
    
    replied = message.reply_to_message
    if not replied:
        await edit_or_reply(message, "❌ <b>Reply to a message to pin it!</b>")
        return
    
    # Check for silent pin
    silent = False
    if len(message.command) > 1:
        if message.command[1].lower() in ["silent", "quiet", "s", "q"]:
            silent = True
    
    try:
        msg = await edit_or_reply(message, "<b>📌 Pinning message...</b>")
        
        await client.pin_chat_message(
            chat_id=message.chat.id,
            message_id=replied.id,
            disable_notification=silent
        )
        
        await msg.edit("<b>📌 Message pinned successfully!</b>")
        
    except errors.ChatAdminRequired:
        await msg.edit("❌ <b>I don't have permission to pin messages!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> {e}")


@Client.on_message(filters.command("unpin", prefix) & filters.me)
async def unpin_cmd(client: Client, message: Message):
    """Unpin message in chat"""
    if not await check_privileges(client, message, ["can_pin_messages"]):
        return
    
    # Check for "unpin all" command
    if len(message.command) > 1 and message.command[1].lower() == "all":
        try:
            msg = await edit_or_reply(message, "<b>📌 Unpinning all messages...</b>")
            
            await client.unpin_all_chat_messages(chat_id=message.chat.id)
            
            await msg.edit("<b>📌 All messages unpinned!</b>")
            return
        except errors.ChatAdminRequired:
            await edit_or_reply(message, "❌ <b>I don't have permission to unpin messages!</b>")
            return
        except Exception as e:
            await edit_or_reply(message, f"❌ <b>Error:</b> {e}")
            return
    
    # Unpin replied message or last pinned
    replied = message.reply_to_message
    
    try:
        msg = await edit_or_reply(message, "<b>📌 Unpinning message...</b>")
        
        if replied:
            await client.unpin_chat_message(
                chat_id=message.chat.id,
                message_id=replied.id
            )
        else:
            # Unpin the last pinned message
            await client.unpin_chat_message(chat_id=message.chat.id)
        
        await msg.edit("<b>📌 Message unpinned successfully!</b>")
        
    except errors.ChatAdminRequired:
        await msg.edit("❌ <b>I don't have permission to unpin messages!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> {e}")


@Client.on_message(filters.command("promote", prefix) & filters.me)
async def promote_cmd(client: Client, message: Message):
    """Promote user in chat"""
    if not await check_privileges(client, message, ["can_promote_members"]):
        return
    
    user_dict = await get_user(client, message)
    if not user_dict:
        await edit_or_reply(message, "❌ <b>User not found!</b>")
        return
    
    user_id = user_dict["user_id"]
    user_first_name = user_dict["user_first_name"]
    
    # Check for custom title
    custom_title = None
    if len(message.command) > 2:
        custom_title = " ".join(message.command[2:])
    
    try:
        msg = await edit_or_reply(message, "<b>👑 Promoting user...</b>")
        
        # Default admin privileges
        privileges = ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        )
        
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            privileges=privileges
        )
        
        # Set admin title if provided
        if custom_title:
            await client.set_administrator_title(
                chat_id=message.chat.id,
                user_id=user_id,
                title=custom_title
            )
        
        # Success message
        text = f"<b>👑 User promoted to admin!</b>\n\n"
        text += f"<b>Chat:</b> {message.chat.title}\n"
        text += f"<b>User:</b> {user_first_name}\n"
        text += f"<b>ID:</b> <code>{user_id}</code>"
        
        if custom_title:
            text += f"\n<b>Title:</b> {custom_title}"
            
        await msg.edit(text)
        
    except errors.ChatAdminRequired:
        await msg.edit("❌ <b>I don't have permission to promote users!</b>")
    except errors.UserAdminInvalid:
        await msg.edit("❌ <b>Cannot promote an admin!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> {e}")


@Client.on_message(filters.command("demote", prefix) & filters.me)
async def demote_cmd(client: Client, message: Message):
    """Demote user in chat"""
    if not await check_privileges(client, message, ["can_promote_members"]):
        return
    
    user_dict = await get_user(client, message)
    if not user_dict:
        await edit_or_reply(message, "❌ <b>User not found!</b>")
        return
    
    user_id = user_dict["user_id"]
    user_first_name = user_dict["user_first_name"]
    
    try:
        msg = await edit_or_reply(message, "<b>👑 Demoting user...</b>")
        
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            privileges=ChatPrivileges()  # Empty privileges = demote
        )
        
        # Success message
        text = f"<b>⬇️ User demoted!</b>\n\n"
        text += f"<b>Chat:</b> {message.chat.title}\n"
        text += f"<b>User:</b> {user_first_name}\n"
        text += f"<b>ID:</b> <code>{user_id}</code>"
            
        await msg.edit(text)
        
    except errors.ChatAdminRequired:
        await msg.edit("❌ <b>I don't have permission to demote users!</b>")
    except errors.UserAdminInvalid:
        await msg.edit("❌ <b>Cannot demote this user!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> {e}")


modules_help["admin"] = {
    "ban [user] [time] [reason]": "Ban user from chat (time format: 10m, 10h, 10d)",
    "unban [user]": "Unban user from chat",
    "kick [user] [reason]": "Kick user from chat",
    "mute [user] [time] [reason]": "Mute user in chat (time format: 10m, 10h, 10d)",
    "unmute [user]": "Unmute user in chat",
    "pin [silent]": "Pin replied message (add 'silent' to pin without notification)",
    "unpin": "Unpin replied message or last pinned",
    "unpin all": "Unpin all messages in chat",
    "promote [user] [title]": "Promote user to admin with optional title",
    "demote [user]": "Demote user from admin",
    "__category__": "admin"
}