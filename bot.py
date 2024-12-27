
import sys
import glob
import importlib
from pathlib import Path
from pyrogram import idle
import logging
import logging.config

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from plugins.Verification import check_all_subscriptions
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script 
from datetime import date, datetime 
import pytz
from aiohttp import web
from plugins import web_server, check_expired_premium

import asyncio
from pyrogram import idle
from lazybot import LazyPrincessBot
from util.keepalive import ping_server
from lazybot.clients import initialize_clients

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "7381399131:AAHtezPzBUhb6sULEJY44FUIDZ9ThnnuC34"
bot = Bot(token=TOKEN)

# चैनल लिस्ट
CHANNELS = [
    {"@MovieDawnloadHub": "@MovieDawnloadHub", "link": "https://t.me/MovieDawnloadHub"},
    {"@MovieDawnloadhub_Updated": "@MovieDawnloadhub_Updated", "link": "https://t.me/MovieDawnloadhub_Updated"},
    {"@Dawnloadbot_support": "@Dawnloadbot_support", "link": "https://t.me/Dawnloadbot_support"}
]

# सभी चैनल्स की सदस्यता जांचने का फंक्शन
def check_all_subscriptions(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel['username'], user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

# चैनल बटन बनाने का फंक्शन
def generate_channel_buttons():
    buttons = []
    for channel in CHANNELS:
        buttons.append([InlineKeyboardButton(f"जॉइन करें {channel['@MovieDawnloadHub']}", url=channel['https://t.me/MovieDawnloadHub'])])
    return InlineKeyboardMarkup(buttons)

# /start कमांड हैंडलर
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # सभी चैनल्स की सदस्यता जांचें
    if not check_all_subscriptions(user_id):
        update.message.reply_text(
            "आपको पहले इन सभी चैनल्स को जॉइन करना होगा:\n",
            reply_markup=generate_channel_buttons()  # बटन जोड़ें
        )
        return

    # अगर सभी चैनल्स जॉइन किए गए हैं
    update.message.reply_text("आप सफलतापूर्वक वेरिफाई हो गए हैं! अब आप बॉट का उपयोग कर सकते हैं।")

# बॉट सेटअप और स्टार्ट करें
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))

updater.start_polling()
updater.idle()


ppath = "plugins/*.py"
files = glob.glob(ppath)
LazyPrincessBot.start()
loop = asyncio.get_event_loop()


async def Lazy_start():
    print('\n')
    print('Initalizing Deendayal Dhakad Bot')
    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Deendayal dhakad Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()
    me = await LazyPrincessBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    LazyPrincessBot.username = '@' + me.username
    LazyPrincessBot.loop.create_task(check_expired_premium(LazyPrincessBot))
    logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await LazyPrincessBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    await idle()                     

if __name__ == '__main__':
    try:
        loop.run_until_complete(Lazy_start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
