# IMDBSCRAPER ITEMS AND ITEMSLOADER

The following items were scraped and processed by the `sitesdata` spider and itemsloaders as elements or features of each movie:

+ `url`: this holds the link to the web page of the movie, it is made a unique key as two movies cannot have the same link.

+ `title`: this holds the title of the movie.

+ `poster`: this holds the link to the movie poster(s).

+ `trailer`: this holds the link to the movie trailer(s).

+ `ratings`: this is a float number between 1.0 and 5.0.

  + Scrapy outputted this data twice, so the **TakeFirst** processor was used to get only one value.

+ `num_ratings`: this is the number of likes the movie has earned on imdb.

  + This number was in text form and abbreviated with 'K' for 1000 and 'M' for million; e.g 2.5K, 3.1M. So there was a need to manipulate this string to obtain actual number of likes.

```py
def numrloader(numr_item):
    abbrev = numr_item[-1]
    # if numeric, return it
    if abbrev.isnumeric():
        return numr_item
    else:
        # if not, manipulate it to extract actual value without abbreviation
        actual =  numr_item[:len(numr_item)-1]
        actual = float(actual)
        if abbrev.lower() == 'k':
            full = actual * 1000
        elif abbrev.lower() == 'm':
            full = actual * 1000000
        return str(int(full))
```

+ `full_cast`: this is a text holding the names of the main actors and actresses that starred in the movie separated by ','

+ `genre`: this holds the movie genre(s) separated by ','

+ `release_date`: this holds the full date a movie was released.

  + This feature was inconsistent across different pages as few dates had no month or day component; e.g 'November 2020' or '2021'. Since aggregation would be done on a month level, random month values were assigned to dates with no month; and day-1 was assigned to dates with no day.

```py
def rdloader(rd_item):
    year = ''.join(findall('[0-9]{4}', rd_item))
    month = findall('[a-z|A-Z]*\s', rd_item)[0].strip() 
    day = ''.join(findall('[0-9]*,', rd_item)).replace(',','')
    # to handle empty components, day or month
    if not month:
        list_month = ['January','February','March','April','May','June','July',\
            'August', 'September','October','November','December']
        month = list_month[randint(0,11)]
    if not day:
        day = 1
    return f'{month} {day}, {year}'
```

+ `language`: this holds data for the languages spoken in the movie.

+ `film_location`: this feature tells you where the movie was shot and directed.

+ `company`: this holds data for the company that made, advertised and distributed the movie.

+ `duration`: this holds data regarding the movie runtime, in minutes.

  + Scrapy collects this data in the form 'xH yM', and so there was a need to convert to minutes; using regex for string manipulation.

```py
def durloader(dur_item):
    dur_item = dur_item.split(';')
    try:
        int(dur_item[0])
        dur_str = ''.join(dur_item).strip(' ')
    except ValueError:
        dur_str = ''.join(dur_item[1:]).strip(' ')
    # dissect hour and minutes with regex
    hour = ''.join(findall('[0-9]h', dur_str)).replace('h','')
    minutes  = ''.join(findall('[0-9]{2}m', dur_str)).replace('m','')
    if not hour:
        hour = 0
    if not minutes:
        minutes = 0
    final_str = int(hour)*60 + int(minutes)
    if final_str == 0:
        str_out = ''
    else:
        str_out = str(final_str)
    return str_out 
```

+ `box_office`: this holds data for the budget of a movie, in USD.

  + **MapCompose** processor was used to convert this item to numeric form

```py
box_office_in = MapCompose(lambda x: sub('\$|,','',x))
```

+ `director`, `writer` & `producer`: this gives information about the crew of a movie.

  + Scrapy collects the data from these three items in an inconsistent format- as a tuple within a list; so there was a need to clean this.

```py
def crewloader(crew_item):
    new = []
    crew_item = crew_item.split(',')
    for each in crew_item:
        each = each[1:]
        each = each.replace('\n','')
        new.append(each)
    return new
```

+ `keywords`: this holds the unique keywords in the movie description.

  + Some movies have multiple movie descriptions or summary so this feature collects all such descriptions, tokenizes this text, removes unneccessary words (stopwords) like titles and prepositions, then outputs a unique list of the remaining words.

```py
def kywdloader(keywords_item):
    kywd_split = keywords_item.split(";;;")
    if kywd_split[-1] != '.':
        kywd_str = keywords_item.lower()
    else:
        return ''
    pretoken = []
    for sentence in nltk.sent_tokenize(kywd_str.lower()):
        pretoken += findall('[a-z]+', sentence)
    post_stpwords = []
    for word in pretoken:
        if word not in set(nltk.corpus.stopwords.words('english')):
            post_stpwords.append(word)
    return ','.join(post_stpwords)
```

+ `about`: this holds the main description of the movie.

  + The longest of all such descriptions as explained above, is taken to be the main description; as this would likely hold the most detail about the movie.

```py
def mdloader(about_item):
    ab_split = about_item.split(";;;")
    if ab_split[-1] == '.':
        return ''
    else:
        len_text = [len(i) for i in ab_split]
        # retain only that
        return ab_split[len_text.index(max(len_text))]
```

## IMDBSCRAPER PIPELINES

This is a logical explanation of the PostgresDump pipeline and what it does from start to finish:

+ `open_spider` method starts this pipeline and attempts to connect to the Postgres instance specified within.

  + P.S: To run this project with a locally installed Postgres database; edit the connection options, especially changing the 'host' parameter to 'localhost'.

```py
self.connection = psycopg2.connect(
    host = 'pg.service',
    port = '5432',
    database = 'imdb',
    user = 'admin',
    password = 'eze'
)
```

+ Once a connection has been made to the database, the SQL query to create a `scrapy_dump` table is run.

  + <details>
    <summary>
    DDL for scrapy_dump
    </summary>

    ```SQL
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
    ```

    </details>

+ The `process_item` method is next in line and this inserts data scraped by items into the `scrapy_dump` table and creates a new table `movies` to clean scrapy_dump data and enforce data types.

  + <details>
    <summary>
    DDL for movies
    </summary>

    ```SQL
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
    ```

    </details>

+ The `close_spider` method ends this pipeline and deletes the `scrapy_dump` table.