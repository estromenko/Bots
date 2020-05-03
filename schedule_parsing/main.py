from parse import *
import datetime
from constants import *
from bot import *



def main():
    prepared_schedule = get_schedule(SCHEDULE_LINK)
    bot = Bot(token=TOKEN, group_id=GROUP_ID, prepared_schedule=prepared_schedule)
    bot.activate_longpoll()


if __name__ == '__main__':
    main()