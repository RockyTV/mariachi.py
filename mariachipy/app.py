"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import os
import time
import telepot
import importlib
from flask import Flask, request
from telepot.loop import MessageLoop

if not 'TELEGRAM_TOKEN' in os.environ:
    raise(RuntimeError('Missing Telegram token'))

bot = telepot.Bot(os.environ['TELEGRAM_TOKEN'])
bot.deleteWebhook()
bot_username = ''

registered_commands = []

def register_commands():
    import types
    to_register = ['Ping', 'Notes']

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
    print(msg)
    for c in registered_commands:
        c.on_chat_message(msg)

MessageLoop(bot, {
    'chat': on_chat_message
}).run_as_thread()

if __name__ == '__main__':
    bot_username = bot.getMe()['username']
    register_commands() 

while 1:
    time.sleep(10)