#importing url opener
from urllib.request import urlopen, Request
#importing web scrapers
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
#allows us to manipulate data in table structure
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import streamlit as st

def sentimentAnalysis(tickers):
    finviz_url = 'https://finviz.com/quote.ashx?t='
    #tickers = ['AAPL', 'AMZN', 'GOOGL', 'TSLA']
    #stores ticker news
    news_tables = {}

    for ticker in tickers:
        url = finviz_url + ticker

        #gets the html of the page
        req = Request(url=url, headers={'user-agent': 'my-app'})
        response = urlopen(req)

        #scrapes the html to find only the news, also puts info in news_table by ticker
        html = BeautifulSoup(response, 'html.parser')
        news_table = html.find(id='news-table')
        news_tables[ticker] = news_table


    #stores clean info
    parsed_data = []

    #get dictionary keys as first part of pair, and each news table
    for ticker, news_table in news_tables.items():
        #in each row, isolate news heading within tr
        for row in news_table.findAll('tr'):
            #look for anchor tag <a> after checking it exists and then get text
            if row.find('a'):
                title = row.a.text
                #date is in the <td> section
                date_data = row.td.text.replace("\r\n", "").split(' ')

                #split dates off of spaces
                if len(date_data) == 1:
                    time = date_data[12]
                else:
                    date = date_data[12]
                    time = date_data[13]
                
                parsed_data.append([ticker,date,time,title])

    #puts data in readable format
    df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title'])

    #initializing sentiment analyzer
    vader = SentimentIntensityAnalyzer()

    #create lambda function to use column property and change title to compound property(sentiment grade)
    f = lambda title: vader.polarity_scores(title)['compound']
    #make a new column and call it compound to access the grade
    df['compound'] = df['title'].apply(f)
    #takes date column and converts string to date time format (easy for matplot lib to recognize)
    df['date'] = pd.to_datetime(df.date).dt.date

    plt.figure(figsize=(20,16))

    #mean function only looks for integer values in a row and averages em up, group by ticker, date isolates those columns
    mean_df = df.groupby(['ticker', 'date']).mean()
    #returns datafram with new level of column labels who's inner most level consists of pivoted index labels
    mean_df = mean_df.unstack()
    #cross section
    mean_df = mean_df.xs('compound', axis="columns").transpose()
    mean_df.plot(kind='bar')
    st.pyplot(plt)
    return df

def show_page():
    st.title("Stock Sentiment Analysis")
    st.write("Using the news, this website predicts if a stock will go up or down at given times using machine learning and sentiment analysis!")
    st.write("""### Which stocks do you want to see today?""")

    stocks1 = (
        'TSLA',
        'AAPL',
        'AMZN',
        'GOOGL',
        'COST',
        'MSFT',
        'NVDA' 
    )
    stocksChosen = []

    for i in stocks1:
        chosen = st.checkbox(i)
        if(chosen):
            stocksChosen.append(i)

    ok = st.button("See the stats!")
    if ok:
        sentimentAnalysis(stocksChosen)

show_page()