# -*- coding: latin-1 -*-
import os
import re
import sys
import time
import telepot	
import pickle

from datetime import date
from flask import Flask, request

try:
	from Queue import Queue
except ImportError:
	from queue import Queue

#GRUPO_SALA = -1001045780811
#GRUPO_SALA = -126875187
GRUPO_SALA = int(os.environ['TELEGRAM_GRUPO_SALA'])
SUBJECTS = ['portugues', 'redacao', 'literatura', 'fisica', 'quimica', 'biologia', 'geografia', 'historia', 'matematica', 'filosofia', 'sociologia', 'ingles', 'espanhol', 'artes']

homework = {}
is_openshift = 'OPENSHIFT_PYTHON_IP' in os.environ
if is_openshift: homework_path = os.path.join(os.path.expanduser('~'), 'app-root/data/homework.pickle')
else: homework_path = 'homework.pickle'

def init_homework():
	homework.clear()
	homework['version'] = '1.0'
	for subject in SUBJECTS:
		homework[subject] = {}
		homework[subject]['provas'] = []
		homework[subject]['deveres'] = []
def save_homework():
	with open(homework_path, 'wb') as f:
		pickle.dump(homework, f, protocol=3)
def load_homework():
	if os.path.exists(homework_path):
		with open(homework_path, 'rb') as f:
			homework.update(pickle.load(f))

def handle(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)

	if content_type == 'text':
		if chat_id == GRUPO_SALA or chat_id == -126875187:
			raw_message = msg['text'].strip()
			regex = r"^/dever\s?(add|del|list|help)?\s?([\w]+)?\s?(.+)?$"
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

							dever = {}
							dever['data'] = today.strftime("%d/%m/%Y")
							dever['conteudo'] = match.group(3)
							homework[subject]['deveres'].append(dever)
							print (homework[subject]['deveres'])

							print ('%s added %s homework' % (msg['from']['username'], subject))
							bot.sendMessage(chat_id, 'Dever de %s adicionado!' % subject)
							save_homework()
				elif cmd == 'list':
					if match.group(2) != None:
						subject = match.group(2)
						if subject in homework:
							print ('%s requested %s homeworks' % (msg['from']['username'], subject))

							reply_deveres = ''
							for dever in homework[subject]['deveres']:
								reply_deveres += '*%s*\r\n%s\r\n\r\n' % (dever['data'], dever['conteudo'])
							
							if reply_deveres is not '': bot.sendMessage(chat_id, 'Deveres de %s:\r\n%s' % (subject, reply_deveres), 'Markdown')
					else:
						print ('%s requested all homeworks' % msg['from']['username'])
						for subject in SUBJECTS:
							if subject in homework:
								if homework[subject]['deveres'] != []:
									reply_deveres = ''
									for dever in homework[subject]['deveres']:
										reply_deveres += '*%s* - #%d\r\n%s\r\n\r\n' % (dever['data'], homework[subject]['deveres'].index(dever) + 1, dever['conteudo'])
							
									if reply_deveres is not '': bot.sendMessage(chat_id, 'Deveres de %s:\r\n%s' % (subject, reply_deveres), 'Markdown')

				elif cmd == 'del':
					if match.group(2) != None:
						subject = match.group(2)
						if subject in homework:
							print ('%s deleted %s homeworks' % (msg['from']['username'], subject))
							bot.sendMessage(chat_id, 'Os deveres de %s foram apagados' % subject)
							del homework[subject]
							save_homework()
				elif cmd == 'help' or cmd == None:
					bot.sendMessage(chat_id, 'Ajuda:\r\n/dever add <materia> <conteudo> - Adiciona um novo dever da máteria.\r\n/dever del <materia> - Apaga todos os deveres salvos da máteria.\r\n/dever list [materia] - Mostrar todos os deveres ou somente os deveres da matéria especificada.\r\n/dever help - Mostra essa mensagem', parse_mode='Markdown')


app = Flask(__name__)
bot = telepot.Bot(os.environ['TELEGRAM_TOKEN'])
update_queue = Queue()
init_homework()
load_homework()

bot.message_loop(handle, source=update_queue)

@app.route('/hook', methods=['POST'])
def pass_update():
	update_queue.put(request.data)
	return 'OK'

@app.route('/')
def hello_world():
	return 'It works!'

@app.route('/deveres')
def show_homework():
	return str(homework)

if __name__ == '__main__':
	if not 'OPENSHIFT_PYTHON_IP' in os.environ: ip = '127.0.0.1'
	else: ip = os.environ['OPENSHIFT_PYTHON_IP']
	bot.setWebhook('https://pymariachi-xinayder.rhcloud.com/hook')
	app.run(host=ip, port=8080, debug=True)