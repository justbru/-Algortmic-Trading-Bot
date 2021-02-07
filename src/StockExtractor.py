"""
Justin Brunings and Luke Argosino
Reddit Trending Stock Extraction Bot
"""

import praw, pandas
from praw.models import MoreComments


def loadTickers():
    colnames = ['Symbol', 'Name', 'Last Sale', 'Net Change', '% Change', 'Market Cap', 'Country', 'IPO Year',
                'Volume', 'Sector', 'Industry']
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

    print("Stock\t\t   Count\t\tPositive   \t\tNegative")
    for key in myData:
        tempwordGood = key + "Good"
        tempwordBad = key + "Bad"
        if key[-3:] != "Bad" and key[-4:] != "Good":
            if myData[key] > 6 and myData[key+"Good"] > myData[key+"Bad"]:
                if len(key) == 1:
                    print(key, "       \t\t", myData[key], "\t\t\t\t", myData[tempwordGood], "\t\t\t\t",
                          myData[tempwordBad])
                if len(key) == 2:
                    print(key, "      \t\t", myData[key], "\t\t\t\t", myData[tempwordGood], "\t\t\t\t",
                          myData[tempwordBad])
                if len(key) == 3:
                    print(key, "     \t\t", myData[key], "\t\t\t\t", myData[tempwordGood], "\t\t\t\t",
                          myData[tempwordBad])
                if len(key) == 4:
                    print(key, "   \t\t", myData[key], "\t\t\t\t", myData[tempwordGood], "\t\t\t\t",
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
    print("Most talked about stocks on r/wsb and r/investing:\n")
    subreddits = ["investing", "wallstreetbets", "Stocks", "StockMarket"]
    AnalyzeRedditData(tickers, subreddits, "hot")
    print("\nMost talked about stocks on r/pennystocks and r/RobinHoodPennyStocks:\n")
    subreddits = ["pennystocks", "RobinHoodPennyStocks"]
    AnalyzeRedditData(tickers, subreddits, "new")
