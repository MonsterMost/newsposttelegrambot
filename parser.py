from bs4 import BeautifulSoup
import requests
from database import db, cursor
import re  # библиотека регулярных выражений

from pprint import pprint

# Парсер сайта новостей с помощью классов
url = 'https://russian.rt.com/world'


class Parser:
    def __init__(self, page_name):
        self.page_name = page_name
        self.URL = 'https://russian.rt.com'
        self.HEADERS = {
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_soup(self):  # Используем немного дуругую технологию, чтобы отлавливать ошибочные запросы
        response = requests.get(f'{self.URL}/{self.page_name}', headers=self.HEADERS)
        try:
            response.raise_for_status()  # отлов ошибок запросов
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            return soup

        except requests.HTTPError:
            print('Не удалось получить данные')

    def get_image_link_and_article_link(self, block):  # Картинки новостей вшиты в бэкграунд, будем получать их отдельно
        main_block = block.find('div', class_='cover__media')
        # Это словарь стиль: описание
        # image_link = main_block['style']
        # [0] нужен, чтобы вернуть всю ссылку а не результат регулярки
        # Будем вытаскивать регулярными выражениями
        image_link = re.search(r'https:[\w\/\.]+', main_block['style'])[
            0]  # пишем потом после того как поняли, что это строка
        # print(main_block.a['href']) # ссылка на страницу новости но она не полная
        article_link = self.URL + main_block.a['href']
        # print(article_link) # теперь полная сслыка
        return {'image_link': image_link, 'article_link': article_link}

    def get_category_id(self, block):  # По названию категории будем возвращать id
        #бодавим проверку, если новость без этого тега
        category_tag = block.find('div', class_='card__trend')
        if category_tag:
            category_name = category_tag.get_text(strip=True)
        else:
            category_name = 'Общее'
        #Сделаем все в одном запросе
        cursor.execute('''
        insert into categories (category_name) values (%s)
        on conflict do nothing;
        select category_id
        from categories
        where category_name = %s
        ''', (category_name,category_name))  # Будет вставлять и возвращать id
        category_id = cursor.fetchone()  # иногда возвращется None или (1,) нужно вытащить числа

        return category_id[0]  # возвращаем первый элемент то есть число

    def get_json_data(self, soup):
        json_data = []
        # soup = self.get_soup() #В конце уберем и передадим в качестве аргумента
        cards = soup.find_all('div', class_='card_sections')  # Берем и ищем в коде div-ы с классом card_sections
        print(len(cards))
        for card in cards:
            # category = ''
            # if card.find('div', class_='card__trend'):
            # category = card.find('div', class_='card__trend').get_text(strip=True)
            # обновляем, чтобы брать id
            category_id = self.get_category_id(card)
            title = card.find('div', class_='card__heading').get_text(strip=True)
            date = card.find('div', class_='card__date').get_text(strip=True)
            author = ''
            if card.find('div', class_='card__author'):
                author = card.find('div', class_='card__author').get_text(strip=True).replace('\n                  ',
                                                                                              ' ')
                # Данные очень не красивые - почистим. replace заменит один кусок строки на другой
            description = card.find('div', class_='card__summary').get_text(strip=True)
            # print(category)
            # print(repr(category))
            print(title)
            print("*********************************************************")
            # print(date)
            # print(author)
            # print(description)

            image_link = self.get_image_link_and_article_link(card)[
                'image_link']  # берем по ключу после того как закончили функцию
            article_link = self.get_image_link_and_article_link(card)['article_link']
            # print("--------------------------------------------------")
            json_data.append({
                # 'category': category,  # будет удобнее, если сюда будет сохраняться id категории а не название
                'category_id': category_id,
                'title': title,
                'date': date,
                'author': author,
                'description': description,
                'image_link': image_link,
                'article_link': article_link
            }
            )
        return json_data

    def fill_database(self, soup):  # Заливаем в базу
        json_data = self.get_json_data(soup)  # вытаскиваем данные
        for data in json_data:
            cursor.execute('''
            insert into articles (title, date, author, description, image_link, article_link, category_id)
            values (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                data['title'],
                data['date'],
                data['author'],
                data['description'],
                data['image_link'],
                data['article_link'],
                data['category_id']
            ))

    def run(self):
        soup = self.get_soup()
        if soup:
            self.fill_database(soup)
        else:
            print('Не удалось получить HTML страницу')

print("runing....")
world = Parser(page_name='world')
world.run()
russia = Parser(page_name='russia')
russia.run()
ussr = Parser(page_name='ussr')
ussr.run()

db.commit()  # добавляем в базу и закрываем
db.close()
