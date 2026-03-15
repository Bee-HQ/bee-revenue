# Claude & AI-Assisted Trading Workflows for Absolute Beginners

Compiled: 2026-03-14

> **User Profiles**
>
> This document is tailored for two specific users:
>
> **⚠️ User 1 (H1B/US):** Indian citizen on an H1B visa, working as an employee in the United States. Has access to US brokerages and markets. Must be mindful of visa-related restrictions on business activity and US/India cross-border tax obligations.
>
> **⚠️ User 2 (India):** Indian citizen living in India, currently unemployed. Has access to Indian brokerages and markets (NSE/BSE). Should focus on Indian market tools and platforms, and be aware of SEBI regulations and Indian tax rules on trading income.
>
> Throughout this document, user-specific notes are marked with the labels above.

---

## 1. What Claude Can Do for Trading

Claude is a general-purpose AI assistant. It has no brokerage connection, no live data feed, and no crystal ball. What it does have is the ability to read, reason, write code, and explain things clearly. That makes it a powerful research partner, coding assistant, and learning tutor for someone entering the trading world.

### 1.1 Research Company Fundamentals

Claude can read and analyze SEC filings (10-K annual reports, 10-Q quarterly reports, 8-K current events), earnings transcripts, and investor presentations when you paste or upload the text. You can ask it to:

- Summarize a 10-K filing into plain English
- Pull out key financial metrics (revenue, net income, free cash flow, debt-to-equity ratio, margins)
- Compare those metrics across multiple companies
- Identify red flags (declining margins, growing debt, revenue concentration in a single customer)
- Explain management discussion & analysis (MD&A) sections
- Walk through an earnings call transcript and highlight forward-looking statements vs. backward-looking results

**Example prompt:**
> "Here is Apple's most recent 10-K filing. Summarize the key financials, list the top 3 risk factors management disclosed, and compare revenue growth to the prior year."

### 1.2 Explain Financial Concepts in Plain Language

Trading and investing have enormous jargon barriers. Claude can serve as a patient, always-available tutor that adjusts explanations to your level:

- What is a P/E ratio and why does it matter?
- Explain options (calls, puts, Greeks) like I'm 12 years old
- What is the difference between a market order and a limit order?
- How does short selling actually work mechanically?
- What is the yield curve and why do people say it predicts recessions?
- What are prediction markets and how do they differ from sports betting?

### 1.3 Write and Debug Trading Bot Code

Claude can write Python, JavaScript, Rust, and other languages. For trading specifically it can help you:

- Write scripts that connect to broker APIs (Alpaca, Interactive Brokers, TD Ameritrade/Schwab)
- Build backtesting frameworks using libraries like `backtrader`, `zipline`, `vectorbt`
- Implement technical indicators (RSI, MACD, Bollinger Bands, moving averages)
- Debug error messages from APIs or libraries
- Refactor messy code into clean, maintainable modules
- Write unit tests for your trading logic
- Implement risk management rules (position sizing, stop losses, maximum drawdown limits)

### 1.4 Analyze Data and Create Visualizations

If you provide data (or write code to fetch it), Claude can help you:

- Write pandas code to clean and transform financial data
- Create matplotlib, plotly, or seaborn charts (candlestick charts, correlation heatmaps, drawdown curves)
- Build statistical analyses (returns distribution, Sharpe ratio calculations, rolling correlations)
- Generate comparison tables and ranking systems

### 1.5 Build Automation Scripts

Claude can help you write automation code for:

- Cron jobs that run daily research reports
- Scripts that send alerts via email, SMS (Twilio), Slack, or Discord
- Web scrapers that collect data from financial sites
- Database schemas to store historical data
- API integrations with data providers (Alpha Vantage, Polygon.io, Yahoo Finance, FRED)
- CI/CD pipelines for deploying trading bots to cloud servers

### 1.6 Summarize News and Research

You can paste news articles, research reports, or analyst notes into Claude and ask for:

- A one-paragraph summary
- Bull case vs. bear case breakdown
- Key data points extracted and organized
- Comparison with previous reports on the same topic
- Potential market impact assessment (though this is opinion, not prediction)

### 1.7 What Claude CANNOT Do

This is equally important to understand:

| Limitation | Details |
|------------|---------|
| **No real-time data** | Claude does not have a live stock ticker. It cannot tell you the current price of AAPL. You need to pair it with data sources. |
| **Not financial advice** | Claude is not a licensed financial advisor. Its outputs are informational, not recommendations. |
| **No direct trading** | Claude cannot place trades on your behalf. It can write code that does, but you must run that code yourself. |
| **Knowledge cutoff** | Claude's training data has a cutoff date. It may not know about very recent events, mergers, or earnings unless you provide the information. |
| **No guaranteed accuracy** | Claude can make mathematical errors, misinterpret data, or hallucinate facts. Always verify critical numbers against primary sources. |
| **Cannot predict the future** | No AI can reliably predict stock prices. Anyone who tells you otherwise is selling something. |
| **No emotional judgment** | Claude does not know your risk tolerance, financial situation, or investment timeline. Those are deeply personal inputs. |

---

## 2. Practical Claude-Assisted Workflows

These are repeatable workflows you can adopt from day one. Each one describes a pattern of interaction, not a one-time prompt.

### 2.1 Research Workflow: Analyzing a Company

**Step-by-step:**

1. **Gather source material**: Download the company's latest 10-K and 10-Q from SEC EDGAR (sec.gov/cgi-bin/browse-edgar). Copy the earnings call transcript from Seeking Alpha or The Motley Fool.
2. **Initial analysis prompt**: Paste the 10-K into Claude and ask: "Summarize this 10-K. Focus on revenue breakdown by segment, profit margins, debt levels, and the top 5 risk factors."
3. **Deep dive**: Follow up with specific questions: "What percentage of revenue comes from services vs. products? How has that mix changed over 3 years?"
4. **Competitive comparison**: Paste a competitor's 10-K and ask Claude to build a comparison table of key metrics.
5. **Valuation sanity check**: Ask Claude to explain common valuation methods (DCF, comparable companies, EV/EBITDA) and walk through a simplified calculation.
6. **Document your findings**: Ask Claude to format your research into a structured investment memo.

**Time investment**: 1-3 hours (vs. 8-15 hours doing it all manually as a beginner).

> **⚠️ User 1 (H1B/US):** The research workflow above works perfectly for US stocks. A great starting prompt is: "Analyze Apple vs Microsoft — compare their latest 10-K filings side by side on revenue growth, margins, and debt levels." You can also ask Claude about H1B-specific tax implications of trading, such as: "I'm on an H1B visa. Explain how short-term vs. long-term capital gains affect my US tax return, and whether I need to report my Indian bank accounts under FBAR/FATCA."

> **⚠️ User 2 (India):** Modify the company research workflow to focus on Indian companies. Indian companies file annual reports with MCA and quarterly results with stock exchanges, not SEC EDGAR. A great starting prompt is: "Analyze Reliance Industries vs TCS vs Infosys — compare revenue growth, profit margins, debt-to-equity, and promoter holding percentages." Use data from Screener.in (free fundamental data for Indian companies) or MoneyControl for financials and analyst reports. Replace SEC EDGAR with BSE/NSE filings and annual reports from company investor relations pages.

