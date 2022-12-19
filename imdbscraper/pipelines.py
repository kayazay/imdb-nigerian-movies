# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import psycopg2

class PostgresDump:
    # all SQL queries used in this script
    movies_query = '''
        DROP TABLE IF EXISTS movies;
        CREATE TABLE movies (
            id SERIAL PRIMARY KEY,
            URL VARCHAR(70) NOT NULL,
            TITLE VARCHAR(100) NOT NULL,
            POSTER VARCHAR(100),
            TRAILER VARCHAR(100),
            RATINGS NUMERIC,
            NUM_RATINGS INT,
            FULL_CAST TEXT,
            GENRE VARCHAR(100),
            RELEASE_DATE DATE,
            LANGUAGE VARCHAR(100),
            FILM_LOCATION TEXT,
            COMPANY TEXT,
            DURATION SMALLINT,
            BOX_OFFICE INT,
            DIRECTOR TEXT,
            WRITER TEXT,
            PRODUCER TEXT,
            KEYWORDS TEXT,
            ABOUT TEXT
        );
        INSERT INTO movies (
            url,
            title, poster, trailer, ratings, num_ratings,
            full_cast,
            genre,
            release_date, language,
            film_location, company, duration, box_office,
            director, writer, producer, keywords, about
        )
        SELECT
            btrim(URL,'{}') as url,
            -- usual break
            btrim(TITLE, '{""}') as title,
            CASE WHEN POSTER = '{}' THEN null ELSE btrim(POSTER, '{}') END as poster,
            CASE WHEN TRAILER = '{}' THEN null ELSE btrim(TRAILER, '{}') END as trailer,
            CASE WHEN RATINGS = '{}' THEN null ELSE btrim(RATINGS, '{}')::NUMERIC END as ratings,
            CASE WHEN NUM_RATINGS = '{}' THEN null ELSE btrim(NUM_RATINGS, '{}')::INT END as num_ratings,
            -- usual break again
            CASE WHEN FULL_CAST = '{}' THEN null ELSE REPLACE(btrim(FULL_CAST, '{""}'),'"','') END as full_cast,
            CASE WHEN GENRE = '{}' THEN null ELSE btrim(GENRE, '{}') END as genre,
            -- usual break again
            CASE WHEN RELEASE_DATE = '{""}' THEN null ELSE TO_DATE(btrim(RELEASE_DATE, '{""}'), 'Month DD, YYYY') END as release_date,
            CASE WHEN LANGUAGE = '{}' THEN null ELSE REPLACE(btrim(LANGUAGE, '{""}'),'"','') END as language,
            CASE WHEN FILM_LOCATION = '{}' THEN null ELSE REPLACE(btrim(film_location, '{""}'),'"','') END as film_location,
            CASE WHEN COMPANY = '{}' THEN null ELSE REPLACE(btrim(COMPANY, '{""}'),'"','') END as company,
            CASE WHEN DURATION IN ('{""}','{}') THEN null ELSE btrim(DURATION, '{}')::INT END as duration,
            CASE WHEN BOX_OFFICE = '{}' THEN null ELSE btrim(BOX_OFFICE, '{}')::FLOAT END as box_office,
            -- usual break
            CASE WHEN DIRECTOR = '{}' THEN null ELSE REPLACE(btrim(DIRECTOR, '{}'),'"','') END as director,
            CASE WHEN WRITER = '{}' THEN null ELSE REPLACE(btrim(WRITER, '{}'),'"','') END as writer,
            CASE WHEN PRODUCER = '{}' THEN null ELSE REPLACE(btrim(PRODUCER, '{}'),'"','') END as producer,
            CASE WHEN KEYWORDS = '{""}' THEN null ELSE REPLACE(btrim(KEYWORDS, '{}'),'"','') END as keywords,
            CASE WHEN ABOUT = '{""}' THEN null ELSE REPLACE(btrim(ABOUT, '{}'),'"','') END as about
        FROM scrapy_dump;
    '''

    create_scrapy_dump = '''
        DROP TABLE IF EXISTS scrapy_dump;
        -- create table now
        CREATE TABLE scrapy_dump (
            url TEXT PRIMARY KEY,
            -- separataing this like in python
            title TEXT, poster TEXT, trailer TEXT, ratings TEXT, num_ratings TEXT,
            -- don't ask why i'm doing this
            full_cast TEXT,
            -- another one
            genre TEXT,
            -- just one more left
            release_date TEXT, language TEXT,
            film_location TEXT, company TEXT, duration TEXT, box_office TEXT,
            -- and i'm done
            director TEXT, writer TEXT, producer TEXT, keywords TEXT,  about TEXT
        );
    '''

    insert_scrapy_dump = '''
        INSERT INTO scrapy_dump (
            url,
            title, poster, trailer, ratings, num_ratings,
            full_cast,
            genre,
            release_date, language,
            film_location, company, duration, box_office,
            director, writer, producer, keywords, about)
        VALUES (    
            %s,
            %s,%s,%s,%s,%s,
            %s,
            %s,
            %s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s,%s
            )
        '''
    
    # open spider and connect to database
    def open_spider(self, spider):
        self.connection = psycopg2.connect(
            host = 'pg.service',
            port = '5432',
            database = 'imdb',
            user = 'admin',
            password = 'eze'
        )
        self.curr = self.connection.cursor()
        # SQL code to create table to dump python data
        self.curr.execute(self.create_scrapy_dump)

    # disconnect from database
    def close_spider(self, spider):
        # drop table used for initial dumping from scrapy
        self.curr.execute('DROP TABLE IF EXISTS scrapy_dump;')
        self.curr.close()
        self.connection.close()

    # process every scraped item and insert into postgres
    def process_item(self, item, spider):
        # to handle empty results
        for x in ['url',
                'title', 'poster', 'trailer', 'ratings', 'num_ratings',
                'full_cast',
                'genre',
                'release_date', 'language', 
                'film_location', 'company', 'duration', 'box_office',
                'director', 'writer', 'producer', 'keywords', 'about']:
            if x not in item:
                item[x] = []
        # insert data from scrapy into scrapy_dump
        try:
            self.curr.execute(self.insert_scrapy_dump,
            (
                item.get('url'),
                # first batch
                item['title'], item['poster'], item['trailer'], item['ratings'], item['num_ratings'],
                # second
                item['full_cast'],
                # third
                item['genre'],
                # fourth
                item['release_date'], item['language'],
                item['film_location'], item['company'], item['duration'], item['box_office'],
                # last batch
                item['director'], item['writer'], item['producer'], item['keywords'], item['about']
            )
        )
            self.connection.commit()
        except:
            self.connection.rollback()
            raise
        # create actual table to be used after cleaning scrapy dump
        self.curr.execute(self.movies_query)
        # finally we do this
        return item
