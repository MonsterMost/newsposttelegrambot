import psycopg2 as sql

db = sql.connect(
    database='russia_today_test',
    host='localhost',
    user='postgres',
    password='123456'
)

cursor = db.cursor()

cursor.execute('''
    drop table if exists articles;
    drop table if exists categories;
    
    create table if not exists categories(
        category_id integer generated always as identity primary key,
        category_name varchar(50) unique
    );
    create table if not exists articles(
        article_id integer generated always as identity primary key,
        title text,
        date text,
        author text,
        description text, 
        image_link text,
        article_link text,
        category_id integer references categories(category_id)
    )
''')

# insert into categories (category_name) values ('world')
# on conflict do nothing  #При повторном заливе той же категории будет ошибка, это строка говорит игнор ошибку
#
# select category)id from categories
# where category_name = 'world'

