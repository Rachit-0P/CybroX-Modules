# Custom module for CybroX-UserBot
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply, with_reply
from utils.db import db


@Client.on_message(filters.command("save", prefix) & filters.me)
async def save_note(client: Client, message: Message):
    """Save a note"""
    if len(message.command) < 2:
        await edit_or_reply(message, "<b>Not enough arguments!</b>\nUsage: .save [name] [content or reply]")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    # Rest of your existing save_note function...


@Client.on_message(filters.command("get", prefix) & filters.me)
async def get_note(client: Client, message: Message):
    """Retrieve a saved note"""
    # Your existing get_note function...


@Client.on_message(filters.command("notes", prefix) & filters.me)
async def list_notes(client: Client, message: Message):
    """List all saved notes"""
    # Your existing list_notes function...


@Client.on_message(filters.command("clear", prefix) & filters.me)
async def clear_note(client: Client, message: Message):
    """Delete a saved note"""
    # Your existing clear_note function...


# Register module in help system
modules_help["notes"] = {
    "save [name] [text]": "Save a note with the given name and content (or reply to a message)",
    "get [name]": "Retrieve a saved note",
    "notes": "List all saved notes",
    "clear [name]": "Delete a saved note",
    "__category__": "utils"
}