# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from email.policy import default
import scrapy


class MovieItems(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url =  scrapy.Field()
    # basic details
    title = scrapy.Field()
    poster =  scrapy.Field(default=None)
    trailer =  scrapy.Field(default = None)
    ratings =  scrapy.Field()
    num_ratings =  scrapy.Field()
    # cast details
    full_cast =  scrapy.Field()
    # technical details
    genre =  scrapy.Field()
    certificate =  scrapy.Field()
    # other details
    release_date =  scrapy.Field()
    origin =  scrapy.Field()
    site =  scrapy.Field()
    language =  scrapy.Field()
    film_location =  scrapy.Field()
    company =  scrapy.Field()
    duration =  scrapy.Field()
    box_office =  scrapy.Field()
    # from previous methods
    director =  scrapy.Field()
    writer =  scrapy.Field()
    producer =  scrapy.Field()
    keywords = scrapy.Field()
    about = scrapy.Field()
