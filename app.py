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

			add_regex = r"^/nov(odever|amateria)\s?([\w]+)?\s?(.+)?$"
			if re.search(add_regex, raw_message, flags=re.ASCII):
				match = re.search(add_regex, raw_message, flags=re.UNICODE)
				func = match.group(1)
				if match.group(2) and match.group(3) != None:
					subject = match.group(2)
					if not subject in SUBJECTS:
						bot.sendMessage(chat_id, u'Matéria inválida. Conheço as seguintes matérias: %s' % ', '.join(['_%s_' % str(x) for x in SUBJECTS]), 'Markdown')
					else:
						today = date.today()

						if func == 'odever':
							dever = {}
							dever['data'] = today.strftime("%d/%m/%Y")
							dever['conteudo'] = match.group(3)
							homework[subject]['deveres'].append(dever)

							print ('%s added %s homework' % (msg['from']['username'], subject))
							bot.sendMessage(chat_id, 'Dever de %s adicionado!' % subject)
							save_homework()
						elif func == 'amateria':
							materia = {}
							materia['data'] = today.strftime("%d/%m/%Y")
							materia['conteudo'] = match.group(3)
							homework[subject]['provas'].append(materia)

							bot.sendMessage(chat_id, 'Matéria de %s adicionada!' % subject)
							save_homework()

				else:
					bot.sendMessage(chat_id, 'Exemplo de uso:\r\n*/novodever* historia Explicar por quê o Jonathan é o melhor professor\r\n*/novamateria* historia Império Romano')
			list_regex = r"/listar(deveres|materias)\s?([\w]+)?$"
			if re.search(list_regex, raw_message, flags=re.ASCII):
				match = re.search(list_regex, raw_message, flags=re.UNICODE)
				func = match.group(1)
				if func == 'materias': func = 'provas'
				text_deveres = 'Deveres'
				if func == 'provas': text_deveres = 'Matérias'
				if match.group(2) != None:
					subject = match.group(2)
					if subject in homework:
						print ('%s requested %s homeworks' % (msg['from']['username'], subject))

						reply_deveres = ''
						for dever in homework[subject][func]:
							reply_deveres += '*%s*\r\n%s\r\n\r\n' % (dever['data'], dever['conteudo'])
							
							if reply_deveres != '': bot.sendMessage(chat_id, '%s de %s:\r\n%s' % (text_deveres, subject, reply_deveres), 'Markdown')
				else:
					print ('%s requested all homeworks' % msg['from']['username'])
					for subject in SUBJECTS:
						if subject in homework:
							if homework[subject][func] != []:
								reply_deveres = ''
								for dever in homework[subject][func]:
									reply_deveres += '*%s* - #%d\r\n%s\r\n\r\n' % (dever['data'], homework[subject][func].index(dever) + 1, dever['conteudo'])
							
								if reply_deveres is not '': bot.sendMessage(chat_id, '%s de %s:\r\n%s' % (text_deveres, subject, reply_deveres), 'Markdown')

			del_regex = r"/apagar(deveres|materias)\s([\w]+)\s?([0-9]+)?$"
			if re.search(del_regex, raw_message, flags=re.ASCII):
				match = re.search(del_regex, raw_message, flags=re.UNICODE)
				func = match.group(1)
				if match.group(2) != None:
					subject = match.group(2)
					idx = int(match.group(3)) if match.group(3) != None else None
					if func == 'deveres':
						if idx != None:
							if idx > len(homework[subject]['deveres']) or idx < 0:
								bot.sendMessage(chat_id, 'O item especificado não existe na lista.')
							else:
								print ('%s removed %s item #%d' % (msg['from']['username'], subject, idx))
								homework[subject]['deveres'].pop(idx-1)
								bot.sendMessage(chat_id, 'O dever #%d de %s foi removido com sucesso!' % (idx, subject))
								save_homework()
						else:
							print('%s removed all %s homework items' % (msg['from']['username'], subject))
							homework[subject]['deveres'].clear()
							save_homework()
							bot.sendMessage(chat_id, 'Os deveres de %s foram removidos com sucesso!' % (subject))
					elif func == 'materias':
						if idx != None:
							if idx > len(homework[subject]['provas']) or idx < 0:
								bot.sendMessage(chat_id, 'O item especificado não existe na lista.')
							else:
								print ('%s removed %s item #%d' % (msg['from']['username'], subject, idx))
								homework[subject]['provas'].pop(idx-1)
								bot.sendMessage(chat_id, 'O dever #%d de %s foi removido com sucesso!' % (idx, subject))
								save_homework()
						else:
							print('%s removed all %s homework items' % (msg['from']['username'], subject))
							homework[subject]['provas'].clear()
							save_homework()
							bot.sendMessage(chat_id, 'Os deveres de %s foram removidos com sucesso!' % (subject))
				else:
					bot.sendMessage(chat_id, 'Exemplo de uso:\r\n*/apagardeveres* historia 1 - apaga o primeiro item na lista de deveres de história\r\n*/apagardeveres* historia - apaga todos os deveres de história\r\n*/apagarmaterias* historia 1 - apaga o primeiro item na lista de matérias de história\r\n*/apagarmaterias* historia - apaga todas as matérias de história')


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