const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 8501;

// Serve static files
app.use(express.static('public'));
app.use(express.json());

// Basic HTML template for the sentiment analyzer
const htmlTemplate = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment Analyzer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .error-message {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .info-message {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .feature-list {
            list-style-type: none;
            padding: 0;
        }
        .feature-list li {
            padding: 10px;
            margin: 5px 0;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 Sentiment Analyzer - Investment Tool</h1>
        
        <div class="error-message">
            <strong>Python Environment Issue Detected</strong><br>
            The Python environment is experiencing core module issues that prevent the Streamlit application from running properly.
        </div>
        
        <div class="info-message">
            <strong>Application Features (Currently Unavailable):</strong>
            <ul class="feature-list">
                <li>📊 Stock sentiment analysis from Finviz news</li>
                <li>🤖 AI-powered investment chatbot</li>
                <li>📈 Real-time sentiment scoring for AMZN, TSLA, AAPL, MSFT</li>
                <li>💡 Investment strategy recommendations</li>
                <li>📋 Analysis history tracking</li>
                <li>💳 PayPal integration for premium features</li>
            </ul>
        </div>
        
        <div class="info-message">
            <strong>Technical Details:</strong><br>
            This application requires a properly configured Python environment with modules like NLTK, Streamlit, OpenAI, and others. 
            The current environment is missing core Python modules including '_signal', which prevents proper execution.
        </div>
    </div>
</body>
</html>
`;

// Main route
app.get('/', (req, res) => {
    res.send(htmlTemplate);
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'Server running', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Visit http://localhost:${PORT} to view the application`);
});