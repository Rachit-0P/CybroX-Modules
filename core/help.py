#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply


@Client.on_message(filters.command(["help", "h"], prefix) & filters.me)
async def help_cmd(client: Client, message: Message):
    """Show help for modules"""
    if len(message.command) == 1:
        # Group modules by category
        categories = {}
        for module_name, commands in sorted(modules_help.items()):
            category = commands.get("__category__", "misc")
            if category not in categories:
                categories[category] = []
            categories[category].append(module_name)
        
        text = f"<b>🚀 CybroX-UserBot Help</b>\n\n"
        
        # Display modules by category
        for category, module_names in sorted(categories.items()):
            text += f"<b>📂 {category.title()}</b>\n"
            for module_name in sorted(module_names):
                text += f"  • <code>{prefix}help {module_name}</code>\n"
            text += "\n"
        
        text += f"<b>Total modules:</b> {len(modules_help)}\n"
        text += f"<b>Command prefix:</b> <code>{prefix}</code>"
        
        await edit_or_reply(message, text)
    
    elif message.command[1].lower() in modules_help:
        module_name = message.command[1].lower()
        commands = modules_help[module_name]
        
        text = f"<b>📚 Help for {module_name} module</b>\n\n"
        for command, description in commands.items():
            if command != "__category__":  # Skip category indicator
                text += f"<code>{prefix}{command}</code>: {description}\n"
        
        await edit_or_reply(message, text)
    else:
        await edit_or_reply(message, f"<b>❌ Module {message.command[1]} not found!</b>")
        await asyncio.sleep(3)
        await message.delete()


@Client.on_message(filters.command("modules", prefix) & filters.me)
async def modules_cmd(client: Client, message: Message):
    """Show list of all installed modules"""
    # Group modules by category
    categories = {}
    for module_name, commands in sorted(modules_help.items()):
        category = commands.get("__category__", "misc")
        if category not in categories:
            categories[category] = []
        categories[category].append(module_name)
    
    text = "<b>📋 Installed modules:</b>\n\n"
    
    # Display modules by category
    for category, module_names in sorted(categories.items()):
        text += f"<b>📂 {category.title()}</b>\n"
        text += ", ".join([f"<code>{module}</code>" for module in sorted(module_names)])
        text += "\n\n"
    
    text += f"<b>Total:</b> {len(modules_help)} modules\n"
    text += f"Use <code>{prefix}help [module]</code> for detailed command information."
    
    await edit_or_reply(message, text)


@Client.on_message(filters.command("loadmodule", prefix) & filters.me)
async def load_module_cmd(client: Client, message: Message):
    """Load a custom module from the repository"""
    if len(message.command) != 2:
        await edit_or_reply(message, f"<b>❌ Usage:</b> <code>{prefix}loadmodule [module_name]</code>")
        return
        
    module_name = message.command[1].lower()
    
    # First send processing message
    msg = await edit_or_reply(message, f"<b>⏳ Loading module {module_name}...</b>")
    
    # Import necessary modules
    import requests
    import os
    import importlib
    import sys
    from utils.db import db
    
    # Get current module list
    all_modules = db.get("custom.modules", "allModules", [])
    
    # Check if module already installed
    if module_name in all_modules:
        await msg.edit(f"<b>⚠️ Module {module_name} is already installed!</b>")
        return
    
    # Add module to the list
    all_modules.append(module_name)
    db.set("custom.modules", "allModules", all_modules)
    
    # Create directory for custom modules if it doesn't exist
    SCRIPT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    custom_modules_path = f"{SCRIPT_PATH}/modules/custom_modules"
    os.makedirs(custom_modules_path, exist_ok=True)
    
    # Download module from repository
    try:
        # Get module list
        f = requests.get(
            "https://raw.githubusercontent.com/YOUR-USERNAME/custom_modules/main/full.txt"
        ).text
        
        modules_dict = {
            line.split("/")[-1].split()[0]: line.strip() for line in f.splitlines()
        }
        
        if module_name not in modules_dict:
            await msg.edit(f"<b>❌ Module {module_name} not found in repository!</b>")
            # Remove from list
            all_modules.remove(module_name)
            db.set("custom.modules", "allModules", all_modules)
            return
            
        # Download module
        module_path = f"{custom_modules_path}/{module_name}.py"
        url = f"https://raw.githubusercontent.com/YOUR-USERNAME/custom_modules/main/{modules_dict[module_name]}.py"
        resp = requests.get(url)
        
        if resp.ok:
            with open(module_path, "wb") as f:
                f.write(resp.content)
                
            # Try to import module
            try:
                sys.path.insert(0, custom_modules_path)
                module_path = f"modules.custom_modules.{module_name}"
                module = importlib.import_module(module_path)
                importlib.reload(module)
                
                await msg.edit(f"<b>✅ Module {module_name} loaded successfully!</b>")
            except Exception as e:
                await msg.edit(f"<b>❌ Error importing module:</b>\n<code>{e}</code>")
                # Remove file and from list on error
                os.remove(module_path)
                all_modules.remove(module_name)
                db.set("custom.modules", "allModules", all_modules)
        else:
            await msg.edit(f"<b>❌ Failed to download module {module_name}!</b>")
            all_modules.remove(module_name)
            db.set("custom.modules", "allModules", all_modules)
    except Exception as e:
        await msg.edit(f"<b>❌ Error:</b>\n<code>{e}</code>")
        # Remove from list on error
        if module_name in all_modules:
            all_modules.remove(module_name)
            db.set("custom.modules", "allModules", all_modules)


modules_help["help"] = {
    "help [module]": "Get help for a specific module or list all modules",
    "h [module]": "Alias for help command",
    "modules": "Show list of all installed modules",
    "loadmodule [name]": "Load a custom module from repository",
    "__category__": "core"
}
