import vk_api
from datetime import datetime
from config import acces_token


class VkTools:
    def __init__(self, acces_toke):
        self.api = vk_api.VkApi(token=acces_toke)

    def get_profile_info(self, user_id):

        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city,sex,bdate,home_town'
                                 }
                                )
        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id': info['id'],
                     'city': info['city']['id'] if 'city' in info else None,
                     'bdate': info['bdate'],
                     'sex': info['sex'],
                     'home_town': info['home_town']
                     }
        return user_info

    def id_city(self, city_name):
        info, = self.api.method('database.getCities',
                                {'q': city_name,
                                 'need_all': 1,
                                 'count': 1})['items']
        city_id = info['id']
        return city_id

    def search_users(self, params, offset=None):

        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5

        users = self.api.method('users.search',
                                {'count': 20,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if not user['is_closed']:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                            }
                           )

        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )

        res.sort(key=lambda x: x['likes'] + x['comments'], reverse=True)

        return res


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(id)
    users = bot.search_users(params)
