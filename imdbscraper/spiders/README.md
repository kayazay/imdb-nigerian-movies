# IMDBSCRAPER SPIDER

For this project, only one spider was created- `sitesdata`; and the following is a logical explanation of how this spider crawls **imdb**, from the search results page to the web page of each movie:

+ The spider starts crawling from the link specified in [`start_urls`](https://www.imdb.com/search/title/?country_of_origin=NG&sort=alpha,asc&start=1&ref_=adv_nxt). This search page is the first of many pages, sorting the movies by alphabet in increasing order and each page holds 50 movies. Thus the next page would be '...start=51..' and this would hold movies numbered 51-100; and so on.

## The `parse` method:

+ extracts the total number of movies hosted on imdb as at the point of running the script;
+ handles pagination by using a for-loop to increment by 50 thus giving scrapy a 'next link' after work has been finished on the present link.
+ `link_edit` holds the next link (actually starting from the first link: '...start=1...') and is set as a callback to **`movieout`** method

## The `movieout` method:

+ collects the unique link ID for each of the 50 movies on the search result page and constructs the story link out of it.
+ `story_link` holds the constructed link to the page where information regarding the movie summary is displayed- and is set as a callback to the **`parse_story`** method.
+ uses a for-loop so that after crawling all data for a movie, the spider does the exact same thing for the next 49 movies and then goes back to the `parse` method to get the link for the next 50 movies

## The `parse_story` method:

+ collects all submitted summaries of the movie
+ another link is constructed- the page that holds the full crew information and this is set as a callback to the **`parse_crew`** method

## The `parse_crew` method:

+ collects all crew information of the movie
+ another link is constructed- the page that holds all other features of the movie and this is set as a callback to the **`parse_basic`** method

## The `parse_basic` method:

+ collects all other basic features of the movie
+ loads all features generated from other methods and this one into the itemsloaders instance- `imdbitems` for processing.