### 2.2 Strategy Development Workflow

**Step-by-step:**

1. **Describe your idea in plain English**: "I want to buy stocks when their 50-day moving average crosses above the 200-day moving average, and sell when it crosses below."
2. **Claude codes it**: Ask Claude to implement this using `backtrader` or `vectorbt` in Python.
3. **Backtest**: Run the code against historical data. Ask Claude to help you interpret the results (Sharpe ratio, maximum drawdown, win rate, profit factor).
4. **Iterate**: "What if we add a volume filter? Only take the signal if volume is above the 20-day average." Claude modifies the code.
5. **Stress test**: Ask Claude to help you test against different time periods, different assets, and different market regimes (bull, bear, sideways).
6. **Risk management**: Ask Claude to add position sizing rules, stop losses, and maximum portfolio exposure limits.

**Warning**: Backtesting is not a guarantee of future performance. Overfitting to historical data is the #1 beginner mistake.

### 2.3 News Synthesis Workflow

**Step-by-step:**

1. **Collect articles**: Gather 3-5 articles about a topic (e.g., "Federal Reserve interest rate decision").
2. **Feed to Claude**: Paste them and ask: "Summarize these articles. What are the key facts vs. opinions? What are the market implications mentioned?"
3. **Identify consensus and disagreement**: "Where do these sources agree? Where do they disagree?"
4. **Historical context**: "How have markets historically reacted to similar Fed decisions? Explain the general pattern."
5. **Action items**: "Based on this information, what are the key dates and data points I should monitor going forward?"

### 2.4 Code Assistance Workflow

**What you can build with Claude's help:**

| Project | Difficulty | Key Libraries |
|---------|-----------|---------------|
| Stock data scraper | Beginner | `yfinance`, `requests`, `beautifulsoup4` |
| Technical indicator calculator | Beginner | `pandas`, `ta-lib` or `pandas-ta` |
| Portfolio tracker spreadsheet | Beginner | `openpyxl`, `pandas` |
| Earnings calendar monitor | Intermediate | `requests`, `schedule`, `smtplib` |
| Sentiment analyzer | Intermediate | `transformers`, `vaderSentiment`, `tweepy` |
| Interactive dashboard | Intermediate | `streamlit`, `dash`, `plotly` |
| Backtesting engine | Intermediate | `backtrader`, `vectorbt`, `zipline-reloaded` |
| Live trading bot | Advanced | `alpaca-trade-api`, `ib_insync`, `ccxt` (crypto) |
| Options pricing calculator | Advanced | `scipy`, `numpy`, `mibian` |

### 2.5 Learning Workflow

**Use Claude as a structured tutor:**

1. **Assessment**: Tell Claude your current knowledge level and goals. "I know nothing about trading. I want to eventually trade stocks and maybe options. Build me a study plan."
2. **Concept explanations**: Ask for explanations at your level. "Explain market capitalization like I'm a complete beginner. Then give me a slightly more advanced version."
3. **Quizzing**: "Quiz me on 10 basic investing concepts. After I answer, tell me what I got right and wrong."
4. **Scenario analysis**: "If the Fed raises interest rates by 0.25%, walk me through what typically happens to bond prices, stock prices, and the dollar. Explain the chain of cause and effect."
5. **Book summaries**: "I just read Chapter 3 of 'A Random Walk Down Wall Street.' Summarize the key points and tell me which ideas are still considered valid today."
6. **Jargon decoder**: Keep a running glossary. Ask Claude to add new terms as you encounter them.

---

## 3. Building Trading Tools with Claude's Help

Each of these is a project you can build incrementally. Claude can generate the initial code, explain every line, help you debug, and iterate on features.

### 3.1 Stock Screener Script (Python)

**What it does**: Filters the universe of stocks based on criteria you define (e.g., P/E ratio below 15, revenue growth above 10%, market cap above $1B).

**Key components:**
- Data source: `yfinance`, Alpha Vantage API, or Financial Modeling Prep API
- Filtering logic: pandas DataFrame operations
- Output: CSV file, terminal table (`tabulate`), or Streamlit web app

**Beginner prompt to Claude:**
> "Write a Python script that screens all S&P 500 stocks and filters for: P/E ratio under 20, dividend yield above 2%, and market cap above $10 billion. Use yfinance. Output results as a sorted table."

**Estimated complexity**: 50-150 lines of Python. A few hours to build and test.

### 3.2 Price Alert System

**What it does**: Monitors stock prices and sends you a notification when a price crosses a threshold you set.

**Key components:**
- Price fetching: `yfinance` or a free API (polling every N minutes)
- Alert logic: compare current price to your thresholds
- Notification: email (`smtplib`), SMS (`twilio`), Slack webhook, or Discord webhook
- Scheduling: `schedule` library or system cron job

**Architecture:**
```
[Cron / Scheduler] → [Fetch Prices] → [Check Thresholds] → [Send Alert]
                                                ↓
                                     [Log to SQLite DB]
```

### 3.3 Sentiment Analysis Pipeline

**What it does**: Collects text from news sources or social media, scores sentiment (positive/negative/neutral), and tracks it over time.

**Key components:**
- Data collection: RSS feeds (`feedparser`), Twitter/X API, Reddit API (`praw`), or web scraping
- Sentiment scoring: VADER (rule-based, fast, good for financial text), FinBERT (transformer model trained on financial text), or Claude itself via API
- Storage: SQLite or PostgreSQL
- Visualization: matplotlib time series charts, Streamlit dashboard

**Levels of sophistication:**

| Level | Approach | Accuracy | Speed |
|-------|----------|----------|-------|
| Basic | VADER sentiment | ~65-70% | Very fast |
| Intermediate | FinBERT model | ~80-85% | Moderate |
| Advanced | Claude API with custom prompts | ~85-90% | Slower, costs money |

### 3.4 Automated Research Reports

**What it does**: Generates a daily or weekly report on your watchlist stocks, pulling together price changes, news summaries, and technical indicator readings.

**Key components:**
- Data fetching: price data, volume, key metrics from APIs
- News fetching: RSS feeds or news APIs (NewsAPI, Finnhub)
- Report generation: Jinja2 templates or markdown formatting
- Delivery: email, Slack, or saved as PDF
- Optional AI layer: use Claude API to write narrative summaries of the data

**Example report structure:**
```
=== Weekly Watchlist Report (2026-03-14) ===

AAPL: $187.32 (+2.1% this week)
  - RSI: 58 (neutral)
  - Above 50-day MA ($182.15)
  - News: 2 articles (sentiment: slightly positive)
  - Earnings in 32 days

MSFT: $412.87 (-0.4% this week)
  - RSI: 45 (neutral)
  - Below 50-day MA ($415.22)
  - News: 5 articles (sentiment: mixed)
  - Earnings in 18 days
```

### 3.5 Portfolio Rebalancing Calculator

**What it does**: Given your current portfolio holdings and target allocations, calculates exactly which trades to make to rebalance.

**Key components:**
- Input: current holdings (ticker, shares, current price) and target allocation percentages
- Calculation: determine current allocation, compare to target, compute trades needed
- Output: list of buy/sell orders with share counts and dollar amounts
- Optional: tax-lot awareness (sell highest-cost lots first for tax efficiency)

