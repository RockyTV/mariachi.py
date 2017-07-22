import os
import pickle
import re
import telepot

from datetime import datetime, date
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply


class Ping():
    bot = telepot.Bot
    bot_username = ''

    def __init__(self, bot, bot_username):
        self.bot = bot
        self.bot_username = bot_username

    def on_chat_message(self, msg):
        pass

    def on_callback_query(self, msg):
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
        chat_id = msg['message']['chat']['id']

        # Retrieve the msg_id from a previous/recently sent inline query
        msg_id = telepot.origin_identifier(msg)

        if data == '%s_menu' % self.__class__.__name__.lower():
            self.bot.editMessageText(msg_id, 'Pong!', reply_markup=None)


class SchoolNotes():
    bot = telepot.Bot
    bot_username = ''
    notes = {}
    pickle_path = ''
    prev_inline_query = None
    class_name = ''
    add_lock = {}
    del_lock = {}
    school_group = 0

    def __init__(self, bot, bot_username):
        self.bot = bot
        self.bot_username = bot_username
        self.notes = {
            'version': '1.0',
            'last_updated': datetime.today().timestamp(),
            -126875187: {
                'subjects': {}
            }
        }
        self.pickle_path = os.path.join(os.path.expanduser(
            '~'), 'app-root/data/notes.pickle') if 'OPENSHIFT_PYTHON_IP' in os.environ else 'notes.pickle'
        self.prev_inline_query = None
        self.class_name = self.__class__.__name__.lower()
        self.add_lock = {}
        self.del_lock = {}
        self.school_group = -126875187

        subjects = {
            'ART': 'Artes',
            'BIO': 'Biologia',
            'EDF': 'Educação Física',
            'ESP': 'Espanhol',
            'FIL': 'Filosofia',
            'FIS': 'Física',
            'GEO': 'Geografia',
            'HIS': 'História',
            'ING': 'Inglês',
            'LIT': 'Literatura',
            'MAT': 'Matemática',
            'POR': 'Português',
            'QUI': 'Química',
            'RED': 'Redação',
            'SOC': 'Sociologia'
        }
        for subject, name in subjects.items():
            self.notes[self.school_group]['subjects'][subject] = {
                'name': name,
                'tarefas': [],
                'materia_provas': []
            }

            #-126875187 test
            #-1001045780811 live

        if os.path.exists(self.pickle_path):
            with open(self.pickle_path, 'rb') as f:
                self.notes.update(pickle.load(f))

    def get_alias(self):
        return 'Escola'

    def save_notes(self):
        self.notes['last_updated'] = datetime.today().timestamp()

        with open(self.pickle_path, 'wb') as f:
            pickle.dump(self.notes, f, protocol=3)

    def on_chat_message(self, msg):
        # Check if the message the user should reply to is the last one from the callback query
        if 'reply_to_message' in msg:
            chat_id, msg_id = (msg['reply_to_message']['chat']
                               ['id'], msg['reply_to_message']['message_id'])

            if self.add_lock != None:
                reply_to = (chat_id, msg_id)

                if reply_to == self.add_lock['id']:
                    if chat_id == self.school_group:
                        db_obj = 'tarefas' if self.add_lock['type'] == 't' else 'materia_provas'
                        text_obj = 'Tarefa de casa adicionada' if self.add_lock[
                            'type'] == 't' else 'Conteúdo de prova adicionado'
                        text_obj2 = 'uma tarefa de casa' if self.add_lock[
                            'type'] == 't' else 'um conteúdo de prova'

                        obj = {
                            'date_added': datetime.today().timestamp(),
                            'text': msg['text']
                        }

                        user_name = '%s (@%s)' % (
                            msg['from']['first_name'], msg['from']['username']) if 'username' in msg['from'] else msg['from']['first_name']
                        subject_name = self.notes[chat_id]['subjects'][self.add_lock['subject']]['name']

                        self.notes[chat_id]['subjects'][self.add_lock['subject']][db_obj].append(
                            obj)
                        self.bot.editMessageText(
                            self.add_lock['id'], '%s com sucesso!' % text_obj)
                        self.bot.sendMessage(chat_id, 'O usuário %s adicionou %s de %s.' % (
                            user_name, text_obj2, subject_name))
                        self.save_notes()

    def on_callback_query(self, msg):
        print(msg)
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
        chat_id = msg['message']['chat']['id']

        # Retrieve the msg_id from a previous/recently sent inline query
        msg_id = telepot.origin_identifier(msg)

        if chat_id == self.school_group:
            cb_data_subjects_t = {}
            cb_data_subjects_m = {}
            for tag in self.notes[chat_id]['subjects']:
                cb_data_subjects_t['%s_list_t_%s' %
                                   (self.class_name, tag.lower())] = tag
                cb_data_subjects_m['%s_list_m_%s' %
                                   (self.class_name, tag.lower())] = tag
                cb_data_subjects_t['%s_add_t_%s' %
                                   (self.class_name, tag.lower())] = tag
                cb_data_subjects_m['%s_add_m_%s' %
                                   (self.class_name, tag.lower())] = tag
                cb_data_subjects_t['%s_del_t_%s' %
                                   (self.class_name, tag.lower())] = tag
                cb_data_subjects_m['%s_del_m_%s' %
                                   (self.class_name, tag.lower())] = tag

            # Handle callback query for module
            if data == '%s_menu' % self.class_name:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Adicionar', callback_data='%s_add' % self.class_name),
                     InlineKeyboardButton(
                        text='Listar', callback_data='%s_list' % self.class_name),
                     InlineKeyboardButton(text='Apagar', callback_data='%s_del' % self.class_name)],
                ])
                self.bot.editMessageText(
                    msg_id, 'O que deseja fazer com as anotações?', reply_markup=keyboard)

            # Add homework or tests/exam content
            elif data == '%s_add' % self.class_name:
                if msg_id != None:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Conteúdo de prova', callback_data='%s_add_m' % self.class_name),
                         InlineKeyboardButton(text='Tarefas de casa', callback_data='%s_add_t' % self.class_name)]
                    ])
                    self.bot.editMessageText(
                        msg_id, 'O que deseja adicionar?', reply_markup=keyboard)

            # Add homework
            elif data == '%s_add_t' % self.class_name:
                if msg_id != None:
                    keyboards = []
                    for tag, content in self.notes[chat_id]['subjects'].items():
                        keyboards.append(InlineKeyboardButton(
                            text=content['name'], callback_data='%s_add_t_%s' % (self.class_name, tag.lower())))

                    keyboards.sort()

                    keyboard = InlineKeyboardMarkup(inline_keyboard=list(
                        keyboards[i:i + 3] for i in range(0, len(keyboards), 3)))
                    self.bot.editMessageText(
                        msg_id, 'Escolha uma disciplina para adicionar tarefas de casa', reply_markup=keyboard)

            # Add homework for given subject
            elif data.startswith('%s_add_t_' % self.class_name):
                if data in cb_data_subjects_t:
                    if msg_id != None:
                        name = self.notes[chat_id]['subjects'][cb_data_subjects_t[data]]['name']

                        reply_msg = 'Responda a esta mensagem com o conteúdo da tarefa de casa. Envie apenas uma resposta.'
                        self.add_lock['id'] = msg_id
                        self.add_lock['type'] = 't'
                        self.add_lock['subject'] = cb_data_subjects_t[data]
                        print(self.add_lock)

                        self.bot.editMessageText(
                            msg_id, reply_msg, parse_mode='Markdown', reply_markup=None)

            # Add exams/tests content
            elif data == '%s_add_m' % self.class_name:
                if msg_id != None:
                    keyboards = []
                    for tag, content in self.notes[chat_id]['subjects'].items():
                        keyboards.append(InlineKeyboardButton(
                            text=content['name'], callback_data='%s_add_m_%s' % (self.class_name, tag.lower())))

                    keyboards.sort()

                    keyboard = InlineKeyboardMarkup(inline_keyboard=list(
                        keyboards[i:i + 3] for i in range(0, len(keyboards), 3)))
                    self.bot.editMessageText(
                        msg_id, 'Escolha uma disciplina para adicionar conteúdo de prova', reply_markup=keyboard)

            # Add exams/tests content for given subject
            elif data.startswith('%s_add_m_' % self.class_name):
                if data in cb_data_subjects_m:
                    if msg_id != None:
                        name = self.notes[chat_id]['subjects'][cb_data_subjects_m[data]]['name']

                        reply_msg = 'Responda a esta mensagem com o conteúdo de prova. Envie apenas uma resposta.'
                        self.add_lock['id'] = msg_id
                        self.add_lock['type'] = 'm'
                        self.add_lock['subject'] = cb_data_subjects_m[data]
                        print(self.add_lock)

                        self.bot.editMessageText(
                            msg_id, reply_msg, parse_mode='Markdown', reply_markup=None)

            # Delete homework or tests/exam content
            elif data == '%s_del' % self.class_name:
                if msg_id != None:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Conteúdo de prova', callback_data='%s_del_m' % self.class_name),
                         InlineKeyboardButton(text='Tarefas de casa', callback_data='%s_del_t' % self.class_name)]
                    ])
                    self.bot.editMessageText(
                        msg_id, 'O que deseja apagar?', reply_markup=keyboard)

            # Delete homework
            elif data == '%s_del_t' % self.class_name:
                if msg_id != None:
                    keyboards = []
                    for tag, content in self.notes[chat_id]['subjects'].items():
                        keyboards.append(InlineKeyboardButton(
                            text=content['name'], callback_data='%s_del_t_%s' % (self.class_name, tag.lower())))

                    keyboards.sort()

                    keyboard = InlineKeyboardMarkup(inline_keyboard=list(
                        keyboards[i:i + 3] for i in range(0, len(keyboards), 3)))
                    self.bot.editMessageText(
                        msg_id, 'Escolha uma disciplina para apagar tarefas de casa', reply_markup=keyboard)

            # Delete homework for given subject
            elif data.startswith('%s_del_t_' % self.class_name):
                # Find the id of the item we want to delete
                if data.rfind('_') == 21:
                    subject = cb_data_subjects_t[data[0:21]]
                    user_name = '%s (@%s)' % (msg['from']['first_name'], msg['from']['username']
                                              ) if 'username' in msg['from'] else msg['from']['first_name']
                    subject_name = self.notes[chat_id]['subjects'][subject]['name']

                    if data[22:].isdigit():
                        note_idx = int(data[22:])

                        del self.notes[chat_id]['subjects'][subject]['tarefas'][note_idx]
                        self.bot.editMessageText(msg_id, 'Tarefa de casa nº %d de %s apagada com sucesso!' % (
                            note_idx, subject_name), reply_markup=None)
                        self.bot.sendMessage(
                            chat_id, 'O usuário %s apagou uma tarefa de %s.' % (user_name, subject_name))
                    else:
                        if data[22:] == 'all':
                            self.notes[chat_id]['subjects'][subject]['tarefas'].clear(
                            )
                            self.bot.editMessageText(
                                msg_id, 'Tarefas de %s apagadas com sucesso!' % subject_name, reply_markup=None)
                            self.bot.sendMessage(chat_id, 'O usuário %s apagou todas as tarefas de %s.' % (
                                user_name, subject_name))

                if data in cb_data_subjects_t:
                    if msg_id != None:
                        name = self.notes[chat_id]['subjects'][cb_data_subjects_t[data]]['name']
                        subject = self.notes[chat_id]['subjects'][cb_data_subjects_t[data]]
                        tag = cb_data_subjects_t[data].lower()

                        content_len = len(subject['tarefas'])

                        t_reply = 'Selecione a tarefa de casa de %s para apagar:\r\n' % name if content_len > 0 else '*Não há tarefas de %s.*' % name

                        if content_len > 0:
                            keyboards = [InlineKeyboardButton(text='Voltar', callback_data='%s_del_t' % self.class_name),
                                         InlineKeyboardButton(
                                             text='Cancelar', callback_data='%s_menu' % self.class_name),
                                         InlineKeyboardButton(
                                             text='Todas', callback_data='%s_del_t_%s_all' % (self.class_name, tag)),
                                         ]

                            for content in subject['tarefas']:
                                note_date = date.fromtimestamp(
                                    content['date_added'])
                                note_index = subject['tarefas'].index(content)
                                t_reply += ' - *#%d*, adicionada em *%s*: %s\r\n' % (
                                    note_index, note_date.strftime('%d/%m/%Y'), content['text'])

                                keyboards.append(
                                    InlineKeyboardButton(text='#%d' % note_index, callback_data='%s_del_t_%s_%d' % (
                                        self.class_name, cb_data_subjects_t[data].lower(), note_index))
                                )

                            keyboard = InlineKeyboardMarkup(
                                inline_keyboard=list(
                                    keyboards[i:i + 5] for i in range(0, len(keyboards), 5))
                            )
                            self.bot.editMessageText(
                                msg_id, t_reply, parse_mode='Markdown', reply_markup=keyboard)
                        else:
                            self.bot.editMessageText(
                                msg_id, t_reply, parse_mode='Markdown')
            # Delete tests/exams content
            elif data == '%s_del_m' % self.class_name:
                if msg_id != None:
                    keyboards = []
                    for tag, content in self.notes[chat_id]['subjects'].items():
                        keyboards.append(InlineKeyboardButton(
                            text=content['name'], callback_data='%s_del_m_%s' % (self.class_name, tag.lower())))

                    keyboards.sort()

                    keyboard = InlineKeyboardMarkup(inline_keyboard=list(
                        keyboards[i:i + 3] for i in range(0, len(keyboards), 3)))
                    self.bot.editMessageText(
                        msg_id, 'Escolha uma disciplina para apagar o conteúdo da prova', reply_markup=keyboard)

            # Delete tests/exams content for given subject
            elif data.startswith('%s_del_m_' % self.class_name):
                # Find the id of the item we want to delete
                if data.rfind('_') == 21:
                    subject = cb_data_subjects_m[data[0:21]]
                    user_name = '%s (@%s)' % (msg['from']['first_name'], msg['from']['username']
                                              ) if 'username' in msg['from'] else msg['from']['first_name']
                    subject_name = self.notes[chat_id]['subjects'][subject]['name']

                    if data[22:].isdigit():
                        note_idx = int(data[22:])

                        del self.notes[chat_id]['subjects'][subject]['materia_provas'][note_idx]
                        self.bot.editMessageText(msg_id, 'Conteúdo nº %d de %s apagado com sucesso!' % (
                            note_idx, subject_name), reply_markup=None)
                        self.bot.sendMessage(
                            chat_id, 'O usuário %s apagou um conteúdo de %s.' % (user_name, subject_name))
                    else:
                        if data[22:] == 'all':
                            self.notes[chat_id]['subjects'][subject]['materia_provas'].clear(
                            )
                            self.bot.editMessageText(
                                msg_id, 'Conteúdo de %s apagado com sucesso!' % subject_name, reply_markup=None)
                            self.bot.sendMessage(chat_id, 'O usuário %s apagou todos os conteúdos de %s.' % (
                                user_name, subject_name))

                if data in cb_data_subjects_m:
                    if msg_id != None:
                        name = self.notes[chat_id]['subjects'][cb_data_subjects_m[data]]['name']
                        subject = self.notes[chat_id]['subjects'][cb_data_subjects_m[data]]
                        tag = cb_data_subjects_m[data].lower()

                        content_len = len(subject['materia_provas'])

                        m_reply = 'Selecione o conteúdo de %s para apagar:\r\n' % name if content_len > 0 else '*Não há conteúdo de %s.*' % name

                        if content_len > 0:
                            keyboards = [InlineKeyboardButton(text='Voltar', callback_data='%s_del_m' % self.class_name),
                                         InlineKeyboardButton(
                                text='Cancelar', callback_data='%s_menu' % self.class_name),
                                InlineKeyboardButton(
                                text='Todos', callback_data='%s_del_m_%s_all' % (self.class_name, tag)),
                            ]

                            for content in subject['materia_provas']:
                                note_date = date.fromtimestamp(
                                    content['date_added'])
                                note_index = subject['materia_provas'].index(
                                    content)
                                m_reply += ' - *#%d*, adicionado em *%s*: %s\r\n' % (
                                    note_index, note_date.strftime('%d/%m/%Y'), content['text'])

                                keyboards.append(
                                    InlineKeyboardButton(text='#%d' % note_index, callback_data='%s_del_m_%s_%d' % (
                                        self.class_name, cb_data_subjects_m[data].lower(), note_index))
                                )

                            keyboard = InlineKeyboardMarkup(
                                inline_keyboard=list(
                                    keyboards[i:i + 5] for i in range(0, len(keyboards), 5))
                            )
                            self.bot.editMessageText(
                                msg_id, m_reply, parse_mode='Markdown', reply_markup=keyboard)
                        else:
                            self.bot.editMessageText(
                                msg_id, m_reply, parse_mode='Markdown')

            # List homeworks or tests/exams content
            elif data == '%s_list' % self.class_name:
                if msg_id != None:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Matérias de prova', callback_data='%s_list_m' % self.class_name),
                         InlineKeyboardButton(text='Tarefas de casa', callback_data='%s_list_t' % self.class_name)]
                    ])
                    self.bot.editMessageText(
                        msg_id, 'O que deseja listar?', reply_markup=keyboard)

            # List homeworks
            elif data == '%s_list_t' % self.class_name:
                keyboards = []
                for tag, content in self.notes[chat_id]['subjects'].items():
                    keyboards.append(InlineKeyboardButton(
                        text=content['name'], callback_data='%s_list_t_%s' % (self.class_name, tag.lower())))

                keyboards.sort()

                if msg_id != None:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=list(
                        keyboards[i:i + 3] for i in range(0, len(keyboards), 3)))
                    self.bot.editMessageText(
                        msg_id, 'Escolha uma matéria para mostrar a lista de tarefas', reply_markup=keyboard)

            # List homeworks for a given subject
            elif data.startswith('%s_list_t_' % self.class_name):
                if data in cb_data_subjects_t:
                    if msg_id != None:
                        name = self.notes[chat_id]['subjects'][cb_data_subjects_t[data]]['name']

                        content_len = len(
                            self.notes[chat_id]['subjects'][cb_data_subjects_t[data]]['tarefas'])

                        t_reply = '*Tarefas de %s*\r\n' % name if content_len > 0 else '*Não há tarefas de %s.*' % name

                        if content_len > 0:
                            t_reply += 'total: %d\r\n\r\n' % content_len

                            for content in self.notes[chat_id]['subjects'][cb_data_subjects_t[data]]['tarefas']:
                                note_date = date.fromtimestamp(
                                    content['date_added'])
                                t_reply += ' - *%s*: %s\r\n' % (
                                    note_date.strftime('%d/%m/%Y'), content['text'])

                        self.bot.editMessageText(
                            msg_id, t_reply, parse_mode='Markdown', reply_markup=None)

            # List tests/exams content
            elif data == '%s_list_m' % self.class_name:
                keyboards = []
                for tag, content in self.notes[chat_id]['subjects'].items():
                    keyboards.append(InlineKeyboardButton(
                        text=content['name'], callback_data='%s_list_m_%s' % (self.class_name, tag.lower())))

                keyboards.sort()

                if msg_id != None:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=list(
                        keyboards[i:i + 3] for i in range(0, len(keyboards), 3)))
                    self.bot.editMessageText(
                        msg_id, 'Escolha uma disciplina para mostrar o conteúdo da próxima prova:', reply_markup=keyboard)

            # List tests/exams content for a given subject
            elif data.startswith('%s_list_m_' % self.class_name):
                if data in cb_data_subjects_m:
                    if msg_id != None:
                        name = self.notes[chat_id]['subjects'][cb_data_subjects_m[data]]['name']

                        content_len = len(
                            self.notes[chat_id]['subjects'][cb_data_subjects_m[data]]['materia_provas'])

                        m_reply = '*Conteúdo de %s*\r\n' % name if content_len > 0 else '*Não há conteúdo de prova de %s.*' % name

                        if content_len > 0:
                            m_reply += 'total: %d\r\n\r\n' % content_len

                            for content in self.notes[chat_id]['subjects'][cb_data_subjects_m[data]]['materia_provas']:
                                m_reply += ' - %s\r\n' % content['text']

                        self.bot.editMessageText(
                            msg_id, m_reply, parse_mode='Markdown', reply_markup=None)
