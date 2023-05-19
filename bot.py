import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

import database
from config import comunity_token, acces_token
from main import VkTools


class BotInterface:

    def __init__(self, comunity_toke, acces_toke):
        self.vk_session = vk_api.VkApi(token=comunity_toke)
        self.api = VkTools(acces_toke)
        self.params = None

    def send_msg(self, user_id, some_text, attachment=None):
        self.vk_session.method("messages.send", {"user_id": user_id,
                                                 "message": some_text,
                                                 "attachment": attachment,
                                                 "random_id": get_random_id()})

    def event_handler(self):
        offset = 0
        new_users = []
        longpool = VkLongPoll(self.vk_session)
        for event in longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                msg = event.text.lower()
                self.params = self.api.get_profile_info(event.user_id)
                if msg in ['привет', 'hi']:
                    self.send_msg(event.user_id, f"Здравствуйте, {self.params['name']}!\n"
                                                 f"Для поиска введите команду: Поиск")
                elif msg == 'поиск':
                    if len(self.params['bdate'].split('.')) != 3:
                        self.send_msg(event.user_id, f"Укажите ваш год рождения в формате ГГГГ")
                        for event in longpool.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                self.params['bdate'] = "Д.М." + event.text.lower()
                                break

                    if self.params['city'] is None:
                        if self.params['home_town'] != '':
                            self.params['city'] = self.api.id_city(self.params['home_town'])
                        else:
                            self.send_msg(event.user_id, f"Укажите ваш город")
                            for event in longpool.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    city = event.text.lower()
                                    self.params['city'] = self.api.id_city(city)
                                    break
                    database.create_db()
                    while len(new_users) == 0:
                        users = self.api.search_users(self.params, offset)
                        offset += 20
                        for i in range(len(users)):
                            user = users[i]
                            if user['id'] not in database.select_db(self.params['id']):
                                new_users.append(user)

                    user = new_users.pop(0)
                    photos_user = self.api.get_photos(user['id'])
                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                        if num == 2:
                            break
                    self.send_msg(event.user_id, f'Результат поиска {user["name"]} https://vk.com/id{user["id"]}',
                                  attachment=attachment)

                    database.insert_db(self.params['id'], user['id'])
                    self.send_msg(event.user_id, 'Для просмотра следующего профиля введите команду: Дальше')
                    for event in longpool.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            msg = event.text.lower()
                            if msg == 'дальше':
                                if len(new_users) == 0:
                                    offset += 20
                                    users = self.api.search_users(self.params, offset)
                                    for i in range(len(users)):
                                        u = users[i]
                                        if u['id'] not in database.select_db(self.params['id']):
                                            new_users.append(u)

                                user = new_users.pop(0)
                                photos_user = self.api.get_photos(user['id'])
                                attachment = ''
                                for num, photo in enumerate(photos_user):
                                    attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                                    if num == 2:
                                        break
                                self.send_msg(event.user_id,
                                              f'Результат поиска {user["name"]} https://vk.com/id{user["id"]}',
                                              attachment=attachment)
                                database.insert_db(self.params['id'], user['id'])
                                self.send_msg(event.user_id, 'Для просмотра следующего профиля введите команду: Дальше')
                            else:
                                self.send_msg(event.user_id, 'Команда не опознана.\n Введите команду: Поиск')
                                break

                elif msg == 'пока':
                    self.send_msg(event.user_id, 'Пока')
                else:
                    self.send_msg(event.user_id, 'Команда не опознана.\n Введите команду: Привет | Поиск | Пока')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