**Beginner prompt to Claude:**
> "Write a Python script that takes a portfolio (dictionary of ticker: shares) and target allocation (dictionary of ticker: percentage), fetches current prices, and outputs the trades needed to rebalance. Account for the case where I want to add new cash to the portfolio."

### 3.6 Prediction Market Probability Tracker

**What it does**: Monitors prediction markets (Polymarket, Kalshi, Metaculus, Manifold) and tracks how probabilities change over time.

**Key components:**
- Data source: Polymarket API, Kalshi API, or web scraping
- Storage: SQLite database with timestamps
- Visualization: probability over time charts (line charts with date on x-axis)
- Alerts: notify when a probability crosses a threshold (e.g., "election outcome drops below 40%")
- Analysis: correlate prediction market movements with news events

**Why this matters for trading**: Prediction markets are leading indicators. If the prediction market for "Fed raises rates in June" jumps from 30% to 70%, that is actionable information for bond and equity positioning.

### 3.7 Interactive Dashboard (Streamlit or Dash)

**What it does**: A web-based dashboard that brings together your watchlist, charts, news, and analysis in one place.

**Key components:**
- Framework: Streamlit (easier for beginners) or Dash (more customizable)
- Charts: plotly for interactive candlestick charts, volume bars, indicator overlays
- Widgets: stock search, date range selector, indicator toggles
- Data: real-time or near-real-time from APIs
- Deployment: run locally, or deploy to Streamlit Cloud / Render / Railway for free

**Streamlit advantages for beginners:**
- Write a dashboard in pure Python (no HTML/CSS/JS required)
- Hot-reload during development
- Free hosting on Streamlit Community Cloud
- Built-in caching for API calls

**Example Streamlit structure:**
```
app.py
├── pages/
│   ├── watchlist.py
│   ├── screener.py
│   ├── backtest.py
│   └── news.py
├── utils/
│   ├── data_fetcher.py
│   ├── indicators.py
│   └── sentiment.py
└── requirements.txt
```

### 3.8 User-Specific Tech Stacks

> **⚠️ User 1 (H1B/US):** All tools listed in sections 3.1-3.7 work as-is for US markets. Alpaca is the best API for building stock trading tools — it offers free paper trading, a clean REST API, real-time data, and easy Python integration via `alpaca-trade-api`. Start with Alpaca for any project that needs broker connectivity.

> **⚠️ User 2 (India):** Replace US-centric tools with Indian equivalents:
>
> | US Tool | Indian Replacement | Notes |
> |---------|-------------------|-------|
> | Alpaca API | Zerodha Kite Connect or Upstox API | Kite Connect costs ₹2,000/month; Upstox has a free tier |
> | `yfinance` (US data) | `jugaad-data` or `nsepy` | Free NSE/BSE historical data |
> | SEC EDGAR | BSE/NSE filings, Screener.in | Free fundamental data |
> | Alpha Vantage | MoneyControl API, Screener.in | Indian company data |
>
> **India-specific tools to build:**
> - **Nifty/Sensex tracker with technical indicators** — real-time index tracking with RSI, MACD, moving averages using NSE data feeds
> - **Indian mutual fund analyzer** — fetch NAV data from AMFI (amfiindia.com API), compare fund performance, calculate SIP returns, track expense ratios
> - **F&O options chain analyzer for NSE** — fetch live options chain data from NSE website, calculate Greeks, identify high OI strikes, track PCR (Put-Call Ratio)
> - **Smallcase portfolio builder** — create and backtest thematic portfolios similar to Smallcase, using NSE stock data
> - **IPO analysis tool (GMP tracker)** — track Grey Market Premium for upcoming IPOs, subscription data, and listing day predictions
> - **Indian crypto tax calculator** — track the 30% flat tax on crypto gains + 1% TDS on transactions above ₹10,000, generate tax reports for ITR filing

---

## 4. MCP Servers & Integrations Relevant to Trading

### 4.1 What Are MCP Servers?

MCP (Model Context Protocol) is an open protocol that lets AI assistants like Claude connect to external tools and data sources in real time. Think of MCP servers as plugins that extend what Claude can do.

Without MCP, Claude is limited to what is in its training data and what you paste into the conversation. With MCP, Claude can:

- Search the web for current information
- Query databases
- Call APIs
- Read and write files on your computer
- Interact with external services

### 4.2 MCP Integrations Relevant to Trading

| Integration | What It Enables | Trading Use Case |
|-------------|----------------|-----------------|
| **Web Search** | Search the internet in real time | Look up current stock prices, breaking news, SEC filings |
| **Web Fetch** | Retrieve and read web pages | Pull earnings reports, analyst notes, financial statements from URLs |
| **Database (SQLite/Postgres)** | Query structured data | Query your historical price database, portfolio records, trade logs |
| **File System** | Read/write local files | Access your trading scripts, update configuration files, read CSV exports |
| **API Caller** | Make HTTP requests to any API | Fetch data from Alpha Vantage, Polygon.io, Alpaca, Polymarket |
| **GitHub** | Interact with repositories | Manage your trading bot codebase, review PRs, track issues |
| **Slack/Discord** | Send messages | Deliver trading alerts to your channels |
| **Google Sheets** | Read/write spreadsheets | Update portfolio tracking sheets, pull data for analysis |
| **Notion** | Read/write Notion pages | Maintain a trading journal, research notes |

### 4.3 Building Custom MCP Servers for Market Data

You can build your own MCP server that wraps a financial data API. This lets Claude directly query market data during your conversation.

**Example: Custom stock data MCP server**

What it would expose to Claude:
- `get_stock_price(ticker)` - current or recent price
- `get_historical_prices(ticker, start_date, end_date)` - OHLCV data
- `get_fundamentals(ticker)` - P/E, market cap, revenue, etc.
- `screen_stocks(filters)` - run a screener with criteria
- `get_news(ticker, days)` - recent news articles

**Implementation approach:**
1. Write a Python MCP server using the MCP SDK
2. Inside each tool function, call a financial data API (e.g., Alpha Vantage, Polygon.io, yfinance)
3. Return structured data that Claude can reason about
4. Configure Claude Code or Claude Desktop to connect to your server

**Resources:**
- MCP specification: https://modelcontextprotocol.io
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk

### 4.4 Using Claude Code with Trading Projects

Claude Code (the CLI tool you are likely reading this from) is particularly powerful for trading projects because:

- **It can read your entire codebase**: Claude Code understands your project structure, dependencies, and existing code. When you ask it to add a feature, it knows what already exists.
- **It can run your code**: Claude Code can execute Python scripts, run tests, and see the output. This means it can help you debug in real time.
- **It can edit files**: Claude Code can directly modify your trading bot code, add new indicators, fix bugs, and refactor.
- **It persists context**: In a long coding session, Claude Code maintains context about what you have been building.
- **It can use MCP tools**: If you have MCP servers configured, Claude Code can use them to fetch live data while helping you code.

