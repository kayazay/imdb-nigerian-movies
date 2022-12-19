FROM python:3.8-slim

# prevent python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# upgrade pip
RUN pip install --upgrade pip

# code to apt-get update and install psycopg2
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# set working directory
WORKDIR /app

# Install dependecies
RUN pip3 install scrapy nltk psycopg2

# select the files to build- the scraper and all config files
COPY imdbscraper/ ./imdbscraper/
COPY scrapy.cfg run.py ./

# run the script that runs scrapy
CMD ["python3", "./run.py"]
