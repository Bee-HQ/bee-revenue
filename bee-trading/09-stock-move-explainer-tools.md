# Stock Move Explainer Tools: Comprehensive Research

> **Goal:** Find tools, APIs, platforms, and open-source projects that answer "WHY did stock X move?" — not just raw news, but categorized, structured explanations like "NVDA dropped 5% because earnings missed expectations."

## User Profiles

- **User 1 (H1B/US):** Indian citizen on H1B visa, employed in US. Interested in US stock market (NYSE/NASDAQ). Can use US-based paid services. Must comply with H1B employment restrictions (passive investing is fine, active day trading may raise questions).
- **User 2 (India):** Indian citizen in India, unemployed. Interested in Indian stock market (NSE/BSE) and possibly US markets via international brokers. Budget-conscious; prefers free or low-cost tools.

---

## Table of Contents

1. [Commercial "Why Is It Moving" Tools](#1-commercial-why-is-it-moving-tools)
2. [APIs That Provide Categorized Stock Move Reasons](#2-apis-that-provide-categorized-stock-move-reasons)
3. [Open-Source Projects on GitHub](#3-open-source-projects-on-github)
4. [MCP Servers and Claude Integrations](#4-mcp-servers-and-claude-integrations)
5. [Indian Market Tools (NSE/BSE)](#5-indian-market-tools-nsebse)
6. [Reddit/Community Sentiment Tools](#6-redditcommunity-sentiment-tools)
7. [Comparison Matrix](#7-comparison-matrix)
8. [Recommendations by User Profile](#8-recommendations-by-user-profile)
9. [Build-Your-Own Approach](#9-build-your-own-approach)

---

## 1. Commercial "Why Is It Moving" Tools

### 1.1 Benzinga Pro — "Why Is It Moving" (WIIM)

- **URL:** https://www.benzinga.com/pro/
- **What it does:** The gold standard for "why did stock X move" in the US market. Benzinga Pro's WIIM feature provides real-time, human-written explanations for significant stock price movements. When a stock makes a big move, Benzinga's editorial team writes a short blurb explaining the catalyst (e.g., "NVDA +8% — earnings beat expectations, raised guidance").
- **How it categorizes reasons:** Categories include earnings beats/misses, FDA approvals/rejections, M&A announcements, analyst upgrades/downgrades, insider buying/selling, management changes, product launches, legal/regulatory events, and macroeconomic impacts.
- **Key features:**
  - Streaming real-time newsfeed (fastest in the industry)
  - Audio squawk for breaking news
  - Sentiment indicators (positive/negative tags on stories)
  - Custom keyword and ticker filters
  - Movers scanner showing biggest movers with attached reasons
  - Email and mobile alerts
- **Pricing:**
  - Free trial: $0
  - Benzinga Pro Essential Monthly: $147/month
  - Benzinga Pro Essential Annual: $1,404/year (~$117/month)
- **API availability:** Yes, via Benzinga Cloud (see API section below). The WIIM data is available programmatically through the `/get-wiims` endpoint.
- **Reliability:** High. Industry standard for real-time stock move explanations. Used by professional traders, brokerages, and fintech companies. Human-curated content ensures quality.
- **User 1 (H1B/US):** Excellent choice. The primary tool for this use case in the US.
- **User 2 (India):** Expensive for Indian budget. US-market focused. Not ideal for NSE/BSE.

### 1.2 LevelFields AI

- **URL:** https://www.levelfields.ai
- **What it does:** AI-powered event detection platform that scans 6,300+ companies for material corporate events "proven to impact stock prices." It identifies the event, categorizes it, and shows historical performance of similar events (e.g., "Stocks that announce return of capital typically gain X% in Y days").
- **How it categorizes reasons:** 25+ event types including:
  - Return of capital / buybacks
  - Product and leadership changes
  - Lawsuits and legal actions
  - Government actions and regulatory changes
  - Restructuring
  - Dividend increases/cuts
  - FDA approvals
  - M&A activity
  - Earnings surprises
- **Key features:**
  - AI scans events 1800x faster than manual research
  - Historical backtesting of event impact (e.g., "NXGL Return of Capital: +22.5% 1-day, +36.7% 1-week")
  - Customizable alerts and scenarios
  - Analyst-called trade alerts (premium tier)
- **Pricing:**
  - Level 1 (DIY): $25/month (annual plan) — self-directed event monitoring, all scenarios, customizable alerts
  - Level 2 (Premium): Higher cost (unspecified) — includes analyst alerts, 1-on-1 training, SMS alerts, options positioning guidance
- **API availability:** No public API mentioned.
- **Reliability:** Good for event-driven trading. Performance claims look impressive but are historical examples, not guarantees. Strong at forward-looking catalyst identification rather than real-time "why did it just move."
- **User 1 (H1B/US):** Good value at $25/month for event-driven research. More of a catalyst anticipation tool than a real-time explainer.
- **User 2 (India):** Affordable at $25/month. US-market focused only.

### 1.3 Stock Titan

- **URL:** https://www.stocktitan.net
- **What it does:** Independent AI-powered platform for real-time stock market news, press releases, SEC filings, and earnings. Features "Rhea-AI" which summarizes news and extracts key insights with sentiment and impact analysis.
- **How it categorizes reasons:** AI-powered sentiment analysis on news items. Categorizes by: earnings, press releases, SEC filings, premarket/afterhours movers.
- **Key features:**
  - 901,477 news items across 24,727 stock tickers (685 daily articles avg)
  - Argus Momentum Scanner: detects stocks with "unusual momentum backed by breaking news"
  - Customizable filters (price range, market cap, float)
  - Audio, voice, and banner notifications
  - Investment calculators
- **Pricing:**
  - Free: $0 (1-min delay, ads, filters disabled)
  - Silver: $19.99/month (30-sec delay, no ads, limited filters)
  - Gold: $59.99/month (real-time, unlimited filters)
  - Platinum: $89.99/month (real-time, full dashboard)
  - Annual: 25% discount
- **API availability:** Not mentioned.
- **Reliability:** Decent for news aggregation with AI summaries. Not as curated as Benzinga WIIM but more affordable.
- **User 1 (H1B/US):** Good mid-range option. Free tier is functional.
- **User 2 (India):** Free tier available. US-market focused.

### 1.4 Hammerstone Markets

- **URL:** https://hammerstonemarkets.com
- **What it does:** Real-time stock market news and analysis service since 2001. Curates financial information with trader context, explaining WHY stocks are moving with "actionable context."
- **How it categorizes reasons:** Real-time breaking news with trader interpretation, floor imbalances, Wall Street research integration, earnings releases with interpretation.
- **Key features:**
  - 1,600+ real-time news updates daily
  - 4 daily reports: Early Look (pre-market), Street Recommendations, Mid-Morning Analysis, Closing Recap
  - Custom filters and email alerts
  - Live chat forum
  - Mobile app
  - Integrations: Interactive Brokers, TradingView, OpenFin
- **Pricing:**
  - Individual Trader: $39-$69/month
  - Institutional Trader: $299-$329/month
  - 14-day trial: $1.00
- **API availability:** Not mentioned.
- **Reliability:** High. 20+ year track record. Trusted by professional traders. The human-curated "why is it moving" context is valuable.
- **User 1 (H1B/US):** Strong option at $39-$69/month. Especially good for pre-market/post-market context.
- **User 2 (India):** Moderately expensive. US-market focused only.

### 1.5 Briefing.com InPlay

- **URL:** https://www.briefing.com/inplay
- **What it does:** Real-time stock mover explanations. InPlay provides structured reasons for significant intraday stock movements. Considered one of the original "why is it moving" services, used by institutional traders since the late 1990s.
- **How it categorizes reasons:** Earnings, analyst actions, FDA decisions, M&A, management changes, guidance updates, sector rotation, technical breakouts, and macro events.
- **Key features:**
  - Real-time InPlay updates explaining stock movers
  - Pre-market and after-hours coverage
  - Sector/industry analysis
  - Economic calendar integration
- **Pricing:** Subscription-based (specific pricing requires contacting sales; historically $25-$100/month range for retail; institutional pricing higher).
- **API availability:** Not publicly documented for retail.
- **Reliability:** Very high. One of the most respected names in real-time market commentary. Used by Bloomberg terminals historically.
- **User 1 (H1B/US):** Excellent for professional-grade "why is it moving" explanations.
- **User 2 (India):** Expensive for Indian use. US-only.

### 1.6 Unusual Whales

- **URL:** https://unusualwhales.com
- **What it does:** Primarily tracks unusual options activity, dark pool data, and institutional flow. Does not have a dedicated "why is it moving" feature, but provides the data to infer WHY (e.g., "NVDA saw massive call buying before earnings" implies institutional anticipation).
- **How it categorizes reasons:** Infers movement from: unusual options flow, dark pool activity, insider buying/selling, congressional trading, institutional activity, short interest.
- **Key features:**
  - Real-time options flow alerts
  - Dark pool monitoring
  - Congressional trading tracker
  - FDA/economic calendar
  - Earnings data (premarket, afterhours, historical)
  - Market sentiment indicators (Market Tide, Sector Tide)
  - **MCP Server available** for Claude integration
- **Pricing:**
  - API: $250/month for full market historical option trades
  - 10% discount for >1 year subscriptions
  - Consumer subscription: multiple tiers (pricing on website)
- **API availability:** Yes, comprehensive REST API + WebSocket + Kafka streaming. Well-documented at https://api.unusualwhales.com/docs. OpenAPI spec available.
- **MCP Server:** Available at https://unusualwhales.com/public-api/mcp — 18 tools, 123+ actions. Integrates with Claude Desktop, Cursor, VS Code.
- **Reliability:** Good for flow-based analysis. Does not directly answer "why did X move" but provides supporting evidence.
- **User 1 (H1B/US):** Good supplementary tool. The MCP integration is unique.
- **User 2 (India):** Expensive. US-market focused.

### 1.7 TipRanks

- **URL:** https://www.tipranks.com
- **What it does:** Aggregates analyst ratings, insider transactions, and news sentiment. Shows analyst track records and performance-based rankings. Provides context for price movements through analyst actions and news sentiment.
- **How it categorizes reasons:** Analyst upgrades/downgrades, price target changes, insider buying/selling, hedge fund activity, news sentiment scores, earnings estimates.
- **Key features:**
  - Analyst consensus and individual track records
  - Smart Score (multi-factor rating system)
  - Insider transaction tracking
  - News sentiment analysis
  - Earnings estimates and surprises
- **Pricing:** Freemium model with premium tiers (specific pricing on website; historically $30-$50/month for premium).
- **API availability:** Not publicly available for retail.
- **Reliability:** High for analyst-driven explanations. Less useful for intraday "why is it moving" — better for understanding medium-term drivers.
- **User 1 (H1B/US):** Good for analyst-driven context.
- **User 2 (India):** Has some Indian market coverage. Premium is moderately priced.

### 1.8 MarketBeat

- **URL:** https://www.marketbeat.com
- **What it does:** Provides daily stock movers lists with attached reasons. Shows analyst ratings, earnings data, insider trades, and news headlines associated with price movements.
- **How it categorizes reasons:** Analyst ratings changes, earnings surprises, dividend announcements, insider trades, and associated news headlines.
- **Pricing:** Free tier available with ads; premium starts around $20-$25/month.
- **API availability:** Not publicly available.
- **Reliability:** Good for end-of-day review. Not real-time.
- **User 1 (H1B/US):** Decent free option for daily review.
- **User 2 (India):** US-focused. Free tier accessible.

### 1.9 Dataminr

- **URL:** https://dataminr.com
- **What it does:** Enterprise AI platform for real-time event detection using 50+ proprietary LLMs across 1M+ public data sources. Used by 2/3 of Fortune 50, 100+ US government agencies, 1,500+ newsrooms.
- **How it categorizes reasons:** Multi-modal AI detects and categorizes events across: geopolitical, corporate, cyber, supply chain, and market events. "Intel Agents" provide contextual analysis explaining event implications.
- **Pricing:** Enterprise only (likely $10K+/month). Not available for retail investors.
- **API availability:** Enterprise API only.
- **Reliability:** Extremely high. Used by the world's largest institutions.
- **User 1 (H1B/US):** Out of reach for individual use (enterprise pricing).
- **User 2 (India):** Not accessible.

### 1.10 Catacal

- **URL:** https://www.catacal.com
- **What it does:** AI-powered stock events calendar tracking market-moving catalysts. Provides early alerts and AI impact ratings showing which catalysts have the greatest potential to move stock prices.
- **How it categorizes reasons:** Earnings, IPOs, corporate events, product launches, economic events, FDA approvals, FOMC decisions, crowd-sourced catalysts.
- **Key features:**
  - AI impact ratings on upcoming catalysts
  - Crowd-sourced catalyst tracking
  - Event calendar with alerts
  - Coverage of major US stocks (AAPL, MSFT, GOOGL, NVDA, TSLA, etc.)
- **Pricing:** Free tier available ($0 USD).
- **API availability:** Not mentioned.
- **Reliability:** Useful for forward-looking catalyst identification. Free makes it accessible.
- **User 1 (H1B/US):** Good free supplement for catalyst calendar.
- **User 2 (India):** Free. US-focused but accessible.

### 1.11 TheStockCatalyst.com

- **URL:** https://thestockcatalyst.com
- **What it does:** Free stock trading research platform identifying catalysts through top movers and earnings reports. Tracks premarket/afterhours movers and connects them with earnings data and news headlines.
- **How it categorizes reasons:** Earnings-driven movers (primary focus), biocatalysts (external links), premarket/afterhours movers with news context.
- **Key features:**
  - Premarket and afterhours top movers
  - Earnings screeners (premarket, afterhours, combined)
  - Historic earnings lookup
  - Entry calculator (pullback prices, targets, stop-loss)
- **Pricing:** Free (ad-supported, donations via Ko-fi).
- **API availability:** None.
- **Reliability:** Basic but free. Good for quick earnings-season scanning.
- **User 1 (H1B/US):** Free tool for earnings-driven moves.
- **User 2 (India):** Free. US-focused.

---

## 2. APIs That Provide Categorized Stock Move Reasons

### 2.1 Benzinga Cloud API — WIIM Endpoint (Best-in-Class)

- **URL:** https://docs.benzinga.com
- **Endpoint:** `/get-wiims`
- **What it does:** The only API that directly provides structured "Why Is It Moving" data — human-curated explanations for stock price movements, available programmatically. This is the API version of Benzinga Pro's WIIM feature.
- **Data format:** Structured JSON with ticker, timestamp, reason text, channel, and filtering capabilities.
- **Related endpoints:**
  - `/get-news-items` — Structured news with ticker filtering
  - `/get-market-movers` — Stocks that moved significantly with screener support
  - `/get-earnings` — Actual vs. estimated earnings figures
  - `/get-ratings` — Analyst rating changes and price targets
  - `/get-guidance` — Forward-looking management projections
  - `/get-short-interest-data` — Short interest metrics
- **WebSocket streams:** Real-time news, earnings, ratings, consensus ratings
- **Authentication:** API key as URL query parameter `token`
- **Pricing:** Enterprise/contact-based (partners@benzinga.com). Historically $200-$500+/month for data feeds.
- **Categories:** Earnings, FDA, M&A, analyst actions, guidance, management changes, legal, technical, macro.
- **User 1:** Ideal for building automated tools. Expensive but definitive.
- **User 2:** Likely too expensive for individual use.

### 2.2 Alpha Vantage — News Sentiment API

- **URL:** https://www.alphavantage.co/documentation/#news-sentiment
- **Endpoint:** `NEWS_SENTIMENT` function
- **What it does:** Delivers news articles with sentiment scores and topic categorization. Covers stocks, crypto, and forex. 15 distinct topic categories allow filtering by reason type.
- **Topic categories:**
  - Earnings, IPO, Mergers & Acquisitions
  - Financial Markets, Economy (Fiscal/Monetary/Macro)
  - Energy & Transportation, Life Sciences, Manufacturing
  - Real Estate & Construction, Retail & Wholesale, Technology
  - Blockchain, Finance
- **Data format:** JSON with sentiment scores, relevance scores per ticker, topic tags, and article metadata.
- **Key parameters:** tickers, topics, time_from/time_to, sort (LATEST/EARLIEST/RELEVANCE), limit (up to 1000).
- **Pricing:**
  - Free: 25 API requests/day
  - Premium: $49.99-$249.99/month (75-1200 requests/min, no daily limits)
  - Annual plans at ~$42-$208/month
- **Reliability:** Good for topic-tagged news. Sentiment scores are automated (NLP-based), not human-curated. Useful for building "stock moved because of [topic]" summaries.
- **User 1:** Great free tier for prototyping. Premium is affordable.
- **User 2:** Free tier is very usable for Indian budget. Covers global markets.

### 2.3 Finnhub — Company News + Sentiment API

- **URL:** https://finnhub.io
- **Endpoints:** Company News, News Sentiment, Social Sentiment
- **What it does:** Provides company news with category tags, sentiment analysis (composite score, bullish/bearish percentages), and social sentiment tracking (-1 to +1 daily scores).
- **Data format:** JSON with headline, summary, source, timestamp, related stocks, category, sentiment scores.
- **Categories:** News articles are tagged with category field (general, forex, crypto, merger, etc.).
- **Pricing:**
  - Free tier: 60 API calls/min (generous for development)
  - Market Data Basic: $49.99/month
  - Market Data Standard: $129.99/month
  - Market Data Professional: $199.99/month
  - Fundamentals: $50-$200/month
  - All-in-One: $3,000/month
- **Reliability:** Good data quality. Categories are automated. Sentiment is useful but not a direct "why is it moving" explanation.
- **User 1:** Free tier is excellent for building tools. Paid tiers are reasonable.
- **User 2:** Free tier covers basic needs. Global coverage.

### 2.4 Polygon.io (now Massive.com) — News API with Sentiment

- **URL:** https://polygon.io (redirects to massive.com)
- **What it does:** News API that associates articles with tickers and provides AI-generated sentiment insights. Each article includes sentiment classification (positive/negative/neutral) with reasoning.
- **Data format:** JSON with tickers array, insights array (sentiment + reasoning per ticker), publisher details, and article metadata.
- **Sentiment detail:** Provides reasoning for sentiment determination (e.g., "UBS analysts are providing a bullish outlook on future Federal Reserve rate cuts").
- **Pricing:** Subscription-based. Historically: Free tier available, paid starts ~$29-$99/month. Recently rebranded to Massive.com.
- **Reliability:** Good. The sentiment reasoning feature is particularly useful for "why" explanations.
- **User 1:** Good option with free tier.
- **User 2:** Free tier available. Good global coverage.

### 2.5 MarketAux — News API with Entity Sentiment

- **URL:** https://www.marketaux.com
- **What it does:** Aggregates financial news from 5,000+ sources in 30+ languages, covering 80+ global markets and 200,000+ entities. Each article includes NLP-powered sentiment scores per mentioned entity.
- **Data format:** JSON with entity extraction (symbol, company name, exchange, country, industry), sentiment scores per entity (-1 to +1 range for title and body), and relevance match scores.
- **Pricing:**
  - Free: $0 (100 requests/day, 3 articles/request)
  - Basic: $29/month ($24/month annual) — 2,500 requests/day, 20 articles/request
  - Standard: $49/month ($41/month annual) — 10,000 requests/day, 50 articles/request
  - Pro: $99/month ($83/month annual) — 25,000 requests/day, 100 articles/request
  - Pro 50K: $199/month ($166/month annual) — 50,000 requests/day
- **Reliability:** Good. Multi-language support and 80+ markets make it one of the best for global coverage including Indian markets.
- **User 1:** Affordable. Good global coverage.
- **User 2:** Free tier is very useful. Covers Indian market (NSE/BSE). Best free option for Indian market news with sentiment.

### 2.6 EODHD — Financial News API

- **URL:** https://eodhd.com/financial-apis/financial-news-api
- **What it does:** Financial news with 50 standard tags plus AI-detected tags, article-level sentiment scores, and aggregate sentiment data over time.
- **Tag categories:** Earnings per share, revenue growth, dividend payments, mergers & acquisitions, artificial intelligence, growth rate, European regulatory news, and many more (50+ standard + AI-detected).
- **Sentiment:** Two approaches — per-article (polarity, positive/negative/neutral scores) and aggregate (normalized -1 to +1 across dates with article counts).
- **News Word Weights API:** Unique feature — analyzes thousands of articles to provide weighted word lists for trend analysis.
- **Pricing:** Included in multiple plans (standalone, All-In-One, Fundamentals). Each request = 5 API calls + 5 per ticker. Free tier available.
- **Reliability:** Good. The AI-detected tags feature is useful for dynamic categorization.
- **User 1:** Affordable with extensive tag system.
- **User 2:** Free tier available. Global coverage.

### 2.7 StockNewsAPI

- **URL:** https://stocknewsapi.com
- **What it does:** Aggregates 50,000+ monthly articles from CNBC, Bloomberg, Zacks, Motley Fool, Fox Business, etc. Provides sentiment labels (positive/negative/neutral) and event tracking.
- **Categories:** General market, technology, healthcare, conference announcements, CEO changes, layoffs, M&A, earnings, analyst upgrades/downgrades.
- **Endpoints:** Top Mentions & Sentiment, Trending Headlines, Events (major corporate announcements), Ratings (analyst upgrades/downgrades).
- **Pricing:**
  - Free trial: 100 calls over 5 days
  - Basic: $19.99/month (20,000 calls, individual ticker + general news)
  - Premium: $49.99/month (50,000 calls, sentiment analysis, trending, events, ratings, historical)
  - Business: Custom pricing (SLA, dedicated account manager)
- **Reliability:** Good for news aggregation. Categories and events endpoint are useful for "why" analysis.
- **User 1:** Affordable. Good category coverage.
- **User 2:** $19.99/month is moderate. US-focused.

### 2.8 Tiingo — News API

- **URL:** https://www.tiingo.com
- **What it does:** Financial data platform with news API, IEX real-time data, and end-of-day data. News API provides articles with ticker associations.
- **Pricing:** Free tier available (limited calls). Paid tiers historically $10-$75/month.
- **Reliability:** Good but documentation was difficult to access. Less feature-rich for "why" analysis compared to alternatives.
- **User 1:** Affordable supplement.
- **User 2:** Free tier available.

### 2.9 Event Registry (NewsAPI.ai)

- **URL:** https://eventregistry.org / https://newsapi.ai
- **What it does:** AI-powered news platform analyzing 150,000+ sources in 60+ languages. Organizes news into events, performs entity recognition, category assignment, and sentiment analysis.
- **Key capability:** Groups individual news articles into coherent "events" — reducing noise and enabling event-level analysis (e.g., "NVDA earnings event" as a single tracked entity with all related articles).
- **Pricing:** Contact-based for API pricing. Enterprise-oriented.
- **Reliability:** High quality. Event clustering is unique and powerful.
- **User 1:** Good for sophisticated analysis but enterprise pricing.
- **User 2:** Likely too expensive.

---

## 3. Open-Source Projects on GitHub

### 3.1 Directly Relevant: "Stock Explain" Projects

#### stock-explain (MSsanjay02) — Indian Stock Focus
- **URL:** https://github.com/MSsanjay02/stock-explain
- **What it does:** Full-stack app helping Indian retail investors understand daily stock price movements through AI-generated explanations. Compares today's price vs. yesterday's opening and generates 3 concise sentences explaining the movement.
- **Tech stack:** Python, FastAPI, LLaMA 3 (8B) via Ollama (local), Yahoo Finance for NSE data, HTML/CSS/JS frontend.
- **Approach:** "Explainability, not prediction" — observational explanations with uncertainty awareness.
- **Stars:** 0 | **Commits:** 8
- **User 2 relevance:** High — specifically designed for Indian market (NSE symbols like INFY.NS).

#### Stock_Movement_Reason_Finder (sushrutha777) — NIFTY100 Focus
- **URL:** https://github.com/sushrutha777/Stock_Movement_Reason_Finder
- **Live demo:** https://stock-movement-reason-finder.streamlit.app
- **What it does:** Analyzes NIFTY100 stocks, identifies top 5 gainers/losers, fetches news via Google RSS, and uses Google Gemini Pro API to generate AI explanations for price movements.
- **Tech stack:** Python, Streamlit, Google Gemini Pro API, Google RSS feeds.
- **Stars:** 0 | **Commits:** 37
- **User 2 relevance:** Very high — NIFTY100 focused, live Streamlit demo available.

#### stockalpha-explainable-ml-llm (ritwikm14)
- **URL:** https://github.com/ritwikm14/stockalpha-explainable-ml-llm
- **What it does:** Combines Alpha Vantage API + ML classifiers (logistic regression, random forest, XGBoost) + OpenAI LLM explanations. Forecasts next-day price direction and generates human-readable explanations.
- **Tech stack:** Python 3.13+, pandas, scikit-learn, XGBoost, Streamlit, Alpha Vantage API, OpenAI API.
- **Coverage:** AAPL, MSFT, AMZN, GOOGL, META (expandable).
- **Stars:** 0

### 3.2 Sentiment Analysis & News Correlation

#### Stocksight (shirosaidev) — 2.4K Stars
- **URL:** https://github.com/shirosaidev/stocksight
- **What it does:** Analyzes how emotions on Twitter and news headlines affect stock prices. Mines tweets and news, performs sentiment analysis, and visualizes correlations using Elasticsearch + Kibana dashboards.
- **Tech stack:** Python 3.x, Elasticsearch 5.x, Kibana 5.x, NLTK, TextBlob, VADER, Newspaper3k, Tweepy, Docker.
- **Stars:** 2,400 | **Forks:** 486
- **License:** Apache 2.0
- **Status:** Last active release June 2020. Mature but not actively maintained.
- **Relevance:** Foundational project for correlating news sentiment with stock movements.

#### Surpriver (tradytics) — 1.9K Stars
- **URL:** https://github.com/tradytics/surpriver
- **What it does:** Identifies stocks with unusual price + volume patterns that precede big moves. Uses machine learning anomaly detection to find stocks that are about to move significantly.
- **Tech stack:** Python, scikit-learn, NumPy, pandas, yfinance, SciPy, Ta (technical analysis).
- **Stars:** 1,900 | **Forks:** 333
- **Status:** Last commit August 2020. Not actively maintained.
- **Limitation:** Detects WHEN anomalies occur but not WHY — does not correlate with news events.

#### FinBERT (ProsusAI) — 2,000+ Stars
- **URL:** https://github.com/ProsusAI/finBERT
- **Hugging Face:** `ProsusAI/finbert`
- **What it does:** Pre-trained NLP model for financial sentiment classification. Classifies financial text as positive/negative/neutral with confidence scores.
- **Stars:** 2,000+ | **Forks:** 505
- **How to use:** Input financial text, get softmax probabilities for 3 sentiment labels + composite sentiment score.
- **Relevance:** Building block for creating "why did stock X move" tools — classify news headlines associated with movers.

### 3.3 Indian Market News Sentiment

#### Indian-Stock-News-Sentiment-Analysis (RelativelyBurberry)
- **URL:** https://github.com/RelativelyBurberry/Indian-Stock-News-Sentiment-Analysis
- **What it does:** Pipeline for collecting Indian stock market news, mapping articles to NSE tickers, and performing FinBERT-based sentiment analysis. Uses Groww's backend API for structured news data.
- **Tech stack:** Python, FinBERT (ProsusAI/finbert), NRC Lexicon, pandas, Plotly, Seaborn, Kaggle environment.
- **Stars:** 1
- **User 2 relevance:** Directly applicable for NSE ticker-mapped sentiment analysis.

### 3.4 News-Price Correlation Projects

| Project | Stars | Description |
|---------|-------|-------------|
| Stock-price-predection-using-LSTM-and-Sentiment-analysis (arpit0891) | 12 | LSTM + tweet sentiment correlation |
| Twitter_and_StockPrice_sem2 (DivyaDevaprasad) | 8 | Twitter sentiment vs. stock market correlation |
| Using-Transfer-Learning-to-Predict-Stock-Sentiment-Correlation (mahadkhanleghari) | 4 | Transfer learning for news-price correlation |
| FundamentalAnalysisStockScreener (AlexRomanenkoNorthwestern) | 4 | News headline sentiment + analyst price targets |
| TraderbotAdvisor (Asheladia) | 3 | News effects on stock prediction |
| Predicting-Price-Moves-with-News-Sentiment (Bekamgenene) | 2 | Financial news sentiment correlation with stocks |

### 3.5 Other Notable Open-Source Tools

#### fin-trend-analyzer (chigwell)
- **URL:** https://github.com/chigwell/fin-trend-analyzer
- **What it does:** Analyzes financial news and sentiment to identify trends and risks in AI/tech stocks. Delivers structured insights for market assessment.

#### financial-parser (chigwell)
- **URL:** https://github.com/chigwell/financial-parser
- **What it does:** Extracts structured information from financial news headlines (company names, financial targets, timeframes, goal updates). Useful as a parsing component.

#### Claude Equity Research (357 stars)
- **What it does:** AI-powered equity research generator using Claude for comprehensive fundamental analysis, technical indicators, and risk assessment.

---

## 4. MCP Servers and Claude Integrations

### 4.1 Unusual Whales MCP Server

- **URL:** https://unusualwhales.com/public-api/mcp
- **What it does:** 18 tools, 123+ actions for accessing options flow, dark pool data, congressional trading, prediction markets, and stock analysis through Claude Desktop, Cursor, VS Code, and Windsurf.
- **Setup:** ~30 seconds via config file.
- **Capabilities:** Options flow alerts, dark pool monitoring, insider/politician trading, technical indicators (RSI, MACD, Bollinger, VWAP), earnings data, FDA calendar.
- **Pricing:** Requires API token purchase (pricing on website).

### 4.2 MaverickMCP (423 stars)

- **URL:** https://github.com/wshobson/maverick-mcp
- **What it does:** Personal stock analysis MCP server with 20+ technical indicators, 15+ built-in backtesting strategies, portfolio optimization, and **news sentiment analysis** (`get_news_sentiment` tool).
- **Tech stack:** Python 3.12+, FastMCP 2.0, SQLAlchemy, Redis, PostgreSQL/SQLite.
- **Pre-seeded:** All 520 S&P 500 stocks with screening recommendations.
- **Transport:** HTTP, SSE, STDIO for MCP clients.
- **Pricing:** Free (open source).

### 4.3 FinanceNews-MCP (5 stars)

- **URL:** https://github.com/guangxiangdebizi/FinanceNews-MCP
- **What it does:** MCP server for financial news search using Finnhub API. Enables Claude to fetch and analyze financial news via natural language queries.
- **Tech stack:** TypeScript, Express, Finnhub API.
- **Pricing:** Free (requires Finnhub API key).

### 4.4 mcp-trader (262 stars, archived)

- **URL:** https://github.com/wshobson/mcp-trader
- **What it does:** Stock trading MCP server. Predecessor to MaverickMCP.
- **Status:** Archived. Use MaverickMCP instead.

### 4.5 IndiaQuant MCP Server

- **URL:** https://github.com/deepak-05dktopG/IndiaQuant-MCP-Server
- **What it does:** MCP server for Indian stock market (NSE/BSE). Provides live prices, options Greeks, trade signals with NewsAPI sentiment analysis, portfolio management, and sector heatmaps.
- **5 modules:** Market Data Engine, Quant Logic Library, AI Trade Signal Generator (with sentiment), Options Chain Analyzer, Portfolio Risk Manager.
- **10 MCP tools:** Live quotes, options chains, sentiment analysis, buy/sell signals, portfolio P&L, virtual trades, Greeks, unusual activity, market scanning, sector heatmaps.
- **Tech stack:** Python 3.10+, yfinance, NewsAPI, Alpha Vantage (all free APIs), SQLite, Claude Desktop.
- **Stars:** 1
- **User 2 relevance:** Very high — specifically designed for NSE/BSE with free data sources.

### 4.6 Other Finance MCP Servers

| Project | Stars | Description |
|---------|-------|-------------|
| yahoo-finance-server (AgentX-ai) | 38 | Yahoo Finance data for AI assistants |
| kospi-kosdaq-stock-server (dragon1086) | 64 | Korean market MCP server |
| finance-query (Verdenroz) | - | Rust-based with 36 MCP tools, REST, WebSocket, GraphQL, SEC EDGAR |
| stock-analysis-mcp (parthashirolkar) | 0 | Indian BSE/NSE with real-time quotes and news |

---

## 5. Indian Market Tools (NSE/BSE)

### 5.1 MoneyControl

- **URL:** https://www.moneycontrol.com
- **What it does:** India's largest financial portal. Provides stock-specific news pages showing recent headlines alongside price charts. Has "Why is [stock] moving" editorial articles for major movers.
- **How it categorizes:** Editorial team writes articles explaining big movers on NSE/BSE. Categories include quarterly results, management commentary, analyst actions, sector trends, regulatory changes.
- **Pricing:** Free (ad-supported). Premium available.
- **API:** No official public API.
- **User 2 relevance:** Essential. Free and comprehensive for Indian market.

### 5.2 Trendlyne

- **URL:** https://www.trendlyne.com
- **What it does:** Indian stock market platform with screeners, alerts, events calendar, insider trading data, research reports, and MarketMind AI agent for document analysis.
- **Key features:**
  - Real-time portfolio alerts
  - Events calendar for corporate announcements
  - Insider trading tracker
  - Data downloader
  - Research reports
  - MarketMind AI agent
  - Supports NIFTY, BANKNIFTY, SENSEX, sector indices
  - Also covers USA market
- **Pricing:** Free tier + Premium subscription (pricing on website; historically INR 500-2000/month range).
- **API:** Not publicly available.
- **User 2 relevance:** High. Indian-focused with comprehensive features.

### 5.3 Screener.in

- **URL:** https://www.screener.in
- **What it does:** Stock screening and fundamental analysis tool for Indian investors. Create custom screens against 10 years of financial data. Has "Screener AI" for extracting insights from company documents.
- **Key features:**
  - Custom stock screens on 10-year financial data
  - Company announcements with search and alerts
  - Commodity prices (10,000+ commodities)
  - Shareholder search
  - Screener AI for document analysis
- **Pricing:** Free basic tier; Premium available (historically INR 3,000-5,000/year).
- **API:** Not publicly available.
- **User 2 relevance:** High for fundamental analysis. The announcements feature helps with "why did it move" but is not as structured as Benzinga WIIM.

### 5.4 indian-stock-ai-agent (Open Source)

- **URL:** https://github.com/svsairevanth/indian-stock-ai-agent
- **What it does:** AI-powered stock analysis for NSE/BSE using 10 specialized agents organized into Analysis Team (5), Debate Team (3), and Risk & Portfolio Team (2).
- **Agent roles:** Fundamental Analyst, Technical Analyst, Sentiment Analyst, Macro Analyst, Document Analyst, Bull Advocate, Bear Advocate, Debate Judge, Risk Manager, Portfolio Analyst.
- **How it explains movements:** Weighted scoring (Fundamentals 30%, Technical 25%, Sentiment 15%, Macro 15%, Debate 15%) producing Strong Buy to Strong Sell recommendations.
- **Tech stack:** GPT-4o via OpenAI Agents SDK, 30+ custom tools, Yahoo Finance, Exa MCP tools.
- **Stars:** 3
- **User 2 relevance:** Very high. Requires OpenAI API key (cost for GPT-4o usage).

---

## 6. Reddit/Community Sentiment Tools

### 6.1 StockTwits

- **URL:** https://stocktwits.com
- **What it does:** 10M+ user community sharing real-time stock sentiment. Shows trending stocks, sentiment shifts, and community reactions to earnings and market events.
- **Key features:**
  - Real-time sentiment data per stock
  - Trending stocks by activity/sentiment
  - Live earnings call streaming with sentiment overlay
  - AI-powered trending insights
- **API:** Developer API exists at api.stocktwits.com/developers BUT currently not accepting new registrations (under review/upgrade).
- **Pricing:** Free to use.
- **User 1:** Good free sentiment source (US market).
- **User 2:** Free. US-focused but accessible.

### 6.2 WallStreetBets Sentiment Trackers (GitHub)

Notable open-source projects:

| Project | Language | Description |
|---------|----------|-------------|
| WallstreetBets-Stock-Tracker (TrentPierce) | JavaScript | Tracks top 50 stocks discussed on r/WSB |
| Wall-Street-Bets-Sentiment-Scraper (aaravp6) | Python | Monitors WSB sentiment and compares to market movements |
| Meme-Stock-Sentiment-Tracker (tomassmilak-cmd) | Python | Real-time Reddit + Twitter sentiment streaming |
| reddit-stock-tracker (nick253) | Python | Trending stocks + sentiment from multiple subreddits |
| wsb-tracker (pmanlukas) | Python | CLI tool for WSB ticker mentions + sentiment |

All are free/open source. Quality varies; most are hobby projects.

---

## 7. Comparison Matrix

### Real-Time "Why Is It Moving" (Direct Answer)

| Tool | Directness | Real-Time | Pricing | API | Coverage |
|------|-----------|-----------|---------|-----|----------|
| **Benzinga Pro WIIM** | Direct human-curated | Yes | $147/month | Yes (paid) | US |
| **Hammerstone Markets** | Direct human-curated | Yes | $39-69/month | No | US |
| **Briefing.com InPlay** | Direct human-curated | Yes | ~$25-100/month | No (retail) | US |
| **Stock Titan** | AI-summarized | Yes | $0-90/month | No | US |
| **LevelFields AI** | Event detection | Near real-time | $25/month | No | US |
| **MoneyControl** | Editorial articles | Delayed | Free | No | India |

### APIs for Building "Why Is It Moving" Tools

| API | News + Sentiment | Categories | Free Tier | Paid Start | Global Coverage |
|-----|-----------------|------------|-----------|------------|----------------|
| **Benzinga WIIM API** | Yes (curated) | 10+ | No | ~$200+/month | US |
| **Alpha Vantage** | Yes (NLP) | 15 topics | 25/day | $49.99/month | Global |
| **Finnhub** | Yes (NLP) | Yes | 60/min | $49.99/month | Global |
| **Polygon/Massive** | Yes (AI reasoning) | Yes | Yes | ~$29/month | US primary |
| **MarketAux** | Yes (NLP) | By entity | 100/day | $29/month | 80+ markets |
| **EODHD** | Yes (NLP + tags) | 50+ tags | Yes | Included | Global |
| **StockNewsAPI** | Yes (NLP) | Yes | 100 trial | $19.99/month | US |

### MCP Servers for Claude Integration

| MCP Server | Focus | News/Sentiment | Free | Indian Market |
|------------|-------|---------------|------|---------------|
| **Unusual Whales** | Options flow + dark pool | News feed | No (paid API) | No |
| **MaverickMCP** | S&P 500 analysis | Yes | Yes | No |
| **FinanceNews-MCP** | Financial news | Yes (Finnhub) | Yes | Global |
| **IndiaQuant** | NSE/BSE | Yes (NewsAPI) | Yes | Yes |
| **finance-query** | Multi-asset | No | Yes | No |

---

## 8. Recommendations by User Profile

### User 1 (H1B/US) — Best Stack

**Tier 1: Best single tool (if budget allows)**
- **Benzinga Pro ($147/month)** — The definitive "why is it moving" tool for US markets. Real-time, human-curated, comprehensive.

**Tier 2: Budget-conscious stack**
1. **Hammerstone Markets ($39/month)** — Real-time "why" explanations with 20+ year track record
2. **Catacal (free)** — Forward-looking catalyst calendar
3. **MaverickMCP (free)** — Claude integration for S&P 500 analysis + news sentiment

**Tier 3: Build-your-own (cheapest)**
1. **Alpha Vantage News Sentiment API (free tier)** — 15 topic categories, 25 calls/day
2. **Finnhub Company News API (free tier)** — 60 calls/min
3. **FinBERT (open source)** — Classify news sentiment
4. **MaverickMCP or FinanceNews-MCP (free)** — Claude integration
5. Use Claude/LLM to summarize: "Given this news about NVDA tagged 'earnings', the stock dropped 5% because..."

### User 2 (India) — Best Stack

**Tier 1: Free tools**
1. **MoneyControl (free)** — "Why is it moving" editorial articles for major NSE/BSE movers
2. **Stock_Movement_Reason_Finder (free, open source)** — NIFTY100 AI-powered explainer with live Streamlit demo
3. **Screener.in (free tier)** — Announcements + fundamental screening
4. **Catacal (free)** — US market catalyst calendar
5. **MarketAux API (free tier)** — 100 requests/day with Indian market coverage and entity sentiment

**Tier 2: Low-cost additions**
1. **Trendlyne (free tier + optional premium)** — Events calendar, insider trading, alerts
2. **IndiaQuant MCP Server (free, open source)** — Claude integration for NSE/BSE with sentiment analysis
3. **stock-explain (free, open source)** — LLaMA 3 based Indian stock explainer (run locally)

**Tier 3: Build-your-own for NSE/BSE**
1. **Indian-Stock-News-Sentiment-Analysis (open source)** — FinBERT pipeline for NSE tickers
2. **Alpha Vantage News Sentiment API (free)** — Topic-categorized news
3. **indian-stock-ai-agent (open source)** — 10-agent AI analysis system (needs OpenAI API key)

---

## 9. Build-Your-Own Approach

### Architecture: "Why Did Stock X Move?" Engine

```
[Data Ingestion Layer]
  - Alpha Vantage News Sentiment API (free, 15 categories)
  - Finnhub Company News API (free, sentiment scores)
  - MarketAux API (free, 80+ markets including India)
  - Yahoo Finance (price data via yfinance)
        |
        v
[Event Detection & Classification Layer]
  - FinBERT (HuggingFace ProsusAI/finbert) for sentiment
  - LLM (Claude/GPT) for categorization:
    * Earnings beat/miss
    * FDA approval/rejection
    * Analyst upgrade/downgrade
    * M&A announcement
    * Insider buying/selling
    * Management change
    * Guidance raise/cut
    * Legal/regulatory
    * Macro/geopolitical
    * Technical/sector rotation
        |
        v
[Correlation Engine]
  - Detect significant price moves (>2% intraday)
  - Find contemporaneous news within time window
  - Rank news by relevance and sentiment impact
  - Generate summary: "NVDA -5.2% because earnings missed
    estimates by $0.15/share, guidance below consensus"
        |
        v
[Delivery Layer]
  - MCP Server for Claude integration
  - Streamlit dashboard
  - API endpoint
  - Alerts (email/SMS/push)
```

### Key Open-Source Building Blocks

1. **FinBERT** — Financial sentiment classification (2K+ stars)
2. **Stocksight** — News + Twitter sentiment analysis framework (2.4K stars)
3. **Surpriver** — Anomalous movement detection (1.9K stars)
4. **MaverickMCP** — MCP server framework with news sentiment (423 stars)
5. **Stock_Movement_Reason_Finder** — Working NIFTY100 explainer
6. **stock-explain** — Indian market explainer with LLaMA 3

### Estimated Cost for Self-Built Solution

| Component | Cost | Notes |
|-----------|------|-------|
| Alpha Vantage API | $0 | Free tier: 25 calls/day |
| Finnhub API | $0 | Free tier: 60 calls/min |
| MarketAux API | $0 | Free tier: 100 calls/day |
| yfinance | $0 | Free (Yahoo Finance) |
| FinBERT | $0 | Open source, runs locally |
| LLM for summarization | $0-20/month | Claude API or local LLaMA |
| Hosting | $0-10/month | Local or cheap VPS |
| **Total** | **$0-30/month** | |

---

## Key Findings Summary

1. **Benzinga WIIM is the gold standard** for "why is stock X moving" in the US market. It's the only tool/API that provides human-curated, structured explanations. Everything else either requires inference from raw news or uses AI to approximate the answer.

2. **No single tool does this for Indian markets (NSE/BSE).** MoneyControl editorials come closest but are not structured/API-accessible. The open-source `Stock_Movement_Reason_Finder` project is the most direct attempt for NIFTY100.

3. **Building your own is feasible and cheap.** Combining free APIs (Alpha Vantage, Finnhub, MarketAux) with FinBERT and an LLM for summarization can approximate Benzinga WIIM at near-zero cost.

4. **MCP integration is an emerging advantage.** Unusual Whales, MaverickMCP, and IndiaQuant MCP servers allow Claude to directly analyze market data and news, making "ask Claude why NVDA dropped" a reality.

5. **The gap is in structured categorization.** Most news APIs provide raw articles with basic sentiment. The value-add is in categorizing the reason (earnings, FDA, M&A, etc.) and correlating it with price movement magnitude and timing. This is where an LLM layer adds the most value.