**Typical Claude Code workflow for a trading project:**
1. Start Claude Code in your project directory
2. Ask it to review your existing code and suggest improvements
3. Describe a new feature you want (e.g., "add RSI indicator to my screener")
4. Claude Code writes the code, you review it, it commits
5. Ask Claude Code to run the backtest and interpret results
6. Iterate until you are satisfied

---

## 5. Automation Possibilities

Automation is where the real leverage comes in. Once you have built tools manually and understand what they do, you can automate them to run on schedules.

### 5.1 Scheduled Research Reports

**Setup:**
- Write a Python script that fetches data and generates a report (see Section 3.4)
- Schedule it with cron (Linux/Mac) or Task Scheduler (Windows)
- Optionally use Claude API to add narrative analysis

**Cron example (runs every weekday at 7:00 AM before market open):**
```
0 7 * * 1-5 /usr/bin/python3 /path/to/daily_report.py
```

**Cloud alternatives:**
- GitHub Actions (free for public repos, generous free tier for private)
- AWS Lambda + EventBridge (pay per execution, very cheap)
- Railway or Render cron jobs

### 5.2 Alert Systems When Conditions Are Met

**Types of alerts you can build:**

| Alert Type | Trigger | Example |
|-----------|---------|---------|
| Price threshold | Price crosses above/below a level | "AAPL crosses above $200" |
| Technical indicator | RSI, MACD, or moving average signal | "RSI drops below 30 (oversold)" |
| Volume spike | Volume exceeds N times the average | "TSLA volume 3x its 20-day average" |
| Earnings approaching | Days until earnings < threshold | "MSFT earnings in 5 days" |
| News sentiment | Sentiment score drops sharply | "Negative news spike for NVDA" |
| Prediction market shift | Probability moves more than X% | "Fed rate cut probability jumps 15% in one day" |
| Portfolio drift | Allocation drifts beyond target | "Tech allocation now 45%, target is 35%" |

**Notification channels (easiest to hardest to set up):**
1. **Discord webhook**: Free, 5 minutes to set up, just POST JSON to a URL
2. **Slack webhook**: Free, similar to Discord
3. **Email (Gmail SMTP)**: Free, requires app password setup
4. **SMS (Twilio)**: ~$0.0079 per message, requires account
5. **Push notification (Pushover)**: $5 one-time, very clean mobile notifications
6. **Telegram bot**: Free, requires creating a bot via BotFather

> **⚠️ User 2 (India):** Scheduled reports and alerts should use Indian market data and timing. Key alerts to set up:
> - **NSE/BSE market open/close** — Indian markets open at 9:15 AM IST and close at 3:30 PM IST (Monday-Friday). Pre-market session runs 9:00-9:08 AM IST.
> - **Quarterly results of watchlist companies** — Indian companies report quarterly results; track dates via BSE/NSE corporate announcements
> - **RBI policy announcements** — Reserve Bank of India monetary policy decisions (bi-monthly) directly affect Nifty, banking stocks, and bond yields
> - **Nifty VIX spikes** — India VIX above 20 signals high fear; set alerts for sudden spikes
> - **Mutual fund NAV changes** — track daily NAV updates for your mutual fund holdings (NAVs are published by 11 PM IST)
>
> **Important timing note:** Indian market hours (9:15 AM - 3:30 PM IST, Mon-Fri) do not overlap with US market hours (9:30 AM - 4:00 PM ET). If you schedule cron jobs, use IST-based schedules. Example:
> ```
> 15 9 * * 1-5 /usr/bin/python3 /path/to/market_open_report.py   # 9:15 AM IST
> 30 15 * * 1-5 /usr/bin/python3 /path/to/market_close_report.py  # 3:30 PM IST
> ```

### 5.3 Automated Portfolio Tracking

**What to track:**
- Daily portfolio value and change
- Individual position P&L (unrealized and realized)
- Asset allocation percentages vs. targets
- Dividend income received
- Transaction history and cost basis
- Performance vs. benchmarks (S&P 500, total market)

**Storage options:**

| Option | Complexity | Best For |
|--------|-----------|----------|
| CSV files | Simplest | Getting started, <20 positions |
| SQLite database | Low | Local-only, moderate data |
| PostgreSQL | Medium | Multi-device access, large data |
| Google Sheets API | Medium | Visual, shareable, mobile-friendly |
| Notion database | Low-Medium | If you already use Notion |

### 5.4 News Monitoring and Filtering

**Architecture:**
```
[RSS Feeds / News APIs] → [Fetch & Deduplicate] → [Relevance Filter] → [Sentiment Score]
                                                                              ↓
                                                                    [Store in DB]
                                                                              ↓
                                                              [Alert if threshold met]
```

**News sources (free or cheap):**
- RSS feeds from Reuters, Bloomberg, CNBC, MarketWatch
- NewsAPI.org (free tier: 100 requests/day, 1-month-old articles)
- Finnhub (free tier: 60 API calls/minute, real-time news)
- Reddit (r/wallstreetbets, r/stocks, r/investing) via `praw`
- SEC EDGAR RSS feeds for new filings

### 5.5 Social Media Sentiment Tracking

**Platforms to monitor:**

| Platform | API Access | Cost | Data Quality |
|----------|-----------|------|-------------|
| Reddit | Free (PRAW) | Free | High for retail sentiment |
| Twitter/X | Paid (Basic: $100/mo) | Expensive | High but noisy |
| StockTwits | Free API | Free | Moderate, trading-focused |
| YouTube comments | Free (YouTube Data API) | Free | Low signal-to-noise |
| Discord servers | Bot access | Free | Variable |

**What to measure:**
- Volume of mentions (is chatter increasing?)
- Sentiment polarity (positive vs. negative)
- Unusual activity (sudden spike in mentions)
- Key influencer posts (accounts with large followings)

### 5.6 Prediction Market Monitoring

**Markets to track:**
- **Polymarket**: Crypto-based, largest volume, political and economic events
- **Kalshi**: US-regulated, economic events, weather, Fed decisions
- **Metaculus**: Community forecasting, longer-term questions
- **Manifold Markets**: Play money, wide range of questions, good for practice

**Automation ideas:**
- Track all markets related to "Federal Reserve" and chart probability over time
- Alert when a market's probability changes by more than 10% in 24 hours
- Cross-reference prediction market probabilities with options-implied probabilities
- Build a "prediction market dashboard" showing probabilities for events that affect your portfolio

---

## 6. A Beginner's Roadmap

This roadmap is sequential. Do not skip phases. Each phase builds on the previous one. Because the two users have different markets, regulations, and starting points, there are two separate roadmaps below.

### **⚠️ User 1 (H1B/US) Roadmap**

| Phase | Timeline | Focus |
|-------|----------|-------|
| 1. Learn | Weeks 1-4 | US market fundamentals, use Claude as tutor |
| 2. Practice | Weeks 5-8 | Paper trade on Alpaca or Webull |
| 3. Build | Weeks 9-12 | Stock screener, price alerts using US APIs |
| 4. Develop | Months 4-6 | Backtest strategies, learn technical analysis |
| 5. Small Live | Months 6-9 | Small capital ($500-$1000), strict risk management |
| 6. Automate | Months 9-12 | Trading bots via Alpaca API |
| 7. Expand | Month 12+ | Prediction markets (Kalshi), options, crypto |

**Phase details:**

