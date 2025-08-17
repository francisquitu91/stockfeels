import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pickle
from datetime import date
import requests
import time
import re
import json
import os
from openai import OpenAI
import base64
from typing import Optional, Dict, Any

# Download NLTK data if not present
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# PayPal Configuration
PAYPAL_CLIENT_ID = st.secrets.get("PAYPAL_CLIENT_ID", os.getenv("PAYPAL_CLIENT_ID"))
PAYPAL_SECRET = st.secrets.get("PAYPAL_SECRET", os.getenv("PAYPAL_SECRET"))
PAYPAL_ENV = st.secrets.get("PAYPAL_ENV", os.getenv("PAYPAL_ENV", "sandbox"))

if PAYPAL_ENV == "live":
    PAYPAL_BASE = "https://api-m.paypal.com"
else:
    PAYPAL_BASE = "https://api-m.sandbox.paypal.com"

class PayPalError(Exception):
    pass

def _get_basic_auth_header() -> Dict[str, str]:
    if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
        raise PayPalError("PayPal credentials not set")
    token = f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()
    b64 = base64.b64encode(token).decode()
    return {"Authorization": f"Basic {b64}", "Content-Type": "application/x-www-form-urlencoded"}

def get_access_token() -> str:
    """Obtain an OAuth2 access token from PayPal."""
    url = f"{PAYPAL_BASE}/v1/oauth2/token"
    headers = _get_basic_auth_header()
    resp = requests.post(url, headers=headers, data={"grant_type": "client_credentials"}, timeout=10)
    if resp.status_code != 200:
        raise PayPalError(f"Failed to obtain access token: {resp.status_code} {resp.text}")
    data = resp.json()
    return data.get("access_token")

def create_order(amount: str, currency: str = "USD") -> Dict[str, Any]:
    """Create a PayPal order and return approval url and order id."""
    access_token = get_access_token()
    url = f"{PAYPAL_BASE}/v2/checkout/orders"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {"currency_code": currency, "value": amount}
        }]
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    if resp.status_code not in (201, 200):
        raise PayPalError(f"Failed to create order: {resp.status_code} {resp.text}")
    data = resp.json()
    
    # Find approval link
    approval_link = None
    for link in data.get("links", []):
        if link.get("rel") == "approve":
            approval_link = link.get("href")
            break
    return {"order_id": data.get("id"), "approval_link": approval_link, "raw": data}

def capture_order(order_id: str) -> Dict[str, Any]:
    """Capture funds for an approved order."""
    access_token = get_access_token()
    url = f"{PAYPAL_BASE}/v2/checkout/orders/{order_id}/capture"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={}, timeout=10)
    if resp.status_code not in (200, 201):
        raise PayPalError(f"Failed to capture order: {resp.status_code} {resp.text}")
    return resp.json()

# AI Configuration
def generate_ai_summary(content_data, ticker, sentiment_score):
    """Generate intelligent summary using OpenRouter AI"""
    try:
        openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        if not openai_key:
            return "AI analysis not available - API key not configured"
            
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openai_key
        )
        
        full_content = "\n".join([f"- {item['title']}: {item['content'][:500]}..." for item in content_data[:5]])
        
        prompt = f"""
        Analyze the following news about {ticker} and provide a concise summary:
        
        {full_content}
        
        General sentiment score: {sentiment_score:.2f} (-1 very negative, +1 very positive)
        
        Please provide:
        1. Summary of main topics (maximum 3 points)
        2. Potential impact on stock price
        3. Key factors to monitor
        
        Keep the response in English and concise (maximum 200 words).
        """
        
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating AI analysis: {str(e)}"

def generate_investment_advice(user_message, investment_profile=None):
    """Generate investment advice using AI"""
    try:
        openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        if not openai_key:
            return "Investment advice not available - API key not configured"
            
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openai_key
        )
        
        prompt = f"""
        You are an expert investment advisor specializing in stock analysis and investment strategies.

        Investment Profile: {investment_profile if investment_profile else 'Not specified'}
        User Question: {user_message}

        Guidelines:
        1. Provide practical, actionable investment advice
        2. Consider risk management and diversification
        3. Explain your reasoning clearly
        4. Keep responses concise and professional
        5. Include relevant disclaimers about investment risks

        Respond in English with practical advice.
        """
        
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating investment advice: {str(e)}"

