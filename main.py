from pprint import pprint
from soupsieve import select
import db.database as database
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from datetime import datetime
import json
from config import user_token, group_token

vk_session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_session)


def write_msg(user_id, msg, attach=''):
    vk_session.method('messages.send', {'user_id': user_id, 'message': msg, 'random_id': randrange(10 ** 7),
                                        'attachment': attach})


def get_param(add_params: dict = None):
    params = {
        'access_token': user_token,
        'v': '5.131'
    }
    if add_params:
        params.update(add_params)
        pass
    return params


data = [{'people': [], 'favorite': []}]


class VkinderBot:

    def __init__(self, user_id):
        self.dict_info = []
        self.user = database.VkinderUser
        self.user_id = user_id
        self.username = self.user_name()
        self.age = int()
        self.sex = int()
        self.city = int()
        self.offset = randrange(100)
        self.searching_user_id = int()
        self.top_photos = ''
        self.commands = ["привет", "q", "start", "l", "n", "e", "w"]
        

    def user_name(self):
        response = requests.get('https://api.vk.com/method/users.get', get_param({'user_ids': self.user_id}))
        for user_info in response.json()['response']:
            self.username = user_info['first_name'] + ' ' + user_info['last_name']
            
        return self.username
    
    def get_userinfo(self,user_id):
        user_id = user_id
        fields = ['bdate', 
                  'city', 
                  'sex',
                  'status',
                  'home_town',
                  'country', 
                  'nickname', 
                  'followers_count', 
                  'occupation', 
                  'activities', 
                  'home_town', 
                  'books', 
                  'music', 
                  'interests', 
                  'langs',
                  'relation',
                  'career',
                  'friend_status',
                  'group_id'
                  ]
        
        param = {'user_ids':user_id,
                'screen_name':user_id,
                'is_closed':False,
                'fields': ', '.join([i for i in fields])}
        
        clear_user = {}
        
        
        response = requests.get('https://api.vk.com/method/users.get', get_param(param))
        
        for user_info in response.json()['response']:
            if user_info['bdate'] =='' or user_info['bdate'] == None:
                continue
            else:
                clear_user['bdate'] = user_info['bdate']
                
            if user_info['sex'] == '' or user_info['sex'] ==0:
                continue
            else:
                clear_user['sex'] = user_info['sex']
                
            if user_info['city']['title'] == '':
                continue
            else:
                clear_user['city'] = user_info['city']
                
            if user_info['relation'] == 0:
                continue
            else:
                clear_user['relation'] = user_info['relation']
                
            clear_user['id'] = user_info['id']
            
        if clear_user['bdate'] != False or clear_user['bdate'] != '': 
               
            clear_user['age'] = self.get_age(clear_user)
        
        return clear_user
        
        
    def get_age(self,user_obj):
        index = 5
        if 'bdate' in user_obj:
            date = len(user_obj['bdate'])
            if date == 9:
                index = 5
            elif date == 8:
                index = 4
            elif date == 10:
                index = 6
            age = datetime.now().year - int(user_obj['bdate'][index:])
            
        return int(age)
        
        
    
    #Все пользователи
    def file_writer_all(self, my_dict):
        data[0]['people'].append(my_dict)
        with open('output.json', 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2,)
            
    #favorite пользователи
    def file_writer_fav(self, my_dict):
        data[0]['favorite'].append(my_dict)
        with open('output.json', 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2,)

    def bot_menu(self):
        '''
        Главное меню
        
        Команды:
        w - запишет всех найденных людей в базу данных.
        l - выведет список людей из базы данных, которые Вам понравились.
        e - позволит изменить критерии поиска.
        n - продолжит поиск людей.
        q - выйти из программы.
        '''

        write_msg(self.user_id, self.bot_menu.__doc__)
        while True:
            
            for new_event in longpoll.listen():
                
                if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                    
                    if new_event.message.lower() == self.commands[3]: #l
                        
                        write_msg(self.user_id, 'Список людей, которые Вам понравились:')
                        target_user = database.view_all(self.user_id)
                        
                        for target_user in target_user:
                            write_msg(self.user_id, f'@id{target_user}')
                        write_msg(self.user_id, self.bot_menu.__doc__)
                        
                    elif new_event.message.lower() == self.commands[5]: #e
                        
                        self.offset = 0
                        self.start()
                        
                    elif new_event.message.lower() == self.commands[4]: #n
                        
                        write_msg(self.user_id, 'Идет поиск...')
                        self.offset += 1
                        self.find_user()
                        self.get_photos()
                        write_msg(self.user_id,
                                  f'Имя  и Фамилия: {self.username}\n Ссылка на пользователя: @id{self.searching_user_id}',
                                  self.top_photos)
                        info = {'vk_id': self.searching_user_id, 'user_name': self.username, 'age': self.age,
                                'url': 'https://vk.com/id' + str(self.searching_user_id)}
                        self.file_writer_all(info)
                        self.searching()
                        
                    elif new_event.message.lower() == self.commands[1]: #q
                        
                        self.new_message(new_event.message.lower())
                        exit(write_msg(self.user_id, 'До скорого!'))
                        
                    elif new_event.message.lower() == self.commands[6]: #w
                        
                        write_msg(self.user_id, 'Записываем данные из файла в базу данных')
                        database.write_master()
                        write_msg(self.user_id, 'Готово.')
                        write_msg(self.user_id, self.bot_menu.__doc__)
                        
                    else:
                        
                        write_msg(self.user_id, f"Не корректная команда.")
                        self.bot_menu()


    def start(self):
        
        self.user_name()
        
        write_msg(self.user_id, 'Автопоиск: 1, Ручной поиск: 2')
        for new_event in longpoll.listen():
            
            if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                message_text = new_event.text
                if message_text.lower() == '2':
                    
                    write_msg(self.user_id, 'В каком городе будем искать?')
                    for new_event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                            
                            message_text = new_event.text
                            self.user_city(message_text)
                            self.user_name()
                            self.user_age()
                            self.user_sex()
                            self.find_user()
                            self.get_photos()
                            people = {'vk_id': self.searching_user_id, 'user_name': self.username, 'age': self.age,
                       '            url': 'https://vk.com/id' + str(self.searching_user_id)}
                            self.file_writer_all(people)
                            write_msg(self.user_id,
                            f'Имя  и Фамилия: {self.username}\n \n Ссылка на пользователя: @id{self.searching_user_id}',
                            self.top_photos)
                
                            return self.searching()
                        
                elif message_text.lower() == '1':
                    
                    user_info = self.get_userinfo(self.user_id)
                    self.user_city(user_info['city']['title'])
                    self.user_name()
                    self.user_age(user_info['age'])
                    self.user_sex(user_info['sex'])
                    self.find_user()
                    self.get_photos()
                    people = {'vk_id': self.searching_user_id, 'user_name': self.username, 'age': self.age,
                       '            url': 'https://vk.com/id' + str(self.searching_user_id)}
                    self.file_writer_all(people)
                    write_msg(self.user_id,
                    f'Имя  и Фамилия: {self.username}\n \n Ссылка на пользователя: @id{self.searching_user_id}',
                    self.top_photos)
                    
                    return self.searching()
                        
                    



    def searching(self):
        write_msg(self.user_id, 'Понравился пользователь? Напишите да или например далее')
        
        while True:     
            for new_event in longpoll.listen():
    
                if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                    
                    if new_event.message.lower() == 'q':
                        
                        return self.new_message(new_event.message.lower())
                    
                    elif new_event.message.lower() == 'да':
                        
                        people = {'vk_id': self.searching_user_id, 'user_name': self.username, 'age': self.age,
                                  'url': 'https://vk.com/id' + str(self.searching_user_id)}
                        self.file_writer_fav(people)
                        write_msg(self.user_id, 'Пользователь добавлен в базу данных')
                        self.bot_menu()
                        
                    else:
                        
                        write_msg(self.user_id, 'Идет поиск...')
                        self.offset += 1
                        self.find_user()
                        self.get_photos()
                        write_msg(self.user_id,
                                  f'Имя  и Фамилия: {self.username}\n Ссылка на пользователя: @id{self.searching_user_id}',
                                  self.top_photos)
                        info = {'vk_id': self.searching_user_id, 'user_name': self.username, 'age': self.age,
                               'url': 'https://vk.com/id' + str(self.searching_user_id)}
                        self.file_writer_all(info)
                        write_msg(self.user_id, 'Понравился пользователь? Напишите да или что-то другое')

    def user_age(self, age=None):
        
        if age != None:
            return self.age
        
        try:
            
            write_msg(self.user_id, 'Введите желаемый возраст')
            for new_event in longpoll.listen():
                
                if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                    self.age = int(new_event.message)
                    if 17 < self.age <= 60:
                        
                        return self.age
                    
                    else:
                        
                        write_msg(self.user_id, 'Некорректное значение, \n Введите число от 18 до 60')
                        return self.user_age()
                    
        except ValueError:
            
            write_msg(self.user_id, 'Некорректное значение, \n Введите число от 18 до 60')
            
            return self.user_age()

    def user_sex(self, sex=None):
        
        if sex != None:
            if sex == 1:
                self.sex = 2
            if sex == 2:
                self.sex == 1
             
            return self.sex
        
        try:
            
            find_message = f'Какой пол будем искать? Введите: \n 1 - женский\n 2 - мужской\n 3 - по умолчанию\n'
            write_msg(self.user_id, find_message)
            
            for new_event in longpoll.listen():
                
                if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                    self.sex = new_event.message
                    
                    if int(self.sex) in [1, 2, 3]:
                        
                        return self.sex
                    else:
                        
                        write_msg(self.user_id, f'Некорректное значение')
                        
                        return self.user_sex()
        except ValueError:
            
            write_msg(self.user_id, f'Некорректное значение')
            self.user_sex()

    def user_city(self, city):
        
        try:
            
            response = requests.get('https://api.vk.com/method/database.getCities',
                                    get_param({'country_id': 1, 'count': 1, 'q': city}))
            user_info = response.json()['response']
            self.city = user_info['items'][0]['id']
            
        except IndexError:
            
            write_msg(self.user_id, f'Некорректное значение')
            self.start()
            
        return self.city

    #костыль с offset)))
    def find_user(self):
            
        try:
            
            response = requests.get('https://api.vk.com/method/users.search',
                                    get_param({'count': 1,
                                                'offset': self.offset,
                                                'city': self.city,
                                                'country': 1,
                                                'sex': self.sex,
                                                'age_from': self.age,
                                                'age_to': self.age,
                                                'fields': 'is_closed',
                                                'status': 6,
                                                'has_photo': 1}
                                               )
                                    )
            if response.json()['response']['items']:
                
                for searching_user_id in response.json()['response']['items']:
                    
                    private = searching_user_id['is_closed']
                    
                    if private:
                        
                        self.offset += randrange(100) 
                        self.find_user()
                        
                    else:
                        
                        self.searching_user_id = searching_user_id['id']
                        self.username = searching_user_id['first_name'] + ' ' + searching_user_id['last_name']
            else:
                
                self.offset += randrange(100)
                self.find_user()
                
        except KeyError:
            
            write_msg(self.user_id, f'попробуйте ввести другие критерии поиска')
            self.start()

    def get_photos(self):
        
        photos = []
        response = requests.get(
            'https://api.vk.com/method/photos.get',
            get_param({'owner_id': self.searching_user_id,
                        'album_id': 'profile',
                        'extended': 1}))
        try:
            
            sorted_response = sorted(response.json()['response']['items'],
                                     key=lambda x: x['likes']['count'], reverse=True)
            for photo_id in sorted_response:
                
                photos.append(f'''photo{self.searching_user_id}_{photo_id['id']}''')
            self.top_photos = ','.join(photos[:3])
            
            return self.top_photos
        
        except:
            
            pass

    def new_message(self, msg):

        if msg.lower() == self.commands[0]:
            return f"Здравствуйте, Вас приветствует чат-бот Vkinder! \n" \
                   f"Отправьте слово 'start' чтобы начать подбор. \n" \
                   f"Чтобы завершить программу, напишите 'q'."

        elif msg.lower() == self.commands[1]:
            
            return f"До скорого!"

        elif msg.lower() == self.commands[2]:
            
            return self.start()
        
        else:
            return f"Некорректная команда, {self.username}."


if __name__ == '__main__':
    
    for event in longpoll.listen():
        
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            
            bot = VkinderBot(event.user_id)
            write_msg(event.user_id, bot.new_message(event.text))