**Phase 1 (Weeks 1-4): Learn US Market Fundamentals**
- Read "The Intelligent Investor" by Benjamin Graham (or ask Claude to summarize each chapter)
- Learn basic financial statement analysis (income statement, balance sheet, cash flow statement)
- Understand order types (market, limit, stop, stop-limit)
- Learn what drives stock prices (earnings, interest rates, sentiment, supply/demand)
- Learn about different asset classes (stocks, bonds, ETFs, options, crypto, prediction markets)
- Ask Claude to explain H1B-specific considerations for trading (passive income is fine, active business is not)

**Phase 2 (Weeks 5-8): Paper Trading**
- Open a paper trading account on Alpaca (alpaca.markets) or Webull
- Start analyzing 2-3 US companies per week using the research workflow from Section 2.1
- Make paper trades and track them in a spreadsheet
- Keep a trading journal: write down why you entered and exited each trade

**Phase 3 (Weeks 9-12): Build Tools**
- Build a stock screener for S&P 500 stocks using `yfinance`
- Build a price alert system with Discord/Slack notifications
- Build a portfolio tracker that calculates P&L and allocation

**Phase 4 (Months 4-6): Backtest Strategies**
- Learn common strategies: trend following, mean reversion, momentum
- Code a backtester with Claude's help using `backtrader` or `vectorbt`
- Run against 10+ years of historical US data
- Analyze results: Sharpe ratio, maximum drawdown, win rate

**Phase 5 (Months 6-9): Small Live Trading**
- Start with $500-$1,000 you can 100% afford to lose
- Set maximum loss limits (1-2% per trade, 5% per week)
- Use limit orders, not market orders
- Continue paper trading alongside live trading

**Phase 6 (Months 9-12): Automate**
- Deploy strategy to a cloud server (AWS, Railway)
- Connect to Alpaca API for live trading
- Implement kill switches and monitoring
- Start with tiny position sizes

**Phase 7 (Month 12+): Expand**
- Prediction markets via Kalshi (US-regulated, legal for H1B holders)
- Options strategies (covered calls, cash-secured puts)
- Crypto trading (track tax implications carefully)
- Consider index fund investing alongside active trading

**Key notes for User 1:**
- All trading profits go on your US tax return (Form 1040, Schedule D, Form 8949)
- Track FBAR (FinCEN 114) if aggregate balance across all Indian bank accounts exceeds $10,000 at any point during the year
- Track FATCA (Form 8938) if Indian financial assets exceed reporting thresholds
- Do not let trading activity look like a business — H1B restricts you to employment with your sponsoring employer. Passive investment income is fine; running a trading operation that looks like self-employment is not. Keep it clearly passive.
- Consult an immigration attorney if trading income becomes significant relative to your salary

---

### **⚠️ User 2 (India) Roadmap**

| Phase | Timeline | Focus |
|-------|----------|-------|
| 1. Learn | Weeks 1-4 | Zerodha Varsity (free, comprehensive), use Claude |
| 2. Practice | Weeks 5-8 | Paper trade on TradingView, StockMock |
| 3. Open Account | Week 9 | Open Zerodha/Groww account (₹0-300, need PAN + Aadhaar) |
| 4. Build | Weeks 10-14 | NSE stock screener, Nifty tracker using Python |
| 5. Small Live | Months 4-6 | Start with ₹5,000-₹10,000, equity delivery trades only |
| 6. Learn F&O | Months 6-9 | Understand options, futures (Varsity Module 5+) |
| 7. Automate | Months 9-12 | Build bots with Kite Connect API |
| 8. Expand | Month 12+ | US stocks via LRS, prediction market skills via Manifold |

**Phase details:**

**Phase 1 (Weeks 1-4): Learn Indian Market Fundamentals**
- Complete Zerodha Varsity modules 1-4 (free at zerodha.com/varsity) — this is the best free resource for Indian markets
- Use Claude to clarify concepts, create quizzes, and explain jargon
- Learn about NSE, BSE, SEBI, NSDL/CDSL (depositories), and how Indian markets work
- Understand Indian order types, market segments (equity, F&O, currency, commodity)
- Learn about Nifty 50, Sensex, and sectoral indices

**Phase 2 (Weeks 5-8): Paper Trading**
- Use TradingView (free) to practice chart reading and virtual trading
- Use StockMock or Neostox for Indian market paper trading simulators
- Analyze 2-3 Indian companies per week using Screener.in data
- Track paper trades in a spreadsheet with entry/exit reasons

**Phase 3 (Week 9): Open a Brokerage Account**
- Open a Zerodha or Groww account — requirements: PAN card + Aadhaar card
- Zerodha charges ₹200 account opening (sometimes free promotions); Groww is free
- Complete KYC verification (typically 1-2 days)
- Link your bank account for fund transfers via UPI or net banking

**Phase 4 (Weeks 10-14): Build Tools**
- Build an NSE stock screener using `jugaad-data` or `nsepy` for data
- Build a Nifty/Sensex tracker with technical indicators
- Build a mutual fund NAV tracker using AMFI data
- Build price alert system for Indian stocks

**Phase 5 (Months 4-6): Small Live Trading**
- Start with ₹5,000-₹10,000 in equity delivery trades only (safest, no leverage)
- Equity delivery: you buy and hold shares in your demat account
- Avoid intraday trading and F&O at this stage
- Set maximum loss limits (1-2% per trade)
- Focus on large-cap Nifty 50 stocks initially

**Phase 6 (Months 6-9): Learn F&O**
- Complete Zerodha Varsity Module 5 (Options Theory) and Module 6 (Option Strategies)
- Understand lot sizes, margin requirements, and expiry cycles
- Paper trade options strategies before using real money
- Learn about Nifty weekly and monthly expiry dynamics
- Understand the risks: F&O is where most retail traders lose money in India

**Phase 7 (Months 9-12): Automate**
- Subscribe to Zerodha Kite Connect API (₹2,000/month) or Upstox API
- Build automated trading bots in Python
- Implement risk management and kill switches
- Start with tiny position sizes in live markets

**Phase 8 (Month 12+): Expand**
- Invest in US stocks via LRS (Liberalized Remittance Scheme — up to $250,000/year) through platforms like INDmoney, Vested, or Groww
- Build prediction market analysis skills using Manifold Markets (play money — real-money prediction markets are mostly illegal in India)
- Explore crypto (30% tax + 1% TDS — factor into strategy)
- Consider systematic investment plans (SIPs) in index funds alongside active trading

**Key notes for User 2:**
- Start with equity delivery trades (safest). Long-term capital gains (LTCG) on equity held >1 year are taxed at 10% above ₹1 lakh per year. Short-term capital gains (STCG) on equity held <1 year are taxed at 15%.
- Avoid F&O until you are comfortable with equity trading — over 90% of retail F&O traders in India lose money (per SEBI study).
- Crypto gains are taxed at a flat 30% with no deduction for losses against other income. 1% TDS applies on transactions above ₹10,000. Factor this into any crypto strategy.
- Being unemployed: use trading as a skill-building exercise first. Start with minimal capital. The goal is to learn, not to generate immediate income. Build tools and skills that are valuable whether or not trading itself becomes profitable.
- Must file ITR (Income Tax Return) if total income including trading income exceeds ₹2.5 lakh, even if unemployed.

