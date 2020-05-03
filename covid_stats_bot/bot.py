import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from constants import *
from bs4 import BeautifulSoup
import requests
import googletrans


def get_covid_stats(page=COVID_PAGE, country=''):
	get_page = requests.get(page)
	page_soup = BeautifulSoup(get_page.text, 'lxml')

	translator = googletrans.Translator()

	if country == None or country == '':
		stat_div = page_soup.find_all('div', class_='maincounter-number')
		full_stat = []
		for i in stat_div:
			full_stat.append(i.find('span').text)

		accepted, deaths, recovered = full_stat
		text = 'Зараженные: {}\nСмерти: {}\nВылечилось: {}'.format(accepted, deaths, recovered)
		return text

	try:
		tr_country = translator.translate(country, src='ru', dest='en').text.lower()
	except:
		return 'Нет информации об этой стране'

	table = page_soup.find('tbody')

	for tr in table.find_all('tr'):
		if tr.find('td').text.lower() == tr_country:
			needed_tr = tr
			break
	try:
		country_info = [i.text for i in needed_tr.find_all('td')][:5]
	except:
		return 'Нет информации об этой стране'
	country_name, total_cases, new_cases, total_deaths, new_deaths = country_info
	text = 'Страна: {0}\nВсего зараженных: {1}\nНовые случаи заражения: {2}\nВсего смертей: {3}\nНовые смерти: {4}\n'.format(
				country_name,
				total_cases if total_cases != '' else '0',
				new_cases if new_cases != '' else '0',
				total_deaths if total_deaths != '' else '0',
				new_deaths if new_deaths != '' else '0')
	return text
		


class Bot:
	def __init__(self, token, group_id):
		self.vk_session = vk_api.VkApi(token=token)
		self.vk_session._auth_token()
		self.vk = self.vk_session.get_api()
		self.group_id = group_id


	def send_message(self, event, text):
		print('Пришло сообщение от ' + str(event.object.message['from_id']))
		print(event.object.message['text'], '\n')

		self.vk.messages.send(
			peer_id = int(event.object.message['peer_id']),
			random_id = get_random_id(),
			message = text,
		)


	def bot_action(self, event):
		event_text = event.object.message['text'].lower()

		if 'бот' in event_text and event_text.split().index('бот') == 0:
			bot_command = event_text.replace('бот', '') 

			if bot_command == '' or bot_command.replace(' ', '') == 'привет':
				text = """
						Вас приветствует бот, собирающий статистику о COVID-19.\n
						Для того, чтобы узнать мировую статистику, введите команду 'Бот коронавирус'.\n
						Для того, чтобы узнать статистику отдельной страны, введите 'Бот коронавирус СТРАНА'
				"""
				self.send_message(event, text)

			if 'коронавирус' in bot_command and bot_command.split().index('коронавирус') == 0:
				self.send_message(event, 'Пожалуйста подождите, вас запрос обрабатывается')
				covid_command = bot_command.replace('коронавирус', '')
				if covid_command.replace(' ', '') == '':
					self.send_message(event, get_covid_stats())
				else:
					self.send_message(event, get_covid_stats(country=covid_command.replace(' ', '')))


	def activate_longpoll(self):
		longpoll = VkBotLongPoll(self.vk_session, group_id=self.group_id)
		while True:
			for event in longpoll.listen():
				if event.type == VkBotEventType.MESSAGE_NEW:
					self.bot_action(event)



def main():
	bot = Bot(token=TOKEN, group_id=GROUP_ID)
	bot.activate_longpoll()

if __name__ == '__main__':
	main()