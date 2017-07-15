import telepot

class Ping():
    bot = telepot.Bot
    def __init__(self, bot):
        self.bot = bot
        print('Module initialized!')
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            if msg['text'] == '/ping':
                self.bot.sendMessage(chat_id, 'Pong!')