---

## 7. Project Ideas to Build

Here are concrete project ideas ranked by difficulty, with enough detail to get started.

### 7.1 Stock Watchlist Tracker with Alerts

**Difficulty**: Beginner
**Time to build**: 2-4 hours
**What you'll learn**: API calls, data formatting, notifications

**Features:**
- Maintain a list of tickers in a YAML or JSON config file
- Fetch current prices and daily change percentages
- Display in a formatted terminal table
- Send an alert if any stock moves more than X% in a day
- Run via cron every 30 minutes during market hours

**Tech stack**: Python, `yfinance`, `tabulate`, Discord/Slack webhook

### 7.2 Earnings Analysis Tool

**Difficulty**: Beginner-Intermediate
**Time to build**: 4-8 hours
**What you'll learn**: Financial data APIs, data analysis, reporting

**Features:**
- Input a ticker, get a comprehensive earnings overview
- Show last 8 quarters of EPS (actual vs. estimate, beat/miss)
- Show revenue trend
- Pull the earnings call transcript and summarize key themes (using Claude API)
- Chart earnings surprise history
- Track upcoming earnings dates for your watchlist

**Tech stack**: Python, Financial Modeling Prep API or Alpha Vantage, `matplotlib`, optionally Claude API

### 7.3 Polymarket Probability Tracker

**Difficulty**: Intermediate
**Time to build**: 6-10 hours
**What you'll learn**: API integration, time-series data, charting

**Features:**
- Track selected Polymarket markets
- Store probability snapshots every hour in SQLite
- Chart probability over time for each market
- Calculate rate of change (is probability moving faster than usual?)
- Alert on large probability swings (>10% in 24 hours)
- Dashboard showing all tracked markets with mini-charts

**Tech stack**: Python, Polymarket API, SQLite, `plotly`, `streamlit`

### 7.4 Simple Moving Average Crossover Bot (Paper Trading)

**Difficulty**: Intermediate
**Time to build**: 8-15 hours
**What you'll learn**: Strategy implementation, backtesting, broker API, risk management

**Features:**
- Implement 50/200 SMA crossover strategy
- Backtest against 10+ years of S&P 500 data
- Paper trade using Alpaca's paper trading API
- Log every signal and trade with timestamps
- Calculate running P&L and compare to buy-and-hold
- Send daily summary report

**Tech stack**: Python, `backtrader` or `vectorbt`, `alpaca-trade-api`, SQLite

### 7.5 News Aggregator with Sentiment Scoring

**Difficulty**: Intermediate
**Time to build**: 10-15 hours
**What you'll learn**: NLP, web scraping, data pipelines, sentiment analysis

**Features:**
- Aggregate news from 3+ sources (RSS feeds, NewsAPI, Finnhub)
- Deduplicate articles (same story from different sources)
- Score sentiment using VADER and/or FinBERT
- Store articles and scores in a database
- Track sentiment trends per ticker over time
- Alert when sentiment drops sharply for a watchlist stock
- Web dashboard to browse articles sorted by relevance and sentiment

**Tech stack**: Python, `feedparser`, `vaderSentiment`, `transformers` (FinBERT), SQLite, `streamlit`

### 7.6 Portfolio Performance Dashboard

**Difficulty**: Intermediate
**Time to build**: 10-15 hours
**What you'll learn**: Portfolio analytics, benchmarking, visualization

**Features:**
- Import trades from CSV or broker API
- Calculate time-weighted and money-weighted returns
- Compare performance to benchmarks (S&P 500, total market, 60/40 portfolio)
- Show asset allocation pie chart
- Display individual position P&L (realized and unrealized)
- Chart portfolio value over time
- Calculate risk metrics (Sharpe ratio, Sortino ratio, maximum drawdown, beta)
- Generate monthly performance reports

**Tech stack**: Python, `pandas`, `plotly`, `streamlit`, `yfinance` (for benchmark data)

### 7.7 Options Chain Analyzer

**Difficulty**: Advanced
**Time to build**: 15-25 hours
**What you'll learn**: Options pricing, Greeks, implied volatility, advanced data visualization

**Features:**
- Fetch options chain data for any ticker
- Display calls and puts with strike prices, premiums, volume, open interest
- Calculate and display Greeks (delta, gamma, theta, vega)
- Chart implied volatility smile/skew
- Identify unusual options activity (high volume relative to open interest)
- Calculate profit/loss diagrams for multi-leg strategies
- Alert on implied volatility rank extremes

**Tech stack**: Python, `yfinance` or `polygon.io`, `scipy` (for Black-Scholes), `plotly`, `streamlit`

### 7.8 Crypto Arbitrage Scanner

**Difficulty**: Advanced
**Time to build**: 15-25 hours
**What you'll learn**: Exchange APIs, real-time data, latency, execution

**Features:**
- Monitor prices on multiple exchanges simultaneously (Binance, Coinbase, Kraken, etc.)
- Identify price discrepancies for the same asset across exchanges
- Calculate arbitrage profit after fees (trading fees, withdrawal fees, network fees)
- Factor in transfer times (some "arbitrage" disappears before you can execute)
- Alert on profitable opportunities above a threshold
- Log all identified opportunities with timestamps for analysis
- **Paper mode only first** -- do not execute real trades until extensively tested

**Tech stack**: Python, `ccxt` (unified exchange API), `asyncio` (for concurrent price fetching), SQLite, websockets

**Warning**: Crypto arbitrage is extremely competitive. By the time you see an opportunity, professional firms with co-located servers have already taken it. This project is valuable for learning, but unlikely to be profitable at small scale.

### 7.9 India-Specific Project Ideas (User 2)

> **⚠️ User 2 (India):** The following projects are tailored for Indian markets and can be built using free or low-cost data sources.

**7.9.1 NSE Options Chain Analyzer**
- **Difficulty**: Intermediate
- **Time to build**: 10-15 hours
- **Data source**: Free options chain data from the NSE website (nseindia.com)
- **Features**: Fetch live options chain for Nifty/BankNifty/stocks, display strike-wise OI and volume, calculate PCR (Put-Call Ratio), identify max pain strike, track OI changes between sessions, chart IV smile
- **Tech stack**: Python, `requests` (with proper headers for NSE), `pandas`, `plotly`, `streamlit`

**7.9.2 Indian Mutual Fund SIP Calculator and Tracker**
- **Difficulty**: Beginner-Intermediate
- **Time to build**: 6-10 hours
- **Data source**: AMFI API (amfiindia.com — free, official NAV data for all Indian mutual funds)
- **Features**: Calculate SIP returns for any fund over any period, compare funds by category, track your SIP portfolio value, calculate XIRR returns, show expense ratio impact over time, alert on significant NAV changes
- **Tech stack**: Python, `requests`, `pandas`, `streamlit`

**7.9.3 Nifty/BankNifty Technical Indicator Dashboard**
- **Difficulty**: Intermediate
- **Time to build**: 8-12 hours
- **Data source**: `jugaad-data` or NSE historical data
- **Features**: Real-time Nifty/BankNifty/Sensex charts with RSI, MACD, Bollinger Bands, moving averages, support/resistance levels, volume analysis, India VIX overlay
- **Tech stack**: Python, `pandas-ta`, `plotly`, `streamlit`

