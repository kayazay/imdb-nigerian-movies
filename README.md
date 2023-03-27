# DATA WAREHOUSE OF NIGERIAN MOVIES

## Run this project periodically
- Make request to [imdb](imdb.com) to get information on Nigerian movies;
- 50 movies each are hosted in one page of [imdb](imdb.com) search;
- next link would be gotten from page as usual.

## What items would be scraped?
- **url** link to the movie;
- **title** of movie;
- link to movie **poster**;
- link to movie **trailer**;
- **ratings** of the movie out of 10;
- number of individuals that reviewed movie **(num_ratings)**;
- names of **stars** in movie;
- names of **directors** of movie;
- names of **writers** of movie;
- movie **genre**;
- date movie was released **(release_date)**;
- **language** used in movie;
- location movie was filmed **(film_location)**;
- movie production **company**;
- **duration** of movie;
- description of movie **(about)**;
- **page** number of movie.

## How do we transform these?

- Many items are gotten as many-in-one rather than one-in-one, so naturally `default_output_processor` is to remove all nextline characters from each matching result then join them all with a semicolon.

- `title`: Filter out movies that are actually episodes of a show and make null.

- `ratings`: Take first non-null result.

- `num_ratings`: Convert numbers to full & actual values.

    > 10K &rarr; **10000** 
    >
    > 3.2M &rarr; **3200000**

- `genre`: Make null and filter out if it is either Music, Talk-Show, Documentary or Short.

- `release_date`: Fill a random month if movie has none and a constant day of 1, so date can be parsed correctly.

    > 1995 &rarr; **September 1, 1995**
    >
    > March 2012 &rarr; **March 1, 2012**

- `duration`: Convert running time written separately and in text to equivalent in minutes.

    > 1h 30m &rarr; **90**
    >
    > 2h &rarr; **120**

## Where does the data go next?

- Data is loaded to a PostgresDB with data types, constraints & rules for INSERT specified.
