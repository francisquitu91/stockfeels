from setuptools import setup, find_packages

setup(
    name="streamlit-sentiment-analyzer",
    version="1.0.0",
    description="Streamlit-based sentiment analysis application",
    packages=find_packages(),
    install_requires=[
        "matplotlib==3.7.1",
        "pandas==1.5.3", 
        "streamlit==1.24.1",
        "beautifulsoup4==4.9.3",
        "nltk==3.6.6",
        "supabase==2.18.1",
        "python-dotenv==1.0.0",
        "websockets==10.4",
        "requests==2.31.0",
        "plotly==5.15.0",
        "openai==1.3.0",
        "firecrawl-py==0.0.8"
    ],
    python_requires=">=3.8",
)