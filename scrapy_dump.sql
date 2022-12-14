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