**7.9.4 Indian IPO Analyzer (GMP Tracker)**
- **Difficulty**: Intermediate
- **Time to build**: 8-12 hours
- **Data source**: Web scraping from IPO-focused websites, BSE/NSE for subscription data
- **Features**: Track Grey Market Premium (GMP) for upcoming IPOs, show subscription data by category (retail, NII, QIB), historical listing day performance vs. GMP, IPO calendar with key dates, allotment probability calculator
- **Tech stack**: Python, `beautifulsoup4`, `requests`, SQLite, `streamlit`

**7.9.5 Crypto Tax Calculator for India (30% Tax + 1% TDS)**
- **Difficulty**: Intermediate
- **Time to build**: 10-15 hours
- **Data source**: Exchange APIs (WazirX, CoinDCX, Binance) or CSV exports
- **Features**: Import trades from Indian crypto exchanges, calculate gains/losses per transaction, apply 30% flat tax (no loss offset against other income), track 1% TDS on transactions above ₹10,000, generate tax report for ITR filing, handle crypto-to-crypto swaps as taxable events
- **Tech stack**: Python, `ccxt` or exchange-specific APIs, `pandas`, `streamlit`

**7.9.6 Zerodha Kite Connect Trading Bot**
- **Difficulty**: Advanced
- **Time to build**: 15-25 hours
- **Data source**: Kite Connect API (₹2,000/month subscription)
- **Features**: Implement a simple strategy (e.g., moving average crossover on Nifty stocks), place orders via Kite Connect, manage positions and risk limits, comprehensive logging, dashboard for monitoring, kill switch for maximum loss
- **Tech stack**: Python, `kiteconnect` library, SQLite, `streamlit`

**7.9.7 Indian Earnings Calendar + Results Analyzer**
- **Difficulty**: Intermediate
- **Time to build**: 8-12 hours
- **Data source**: BSE/NSE corporate announcements, MoneyControl, Trendlyne
- **Features**: Track quarterly results dates for watchlist companies, auto-fetch results when published, compare actual vs. estimated numbers, track revenue/profit growth trends, alert before earnings dates, summarize results using Claude API
- **Tech stack**: Python, `beautifulsoup4`, `requests`, SQLite, `streamlit`

---

## 8. Important Disclaimers

Read these carefully. They are not boilerplate. Ignoring them is the most common way beginners lose money.

### 8.1 AI Is Not a Crystal Ball

Claude, GPT, and every other AI model cannot predict the future. They can analyze data, identify patterns, and explain concepts, but the market is a complex adaptive system with millions of participants. No model captures all the variables that drive prices. If someone tells you their AI can predict stock prices with 90% accuracy, they are either lying, overfitting, or selling you something.

### 8.2 Past Performance Does Not Guarantee Future Results

This is the most important sentence in finance and it is not a cliche. A strategy that returned 40% per year in backtesting might lose 40% in the next year. Reasons include:

- **Overfitting**: The strategy was tuned to fit historical data and does not generalize
- **Regime change**: Market conditions have changed (e.g., rising vs. falling interest rates)
- **Crowding**: Too many people discovered the same strategy, eliminating the edge
- **Survivorship bias**: Your backtest only included companies that survived, not the ones that went bankrupt
- **Transaction costs**: Backtests often underestimate slippage, fees, and market impact

### 8.3 Start with Paper Trading

There is zero reason to risk real money while you are still learning. Paper trading:

- Costs nothing
- Teaches you the mechanics of placing orders
- Lets you test strategies in real time
- Builds emotional discipline (though real money adds a psychological dimension paper trading cannot simulate)

Most brokers offer paper trading accounts: Alpaca, TD Ameritrade/Schwab, Webull, Interactive Brokers.

### 8.4 Never Risk Money You Cannot Afford to Lose

This is not motivational advice. It is risk management. Before trading with real money, answer these questions:

- If I lose 100% of this money tomorrow, does it affect my ability to pay rent, buy food, or meet financial obligations?
- Am I taking on debt (credit cards, loans) to fund trading?
- Am I using money earmarked for emergencies, education, or retirement?

If the answer to any of these is yes, you are not ready to trade with real money.

### 8.5 Regulatory Requirements

**United States:**
- **Pattern Day Trader (PDT) rule**: If you make 4+ day trades in 5 business days in a margin account, you need at least $25,000 in your account. This does not apply to cash accounts, but cash accounts have settlement delays (T+1 for stocks).
- **FINRA and SEC oversight**: Brokers are regulated. Use a reputable, regulated broker.
- **Accredited investor requirements**: Some investments (certain hedge funds, private placements) require you to be an accredited investor ($200K+ annual income or $1M+ net worth excluding primary residence).

**Prediction markets:**
- **Polymarket**: Not available to US residents (crypto-based, offshore)
- **Kalshi**: Available to US residents, CFTC-regulated
- **Manifold**: Play money, no real financial risk

**Crypto:**
- Regulations vary by state and are changing rapidly
- Some states require money transmitter licenses for exchanges
- DeFi operates in a regulatory gray area

### 8.6 Tax Obligations

Trading creates tax events. In the US:

| Event | Tax Treatment |
|-------|--------------|
| Short-term capital gains (held < 1 year) | Taxed as ordinary income (10-37%) |
| Long-term capital gains (held > 1 year) | Taxed at 0%, 15%, or 20% depending on income |
| Dividends (qualified) | Taxed at long-term capital gains rates |
| Dividends (non-qualified) | Taxed as ordinary income |
| Wash sale rule | Cannot deduct a loss if you buy the same security within 30 days before/after selling |
| Crypto | Every trade is a taxable event (including crypto-to-crypto swaps) |
| Prediction markets | Taxed as ordinary income in most cases |

**Record-keeping requirements:**
- Track every trade: date, ticker, buy/sell, shares, price, fees
- Your broker provides Form 1099-B at year end, but it may not capture everything (especially crypto)
- Consider using tax software like TurboTax, H&R Block, or crypto-specific tools like CoinTracker or Koinly
- If your trading is complex, hire a CPA who understands trading taxes

### 8.7 Emotional and Psychological Risks

Trading affects your psychology in ways paper trading cannot fully prepare you for:

- **Loss aversion**: Losses feel roughly 2x worse than equivalent gains feel good. This leads to holding losers too long and selling winners too early.
- **FOMO (Fear of Missing Out)**: Seeing others profit makes you take impulsive trades.
- **Revenge trading**: After a loss, you increase position size to "make it back." This is how small losses become catastrophic losses.
- **Overconfidence after wins**: A few wins can make you think you have figured out the market. You have not. Nobody has.
- **Addiction**: The variable-reward nature of trading can trigger addictive behavior patterns similar to gambling.

**Mitigation strategies:**
- Set strict rules and follow them (maximum loss per trade, per day, per week)
- Take breaks after large wins or losses
- Keep a trading journal and review it honestly
- If trading is causing anxiety, sleep problems, or relationship issues, stop

### 8.8 User-Specific Legal, Tax, and Regulatory Notes

