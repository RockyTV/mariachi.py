# -*- coding: latin-1 -*-
"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import os
import re
import time
import telepot
import importlib
from flask import Flask, request
from telepot.loop import MessageLoop, OrderedWebhook
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

if not 'TELEGRAM_TOKEN' in os.environ:
    raise(RuntimeError('Missing Telegram token'))

app = Flask(__name__)

SECRET_URL='/bot' + os.environ['TELEGRAM_TOKEN']

bot = telepot.Bot(os.environ['TELEGRAM_TOKEN'])
bot.deleteWebhook()
bot_username = ''

registered_commands = []

def register_commands():
    import types
    to_register = ['Ping', 'SchoolNotes']

    def import_from(module, name):
        module = importlib.import_module(module)
        return getattr(module, name)

    def register_command(cmd: types.ModuleType):
        try:
            registered_commands.index(cmd)
        except ValueError:
            registered_commands.append(cmd(bot, bot_username))
            print('Registered command module:', cmd.__name__)

    for command in to_register:
        register_command(import_from('commands', command))

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text':
        raw_message = msg['text'].strip()
        command = r"^(?:@%s)$" % bot_username

        if re.search(command, raw_message, flags=re.ASCII):
            keyboards = [[]]
            for cmd in registered_commands:
                class_name = cmd.__class__.__name__
                alias = cmd.get_alias() if hasattr(cmd, 'get_alias') else class_name
                keyboards[0].append(InlineKeyboardButton(text=alias, callback_data='%s_menu' % class_name.lower()))

            bot.sendMessage(chat_id, 'Escolha um comando abaixo', reply_to_message_id=msg['message_id'], reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboards))

        else:
            for cmd in registered_commands:
                cmd.on_chat_message(msg)

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    for cmd in registered_commands:
        if query_data.startswith(cmd.__class__.__name__.lower()):
            if from_id == msg['message']['reply_to_message']['from']['id']:
                cmd.on_callback_query(msg)

#MessageLoop(bot, {
#    'chat': on_chat_message,
#    'callback_query': on_callback_query
#}).run_as_thread()

def handle(msg):
    print(msg)

WEBHOOK = OrderedWebhook(bot, handle)

@app.route(SECRET_URL, methods=['GET', 'POST'])
def pass_update():
    WEBHOOK.feed(request.data)
    return 'OK'

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, world!'


if __name__ == '__main__':
    bot_username = bot.getMe()['username']
    register_commands()
    ip='127.0.0.1'

    if 'OPENSHIFT_PYTHON_IP' in os.environ:
        ip = os.environ['OPENSHIFT_PYTHON_IP']
        try:
            bot.setWebhook('https://pymariachi-xinayder.rhcloud.com' + SECRET_URL)
        except telepot.exception.TooManyRequestsError:
            pass
        WEBHOOK.run_as_thread()
        app.run(host=ip, port=8080, debug=True)
    else:
        while(1): time.sleep(10)