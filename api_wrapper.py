#!/usr/bin/env python3
"""
API wrapper to expose Python sentiment analysis features via HTTP
"""
import json
import sys
import traceback
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from datetime import datetime

# Download VADER lexicon if not present
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

def get_news_sentiment(tickers=['AMZN', 'TSLA', 'AAPL', 'MSFT']):
    """
    Get sentiment analysis for given tickers
    """
    try:
        finviz_url = 'https://finviz.com/quote.ashx?t='
        news_tables = {}
        
        for ticker in tickers:
            url = finviz_url + ticker
            req = Request(url=url, headers={'user-agent': 'Mozilla/5.0'})
            response = urlopen(req).read()
            
            html = BeautifulSoup(response, 'html.parser')
            news_table = html.find(id='news-table')
            news_tables[ticker] = news_table
        
        # Parse news data
        parsed_news = []
        for file_name, news_table in news_tables.items():
            if news_table is None:
                continue
                
            for x in news_table.findAll('tr'):
                try:
                    text = x.a.get_text()
                    date_scrape = x.td.text.split()
                    
                    if len(date_scrape) == 1:
                        time = date_scrape[0]
                    else:
                        date = date_scrape[0]
                        time = date_scrape[1]
                    
                    ticker = file_name.split('_')[0]
                    parsed_news.append([ticker, date, time, text])
                except:
                    continue
        
        # Create DataFrame
        columns = ['ticker', 'date', 'time', 'title']
        parsed_news_df = pd.DataFrame(parsed_news, columns=columns)
        
        # Sentiment analysis
        vader = SentimentIntensityAnalyzer()
        scores = parsed_news_df['title'].apply(vader.polarity_scores).tolist()
        
        scores_df = pd.DataFrame(scores)
        parsed_news_df = parsed_news_df.join(scores_df, rsuffix='_right')
        
        # Calculate mean sentiment by ticker
        mean_scores = parsed_news_df.groupby('ticker').mean()
        
        result = {}
        for ticker in tickers:
            if ticker in mean_scores.index:
                compound_score = mean_scores.loc[ticker, 'compound']
                if compound_score >= 0.05:
                    sentiment = "Bullish"
                elif compound_score <= -0.05:
                    sentiment = "Bearish"
                else:
                    sentiment = "Neutral"
                
                result[ticker] = {
                    'sentiment': sentiment,
                    'compound_score': round(compound_score, 4),
                    'positive': round(mean_scores.loc[ticker, 'pos'], 4),
                    'negative': round(mean_scores.loc[ticker, 'neg'], 4),
                    'neutral': round(mean_scores.loc[ticker, 'neu'], 4)
                }
            else:
                result[ticker] = {
                    'sentiment': 'No data',
                    'compound_score': 0,
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0
                }
        
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': result
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def analyze_single_ticker(ticker):
    """
    Analyze sentiment for a single ticker
    """
    return get_news_sentiment([ticker.upper()])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "analyze":
            if len(sys.argv) > 2:
                ticker = sys.argv[2]
                result = analyze_single_ticker(ticker)
            else:
                result = get_news_sentiment()
            print(json.dumps(result, indent=2))
        
        elif command == "health":
            print(json.dumps({"status": "Python API is working", "nltk_available": True}))
    
    else:
        # Default: analyze all tickers
        result = get_news_sentiment()
        print(json.dumps(result, indent=2))