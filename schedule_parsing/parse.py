from bs4 import BeautifulSoup
import requests
from constants import *
import datetime
from selenium import webdriver


def get_link_list(page):
    teachers_page = requests.get(page)
    teachers_page_soup = BeautifulSoup(teachers_page.text, 'lxml')

    link_table = {}
    for tr in teachers_page_soup.find_all('tr')[3:]:
        row = [i.text for i in tr.find_all('td')]
        if row[1] == '':
            continue
        link_table[row[0]] = [row[1], row[2]]

    return link_table


def parse_schedule(target):
    splitted_tags = []
    for i in target:
        text = i.text.split()
        text.remove(text[-1])
        text.remove(text[-1])
        text[1] = text[1].join(text[1:])
        text = text[:2]

        prepared_text = text[1][::-1]
        
        full_name = prepared_text[:5]
        for j in prepared_text[5:]:
            full_name += j
            if j != j.lower():
                break
        full_name = full_name[::-1].replace('—', ' ').replace(',','')
        splitted_tags.append([text[0], full_name])

    return splitted_tags


def get_schedule(page):
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    driver.get(page)
    select = driver.find_element_by_id('group')
    for option in select.find_elements_by_css_selector('option'):
        if option.get_attribute('value') == 'ПОКС-12':
            option.click()
            break
    button = driver.find_element_by_name('stt')
    button.click()
    schedule_page_soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()

    p_tags = schedule_page_soup.find('main').find_all('p')[1:]

    if len(p_tags) <= 1:
        return 1

    schedule = {}
    for t in parse_schedule(p_tags[::-1]):
        schedule[t[0]] = t[1]
    
    return schedule
 

def get_current_pare(links, schedule, time):
    try:
        schedule_keys = list(schedule.keys())[:4]
    except AttributeError:
        return 'Расписание отсутствует.\nЕсли это не так, обратитесь к моему создателю и скажите, что он придурок'

    if int(schedule_keys[1].replace(':', '')) >= int(schedule_keys[-1].replace(':', '')):
        schedule_keys = schedule_keys[:3]

    for t in schedule_keys[::-1]:
        if int(t.replace(':', '')) + TIME_TO_CHANGE_PARE > int(time.replace(':', '')):
            current_pare_time = t
            break
    try:
        current_pare_teacher = schedule[current_pare_time]
        current_pare_link = links[schedule[current_pare_time]]
    except KeyError:
        return 'Фамилия преподавателя отсутствует или искажена'
    except:
        return 'Следующая пара отсутствует'

    return current_pare_teacher, current_pare_link, t


def post_schedule(parsed_schedule, time):
    links = get_link_list(TEACHERS_PAGE_LINK)
    schedule = parsed_schedule
    time = time
    current_pare = get_current_pare(links, schedule, time)
    try:
        text = 'Преподаватель: {}\nСсылка: {}\nПочта: {}\nНачало в {}\n\n'.format(
                                                                        current_pare[0],
                                                                        current_pare[1][0],
                                                                        current_pare[1][1],
                                                                        current_pare[2],
                                                                    )
    except IndexError:
        return current_pare
    return text


def get_full_schedule(parsed_schedule):
    links = get_link_list(TEACHERS_PAGE_LINK)
    schedule = parsed_schedule

    text = []

    time = list(schedule.keys())

    for t in time[::-1]:
        text.append(post_schedule(parsed_schedule, t))

    return text


#def planed_schedule_post(parsed_schedule, time):
#    keys = [i for i in list(parsed_schedule.keys()[::-1])]
#
 #   for key in keys:
#        if time == key:
#            return post_schedule(parsed_schedule, key)

