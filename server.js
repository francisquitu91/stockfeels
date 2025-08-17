const express = require('express');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 8501;

// Serve static files
app.use(express.static('public'));
app.use(express.json());

// Function to run Python sentiment analysis
function runPythonAnalysis(ticker = null) {
    return new Promise((resolve, reject) => {
        const args = ticker ? ['api_wrapper.py', 'analyze', ticker] : ['api_wrapper.py', 'analyze'];
        const pythonProcess = spawn('python3', args);
        
        let dataString = '';
        let errorString = '';
        
        pythonProcess.stdout.on('data', (data) => {
            dataString += data.toString();
        });
        
        pythonProcess.stderr.on('data', (data) => {
            errorString += data.toString();
        });
        
        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(dataString);
                    resolve(result);
                } catch (e) {
                    reject({ error: 'Failed to parse Python output', details: dataString });
                }
            } else {
                reject({ error: 'Python process failed', code, stderr: errorString });
            }
        });
        
        // Timeout after 30 seconds
        setTimeout(() => {
            pythonProcess.kill();
            reject({ error: 'Python process timeout' });
        }, 30000);
    });
}

// Basic HTML template for the sentiment analyzer
const getHtmlTemplate = (sentimentData = null) => `
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
        .sentiment-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            transition: transform 0.2s ease;
        }
        .sentiment-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .bullish { border-left: 4px solid #28a745; }
        .bearish { border-left: 4px solid #dc3545; }
        .neutral { border-left: 4px solid #ffc107; }
        .ticker-symbol {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }
        .sentiment-score {
            font-size: 1.2em;
            margin: 10px 0;
        }
        .score-details {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
        }
        .refresh-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 20px 0;
            transition: background 0.2s ease;
        }
        .refresh-btn:hover {
            background: #0056b3;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 Sentiment Analyzer - Investment Tool 
            <span class="status-indicator status-running"></span>
        </h1>
        
        ${sentimentData ? generateSentimentHTML(sentimentData) : `
            <div class="info-message">
                <strong><span class="status-indicator status-running"></span>Live Sentiment Analysis Available</strong><br>
                Click "Analyze Stocks" to get real-time sentiment analysis from Finviz news.
            </div>
            
            <button class="refresh-btn" onclick="analyzeSentiment()">📊 Analyze Stocks</button>
            
            <div id="loading" class="loading" style="display: none;">
                <p>🔄 Analyzing sentiment from financial news...</p>
                <p>This may take a few moments...</p>
            </div>
            
            <div id="sentiment-results"></div>
        `}
        
        <div class="info-message">
            <strong>✅ Active Features:</strong>
            <ul class="feature-list">
                <li>📊 <strong>Live Stock Sentiment Analysis</strong> - Real-time analysis from Finviz news</li>
                <li>📈 Real-time sentiment scoring for AMZN, TSLA, AAPL, MSFT</li>
                <li>🎯 Bullish/Bearish/Neutral classifications</li>
                <li>📊 Detailed sentiment scores (positive, negative, neutral, compound)</li>
            </ul>
        </div>
        
        <script>
            async function analyzeSentiment() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('sentiment-results').innerHTML = '';
                
                try {
                    const response = await fetch('/api/sentiment');
                    const data = await response.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.success) {
                        displaySentimentResults(data.data);
                    } else {
                        document.getElementById('sentiment-results').innerHTML = 
                            '<div class="error-message">Error: ' + data.error + '</div>';
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('sentiment-results').innerHTML = 
                        '<div class="error-message">Network error: ' + error.message + '</div>';
                }
            }
            
            function displaySentimentResults(data) {
                let html = '<h2>📊 Current Sentiment Analysis</h2>';
                
                for (const [ticker, analysis] of Object.entries(data)) {
                    const sentimentClass = analysis.sentiment.toLowerCase();
                    const emoji = analysis.sentiment === 'Bullish' ? '📈' : 
                                 analysis.sentiment === 'Bearish' ? '📉' : '➡️';
                    
                    html += \`
                        <div class="sentiment-card \${sentimentClass}">
                            <div class="ticker-symbol">\${ticker} \${emoji}</div>
                            <div class="sentiment-score">
                                <strong>\${analysis.sentiment}</strong> 
                                (Score: \${analysis.compound_score})
                            </div>
                            <div class="score-details">
                                <span>Positive: \${analysis.positive}</span>
                                <span>Negative: \${analysis.negative}</span>
                                <span>Neutral: \${analysis.neutral}</span>
                            </div>
                        </div>
                    \`;
                }
                
                html += '<button class="refresh-btn" onclick="analyzeSentiment()">🔄 Refresh Analysis</button>';
                document.getElementById('sentiment-results').innerHTML = html;
            }
        </script>
        
        <div class="footer">
            <p>🚀 Application successfully running on port ${PORT}</p>
            <p>Built with Express.js + Python • Live sentiment analysis active</p>
        </div>
    </div>
</body>
</html>
`;

