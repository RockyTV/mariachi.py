import pickle
import re
import telepot

class Ping():
    bot = telepot.Bot
    bot_username = ''

    def __init__(self, bot, bot_username):
        self.bot = bot
        self.bot_username = bot_username

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            if msg['text'] == '/ping':
                self.bot.sendMessage(chat_id, 'Pong!')

class Notes():
    bot = telepot.Bot
    bot_username = ''
    data = {}

    def __init__(self, bot, bot_username):
        self.bot = bot
        self.bot_username = bot_username
        self.data = {}

    def save_pickle(self):
        with open('test.pickle', 'wb') as f:
            pickle.dump(self.data, f, protocol=3)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            raw_message = msg['text'].strip();

            add = r"^/add(?:@%s)?\s([\w]+)$" % self.bot_username

            if re.search(add, raw_message, flags=re.ASCII):
                match = re.search(add, raw_message, flags=re.UNICODE)

                self.data[match.group(1)] = "test: %s" % match.group(1)
                self.bot.sendMessage(chat_id, 'Added key successfully!')
                self.save_pickle()
                print(self.data)