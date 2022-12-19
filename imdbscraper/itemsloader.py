from itemloaders.processors import MapCompose, TakeFirst, Identity, Join, Compose
import scrapy.loader
from re import sub, findall
from random import randint
import nltk
nltk.download('punkt')
nltk.download('stopwords')


class MovieItemsLoader(scrapy.loader.ItemLoader):
    default_outptut_processor = Identity()
    # for poster item
    poster_in =  MapCompose(lambda x: 'https://imdb.com/'+x)
    # for trailer item
    trailer_in =  MapCompose(lambda y: 'https://imdb.com/'+y)
    # for the ratings item
    ratings_in = TakeFirst()
    # for the num_ratings item
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
            # return the final value but in string
            return str(int(full))
    num_ratings_in = TakeFirst()
    num_ratings_out = MapCompose(numrloader)
    # release_date item
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
    release_date_in = MapCompose(rdloader)
    # for the duration item
    def durloader(dur_item):
        dur_item = dur_item.split(';')
        try:
            int(dur_item[0])
            dur_str = ''.join(dur_item).strip(' ')
        except ValueError:
            dur_str = ''.join(dur_item[1:]).strip(' ')
        # disect hour and minutes with regex
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
    duration_in = Join(';')
    duration_out = MapCompose(durloader)
    # for the box_office item
    box_office_in = MapCompose(lambda x: sub('\$|,','',x))    
    # for the director, writer and producer items
    def crewloader(crew_item):
        new = []
        crew_item = crew_item.split(',')
        for each in crew_item:
            each = each[1:]
            each = each.replace('\n','')
            new.append(each)
        return new
    director_in = MapCompose(crewloader)
    writer_in = MapCompose(crewloader)
    producer_in = MapCompose(crewloader)
    # do function to tokenize the words in all the description of the movie
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
    keywords_in =  Join(';;;')
    keywords_out = MapCompose(kywdloader)
    # do function to get only the longest movie description
    def mdloader(about_item):
        ab_split = about_item.split(";;;")
        if ab_split[-1] == '.':
            return ''
        else:
            len_text = [len(i) for i in ab_split]
            # retain only that
            return ab_split[len_text.index(max(len_text))]
    about_in = Join(';;;')
    about_out = MapCompose(mdloader)
    