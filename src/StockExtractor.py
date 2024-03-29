"""
Justin Brunings
Reddit Trending Stock Extraction Bot
"""

import pandas
import praw
from praw.models import MoreComments


def loadTickers():
    colnames = ['Symbol', 'Company Name']
    data = pandas.read_csv('Tickers.csv', names=colnames)
    tickers = data.Symbol.tolist()
    return tickers


def loadPositiveWords():
    colnames = ['Word', '']
    data = pandas.read_csv('PositiveWords.csv', names=colnames)
    posNames = data.Word.tolist()
    return posNames


def loadNegativeWords():
    colnames = ['Word', '']
    data = pandas.read_csv('NegativeWords.csv', names=colnames)
    posNames = data.Word.tolist()
    return posNames


def AnalyzeRedditData(tickers, subreddits, condition):
    reddit = praw.Reddit(client_id="bgzEHVmGS23rZw",
                         client_secret="jaFzjBfQM2VCBfEISB2qnO3YY1lrUA",
                         user_agent="trending stock extractor v1.0 by /u/justbru")
    myData = {}
    if condition == "hot and new":
        for subreddit in subreddits:
            for post in reddit.subreddit(subreddit).hot(limit=1000):
                if not post.stickied:
                    myData = scrapePost(post, myData, tickers)
            for post in reddit.subreddit(subreddit).new(limit=1000):
                if not post.stickied:
                    myData = scrapePost(post, myData, tickers)
    if condition == "hot":
        for subreddit in subreddits:
            for post in reddit.subreddit(subreddit).hot(limit=1000):
                if not post.stickied:
                    myData = scrapePost(post, myData, tickers)
    elif condition == "new":
        for subreddit in subreddits:
            for post in reddit.subreddit(subreddit).new(limit=1000):
                if not post.stickied:
                    myData = scrapePost(post, myData, tickers)
    else:
        for subreddit in subreddits:
            for post in reddit.subreddit(subreddit).rising(limit=1000):
                if not post.stickied:
                    myData = scrapePost(post, myData, tickers)

    print("Stock, Count, Positive, Negative")
    for key in myData:
        tempwordGood = key + "Good"
        tempwordBad = key + "Bad"
        if key[-3:] != "Bad" and key[-4:] != "Good":
            if ((condition == "hot and new" and myData[key] > 10) or (condition == "rising" and myData[key] > 3)
                or (condition == "new" and myData[key] > 8)) and myData[key + "Good"] > myData[key + "Bad"]:
                print(key, ": ", myData[key], "| ", myData[tempwordGood], "| ",
                      myData[tempwordBad])


def scrapePost(post, myData, tickers):
    containsTicker = False
    postData = post.selftext.split()
    postTickers = []
    for word in postData:
        if word.isupper() and word in tickers:
            if myData.__contains__(word):
                myData[word] += 1
                containsTicker = True
                postTickers.append(word)
            else:
                myData[word] = 1
                postTickers.append(word)

    max = 0
    referenceTicker = ""

    # Creates a new entry in myData that contains a good and bad for each ticker that has the value of each
    for ticker in postTickers:
        badWord = ticker + "Bad"
        goodWord = ticker + "Good"
        if goodWord not in myData:
            myData[goodWord] = 0
        if badWord not in myData:
            myData[badWord] = 0
        if myData[ticker] > max:
            referenceTicker = ticker
            max = myData[ticker]

    # If the post contains a ticker, this portion looks through the data again adding to the tickers good and bad entry
    if containsTicker:
        myData = scrapeDataHelper(myData, postData, referenceTicker)
        for top_level_comment in post.comments:
            if isinstance(top_level_comment, MoreComments):
                continue
            myData = scrapeDataHelper(myData, top_level_comment.body.split(), referenceTicker)
    return myData


def scrapeDataHelper(myData, postData, referenceTicker):
    for word in postData:
        if word in positiveWords:
            tempword = referenceTicker + "Good"
            myData[tempword] += 1
        if word in negativeWords:
            tempword = referenceTicker + "Bad"
            myData[tempword] += 1
    return myData


if __name__ == '__main__':
    positiveWords = loadPositiveWords()
    negativeWords = loadNegativeWords()
    tickers = loadTickers()
    print("\nMost talked about stocks on r/WallStreetBets, r/Investing, r/Stocks, and r/StockMarket:\n")
    subreddits = ["investing", "wallstreetbets", "Stocks", "StockMarket"]
    AnalyzeRedditData(tickers, subreddits, "hot and new")
    print("\nMost talked about rising stocks on r/WallStreetBets, r/Investing, r/Stocks, and r/StockMarket:\n")
    AnalyzeRedditData(tickers, subreddits, "rising")
    print("\nMost talked about stocks on r/pennystocks and r/RobinHoodPennyStocks:\n")
    subreddits = ["pennystocks", "RobinHoodPennyStocks"]
    AnalyzeRedditData(tickers, subreddits, "new")