# Sentiment Analysis Functions
def get_news(ticker):
    """Scrape news from Finviz for a given ticker"""
    try:
        url = f'https://finviz.com/quote.ashx?t={ticker}'
        req = Request(url=url, headers={'user-agent': 'Mozilla/5.0'})
        response = urlopen(req).read()
        html = BeautifulSoup(response, 'html.parser')
        news_table = html.find(id='news-table')
        
        if not news_table:
            return []
            
        news_data = []
        for row in news_table.findAll('tr'):
            try:
                title_cell = row.find('a')
                if title_cell:
                    title = title_cell.get_text()
                    link = title_cell.get('href', '')
                    
                    time_cell = row.find('td')
                    time_text = time_cell.get_text() if time_cell else ''
                    
                    news_data.append({
                        'title': title,
                        'link': link,
                        'time': time_text,
                        'content': title  # Using title as content for sentiment analysis
                    })
            except Exception:
                continue
                
        return news_data[:10]  # Return top 10 news items
        
    except Exception as e:
        st.error(f"Error fetching news for {ticker}: {str(e)}")
        return []

def analyze_sentiment(news_data):
    """Analyze sentiment of news data"""
    if not news_data:
        return 0, []
        
    analyzer = SentimentIntensityAnalyzer()
    scores = []
    
    for item in news_data:
        score = analyzer.polarity_scores(item['content'])
        scores.append(score['compound'])
        item['sentiment'] = score['compound']
    
    avg_sentiment = sum(scores) / len(scores) if scores else 0
    return avg_sentiment, news_data

