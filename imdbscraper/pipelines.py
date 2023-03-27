# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import psycopg2
from datetime import datetime as dt
from scrapy.exceptions import DropItem


class PostgresDump:
    # open spider and connect to database
    def open_spider(self, spider):
        QUERY = '''
            DROP TABLE movies;
            CREATE TABLE movies (
                url VARCHAR(63) NOT NULL,
                title VARCHAR(63), poster VARCHAR(128), trailer VARCHAR(128), ratings NUMERIC, num_ratings INTEGER,
                stars TEXT, director VARCHAR(127), writer VARCHAR(127),
                genre VARCHAR(32),
                release_date DATE, language VARCHAR(32), film_location VARCHAR(64), company VARCHAR(128), duration SMALLINT,
                about TEXT, page INT
            );
        '''
        executeIT(query=QUERY)

    # process every scraped item and insert into postgres
    def process_item(self, item, spider):
        values, percents = [], []
        for col in cols():
            if col in item:
                if col in ('num_ratings','duration','page'):
                    item[col] = int(item[col])
                elif col=='ratings':
                    item[col] = float(item[col])
                elif col=='release_date':
                    item[col] = dt.strptime(item[col], r"%B %d, %Y").date()
                values.append(item[col])
            else:
                values.append(None) # handling null values
            percents.append('%s')
        if not item.get('title') or item.get('genre')=="Genre not supported":
            raise DropItem()
        QUERY = '''INSERT INTO movies ({0}) VALUES ({1})
        ON CONFLICT DO NOTHING;
        '''.format(
            ','.join(cols()), ','.join(percents))
        executeIT(query=QUERY, extra=values)
        return item


def cols():
    return ['url', 'title', 'poster', 'trailer', 'ratings', 'num_ratings',
    'stars', 'director', 'writer',
    'genre',
    'release_date', 'language', 'film_location', 'company', 'duration',
    'about', 'page']


def executeIT(query='', extra=''):
    with psycopg2.connect(
        host='localhost',
        port='5432',
        database='imdb_db',
        user='postgres',
    ) as conn:
        with conn.cursor() as curr:
            if query=='' and extra=='':
                curr.execute('select count(*) from movies;')
                return curr.fetchone()[0]
            elif extra=='':
                curr.execute(query)
            else:
                curr.execute(query, extra)
        conn.commit()
