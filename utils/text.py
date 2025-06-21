# Custom module for CybroX-UserBot
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply


@Client.on_message(filters.command("type", prefix) & filters.me)
async def type_cmd(client: Client, message: Message):
    """Type message with a typing animation effect"""
    # Your existing type_cmd function...


@Client.on_message(filters.command("mock", prefix) & filters.me)
async def mock_cmd(client: Client, message: Message):
    """Convert text to mOcK tExT"""
    # Your existing mock_cmd function...


@Client.on_message(filters.command("vapor", prefix) & filters.me)
async def vapor_cmd(client: Client, message: Message):
    """Convert text to vaporwave text"""
    # Your existing vapor_cmd function...


@Client.on_message(filters.command("reverse", prefix) & filters.me)
async def reverse_cmd(client: Client, message: Message):
    """Reverse the given text"""
    # Your existing reverse_cmd function...


# Register module in help system
modules_help["text"] = {
    "type [text]": "Type message with a typing animation effect",
    "mock [text]": "Convert text to mOcK tExT",
    "vapor [text]": "Convert text to vaporwave text",
    "reverse [text]": "Reverse the given text",
    "__category__": "fun"
}