import streamlit as st
import os
from new_main import *

# Configure page
st.set_page_config(
    page_title="Stock Sentiment Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"

# Main app logic
def main():
    if st.session_state.current_page == "landing":
        show_landing_page()
    elif st.session_state.current_page == "investment":
        show_investment_chatbot()
    elif st.session_state.current_page == "sentiment":
        show_sentiment_analysis()

def show_landing_page():
    st.title("📈 Stock Analysis Suite")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Investment Strategy Assistant
        Get personalized Finviz screening strategies and put options guidance.
        """)
        if st.button("Launch Investment Assistant", use_container_width=True, type="primary"):
            st.session_state.current_page = "investment"
            st.experimental_rerun()
    
    with col2:
        st.markdown("""
        ### 📊 Sentiment Analysis
        Analyze stock sentiment from news and social media.
        """)
        if st.button("Launch Sentiment Analysis", use_container_width=True, type="secondary"):
            st.session_state.current_page = "sentiment"
            st.experimental_rerun()

def show_sentiment_analysis():
    st.title("📊 Stock Sentiment Analysis")
    
    col_left, col_center, col_right = st.columns([1, 8, 1])
    with col_left:
        if st.button("← Back", type="secondary"):
            st.session_state.current_page = "landing"
            st.experimental_rerun()
    
    st.markdown("---")
    st.info("Sentiment analysis functionality - integrate your existing sentiment analysis code here")

if __name__ == "__main__":
    main()