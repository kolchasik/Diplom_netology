# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import DBase


class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None
        self.data = DBase()
        self.status = None
        self.worksheets = []

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()})

    def see_profile(self):
        while True:
            if self.worksheets:
                anket = self.worksheets.pop()
                if self.data.from_bd(self.params['id'], anket['id']):
                    continue
                else:
                    self.data.to_bd(self.params['id'], anket['id'])
                    return anket
            else:
                self.worksheets = self.api.serch_users(self.params)
                if not self.worksheets:
                    return None

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                attach = None
                if not self.status and command:
                    self.params = self.api.get_profile_info(event.user_id)
                    self.status = 'run'
                    msg = (f'Здравствуй, {self.params["name"]}\n'
                           f'Смотри, сейчас покажу людей из своего города\n'
                           f'и твоего возраста для знакомства, поехали?\n'
                           f'"да/нет"')

                elif command in ('завершить', 'пока', 'q', 'exit', 'n', 'no', 'нет'):
                    self.params, self.status = None, None
                    msg = "Рад был помочь"

                elif self.status == 'run':
                    if not self.params['age']:
                        msg = 'Без года рождения я не смогу начать поиск'
                        self.status = 'age'

                    elif not self.params['city']:
                        msg = 'Без города я не смогу начать поиск'
                        self.status = 'city'

                    else:
                        msg = (f'Начинаем поиск!\n'
                               f'Данные для поиска:\n'
                               f'Возраст: {self.params["age"]}\n'
                               f'Город: {self.params["city"]}\n'
                               f'Для продолжения просмотра анкет напиши "далее"')
                        self.status = 'view'

                elif self.status == 'age':
                    if command.isdigit():
                        self.params['age'] = int(command)
                        msg = (f'Ваш возраст изменён на {self.params["age"]}\n'
                               f'отправьте любое сообщение для подтверждения')
                        self.status = 'run'
                    else:
                        msg = f'{command} не является числом - повторите'

                elif self.status == 'city':
                    if not command.isdigit():
                        self.params['city'] = command.capitalize()
                        msg = (f'Ваш город изменён на {self.params["city"]}\n'
                               f'отправьте любое сообщение для подтверждения')
                        self.status = 'run'
                    else:
                        msg = f'{command} не является городом - повторите'

                elif self.status == 'view' and command in ('f', 'd', 'далее', 'next'):
                    partner = self.see_profile()
                    if partner:
                        msg = f'{partner["name"]}  vk.com/id{partner["id"]}'
                        attach = self.api.get_photos(partner['id'])
                    else:
                        msg = 'Анкет не найдено :('

                self.message_send(event.user_id, msg, attach)


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()


