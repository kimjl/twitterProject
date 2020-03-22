# Twitter Project
An application built with Python and Flask. This application crawls Twitter, using their API, to search for tweets with #tradewar.
The site collects the data and displays information to the user in the form of graphs and uses sentiment analysis to show how positive
or negative the data is. 

## Visit at:
https://radiant-basin-45483.herokuapp.com/

## How to use:
To install. make sure you are in the directory you want the folder to be in. In your terminal use the following command:

```
git clone https://github.com/kimjl/twitterProject.git
```

## Running locally:
Once you have cloned the files, you you need to install the packages using:
```
pip install -r requirements.txt
```
Once completed make sure you have MongoDB running locally and finally launch the application:
```
python app.py
```

## Collecting Tweets:
If you want to collect your own data, or change the hashtag use the tweetstream.py file.

```
python tweetstream.py
```
