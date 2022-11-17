# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import psycopg2


class SavingOpenClose:
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
            NUM_RATINGS SMALLINT,
            FULL_CAST TEXT,
            GENRE VARCHAR(100),
            CERTIFICATE VARCHAR(20),
            RELEASE_DATE DATE,
            ORIGIN VARCHAR(100),
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
            genre, certificate,
            release_date, origin, duration, box_office,
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
            CASE WHEN CERTIFICATE = '{}' THEN null ELSE REPLACE(btrim(CERTIFICATE, '{}'),'"','') END as certificate,
            -- as release_date,
            CASE WHEN RELEASE_DATE = '{""}' THEN null ELSE TO_DATE(btrim(RELEASE_DATE, '{""}'), 'Month DD, YYYY') END as release_date,
            CASE WHEN ORIGIN = '{}' THEN null ELSE btrim(ORIGIN, '{}') END as origin,
            CASE WHEN DURATION IN ('{""}','{}') THEN null ELSE btrim(DURATION, '{}')::INT END as duration,
            CASE WHEN BOX_OFFICE = '{}' THEN null ELSE 800*btrim(BOX_OFFICE, '{}')::FLOAT END as box_office,
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
            genre TEXT, certificate TEXT,
            -- just one more left
            release_date TEXT, origin TEXT, duration TEXT, box_office TEXT,
            -- and i'm done
            director TEXT, writer TEXT, producer TEXT, keywords TEXT,  about TEXT
        );
    '''

    insert_scrapy_dump = '''
        INSERT INTO scrapy_dump (
            url,
            title, poster, trailer, ratings, num_ratings,
            full_cast,
            genre, certificate,
            release_date, origin, duration, box_office,
            director, writer, producer, keywords, about)
        VALUES (    
            %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s
            )
        '''

    # function to connect to database
    def open_spider(self, spider):
        self.connection = psycopg2.connect(
            host = 'localhost',
            database = 'imdb',
            user = 'postgres',
            password = 'eze'
        )
        self.curr = self.connection.cursor()
        # SQL code to create table to dump python data
        self.curr.execute(self.create_scrapy_dump)

    #function to disconnect from database
    def close_spider(self, spider):
        self.curr.close()
        self.connection.close()

    # function to process every scraped item and insert into postgres
    def process_item(self, item, spider):
        #self.curr.execute('''''')
        # to handle empty results
        for x in ['url',
                'title', 'poster', 'trailer', 'ratings', 'num_ratings',
                'full_cast',
                'genre', 'certificate',
                'release_date', 'origin', 'duration', 'box_office',
                'director', 'writer', 'producer', 'keywords', 'about']:
            if x not in item:
                item[x] = []
        # connect to table created above and insert scrapy data
        try:
            self.curr.execute(self.insert_scrapy_dump,
            (
                item.get('url'),
                # first batch
                item['title'], item['poster'], item['trailer'], item['ratings'], item['num_ratings'],
                # second
                item['full_cast'],
                # third
                item['genre'], item['certificate'],
                # third
                item['release_date'], item['origin'], item['duration'], item['box_office'],
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