# Streamlit App Configuration
st.set_page_config(
    page_title="Stock Sentiment Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4037 0%, #99f2c8 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 1rem 0;
    }
    .news-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
    .positive { border-left-color: #28a745 !important; }
    .negative { border-left-color: #dc3545 !important; }
    .neutral { border-left-color: #ffc107 !important; }
</style>
""", unsafe_allow_html=True)

def show_premium_features():
    """Show premium features section"""
    st.markdown("### 🚀 Premium Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Premium Analysis includes:**
        - ✅ AI-powered market insights
        - ✅ Advanced sentiment tracking
        - ✅ Investment recommendations
        - ✅ Real-time alerts
        - ✅ Portfolio optimization
        """)
    
    with col2:
        st.markdown("**Unlock Premium for $9.99/month**")
        
        if st.button("🔓 Upgrade to Premium", type="primary", use_container_width=True):
            try:
                order = create_order("9.99", "USD")
                if order.get("approval_link"):
                    st.success("✅ PayPal order created successfully!")
                    st.markdown(f"[Complete Payment]({order['approval_link']})")
                    st.session_state.paypal_order_id = order["order_id"]
                else:
                    st.error("❌ Failed to create PayPal order")
            except PayPalError as e:
                st.error(f"❌ PayPal Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

def show_investment_chatbot():
    """Display investment strategy chatbot interface"""
    st.markdown("### 🎯 Investment Strategy Assistant")
    
    # Initialize chat history
    if "investment_chat_history" not in st.session_state:
        st.session_state.investment_chat_history = []
    
    # Chat interface
    if len(st.session_state.investment_chat_history) == 0:
        st.markdown("""
        **Welcome to the Investment Strategy Assistant!**
        
        Ask me about:
        - Stock analysis and recommendations
        - Portfolio diversification strategies
        - Risk management techniques
        - Market trends and insights
        """)
        
        # Quick start buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💎 Value Investing Tips"):
                user_input = "Give me tips for value investing in the current market"
                st.session_state.investment_chat_history.append({"role": "user", "content": user_input})
                with st.spinner("Analyzing..."):
                    ai_response = generate_investment_advice(user_input, "Value Investing")
                st.session_state.investment_chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        with col2:
            if st.button("📊 Portfolio Analysis"):
                user_input = "How should I analyze my investment portfolio?"
                st.session_state.investment_chat_history.append({"role": "user", "content": user_input})
                with st.spinner("Analyzing..."):
                    ai_response = generate_investment_advice(user_input, "Portfolio Management")
                st.session_state.investment_chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        with col3:
            if st.button("⚡ Growth Strategies"):
                user_input = "What are effective growth investing strategies?"
                st.session_state.investment_chat_history.append({"role": "user", "content": user_input})
                with st.spinner("Analyzing..."):
                    ai_response = generate_investment_advice(user_input, "Growth Investing")
                st.session_state.investment_chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()
    
    # Display chat history
    for message in st.session_state.investment_chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI Assistant:** {message['content']}")
        st.markdown("---")
    
    # User input
    user_input = st.text_area("Ask your investment question:", height=100)
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("Send", type="primary"):
            if user_input.strip():
                st.session_state.investment_chat_history.append({"role": "user", "content": user_input})
                with st.spinner("Generating response..."):
                    ai_response = generate_investment_advice(user_input)
                st.session_state.investment_chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()
    
    with col2:
        if st.button("Clear Chat"):
            st.session_state.investment_chat_history = []
            st.rerun()

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📈 Stock Sentiment Analysis Platform</h1>
        <p>AI-powered sentiment analysis for informed investment decisions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Controls")
        
        # Navigation
        page = st.selectbox("Choose Analysis Type:", 
                          ["Sentiment Analysis", "Investment Assistant", "Premium Features"])
        
        if page == "Sentiment Analysis":
            st.markdown("### 📊 Stock Selection")
            
            # Predefined tickers
            popular_tickers = ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "NFLX"]
            selected_ticker = st.selectbox("Select a popular stock:", [""] + popular_tickers)
            
            # Custom ticker input
            custom_ticker = st.text_input("Or enter custom ticker:", placeholder="e.g., AAPL")
            
            # Use custom ticker if provided, otherwise use selected
            ticker = custom_ticker.upper() if custom_ticker else selected_ticker
            
            analyze_button = st.button("🔍 Analyze Sentiment", type="primary", disabled=not ticker)
            
            # Analysis settings
            st.markdown("### ⚙️ Settings")
            show_ai_summary = st.checkbox("Show AI Summary", value=True)
            show_news_details = st.checkbox("Show News Details", value=True)
    
    # Main content based on page selection
    if page == "Sentiment Analysis":
        if 'analyze_button' in locals() and analyze_button and ticker:
            with st.spinner(f"Analyzing sentiment for {ticker}..."):
                # Get news and analyze sentiment
                news_data = get_news(ticker)
                
                if news_data:
                    avg_sentiment, analyzed_news = analyze_sentiment(news_data)
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        sentiment_color = "🟢" if avg_sentiment > 0.1 else "🔴" if avg_sentiment < -0.1 else "🟡"
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{sentiment_color} Sentiment Score</h3>
                            <h2>{avg_sentiment:.3f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        sentiment_label = "Bullish" if avg_sentiment > 0.1 else "Bearish" if avg_sentiment < -0.1 else "Neutral"
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>📊 Market Sentiment</h3>
                            <h2>{sentiment_label}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>📰 News Articles</h3>
                            <h2>{len(news_data)}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Sentiment visualization
                    st.markdown("### 📈 Sentiment Visualization")
                    
                    # Create sentiment distribution chart
                    sentiments = [item['sentiment'] for item in analyzed_news]
                    fig = go.Figure(data=go.Histogram(x=sentiments, nbinsx=20))
                    fig.update_layout(
                        title=f"Sentiment Distribution for {ticker}",
                        xaxis_title="Sentiment Score",
                        yaxis_title="Frequency",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # AI Summary
                    if show_ai_summary:
                        st.markdown("### 🤖 AI Analysis")
                        with st.spinner("Generating AI insights..."):
                            ai_summary = generate_ai_summary(analyzed_news, ticker, avg_sentiment)
                            st.markdown(ai_summary)
                    
                    # News details
                    if show_news_details:
                        st.markdown("### 📰 Recent News Analysis")
                        
                        for item in analyzed_news[:5]:  # Show top 5 news items
                            sentiment_class = "positive" if item['sentiment'] > 0.1 else "negative" if item['sentiment'] < -0.1 else "neutral"
                            
                            st.markdown(f"""
                            <div class="news-item {sentiment_class}">
                                <strong>{item['title']}</strong><br>
                                <small>Sentiment: {item['sentiment']:.3f} | {item['time']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                
                else:
                    st.error(f"❌ No news data found for {ticker}. Please check the ticker symbol.")
        
        elif not ticker:
            st.info("👆 Please select or enter a stock ticker to begin analysis")
    
    elif page == "Investment Assistant":
        show_investment_chatbot()
    
    elif page == "Premium Features":
        show_premium_features()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>📈 Stock Sentiment Analysis Platform | Powered by AI & Real-time Data</p>
        <p><small>Disclaimer: This tool is for educational purposes only. Not financial advice.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()