> **⚠️ User 1 (H1B/US):**
> - **H1B and trading**: H1B holders can legally invest in stocks, options, crypto, and prediction markets as passive investment activity. However, you must ensure trading activity remains clearly passive. If trading income becomes very large relative to your employment income, or if you are spending significant work hours trading, it could be characterized as unauthorized business activity. Consult an immigration attorney if trading income becomes significant.
> - **FBAR (FinCEN 114)**: If you have Indian bank accounts (savings, FDs, NRE/NRO accounts) and the aggregate balance across all foreign financial accounts exceeds $10,000 at any point during the calendar year, you must file FBAR. This is a separate filing from your tax return, due April 15 (auto-extended to October 15). Penalties for non-filing are severe ($10,000+ per violation).
> - **FATCA (Form 8938)**: If your foreign financial assets exceed $50,000 at year-end (or $75,000 at any point during the year for single filers), you must report them on Form 8938, filed with your tax return.
> - **Tax treaty**: The US-India tax treaty may affect how certain types of income are taxed. Consult a CPA familiar with cross-border taxation.
> - **State taxes**: Some states (California, New York) have additional capital gains taxes. Factor this into your returns calculations.

> **⚠️ User 2 (India):**
> - **SEBI Registration**: SEBI (Securities and Exchange Board of India) registration is required to provide paid investment advice in India. Do not start a "stock tip" service, paid Telegram group, or advisory newsletter without obtaining SEBI Registered Investment Adviser (RIA) or Research Analyst (RA) registration. Penalties for unregistered advisory are severe (up to ₹25 crore or imprisonment).
> - **F&O tax audit**: If your F&O turnover (calculated as sum of absolute profits and losses on each trade) exceeds ₹10 crore in a financial year, a tax audit under Section 44AB is mandatory. Below this threshold, if you declare less than 6% of turnover as profit, audit may still apply. Consult a CA (Chartered Accountant).
> - **Prediction markets**: Real-money prediction markets are mostly illegal in India under the Public Gambling Act and various state gambling laws. Polymarket, Kalshi, and similar platforms are not accessible or legal for Indian residents. Use play-money alternatives like Manifold Markets to build forecasting skills without legal risk.
> - **ITR filing when unemployed**: Even if you are unemployed, you must file an Income Tax Return (ITR) if your total income (including trading income — capital gains, F&O profits, dividends, interest) exceeds ₹2.5 lakh in a financial year. F&O income is treated as business income, not capital gains.
> - **Crypto regulation**: As of now, crypto is legal to hold and trade in India but faces a 30% flat tax on gains (no loss offset against other income, no deduction for expenses except cost of acquisition) and 1% TDS on transactions above ₹10,000. Crypto losses cannot be set off against any other income, including other crypto gains from a different asset. Each crypto asset's gains/losses are calculated independently.
> - **LRS for US investing**: If you want to invest in US stocks later, you can remit up to $250,000 per financial year under the Liberalized Remittance Scheme. TCS (Tax Collected at Source) of 20% applies on LRS remittances above ₹7 lakh, but this is adjustable against your income tax liability.

---

## 9. Recommended Free and Low-Cost Resources

### Data APIs

| Provider | Free Tier | Best For |
|----------|-----------|----------|
| Yahoo Finance (`yfinance`) | Unlimited (unofficial) | Historical prices, basic fundamentals |
| Alpha Vantage | 25 requests/day | Historical and intraday data, technical indicators |
| Finnhub | 60 calls/min | Real-time quotes, news, earnings |
| Polygon.io | 5 API calls/min (free) | Detailed market data, options |
| FRED (Federal Reserve) | Unlimited | Economic data (GDP, unemployment, inflation, rates) |
| Financial Modeling Prep | 250 requests/day | Fundamentals, financial statements |
| Alpaca | Generous free tier | Real-time and historical data, paper trading, live trading |
| CoinGecko | 10-30 calls/min | Crypto prices and data |

### Python Libraries

| Library | Purpose |
|---------|---------|
| `yfinance` | Fetch stock data from Yahoo Finance |
| `pandas` | Data manipulation and analysis |
| `numpy` | Numerical computing |
| `matplotlib` / `plotly` | Charting and visualization |
| `backtrader` | Backtesting trading strategies |
| `vectorbt` | Vectorized backtesting (faster than backtrader) |
| `ta` / `pandas-ta` | Technical indicators |
| `streamlit` | Build web dashboards in Python |
| `alpaca-trade-api` | Connect to Alpaca brokerage |
| `ccxt` | Unified crypto exchange API |
| `praw` | Reddit API wrapper |
| `feedparser` | Parse RSS feeds |
| `vaderSentiment` | Rule-based sentiment analysis |
| `transformers` | Hugging Face models (FinBERT for financial sentiment) |
| `schedule` | Job scheduling |
| `sqlite3` | Built-in database |

### Books (Start Here)

1. **"The Intelligent Investor" by Benjamin Graham** -- the foundational text on value investing
2. **"A Random Walk Down Wall Street" by Burton Malkiel** -- why most active trading underperforms index investing (important to understand even if you choose to trade)
3. **"Trading in the Zone" by Mark Douglas** -- trading psychology
4. **"Quantitative Trading" by Ernest Chan** -- introduction to systematic trading
5. **"Python for Finance" by Yves Hilpisch** -- technical reference for building financial tools in Python

---

## 10. Quick-Start: Your First Week

If you have read this far and want to start immediately, here is a concrete plan for your first 7 days:

**Day 1: Set up your environment**
- Install Python 3.11+ and VS Code
- Install Claude Code (CLI)
- Create a project folder for your trading tools
- Install key libraries: `pip install yfinance pandas matplotlib streamlit`

**Day 2: Learn the basics with Claude**
- Ask Claude: "Explain the stock market to me like I'm a complete beginner. Cover: what stocks are, how prices are determined, what a broker does, and what common order types exist."
- Ask Claude: "Create a glossary of the 30 most important trading terms a beginner needs to know."

**Day 3: Fetch your first data**
- Ask Claude to write a Python script that fetches 1 year of daily price data for AAPL, MSFT, and GOOGL and plots them on a chart
- Run the script. Look at the chart. Ask Claude to explain what you see.

**Day 4: Build a simple watchlist**
- Ask Claude to write a script that takes a list of tickers, fetches current prices, calculates daily change, and displays a formatted table
- Add 10 stocks you are interested in

**Day 5: Open a paper trading account**
- Sign up for Alpaca (alpaca.markets) -- it is free and beginner-friendly
- Place your first paper trade manually through their web interface
- Ask Claude to explain what happened when you placed the trade

**Day 6: Analyze a company**
- Pick one company you are interested in
- Go to SEC EDGAR and download their latest 10-K
- Paste the financial statements section into Claude and ask for an analysis
- Ask Claude to compare the company's metrics to its competitors

**Day 7: Plan your next steps**
- Review what you learned this week
- Identify your biggest knowledge gaps
- Ask Claude to create a personalized study plan for the next 4 weeks
- Start a trading journal (even for paper trades)

---

*This document is for educational and informational purposes only. It does not constitute financial advice. Trading and investing involve risk of loss. Consult a qualified financial advisor before making investment decisions.*
