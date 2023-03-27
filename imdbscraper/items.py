# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItems(scrapy.Item):
    # define the fields for your item here like:
    url =  scrapy.Field()
    # basic details
    title = scrapy.Field()
    poster =  scrapy.Field()
    trailer =  scrapy.Field()
    ratings =  scrapy.Field()
    num_ratings =  scrapy.Field()
    # cast & crew
    stars =  scrapy.Field()
    director =  scrapy.Field()
    writer =  scrapy.Field()
    # technical details
    genre =  scrapy.Field()
    # other details
    release_date =  scrapy.Field()
    language =  scrapy.Field()
    film_location =  scrapy.Field()
    company =  scrapy.Field()
    duration =  scrapy.Field()
    # from previous methods
    about = scrapy.Field()
    page = scrapy.Field()
