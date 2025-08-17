const express = require('express');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

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
            line-height: 1.6;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
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
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-running { background-color: #28a745; }
        .status-error { background-color: #dc3545; }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 Sentiment Analyzer - Investment Tool 
            <span class="status-indicator status-running"></span>
        </h1>
        
        <div class="info-message">
            <strong><span class="status-indicator status-running"></span>Server Status: Running Successfully</strong><br>
            The Node.js server is running properly and serving the application interface.
        </div>
        
        <div class="info-message">
            <strong>Original Python Application Features:</strong>
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
            <strong>Current Implementation:</strong><br>
            Running on Node.js Express server due to Python environment limitations in WebContainer. 
            The original Streamlit application with sentiment analysis and AI features is preserved in the codebase 
            and can be deployed to environments with proper Python support.
        </div>
        
        <div class="footer">
            <p>🚀 Application successfully running on port ${PORT}</p>
            <p>Built with Express.js • Original Python code preserved</p>
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
    res.json({ 
        status: 'Server running successfully', 
        timestamp: new Date().toISOString(),
        port: PORT,
        environment: 'WebContainer with Node.js fallback'
    });
});

// API endpoint to show original Python features
app.get('/api/features', (req, res) => {
    res.json({
        originalFeatures: [
            'Stock sentiment analysis from Finviz',
            'AI-powered investment chatbot',
            'Real-time sentiment scoring',
            'Investment strategy recommendations',
            'Analysis history tracking',
            'PayPal integration'
        ],
        currentStatus: 'Node.js server running',
        pythonCodePreserved: true
    });
});

app.listen(PORT, () => {
    console.log(`✅ Server running successfully on port ${PORT}`);
    console.log(`🌐 Application available at http://localhost:${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
    console.log(`🔧 Features API: http://localhost:${PORT}/api/features`);
});