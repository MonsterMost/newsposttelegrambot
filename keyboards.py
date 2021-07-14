from telebot.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup

)
#Позключение модуля кнопок


# category_button = KeyboardButton(text='Политика')
#
# #Это экземпляр класса    это запуск конструктора
# category_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
# # ширина коробочки row_width=1 по дэфолту =3
# # resize_keyboard=True разрешение на изменение размера
# #Создаем коробочку, в которой будет лежать кнопочка
# category_markup.add(category_button)

#Теперь сделаем так, чтобы можно было брать категории с базы


# def generate_category_markup(category_name):
#     category_button = KeyboardButton(text=category_name)
#
#     category_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
#     category_markup.add(category_button)
#
#     return category_markup


# [('Внешняя политика',), ('США',), ('Европа',),
#  ('Военные преступления на Украине',), ('Украина',), ('Белоруссия',)]



#Обновляем функцию под список категорий
def generate_category_markup(category_list):
    category_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1) #Надо вытащить за цикл. Сначала создается коробка

    for category in category_list: # проходим по всем картежам в списке
        category_button = KeyboardButton(text=category[0]) #Кладем нулевой элемент кортежа (единственный)
        category_markup.add(category_button)

    return category_markup


def generate_link_murkup(link):
    link_murkup = InlineKeyboardMarkup() #коробочка для кнопки
    link_button = InlineKeyboardButton(url=link, text='Читать на сайте') #кнопка в сообщении
    image_button = InlineKeyboardButton(url=link, text='Ссылка на картинку') #кнопка в сообщении
    link_murkup.add(link_button, image_button)
    #link_murkup.row(link_button, image_button)
    return link_murkup #вернуть коробочку