import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from constants import *
from main import *


class Bot:
    def __init__(self, token, group_id, prepared_schedule):
        self.vk_session = vk_api.VkApi(token=token)
        self.vk_session._auth_token()
        self.vk = self.vk_session.get_api()
        self.group_id = group_id
        self.prepared_schedule = prepared_schedule
        print(self.prepared_schedule)


    def send_message(self, event, text):
        print(event.object.message['text'], '\t', str(event.object.message['from_id']))

        self.vk.messages.send(
            peer_id = int(event.object.message['peer_id']),
            random_id = get_random_id(),
            message = text,
        ) 


    def bot_action(self, event):
        event_text = event.object.message['text'].lower()

        if 'бот' in event_text:
            if event_text.split().index('бот') == 0:
                bot_command = event_text.replace('бот', '')

                if bot_command.replace(' ', '') == 'пара':
                    current_time = str(datetime.datetime.now().time())[:5]
                    text = post_schedule(self.prepared_schedule, current_time)
                    self.send_message(event, text)

                elif bot_command.replace(' ', '') == 'расписание':
                    self.send_message(event, 'Пожалуйста, подождите')
                    text = get_full_schedule(self.prepared_schedule)
                    self.send_message(event, text)

                elif bot_command.replace(' ', '') == 'привет' or bot_command == '':
                    text = '''
                        Вас приветствует бот.\n
                        Чтобы узнать следующую пару, напишите "Бот пара"\n
                        Чтобы узнать все расписание на сегодня, напишите "Бот расписание"'''
                    self.send_message(event, text)

                else:
                    text = 'Не удалось распознать команду'
                    self.send_message(event, text)

    def activate_longpoll(self):
        longpoll = VkBotLongPoll(self.vk_session, group_id=self.group_id)
        while True:
            for event in longpoll.listen():

                #current_time = str(datetime.datetime.now().time())[:5]
               #if planed_schedule_post(self.prepared_schedule, current_time) != None:
                    #text = post_schedule(event, current_time)
                    #self.vk.messages.send(
                    #    peer_id = int(event.object.message['peer_id']),
                    #    random_id = get_random_id(),
                    #    message = text,
                   # ) 

                if event.type == VkBotEventType.MESSAGE_NEW:
                    self.bot_action(event)
                    
