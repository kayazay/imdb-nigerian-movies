import scrapy
from ..items import MovieItems
from ..itemsloader import MovieItemsLoader
from re import findall, sub

class SitesdataSpider(scrapy.Spider):
    name = 'sitesdata'
    start_urls = ['https://www.imdb.com/search/title/?country_of_origin=NG&sort=year,asc&start=1&ref_=adv_prv']
    allowed_domain = ['imdb.com']

    def parse(self, response):
        # get page number from url
        page_num = int(findall(r'[0-9]+', response.url)[0]) # converted to number
        for link in response.xpath('//h3/a/@href').getall():
            movie = response.urljoin(link.split('?')[0]) # removed tag at end of link
            # callback to parse_story method
            yield scrapy.Request(movie+'plotsummary/', callback=self.parse_story, meta={'page number':page_num})
        # make next page by editing link
        next_page = sub(r'[0-9]+',str(page_num+50), response.url)
        if page_num>2: # break if needed or continue
            return
        # Callback to same method and start scraping process again
        yield scrapy.Request(
            url=next_page, callback=self.parse)
        
    def parse_story(self, response):
        about = response.xpath('//div[contains(@class, "content-inner")]/text()').getall()
        page_num = response.meta.get('page number')
        yield scrapy.Request(response.url.replace('plotsummary/',''), callback=self.parse_basic, meta={'two_var':[about, str(page_num)]})

    # collect every other necessary and yield into itemsloaders
    def parse_basic(self, response):
        imdbmain = MovieItemsLoader(item=MovieItems(), response=response)
        # basic details
        imdbmain.add_value('url', response.url)
        imdbmain.add_xpath('title', '//h1[@data-testid="hero-title-block__title"]/text()')
        POSTER = response.xpath('//a[@data-testid="photos-image-overlay-1"]/@href').get()
        imdbmain.add_value('poster', response.urljoin(POSTER)) # joined url for poster
        TRAILER = response.xpath('//a[@data-testid="videos-slate-overlay-1"]/@href').get()
        imdbmain.add_value('trailer', response.urljoin(TRAILER)) # joined url for trailer
        imdbmain.add_xpath('ratings', '//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/span[starts-with(@class, "sc")]/text()')
        imdbmain.add_xpath('num_ratings', '//div[starts-with(@class, "sc") and contains(@class, "-3 ")]/text()')
        # cast details
        imdbmain.add_xpath('stars', '//a[@data-testid="title-cast-item__actor"]/text()')
        imdbmain.add_xpath('director', '//a[contains(@href, "tt_cl_dr")]/text()')
        imdbmain.add_xpath('writer', '//a[contains(@href, "tt_cl_wr")]/text()')
        # technical details
        imdbmain.add_xpath('genre', '//div[@data-testid="genres"]//span/text()')
        # other details
        imdbmain.add_xpath('release_date', '//li[@data-testid="title-details-releasedate"]/div//a/text()')
        imdbmain.add_xpath('language', '//li[@data-testid="title-details-languages"]/div//a/text()')
        imdbmain.add_xpath('film_location', '//li[@data-testid="title-details-filminglocations"]/div//a/text()')
        imdbmain.add_xpath('company', '//li[@data-testid="title-details-companies"]/div//a/text()')
        imdbmain.add_xpath('duration', '//ul[@data-testid="hero-title-block__metadata"]/li[@class="ipc-inline-list__item"]/text()')
        imdbmain.add_value('about', response.meta.get('two_var')[0])
        imdbmain.add_value('page', response.meta.get('two_var')[1])
        yield imdbmain.load_item()
