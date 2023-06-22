from datetime import datetime
import vk_api

from config import acces_token


class VkTools():
    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)
        self.offset = 0

    def get_profile_info(self, user_id):

        info, = self.api.method('users.get', {'user_id': user_id,
                                              'fields': 'city,bdate,sex,relation'})
        age = info.get('bdate', '').split('.')[-1]
        user_info = {'name': info.get('first_name') + ' ' + info.get('last_name'),
                     'id': info['id'],
                     'age': datetime.now().year - int(age) if age else '',
                     'sex': info.get('sex', 1),
                     'city': info.get('city', {}).get('title'),
                     'relation': info.get('relation', 1)}
        return user_info

    def serch_users(self, params):
        users = self.api.method('users.search',
                                {'count': 20,
                                 'offset': self.offset,
                                 'age_from': params['age'] - 5,
                                 'age_to': params['age'] + 5,
                                 'sex': 1 if params['sex'] == 2 else 2,
                                 'hometown': params['city'],
                                 'status': params['relation'],
                                 'is_closed': False})
        self.offset += 20
        result = []
        if users.get('items'):
            users = users['items']
            for user in users:
                if user['is_closed'] == False:
                    result.append({'id': user['id'],
                                   'name': user.get('first_name') + ' '
                                           + user.get('last_name')})
        return result

    def get_photos(self, user_id):
        photos = self.api.method('photos.get', {'user_id': user_id,
                                                'album_id': 'profile', 'extended': 1})
        result = []
        if photos.get('items'):
            for photo in photos['items']:
                result.append((photo['id'],
                               photo['likes']['count'] + photo['comments']['count']))
            result.sort(key=lambda x: x[1], reverse=True)
            return ','.join(f'photo{user_id}_{r[0]}' for r in result[:3])


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(789657038)

    users = bot.serch_users(params)
    for e, u in enumerate(users):
        print(u)
        if e == 5:
            break

    print(bot.get_photos(users[2]['id']))