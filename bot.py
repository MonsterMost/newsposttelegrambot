from telebot import TeleBot
import psycopg2 as sql
import keyboards
import configs

bot = TeleBot(configs.TOKEN)
db = sql.connect(
    database='russia_today_test',
    host='localhost',
    user='postgres',
    password='123456'
)

cursor = db.cursor()

@bot.message_handler(commands=['start'])
def command_start(message):
    chat_id = message.chat.id
    first_name = message.chat.first_name
    message_to_user = f'Привет, {first_name}\nЭто новостной бот!'
    bot.send_message(chat_id, message_to_user)
    choose_category(message)


def choose_category(message):
    chat_id = message.chat.id
    message_to_user = 'Выберите категорию'
    # Надо создать кнопочки
    # bot.send_message(chat_id, message_to_user, reply_markup=keyboards.category_markup) #Вместе с сообщением отправляем кнопки

    #Улучшаем код под новую функцию
    cursor.execute(
        '''
        select category_name from categories
        '''
    )
    categories = cursor.fetchall() #возвращается список кортежей
    category_markup = keyboards.generate_category_markup(categories)# теперь передаем сюда список кортежей категорий
    msg = bot.send_message(chat_id, message_to_user, reply_markup=category_markup) #Вместе с сообщением отправляем кнопки
    bot.register_next_step_handler(msg, show_category) #ждем после того как появится msg отработать функцию ПОКАЗАТЬ


def show_category(message): #Функция возвращает новости с выбранной категорией
    chat_id = message.chat.id
    category_name = message.text # внешняя политика
    cursor.execute('''
    select title, description, date, author, article_link, image_link
    from articles
    join categories using(category_id)
    where category_name = %s
    ''', (category_name,))# кортеж с одним элементом в конце запятая, чтобы показывать что это кортеж

    articles = cursor.fetchall() #вернет список
    if articles: #Если есть они

        for article in articles:
            title = article[0]
            description = article[1]
            date = article[2]
            author = article[3]
            article_link = article[4]
            image_link = article[5]

            message_to_user = f'''<i>{date}</i>
        
<b>{title}</b>

{description}<a href="{article_link}">Подробее</a>

<u>{author}</u>
'''
        link_murkup = keyboards.generate_link_murkup(article_link)
        msg = bot.send_photo(chat_id=chat_id,
                             photo=image_link,
                             caption=message_to_user,
                             parse_mode='HTML',
                             reply_markup=link_murkup) # Метод отправки фото
        #chat_id=chat_id чат id, photo=image_link ссылка на картинку, caption=message_to_user описание <200 символов

        # print(articles)

    else:
        msg = bot.send_message(chat_id, 'Такой категории нет. Выберите из существующих!')


    # choose_category(message) #Зацикливаем бота снова, но он снова просит выбрать категою, переделаем
    #может ругаться, но ничего страшного
    bot.register_next_step_handler(msg, show_category)

print("Бот работает...")
bot.polling()

db.close()