function generateSentimentHTML(sentimentData) {
    if (!sentimentData.success) {
        return `<div class="error-message">Error loading sentiment data: ${sentimentData.error}</div>`;
    }
    
    let html = '<h2>📊 Current Sentiment Analysis</h2>';
    
    for (const [ticker, analysis] of Object.entries(sentimentData.data)) {
        const sentimentClass = analysis.sentiment.toLowerCase();
        const emoji = analysis.sentiment === 'Bullish' ? '📈' : 
                     analysis.sentiment === 'Bearish' ? '📉' : '➡️';
        
        html += `
            <div class="sentiment-card ${sentimentClass}">
                <div class="ticker-symbol">${ticker} ${emoji}</div>
                <div class="sentiment-score">
                    <strong>${analysis.sentiment}</strong> 
                    (Score: ${analysis.compound_score})
                </div>
                <div class="score-details">
                    <span>Positive: ${analysis.positive}</span>
                    <span>Negative: ${analysis.negative}</span>
                    <span>Neutral: ${analysis.neutral}</span>
                </div>
            </div>
        `;
    }
    
    html += '<button class="refresh-btn" onclick="analyzeSentiment()">🔄 Refresh Analysis</button>';
    return html;
}

// Main route
app.get('/', (req, res) => {
    res.send(getHtmlTemplate());
});

// Sentiment analysis API endpoint
app.get('/api/sentiment', async (req, res) => {
    try {
        const result = await runPythonAnalysis();
        res.json(result);
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.error || 'Unknown error',
            details: error
        });
    }
});

// Single ticker analysis
app.get('/api/sentiment/:ticker', async (req, res) => {
    try {
        const ticker = req.params.ticker.toUpperCase();
        const result = await runPythonAnalysis(ticker);
        res.json(result);
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.error || 'Unknown error',
            details: error
        });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'Server running successfully', 
        timestamp: new Date().toISOString(),
        port: PORT,
        environment: 'WebContainer with Node.js + Python integration',
        features: ['Live sentiment analysis', 'Real-time stock data', 'Finviz scraping']
    });
});

// API endpoint to show original Python features
app.get('/api/features', (req, res) => {
    res.json({
        activeFeatures: [
            'Live stock sentiment analysis from Finviz',
            'Real-time sentiment scoring',
            'NLTK VADER sentiment analysis',
            'Support for AMZN, TSLA, AAPL, MSFT',
            'Bullish/Bearish/Neutral classification'
        ],
        currentStatus: 'Node.js + Python integration active',
        endpoints: [
            'GET /api/sentiment - Analyze all stocks',
            'GET /api/sentiment/:ticker - Analyze specific stock',
            'GET /health - Server health check'
        ]
    });
});

app.listen(PORT, () => {
    console.log(`✅ Server running successfully on port ${PORT}`);
    console.log(`🌐 Application available at http://localhost:${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
    console.log(`📈 Sentiment API: http://localhost:${PORT}/api/sentiment`);
    console.log(`🔧 Features API: http://localhost:${PORT}/api/features`);
});