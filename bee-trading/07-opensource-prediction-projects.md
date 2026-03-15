# Open-Source Projects That Predict Anything

> A curated catalog of the best open-source prediction, forecasting, and AI trading projects on GitHub — organized by category with star counts, tech stacks, and user-specific notes.

Compiled: 2026-03-14

---

## User Profiles

> **⚠️ User 1 (H1B/US):** Indian citizen on H1B visa, employed in US.
> **⚠️ User 2 (India):** Indian citizen in India, unemployed.
> Legal/access notes marked with ⚠️ where applicable.

---

## Table of Contents

1. [Swarm Intelligence & General Prediction](#1-swarm-intelligence--general-prediction)
2. [Financial AI Platforms & Frameworks](#2-financial-ai-platforms--frameworks)
3. [Financial LLMs & AI Agents](#3-financial-llms--ai-agents)
4. [Prediction Market Bots](#4-prediction-market-bots)
5. [Stock Prediction Models](#5-stock-prediction-models)
6. [Crypto Trading & Prediction](#6-crypto-trading--prediction)
7. [Sports Prediction](#7-sports-prediction)
8. [Time Series Forecasting (General Purpose)](#8-time-series-forecasting-general-purpose)
9. [Curated Lists & Awesome Repos](#9-curated-lists--awesome-repos)
10. [What You Can Build With These](#10-what-you-can-build-with-these)

---

## 1. Swarm Intelligence & General Prediction

### MiroFish ⭐ 24,642

**Repo:** [666ghj/MiroFish](https://github.com/666ghj/MiroFish)
**Language:** Python | **License:** AGPL-3.0

**What it does:** A swarm intelligence prediction engine that creates "high-fidelity parallel digital worlds" where thousands of AI agents with distinct personalities, memories, and behavioral logic interact and evolve. You inject variables from a "god's perspective" to simulate future outcomes.

**How it works (5-stage pipeline):**
1. **Graph Construction** — Seed extraction, memory injection, GraphRAG integration
2. **Environment Setup** — Entity relation extraction, character generation, simulation parameters
3. **Simulation** — Dual-platform parallel modeling with dynamic timeline memory updates
4. **Report Generation** — ReportAgent interacts with simulation results
5. **Deep Interaction** — Dialogue with simulated entities

**Tech stack:** Python 3.11-3.12, LLM APIs (OpenAI-compatible, recommends Alibaba Qwen), Vue frontend, Node.js 18+, Zep Cloud (agent memory), OASIS simulation engine (by CAMEL-AI), Docker

**Demonstrated capabilities:**
- Public opinion event prediction (Wuhan University case study)
- Literary analysis (predicting lost *Dream of the Red Chamber* ending)
- Financial and political forecasting (forthcoming)

**Why it's interesting:** Unlike most prediction tools that analyze historical data, MiroFish creates simulated worlds with autonomous agents — a fundamentally different approach to forecasting. The "predict anything" framing is ambitious and the 24K+ stars suggest strong community interest.

**User notes:**
- ⚠️ Both users: Purely a research/simulation tool. No live trading. Legal to use anywhere.
- Requires LLM API access (OpenAI, Qwen, etc.) which has usage costs.

---

## 2. Financial AI Platforms & Frameworks

### OpenBB ⭐ 63,068

**Repo:** [OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB)
**Language:** Python

**What it does:** An open-source financial data platform for analysts, quants, and AI agents. Think of it as the open-source alternative to Bloomberg Terminal. Aggregates data from dozens of free and premium sources into a unified interface.

**Key features:**
- Unified API for stock, crypto, forex, options, macro data
- AI-powered research workspace
- Extensions for custom data providers
- Python SDK for programmatic access
- Beautiful CLI and web interfaces

**Why it's #1:** Most starred financial open-source project. Huge community. Active development. Constantly adding new data sources.

**User notes:**
- ⚠️ User 1: Full access to all US data sources.
- ⚠️ User 2: Supports some Indian data. Use alongside Indian-specific tools (Screener.in, jugaad-data).

---

### Freqtrade ⭐ 47,650

**Repo:** [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade)
**Language:** Python

**What it does:** The most popular open-source crypto trading bot. Supports backtesting, strategy optimization, paper trading, and live trading across 15+ exchanges.

**Key features:**
- Strategy development in Python
- Built-in backtesting engine with detailed reports
- Hyperparameter optimization (Hyperopt)
- Paper trading mode
- Telegram bot integration for monitoring
- Supports Binance, Kraken, OKX, and more

**Why it matters:** The gold standard for DIY crypto trading bots. Massive community, excellent docs, battle-tested.

**User notes:**
- ⚠️ User 1: ✅ Full access. Use with Coinbase/Kraken (US-regulated exchanges).
- ⚠️ User 2: ✅ Usable from India. But remember: 30% crypto tax + 1% TDS on every trade. High-frequency strategies may not be profitable after tax.

---

### MiroFish ⭐ 24,642

See [Section 1](#1-swarm-intelligence--general-prediction) above.

---

### QuantConnect Lean ⭐ 17,805

**Repo:** [QuantConnect/Lean](https://github.com/QuantConnect/Lean)
**Language:** C#

**What it does:** Professional-grade algorithmic trading engine supporting stocks, forex, crypto, futures, and options. Used by institutional quants and retail traders alike.

**Key features:**
- Cloud or desktop deployment
- Python and C# strategy development
- Backtesting with tick-level data
- Live trading with multiple brokerages
- Built-in universe selection, alpha models, risk management

**Why it matters:** The closest thing to institutional-grade infrastructure available for free. Powers QuantConnect's cloud platform.

**User notes:**
- ⚠️ User 1: ✅ Full access. Connect to Alpaca, IBKR for live trading.
- ⚠️ User 2: ✅ Backtesting works globally. Live trading via IBKR from India.

---

### Hummingbot ⭐ 17,708

**Repo:** [hummingbot/hummingbot](https://github.com/hummingbot/hummingbot)
**Language:** Python

**What it does:** Open-source software for building and running high-frequency crypto market-making and trading bots. Focus on market-making strategies (earning from bid-ask spread).

**Key features:**
- Market making, arbitrage, grid, DCA strategies
- 15+ exchange connectors
- Liquidity mining rewards on some exchanges
- Dashboard for monitoring

**User notes:**
- ⚠️ User 2: Market making generates many small trades — 1% TDS per transaction makes this less viable in India.

---

### OctoBot ⭐ 5,449

**Repo:** [Drakkar-Software/OctoBot](https://github.com/Drakkar-Software/OctoBot)
**Language:** Python

**What it does:** Crypto trading bot with a simple web interface. Supports grid, DCA, and TradingView signal strategies. Has a Polymarket prediction market extension.

**Key features:**
- Web UI for non-coders
- Copy trading support
- TradingView webhook integration
- Prediction market module (Polymarket)

**User notes:**
- ⚠️ User 2: Polymarket module — legal gray area in India. Crypto trading features are fine.

---

## 3. Financial LLMs & AI Agents

### FinGPT ⭐ 18,830

**Repo:** [AI4Finance-Foundation/FinGPT](https://github.com/AI4Finance-Foundation/FinGPT)
**Language:** Jupyter Notebook / Python

**What it does:** Open-source financial large language model. The affordable alternative to Bloomberg Terminal's AI. Fine-tunable on financial data for sentiment analysis, stock prediction, and financial Q&A.

**Key features:**
- Data-centric approach with automated data curation
- Fine-tuning on financial news, earnings calls, SEC filings
- Sentiment analysis, stock movement prediction
- Costs ~$300 to fine-tune (vs $3M for BloombergGPT)
- Released models on HuggingFace

**Why it's huge:** Democratizes financial AI. Instead of paying $20K+/year for Bloomberg, you get a surprisingly capable model for free.

**User notes:**
- ⚠️ Both users: Research/analysis tool. Free to use. Models work for US and some global markets.
- ⚠️ User 2: Could fine-tune on Indian financial news for India-specific predictions.

---

### FinRL ⭐ 14,186

**Repo:** [AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL)
**Language:** Jupyter Notebook / Python

**What it does:** Financial reinforcement learning framework. Trains AI agents to make trading decisions through trial and error, like teaching a robot to trade by letting it practice millions of times.

**Key features:**
- Train DRL agents for stock trading, crypto, portfolio allocation
- Built-in market environments (StockTradingEnv)
- Multiple RL algorithms (A2C, PPO, DDPG, SAC, TD3)
- Paper trading integration
- Tutorials and Jupyter notebooks

**Why it matters:** The first and most popular framework for applying deep RL to trading. Academic-quality with practical applications.

---

### AI-Trader ⭐ 11,717

**Repo:** [HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader)
**Language:** Python

**What it does:** Research project exploring "Can AI Beat the Market?" Provides a live trading benchmark at ai4trade.ai with academic paper backing (arxiv.org/abs/2512.10971).

**Key features:**
- Live trading benchmark with real performance tracking
- Multiple AI trading strategies compared
- Academic rigor with peer-reviewed research
- Open-source for reproducibility

---

### FinRobot ⭐ 6,398

**Repo:** [AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)
**Language:** Jupyter Notebook / Python

**What it does:** AI agent platform for financial analysis using LLMs. Goes beyond FinGPT's single-model approach by unifying multiple AI technologies — LLMs, reinforcement learning, and quantitative analytics.

**Key features:**
- Investment research automation
- Multi-agent framework (research agent, trading agent, risk agent)
- Algorithmic trading strategies
- Risk assessment
- Report generation

---

## 4. Prediction Market Bots

### Polymarket Agents (Official) ⭐ 2,505

**Repo:** [Polymarket/agents](https://github.com/Polymarket/agents)
**Language:** Python

**What it does:** Official developer framework from Polymarket for building AI agents that trade autonomously on prediction markets.

**Key features:**
- LLM-powered decision making
- Market data integration
- Order execution framework
- Extensible agent architecture

**User notes:**
- ⚠️ User 1: ✅ Fully legal to use with Polymarket US.
- ⚠️ User 2: ❌ Prediction market trading is illegal in India. Can study the code for learning purposes only.

---

### Poly-Maker ⭐ 932

**Repo:** [warproxxx/poly-maker](https://github.com/warproxxx/poly-maker)
**Language:** Python

**What it does:** Automated market-making bot for Polymarket. Maintains orders on both sides of the order book, profiting from the spread. Parameters configured via Google Sheets for easy adjustment.

**Key features:**
- Automated bid/ask placement
- Google Sheets configuration (no code changes needed)
- Inventory management
- Risk controls

---

### Fully-Autonomous-Polymarket-AI-Trading-Bot ⭐ 12

**Repo:** [dylanpersonguy/Fully-Autonomous-Polymarket-AI-Trading-Bot](https://github.com/dylanpersonguy/Fully-Autonomous-Polymarket-AI-Trading-Bot)
**Language:** Python

**What it does:** Multi-model ensemble AI bot using GPT-4o, Claude, and Gemini for prediction market forecasting. Small but very feature-complete.

**Key features:**
- Multi-model ensemble (GPT-4o, Claude, Gemini)
- Automated research engine
- 15+ risk checks
- Whale tracking
- Fractional Kelly criterion sizing
- Real-time 9-tab monitoring dashboard
- Paper & live trading modes

**Why it's interesting:** Despite low stars, this is one of the most sophisticated open-source prediction market bots. The multi-model approach (asking 3 different AIs and combining answers) is a smart design pattern.

---

### OctoBot Prediction Market

**Repo:** [Drakkar-Software/OctoBot-Prediction-Market](https://github.com/Drakkar-Software/OctoBot-Prediction-Market)
**Language:** Python

**What it does:** Polymarket extension for OctoBot. Copy trading and arbitrage on prediction markets with a simple interface.

---

## 5. Stock Prediction Models

### Stock-Prediction-Models ⭐ 9,240

**Repo:** [huseinzol05/Stock-Prediction-Models](https://github.com/huseinzol05/Stock-Prediction-Models)
**Language:** Jupyter Notebook

**What it does:** A comprehensive collection of ML and deep learning models for stock forecasting. Includes trading bots and market simulations. Essentially a textbook of every approach to stock prediction.

**Models included:**
- Deep learning: LSTM, GRU, BiLSTM, CNN-LSTM, Attention, Transformer
- Classical ML: Random Forest, XGBoost, SVM, KNN
- RL agents: Q-learning, DQN, Policy Gradient
- Signal processing: Fourier, wavelet transforms
- Simulation: Monte Carlo, agent-based

**Why it matters:** The best single repo for learning every stock prediction technique. Great for education and experimentation.

---

### MachineLearningStocks ⭐ 1,931

**Repo:** [robertmartin8/MachineLearningStocks](https://github.com/robertmartin8/MachineLearningStocks)
**Language:** Python

**What it does:** Beginner-friendly project using scikit-learn for stock predictions. Simple, clean code that's easy to understand and modify.

**User notes:**
- ⚠️ Both users: Great starting project for learning. Replace data source with Indian stocks (jugaad-data) for User 2.

---

## 6. Crypto Trading & Prediction

### Freqtrade ⭐ 47,650

See [Section 2](#2-financial-ai-platforms--frameworks) — the dominant crypto trading bot.

### Hummingbot ⭐ 17,708

See [Section 2](#2-financial-ai-platforms--frameworks) — market-making focus.

### CryptoPredictions ⭐ 264

**Repo:** [alimohammadiamirhossein/CryptoPredictions](https://github.com/alimohammadiamirhossein/CryptoPredictions)
**Language:** Python

**What it does:** Open-source toolbox for crypto price prediction with 30+ indicators and 15+ cryptocurrency support. Uses ML/DL models.

**Key features:**
- 30+ technical indicators auto-generated
- Multiple model architectures (LSTM, GRU, CNN)
- 15+ cryptocurrencies supported
- Configurable prediction horizons
- Evaluation metrics built in

---

## 7. Sports Prediction

### NBA-Machine-Learning-Sports-Betting ⭐ 1,599

**Repo:** [kyleskom/NBA-Machine-Learning-Sports-Betting](https://github.com/kyleskom/NBA-Machine-Learning-Sports-Betting)
**Language:** Python

**What it does:** Predicts NBA game winners and totals using team stats and sportsbook odds. Includes moneyline and over/under predictions with XGBoost and neural net models.

**Key features:**
- Data from 2007-08 through current season
- Matchup feature engineering
- Win probability estimation
- Expected value calculation
- Kelly Criterion bet sizing

**User notes:**
- ⚠️ User 1: ✅ Sports betting is legal in many US states. Check your state.
- ⚠️ User 2: ❌ Sports betting is illegal in India. Use for learning ML only.

---

### Other Notable Sports Projects

- **Football predictions** — Multiple projects for EPL, La Liga, Bundesliga prediction
- **Cricket/IPL** — IPL match win probability predictors using logistic regression (relevant for User 2 as educational projects)
- **WINNER12** — AI football prediction tool claiming 86.3% accuracy

---

## 8. Time Series Forecasting (General Purpose)

These projects can predict ANYTHING with time-series data — stock prices, weather, energy demand, website traffic, etc.

### Time-Series-Library ⭐ 11,727

**Repo:** [thuml/Time-Series-Library](https://github.com/thuml/Time-Series-Library)
**Language:** Python

**What it does:** A library of advanced deep time series models covering 5 mainstream tasks: long-term forecasting, short-term forecasting, imputation, anomaly detection, and classification.

**Models included:** Transformer, Informer, Autoformer, FEDformer, PatchTST, TimesNet, iTransformer, and many more.

**Why it matters:** The most comprehensive collection of state-of-the-art time series models in one repo. If you want to try every modern forecasting approach, start here.

---

### Chronos (Amazon) ⭐ 4,927

**Repo:** [amazon-science/chronos-forecasting](https://github.com/amazon-science/chronos-forecasting)
**Language:** Python

**What it does:** Pretrained foundation models for time series forecasting. Like GPT but for numbers. Zero-shot forecasting — works on data it has never seen before.

**Key features:**
- Pretrained on diverse time series data
- Zero-shot: no training needed for new datasets
- Chronos-2 (Oct 2025): supports univariate, multivariate, and covariate-informed forecasting
- State-of-the-art performance on benchmarks
- HuggingFace integration

**Why it's revolutionary:** You can literally feed it any sequence of numbers and it will forecast the future. No training, no feature engineering.

---

### Other Notable Forecasting Projects

- **PyAF** — Automated time series forecasting (like auto-sklearn for time series)
- **pytorch-forecasting** — Time series forecasting with PyTorch Lightning
- **BasicTS** — Fair and scalable time series forecasting benchmark
- **Microsoft Forecasting** — Best practices and examples from Microsoft Research
- **MOIRAI-2 (Salesforce)** — Foundation model adapting to any frequency, variables, prediction length

---

## 9. Curated Lists & Awesome Repos

These are meta-repositories that catalog hundreds of financial/prediction tools:

| Repo | Stars | Focus |
|------|-------|-------|
| [awesome-quant](https://github.com/wilsonfreitas/awesome-quant) | 24,912 | Libraries for quantitative finance |
| [awesome-ai-in-finance](https://github.com/georgezouq/awesome-ai-in-finance) | 5,157 | LLMs & deep learning in finance |
| [awesome-systematic-trading](https://github.com/wangzhe3224/awesome-systematic-trading) | 3,698 | Systematic trading resources |

**Start here if you want to explore further.** These lists are regularly updated and cover hundreds of tools.

---

## 10. What You Can Build With These

### Beginner Projects (Week 1-4)

| Project | Use These Repos | Difficulty |
|---------|----------------|------------|
| Stock price predictor | MachineLearningStocks, Stock-Prediction-Models | Easy |
| Crypto price forecast | CryptoPredictions, Chronos | Easy-Medium |
| Financial data dashboard | OpenBB | Easy |
| NBA game predictor | NBA-ML-Sports-Betting | Medium |

### Intermediate Projects (Month 2-3)

| Project | Use These Repos | Difficulty |
|---------|----------------|------------|
| Backtested trading strategy | Freqtrade, QuantConnect Lean | Medium |
| AI-powered stock screener | FinGPT + OpenBB | Medium |
| Sentiment-driven signals | FinGPT, FinBERT | Medium |
| Time series any-data predictor | Chronos, Time-Series-Library | Medium |

### Advanced Projects (Month 3+)

| Project | Use These Repos | Difficulty |
|---------|----------------|------------|
| RL trading agent | FinRL | Hard |
| Prediction market bot | Polymarket Agents | Hard |
| Multi-agent simulation | MiroFish | Hard |
| Financial AI analyst | FinRobot | Hard |
| Market-making bot | Hummingbot, Poly-Maker | Hard |

### ⚠️ User 1 (H1B/US) — Recommended Path

1. **Start:** OpenBB for data → MachineLearningStocks for first model
2. **Build:** Freqtrade for crypto bot (paper trade first)
3. **Advance:** FinRL for RL trading → Polymarket Agents for prediction markets
4. **Research:** MiroFish for simulation experiments

### ⚠️ User 2 (India) — Recommended Path

1. **Start:** OpenBB (limited Indian data) + Screener.in → Stock-Prediction-Models for learning
2. **Build:** Freqtrade for crypto (watch 30% tax + 1% TDS impact)
3. **Advance:** FinRL for RL on Indian stocks → Chronos for general forecasting
4. **Research:** MiroFish for simulation → FinGPT fine-tuned on Indian financial news
5. **Avoid:** Prediction market bots (illegal in India)

---

## Summary Table

| Project | Stars | Category | Predicts | User 1 | User 2 |
|---------|-------|----------|----------|--------|--------|
| **OpenBB** | 63,068 | Data Platform | — (data tool) | ✅ | ✅ |
| **Freqtrade** | 47,650 | Crypto Trading Bot | Crypto prices | ✅ | ⚠️ Tax |
| **MiroFish** | 24,642 | Swarm Intelligence | Anything | ✅ | ✅ |
| **awesome-quant** | 24,912 | Curated List | — (resource list) | ✅ | ✅ |
| **FinGPT** | 18,830 | Financial LLM | Sentiment, stocks | ✅ | ✅ |
| **QuantConnect Lean** | 17,805 | Algo Trading Engine | Stocks, crypto, forex | ✅ | ✅ |
| **Hummingbot** | 17,708 | Market Making Bot | Spread capture | ✅ | ⚠️ TDS |
| **FinRL** | 14,186 | Reinforcement Learning | Trading decisions | ✅ | ✅ |
| **AI-Trader** | 11,717 | AI Trading Research | Stock market | ✅ | ✅ |
| **Time-Series-Library** | 11,727 | Time Series Models | Anything numeric | ✅ | ✅ |
| **Stock-Prediction-Models** | 9,240 | Stock ML Models | Stock prices | ✅ | ✅ |
| **FinRobot** | 6,398 | AI Agent Platform | Financial analysis | ✅ | ✅ |
| **OctoBot** | 5,449 | Crypto Bot | Crypto + predictions | ✅ | ⚠️ |
| **Chronos** | 4,927 | Foundation Model | Any time series | ✅ | ✅ |
| **Polymarket Agents** | 2,505 | Prediction Market | Event outcomes | ✅ | ❌ |
| **MachineLearningStocks** | 1,931 | Stock Prediction | Stock prices | ✅ | ✅ |
| **NBA-ML-Betting** | 1,599 | Sports Prediction | NBA games | ✅ | ❌ Legal |
| **Poly-Maker** | 932 | Market Making | Prediction spreads | ✅ | ❌ |
| **CryptoPredictions** | 264 | Crypto ML | Crypto prices | ✅ | ⚠️ Tax |

---

## Key Takeaways

1. **MiroFish is unique** — The swarm intelligence approach (simulating worlds of AI agents) is fundamentally different from traditional ML prediction. Worth experimenting with.

2. **The AI4Finance ecosystem is massive** — FinGPT (18K stars), FinRL (14K), FinRobot (6K) form a complete suite for financial AI. All from the same foundation.

3. **Chronos is a game-changer** — Amazon's pretrained time series model works zero-shot on ANY numeric data. No training needed. Feed it numbers, get predictions.

4. **Freqtrade is the crypto king** — At 47K stars, it's the most battle-tested open-source crypto trading bot. Start here for crypto.

5. **OpenBB replaces Bloomberg** — At 63K stars, it's the most popular financial open-source project. Essential data infrastructure.

6. **Prediction market bots exist but are niche** — Polymarket's official agents repo (2.5K stars) is the best starting point. Legal only for User 1.

7. **Most projects are Python** — The entire ecosystem runs on Python + Jupyter. Learning Python is the single highest-ROI skill for this domain.

---

*Star counts as of March 2026. Projects are actively evolving — check GitHub for latest updates.*
