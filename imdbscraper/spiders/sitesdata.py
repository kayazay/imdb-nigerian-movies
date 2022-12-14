import scrapy
from ..items import MovieItems
from ..itemsloader import MovieItemsLoader
from re import findall

class SitesdataSpider(scrapy.Spider):
    name = 'sitesdata'
    start_urls = ['https://www.imdb.com/search/title/?country_of_origin=NG&sort=alpha,asc&start=1&ref_=adv_nxt']
    allowed_domain = ['imdb.com']

    def parse(self, response):
        # to get the total number of pages
        total_movies = response.xpath('//div[@class="nav"]/div[@class="desc"]/span/text()').get()
        num_movies = ''.join(findall('\s[0-9]+.+\s', total_movies))
        num_movies = int(num_movies.replace(',','').strip())
        num_movies = 501
        print(f'About to scrape {num_movies} movies')
        for i in range(1, num_movies, 50):
            link_edit = f'https://www.imdb.com/search/title/?country_of_origin=NG&sort=alpha,asc&start={i}&ref_=adv_nxt'
            yield scrapy.Request(link_edit, self.movieout)

    def movieout(self, response):
        for movie in response.xpath('//h3[@class="lister-item-header"]/a/@href').getall():
            story_link = 'https://www.imdb.com'+ movie+ 'plotsummary?ref_=tt_ov_pl'
            yield scrapy.Request(story_link, callback=self.parse_story)

    # for the details about movie description
    def parse_story(self, response):
        about = response.xpath('//ul[@id="plot-summaries-content"]//p/text()').getall()
        next_url = response.url.replace("plotsummary?ref_=tt_ov_pl","fullcredits/?ref_=tt_cl_sm")
        #return desc
        yield scrapy.Request(
            next_url, self.parse_cast, meta={'about':about}
            )

    # for the cast details of the movie
    def parse_cast(self, response):
        director = response.xpath('//h4[@id="director"]/following::table[1]//a/text()').getall()
        writer = response.xpath('//h4[@id="writer"]/following::table[1]//a/text()').getall()
        producer = response.xpath('//h4[@id="producer"]/following::table[1]//a/text()').getall()
        next_url2 = response.url.replace('fullcredits/?ref_=tt_cl_sm','')
        yield scrapy.Request(
            next_url2, self.parse_basic, meta={
                'director': director,
                'writer': writer,
                'producer': producer,
                'about': response.meta.get('about'),
                }
            )

    # for the basic features of movie
    def parse_basic(self, response):
        imdbitems = MovieItemsLoader(item=MovieItems(), response=response)
        # time to itemize
        imdbitems.add_value('url', response.url)
        # basic details
        imdbitems.add_xpath('title', '//div[@class="sc-80d4314-1 fbQftq"]/h1/text()') 
        imdbitems.add_xpath('poster', '//a[@data-testid="photos-image-overlay-1"]/@href')
        imdbitems.add_xpath('trailer', '//a[@data-testid="videos-slate-overlay-1"]/@href')
        imdbitems.add_xpath('ratings', '//span[@class="sc-7ab21ed2-1 jGRxWM"]/text()')
        imdbitems.add_xpath('num_ratings', '//div[@class="sc-7ab21ed2-3 dPVcnq"]/text()')
        # cast details
        imdbitems.add_xpath('full_cast', '//a[@data-testid="title-cast-item__actor"]/text()')
        # technical details
        imdbitems.add_xpath('genre', '//div[@data-testid="genres"]//span/text()')
        imdbitems.add_xpath('certificate', '//ul[contains(@data-testid,"hero")]//a[contains(@href, "cert")]/text()')
        # other details
        imdbitems.add_xpath('release_date', '//li[@data-testid="title-details-releasedate"]/div//a/text()')
        imdbitems.add_xpath('origin', '//li[@data-testid="title-details-origin"]/div//a/text()')
        imdbitems.add_xpath('site', '//li[@data-testid="details-officialsites"]/div//a/text()')
        imdbitems.add_xpath('language', '//li[@data-testid="title-details-languages"]/div//a/text()')
        imdbitems.add_xpath('film_location', '//li[@data-testid="title-details-filminglocations"]/div//a/text()')
        imdbitems.add_xpath('company', '//li[@data-testid="title-details-companies"]/div//a/text()')
        imdbitems.add_xpath('duration', '//ul[@data-testid="hero-title-block__metadata"]/li[@class="ipc-inline-list__item"]/text()')
        imdbitems.add_xpath('box_office', '//li[@data-testid="title-boxoffice-cumulativeworldwidegross"]/div//span/text()')
        # from previous methods
        imdbitems.add_value('director', response.meta.get('director'))
        imdbitems.add_value('writer', response.meta.get('writer'))
        imdbitems.add_value('producer', response.meta.get('producer'))
        imdbitems.add_value('keywords', response.meta.get('about'))
        imdbitems.add_value('about', response.meta.get('about'))
        # end of itemizng
        yield imdbitems.load_item()
