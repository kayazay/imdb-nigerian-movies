from itemloaders.processors import MapCompose, TakeFirst, Identity, Join, Compose
import scrapy.loader
from random import randint


class MovieItemsLoader(scrapy.loader.ItemLoader):
    default_output_processor = Compose(
        MapCompose(lambda x: x.replace(r'\n', '')),
        Join(';')
    )
    # for the title item
    title_in = MapCompose(lambda x: None if x[:9]=='Episode #' else x)
    ratings_in = TakeFirst() # for the ratings item
    def numrloader(numr_item):
        abbrev = numr_item[-1].lower()
        # if numeric, return it
        if abbrev.isnumeric():
            return numr_item
        else: # if not, get numeric equivalent
            actual = float(numr_item[:-1]) * {'k':1000, 'm':1000000}[abbrev] # product of rem. digits and abbreviation
            # return the final value but in string
            return str(int(actual))
    num_ratings_in = Compose(
        lambda item_list: [each for each in item_list if each.isnumeric()],
        TakeFirst(), numrloader
    )
    # for the genre item
    genre_in = Compose(lambda list_item: 'Genre not supported' if set(list_item) & set(['Music','Talk-Show','Documentary','Short']) else list_item)
    # for the release_date item
    def rdloader(rd_item):
        elements = rd_item.split()
        month, year = 0, ''
        months_in_a_year = ['January','February','March','April','May','June','July','August', 'September','October','November','December']
        for element in elements:
            if element.isnumeric() and len(element)==4:
                year = element
            elif element in months_in_a_year:
                month = element
        month = month if month else months_in_a_year[randint(0,11)]
        return f'{month} 1, {year}'
    release_date_in = MapCompose(rdloader)
    # for the duration item
    def durloader(dur_item):
        if not dur_item:
            return
        if 'h' in dur_item: # get the hour component by getting the element before 'h' 
            hour = int(dur_item[dur_item.index('h')-1])
        else:
            hour = 0
        if 'm' in dur_item: # get the minutes component by getting the element before 'm' 
            minute = int(dur_item[dur_item.index('m')-1])
        else:
            minute = 0
        return str(hour*60 + minute)
    duration_in = Compose(
        lambda item_list: [each for each in item_list if len(each)<=2],
        durloader
    )
