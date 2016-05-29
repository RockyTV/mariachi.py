# -*- coding: latin-1 -*-
import os
import re
import sys
import time
import telepot	
import pickle

from datetime import date

TOKEN = '173136669:AAGuqYDvnibwF0xJzUnzcsREoUVWxVZMYMY'
#GRUPO_SALA = -1001045780811
GRUPO_SALA = -126875187
SUBJECTS = ['matematica', 'historia', 'quimica', 'geografia']

homework = {}

def save_homework():
	with open('homework.pickle', 'wb') as f:
		pickle.dump(homework, f, pickle.HIGHEST_PROTOCOL)
def load_homework():
	if os.path.exists('homework.pickle'):
		with open('homework.pickle', 'rb') as f:
			homework.update(pickle.load(f))

def handle(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)

	if content_type == 'text':
		if chat_id == GRUPO_SALA:
			raw_message = msg['text'].strip()
			regex = r"^/dever\s(add|del|list|help)\s?([\w]+)?\s?(.+)?$"
			if re.search(regex, raw_message, flags=re.ASCII):
				match = re.search(regex, raw_message, flags=re.UNICODE)
				cmd = match.group(1)
				# Check command
				if cmd == 'add':
					# Check if subject is valid
					if match.group(2) and match.group(3) != None:
						subject = match.group(2)
						if not subject in SUBJECTS:
							bot.sendMessage(chat_id, u'Matéria inválida. Conheço as seguintes matérias: %s' % ', '.join(['_%s_' % str(x) for x in SUBJECTS]), 'Markdown')
						else:
							today = date.today()
							formatted_string = '*%s*\r\n%s\r\n\r\n' % (today.strftime("%d/%m/%Y"), match.group(3))
							if subject in homework: homework[subject] += formatted_string
							else: homework[subject] = formatted_string
							print ('%s added %s homework' % (msg['from']['username'], subject))
							bot.sendMessage(chat_id, 'Dever de %s adicionado!' % subject)
							save_homework()
					else:
						print ('Invalid usage.')
				elif cmd == 'list':
					if match.group(2) != None:
						if subject in homework:
							subject = match.group(2)
							print ('%s requested %s homeworks' % (msg['from']['username'], subject))
							bot.sendMessage(chat_id, 'Deveres de %s:\r\n%s' % (subject, homework[subject]), 'Markdown')
					else:
						print ('%s requested all homeworks' % msg['from']['username'])
						for subject in homework:
							if homework[subject] != None:
								bot.sendMessage(chat_id, 'Deveres de %s:\r\n%s' % (subject, homework[subject]), 'Markdown')
				elif cmd == 'del':
					if match.group(2) != None:
						subject = match.group(2)
						if subject in homework:
							print ('%s deleted %s homeworks' % (msg['from']['username'], subject))
							bot.sendMessage(chat_id, 'Os deveres de %s foram apagados' % subject)
							del homework[subject]
							save_homework()
				elif cmd == 'help':
					bot.sendMessage(chat_id, 'Help was called')



bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening...')
load_homework()
print ('Loaded homework!')

while 1:
	time.sleep(10)
