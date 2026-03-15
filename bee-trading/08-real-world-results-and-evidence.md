# Real-World Results and Evidence: Prediction Markets, Trading Bots, and ML Trading

> **Research Date:** March 2026
> **Purpose:** Honest, evidence-based assessment of what actually works (and what doesn't) in open-source prediction/trading tools

## User Profiles

- **User 1 (H1B/US):** Indian citizen on H1B visa, employed in the United States
  - Can invest/trade passively (stocks, crypto, prediction markets) as long as it does not resemble self-employment or a business
  - Active day-trading or frequent profit-driven trading may jeopardize H1B status if it "looks like a job"
  - Prediction markets (Kalshi) are CFTC-regulated in the US; position limits capped at $25,000 per event contract
  - Polymarket is NOT available to US residents (geo-blocked; US persons are restricted)
  - State-level restrictions vary (NJ, NV have issued cease-and-desist orders on some prediction markets)
  - **Key risk:** Any activity that USCIS interprets as unauthorized employment can result in visa revocation
  - **Recommendation:** Consult immigration attorney before engaging in any regular trading activity; passive investing (ETFs, stocks) is generally safe

- **User 2 (India):** Indian citizen in India, unemployed
  - Crypto trading is legal in India but taxed at 30% flat + 1% TDS on every transaction
  - Polymarket is effectively banned in India under the Promotion and Regulation of Online Gaming Act 2025; telecom operators use DPI to block connections; bank accounts can be frozen for interacting with blacklisted addresses
  - Domestic "opinion trading" platforms like Probo exist in a regulatory grey area (classified as skill games, but face gambling allegations)
  - Algorithmic trading on Indian exchanges is regulated by SEBI; no separate crypto algo law exists
  - FEMA (Foreign Exchange Management Act) violations possible if converting INR to stablecoins for offshore betting
  - **Key risk:** Legal jeopardy from offshore prediction markets; punitive taxation on crypto gains
  - **Recommendation:** Focus on SEBI-regulated markets, domestic platforms, or skill-development; avoid Polymarket entirely

---

## 1. The Harsh Reality: Success Rates

### Day Trading / Retail Trading

The data is devastating and remarkably consistent across studies:

| Study / Source | Finding |
|---|---|
| Brazilian futures study (Chague et al.) | **97% of day traders lost money** over 300 days; only 7% persisted the full period |
| Second independent study | **97% lost money** -- the exact same figure as the Brazilian study |
| University of California | Only **13%** maintained profitability over 6 months; only **1%** consistently profitable over 5+ years |
| FINRA 2020 report | **72%** of day traders ended the year in deficit |
| Retail FX brokers (12 brokers studied) | **~70%** lost money each quarter, highly consistent across brokers |
| CFTC study (36,000+ accounts) | **60%** lost money; median losses $100-$200 per session |
| Overall retail forex (2024 broker data) | **86%** of retail traders lost money |

**Sources:**
- [Day Trading Statistics 2025 - QuantifiedStrategies](https://www.quantifiedstrategies.com/day-trading-statistics/)
- [24 Statistics Why Most Traders Lose Money - Tradeciety](https://tradeciety.com/24-statistics-why-most-traders-lose-money)
- [Is Day Trading Profitable? - NewTrading](https://www.newtrading.io/is-day-trading-profitable/)
- [Every Major Day Trading Study Reviewed - Medium](https://medium.com/@faisal_haroon/i-reviewed-every-major-day-trading-study-from-the-last-25-years-the-data-is-devastating-4b116273b956)

### Algorithmic Trading

- Most quant traders fail; the field is extremely competitive
- Consistent annual returns above 20% are rare and generally unsustainable for retail traders
- Realistic expectations for profitable retail algo traders: **5-20% annual returns** (with significant risk)
- The most active traders underperformed less active traders even on a gross return basis (UC Berkeley study)
- Algorithmic trading can be profitable "provided you get a couple of things right" -- but most never do

**Sources:**
- [Can Algorithmic Traders Still Succeed? - QuantStart](https://www.quantstart.com/articles/Can-Algorithmic-Traders-Still-Succeed-at-the-Retail-Level/)
- [Is Algorithmic Trading Profitable? - QuantifiedStrategies](https://www.quantifiedstrategies.com/is-algorithmic-trading-profitable/)
- [Retail Trades Positively Predict Returns but Are Not Profitable - UC Berkeley](https://faculty.haas.berkeley.edu/odean/Papers%20current%20versions/resolving_a_paradox_retail_trades_positively_predict_returns_but_are_not_profitable.pdf)

### Prediction Markets

- Only **0.51% of wallets** on Polymarket have realized profits exceeding $1,000
- **80% of Polymarket participants are net losers**
- On Kalshi, low-price contracts win far less often than required to break even (favorite-longshot bias)
- "Like poker, sharp players profit while casual participants fund both their winnings and the house"

**Sources:**
- [Polymarket Leaderboard 2025 - PolyTrack](https://www.polytrackhq.app/blog/polymarket-leaderboard-top-traders)
- [Economics of Kalshi - CEPR](https://cepr.org/voxeu/columns/economics-kalshi-prediction-market)

---

## 2. Prediction Market Success Stories (Polymarket, Kalshi)

### The French Whale: Theo ($85 Million)

The single most famous prediction market success story. Key facts:

- **Profit:** $78.7M - $85M (estimates vary by analysis; Chainalysis estimates ~$85M)
- **Identity:** French former bank trader known as "Theo" or "Fredi9999"
- **Accounts:** Operated up to 11 accounts (initially thought to be 4)
- **Bets:** Trump to win presidency, swing states (PA, MI, WI), and popular vote
- **Strategy:** "Neighbour polling" -- commissioned private surveys asking people who their *neighbours* supported (not who they'd vote for themselves), reasoning people are more honest about others' preferences
- **Edge:** Private polling data from a major pollster with "mind-blowing" results favoring Trump
- **Capital deployed:** $30M+ in bets
- **Aftermath:** France investigating Polymarket; regulatory scrutiny

**Key insight:** Theo's edge was NOT algorithmic -- it was an **information edge** from privately commissioned polling data that contradicted public polls. He was essentially a sophisticated pollster who expressed his conviction through prediction markets.

**Sources:**
- [Polymarket Whale Made $85M - Yahoo Finance](https://finance.yahoo.com/news/polymarket-whale-actually-made-85-050139914.html)
- [French Whale $80M on Polymarket - CBS News](https://www.cbsnews.com/news/french-whale-made-over-80-million-on-polymarket-betting-on-trump-election-win-60-minutes/)
- [How Theo Made $85M - The Free Press](https://www.thefp.com/p/french-whale-makes-85-million-on-polymarket-trump-win)
- [Mystery Trump Whale - Newsweek](https://www.newsweek.com/trump-whale-trader-wins-50-million-election-polls-1982768)

### Other Top Polymarket Traders

| Trader | Profit | Strategy |
|---|---|---|
| WindWalk3 | $1.1M+ | Predictions on RFK Jr. |
| 1j59y6nk | $1.4M | Sports and games markets; single $90K win |
| Erasmus | $1.3M+ | Political markets; polling analysis + policy tracking |

**Sources:**
- [10 Top Polymarket Traders - Webopedia](https://www.webopedia.com/crypto/learn/top-polymarket-traders/)
- [Polymarket Top Traders - Polyburg](https://polyburg.com/polymarket-top-traders)

### Polymarket Bot Profits (Arbitrage)

- **$40 million** in arbitrage profits extracted from Polymarket between April 2024 and April 2025 (peer-reviewed research from IMDEA Networks Institute, analyzing 86 million bets)
- Top 3 wallets alone: 10,200+ bets, $4.2M in profits
- Market makers earned $20M+ in 2024; active makers reported $200-$800/day during elections
- One bot turned **$313 into $414,000** in a single month trading BTC/ETH/SOL 15-minute up/down markets
- Average arbitrage opportunity duration: **2.7 seconds** (down from 12.3s in 2024)
- 73% of arbitrage profits captured by sub-100ms execution bots

**Caveat:** These are sophisticated, technically demanding operations requiring low-latency infrastructure and significant programming expertise.

**Sources:**
- [Arbitrage Bots Dominate Polymarket - Yahoo Finance](https://finance.yahoo.com/news/arbitrage-bots-dominate-polymarket-millions-100000888.html)
- [Polymarket HFT Traders - QuantVPS](https://www.quantvps.com/blog/polymarket-hft-traders-use-ai-arbitrage-mispricing)
- [Polymarket Six Profit Models - ChainCatcher](https://www.chaincatcher.com/en/article/2233047)

### Kalshi Success Stories

- **Logan Sudeith** (25, former financial risk analyst): Made $100,000 in one month; biggest wins include $40,236 on Time Person of the Year, $11,083 on most-searched Google person, $7,448 on NYC mayoral race
- Kalshi processed **$1 billion** in trading volume during 2024 election night; 1 million new sign-ups
- DL Trading and Susquehanna rumored to be largest market makers on Kalshi
- Sports markets offer edge to those with real-time data procurement capabilities

**Sources:**
- [How Prediction Market Traders Make Money - NPR](https://www.npr.org/2026/01/17/nx-s1-5672615/kalshi-polymarket-prediction-market-boom-traders-slang-glossary)
- [Economics of Kalshi - CEPR](https://cepr.org/voxeu/columns/economics-kalshi-prediction-market)
- [Kalshi: The Winner of the 2024 Election - Startup Signals](https://startupsignals.substack.com/p/kalshi-the-winner-of-the-2024-election)

---

## 3. Crypto Bot Results (Freqtrade, etc.)

### Freqtrade Real Results

**The Backtest vs. Reality Gap:**
- One documented case: backtesting showed **+17.07% profit**; live trading produced **-0.79%**
- This gap is a well-known and frequently discussed problem in the Freqtrade community

**Real Money Experience (Documented Blog Post):**
- Trader ran Freqtrade connected to Binance, trading 20 crypto coins for one month
- Week 1: Made 19.464 USDT (~1.9% profit); projected 10% monthly
- Week 2: Market became volatile; lost 109.94 USD
- Day 25: Net loss of **-121.78 USDT (-12.2% of initial investment)**

**Two-Year Freqtrade User Review:**
- Powerful tool but requires significant learning investment
- "If you're looking for a plug-and-play solution that guarantees profits, look elsewhere"
- Even the best strategies need solid risk controls: stop-losses, take-profit settings, trailing stops, position sizing

**Official Freqtrade Warning:**
- "The bot will always be a gamble, which should leave you with modest wins on monthly basis"
- Public strategies are generally not good performers
- Strategies are for educational purposes only; do not risk money you're afraid to lose

**Sources:**
- [Backtesting vs Real Results - Freqtrade GitHub Issue #2662](https://github.com/freqtrade/freqtrade/issues/2662)
- [Trading Bot Experience for a Month - LinkedIn](https://www.linkedin.com/pulse/how-much-can-you-make-trading-bot-my-experience-month-gothireddy)
- [Freqtrade Review - Gainium](https://gainium.io/blog/freqtrade)

### Other Crypto Trading Bot Results

| Platform/Bot | Reported Performance | Notes |
|---|---|---|
| 3Commas / Trendhoo | 18.7% annualized; 193% ROI | Drawdowns capped at 12% |
| Grid trading bots (general) | 15-40% annualized in ranging markets | Requires 10-20% price fluctuation conditions |
| Bitsgap Grid Bot | 11% average 30-day return (Nov 2025) | Not guaranteed; market-dependent |
| DCA bots (2024-2026) | Outperformed lump-sum in ~65% of tested scenarios | Most conservative strategy |

**Key caveat:** "Most retail bots barely break even. Fees eat into gains, market noise throws off signals, and pro-level algorithms leave smaller players in the dust."

**Sources:**
- [AI Bot Trading Profitable 2025? - AgentiveAIQ](https://agentiveaiq.com/blog/is-ai-bot-trading-profitable-the-2025-reality-check)
- [Most Profitable Trading Bots 2026 - WunderTrading](https://wundertrading.com/journal/en/reviews/article/top-profitable-trading-bots)
- [Top Automated Trading Bots - Nansen](https://www.nansen.ai/post/top-automated-trading-bots-for-cryptocurrency-in-2025-maximize-your-profits-with-ai)

---

## 4. ML/AI Stock Prediction: Academic Evidence

### What Academic Studies Actually Show

**The Promising Claims:**
- Deep neural networks generally outperform shallow neural networks and representative ML models for stock return prediction (Japanese market study)
- Neural networks with 1-2 hidden layers achieved long-short returns of 0.66% and 0.85% per month
- ML methods are better at predicting returns of smaller stocks (where news is incorporated more slowly)
- Technical trading rules using ML can find profitable opportunities, but profitability decreases through time as markets become more efficient

**The Sobering Reality:**
- "There is a huge divergence between academic literature and its claims and limited (and not always successful) adoption of AI in the investment decision-making process" (PMC systematic review)
- Out-of-sample accuracy often drops to ~50% (essentially random)
- Random Forest models showed strong in-sample performance but "failure to generalize to unseen data suggests that high-frequency stock price movements are dominated by noise"
- Hybrid strategies combining multiple indicators "failed to outperform the buy-and-hold benchmark in return generation"
- "The profitability of a trading strategy might be significantly overstated since it was actually based on information that could not have been used in real-time trading"

**The Overfitting Problem:**
- Testing just 7 strategy variations can produce at least one 2-year backtest with Sharpe ratio >1.0 -- even if true expected performance is zero
- Survivorship bias inflates returns: 7.4% annualized (survivorship-free) vs. 9.0% (biased), a 1.6% gap
- A dataset covering last 10 years could exclude up to 75% of stocks that were actually trading during that period
- Real example: Quantitative Investment Management (QIM) expected 20% return; got only 8% after correcting for survivorship bias

**Sources:**
- [ML and the Stock Market - Cambridge Core](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/machine-learning-and-the-stock-market/F54ECC9DA40067B35261B32691D1DDA2)
- [Why Most Published ML Research Findings Do Not Live Up to Promise - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8019690/)
- [Deep Learning in Stock Market - Systematic Survey - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9245389/)
- [Survivorship Bias in Backtesting - LuxAlgo](https://www.luxalgo.com/blog/survivorship-bias-in-backtesting-explained/)
- [Common Pitfalls in Backtesting - Medium](https://medium.com/funny-ai-quant/ai-algorithmic-trading-common-pitfalls-in-backtesting-a-comprehensive-guide-for-algorithmic-ce97e1b1f7f7)

### Hedge Funds and Open-Source Tools

- QuantConnect: 300,000+ users, 375,000+ live strategies deployed, processing $45B+ notional volume/month
- No public evidence that retail traders using open-source ML tools consistently beat the market after transaction costs
- Institutional quant funds have massive infrastructure, data, and talent advantages

**Sources:**
- [QuantConnect - Open Source Trading Platform](https://www.quantconnect.com/)
- [AI Hedge Fund - GitHub](https://github.com/virattt/ai-hedge-fund)

---

## 5. Reinforcement Learning Trading (FinRL etc.)

### FinRL Backtesting Results (Impressive on Paper)

| Metric | Result |
|---|---|
| Ensemble strategy Sharpe ratio | 2.81 |
| Ensemble annual return | 52.61% |
| A2C agent Sharpe ratio | 2.24 |
| PPO agent Sharpe ratio | 2.23 |
| FinRL-Podracer cumulative returns | 149.5% and 362.4% |
| FinRL-Podracer annual returns | 56.4% and 111.5% |

### The Critical Gap: No Real Trading Evidence

- **"A trained agent cannot be directly deployed in real-world markets due to the simulation-to-reality gap"** -- FinRL project's own acknowledgment
- The project provides paper trading demos but no confirmed live money results
- FinRL-Meta aims to enable real-time paper trading to "facilitate the real-world adoption" (meaning it hasn't happened yet)
- "The current body of literature lacks substantial evidence supporting the practical efficacy of reinforcement learning agents"
- Multiple studies "not able to provide evidence of the strategy performance in live trading"

### Why the Gap Exists

- Transaction costs, slippage, and market impact are often not modeled
- Training on historical data leads to overfitting to past regimes
- Market microstructure changes make backtested strategies stale
- RL agents can be brittle -- small changes in market conditions cause catastrophic failures

**Sources:**
- [FinRL Paper - arXiv](https://arxiv.org/pdf/2111.09395)
- [FinRL GitHub](https://github.com/AI4Finance-Foundation/FinRL)
- [FinRL Benchmark Documentation](https://finrl.readthedocs.io/en/latest/finrl_meta/Benchmark.html)
- [Reinforcement Learning in Finance - Neptune.ai](https://neptune.ai/blog/7-applications-of-reinforcement-learning-in-finance-and-trading)

---

## 6. Sports Betting with ML

### What the Research Shows

**Promising Results:**
- ML model selection based on **calibration** (not accuracy) yields dramatically better returns: +34.69% ROI vs. -35.17% ROI
- Best-case calibration-based model: +36.93% ROI vs. +5.56% for accuracy-based
- One model achieved **58% success rate** across ~140 games (profitable at -110 odds, where 53% is breakeven)
- Ensemble ML algorithms on 47,856 European football matches (2006-2018): **1.58% return per match**
- Partial Kelly criterion (coefficient 0.50, 10% threshold) as bet sizing: potentially ~80% annual ROI over 11 years

**The Catch:**
- Only **3-5% of sports bettors** are profitable long-term
- Market inefficiencies exist but are **short-lived and do not occur persistently** over time or across leagues
- Bookmakers adjust; edges erode quickly
- The key is not just predicting outcomes but finding where bookmaker odds are mispriced (decorrelating from the bookmaker's predictions)

**The Strategy That Works (According to Research):**
1. Build a model that predicts outcomes
2. Compare predictions to bookmaker odds
3. Bet only where there's a positive expected value gap
4. Use proper bankroll management (fractional Kelly)
5. Specialize in specific leagues/sports where you have domain knowledge

**Sources:**
- [Exploiting Sports-Betting Market Using ML - ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S016920701930007X)
- [ML for Sports Betting: Accuracy vs. Calibration - ScienceDirect](https://www.sciencedirect.com/science/article/pii/S266682702400015X)
- [Beating the Bookies with ML - KDnuggets](https://www.kdnuggets.com/2019/03/beating-bookies-machine-learning.html)
- [Systematic Review of ML in Sports Betting - arXiv](https://arxiv.org/abs/2410.21484)
- [Beating the Books Using ML - Medium/CodeX](https://medium.com/codex/beating-the-books-using-machine-learning-to-make-money-sports-betting-7b5195b405d2)

---

## 7. Time Series Forecasting Accuracy

### LSTM for Stock Prediction

| Model / Study | Metric | Result |
|---|---|---|
| Advanced LSTM with sentiment | MAPE | 2.72% (on unseen test data) |
| LSTM for S&P 500 (Bao et al.) | R-score | Below 88% |
| LSTM for China stock returns (Chen et al.) | Accuracy improvement | From 14.3% to 27.2% vs random prediction |
| VMD-TMFG-LSTM (hybrid) | RMSE reduction | 69.76% |
| VMD-TMFG-LSTM (hybrid) | MAE reduction | 71.41% |

**Critical caveat:** Low MAPE on stock price prediction is misleading. Stock prices are highly autocorrelated (today's price is very close to yesterday's), so a naive "predict yesterday's price" model also has low MAPE. What matters is whether the model can predict **direction** and **magnitude of changes** accurately enough to profit after costs.

### Chronos (Amazon) for Financial Forecasting

- Zero-shot accuracy superior to AutoARIMA and AutoETS (without seeing the data)
- Chronos-Bolt: 5% lower error, 250x faster, 20x more memory efficient
- 600M+ downloads from Hugging Face
- Real-world deployment: Deutsche Bahn uses it for construction cost prediction and revenue forecasting
- **Not designed specifically for financial trading; general-purpose time series model**

**Sources:**
- [Chronos-2 - Amazon Science](https://www.amazon.science/blog/introducing-chronos-2-from-univariate-to-universal-forecasting)
- [Stock Market Prediction Using LSTM - ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1877050920304865)
- [Advanced LSTM Stock Prediction - arXiv](https://arxiv.org/html/2505.05325v1)

---

## 8. What Actually Works (Evidence-Based)

### Tier 1: Strongest Evidence of Real Profitability

1. **Information-edge prediction market trading** (Theo model)
   - Have genuinely superior information (e.g., private polling)
   - Express conviction in prediction markets
   - Requires significant capital and domain expertise
   - NOT scalable or repeatable for most people

2. **Automated arbitrage on prediction markets**
   - $40M extracted from Polymarket in one year
   - Requires sub-100ms execution, technical infrastructure, programming expertise
   - Opportunities shrinking (2.7-second windows in 2025)
   - Zero-sum: your gain is someone else's loss

3. **Market making on prediction markets**
   - $20M+ earned by market makers in 2024
   - $200-$800/day during high-volume periods
   - Requires capital, sophistication, and infrastructure
   - DL Trading, Susquehanna are professional participants

### Tier 2: Evidence Exists But Results Are Mixed

4. **Sports betting with calibrated ML models**
   - Academic evidence of positive ROI (up to +37% in best cases)
   - Requires domain specialization, not just generic ML
   - Edges are short-lived; bookmakers adapt
   - Fractional Kelly sizing critical for survival

5. **Grid/DCA crypto bots in ranging markets**
   - 15-40% annualized in favorable conditions
   - Performance is highly market-regime dependent
   - DCA bots outperformed lump-sum in ~65% of scenarios
   - Requires discipline not to override during drawdowns

6. **Quantitative value/momentum strategies**
   - Long academic track record (Fama-French factors)
   - 5-20% annual returns realistic for disciplined retail quant traders
   - Requires proper backtesting methodology (survivorship-free data, walk-forward optimization)

### Tier 3: Mostly Doesn't Work for Retail

7. **Deep learning stock prediction**
   - Out-of-sample accuracy often drops to ~50%
   - Academic papers oversell; real deployment disappoints
   - Transaction costs eat whatever small edge might exist

8. **Reinforcement learning trading (FinRL etc.)**
   - No documented real-money success
   - Simulation-to-reality gap is acknowledged by the project itself
   - Purely academic exercise at this stage

---

## 9. What Doesn't Work (Common Failures)

### Guaranteed Failure Patterns

1. **Using public strategies without modification**
   - If everyone can see it, the edge is already gone
   - Freqtrade official warning: "most public strategies are not good performers"

2. **Trusting backtests at face value**
   - Backtest-to-reality gap is enormous and well-documented
   - Survivorship bias alone can inflate returns by 1.6% annually
   - Testing 7 strategies produces at least one with Sharpe >1.0 by chance alone
   - Example: 17.07% backtest vs -0.79% live trading (Freqtrade case)

3. **Using LSTM/deep learning to predict stock prices and trading on it**
   - Low MAPE is misleading due to price autocorrelation
   - Models fail to generalize to unseen market regimes
   - "High-frequency stock price movements are dominated by noise"

4. **Expecting FinRL or similar RL agents to work in real trading**
   - Zero documented live trading success
   - Fragile to market regime changes
   - Training is computationally expensive and unstable

5. **Trying to manually arbitrage prediction markets**
   - Bots close gaps in 2.7 seconds (average)
   - 73% of profits go to sub-100ms bots
   - Human reaction time cannot compete

6. **Over-optimizing / curve fitting**
   - The more parameters you tune, the worse live performance will be
   - "Optimization bias: fine-tuning with available data, testing with concerns that had happened, not what could happen"

7. **Ignoring transaction costs, slippage, and taxes**
   - Even strategies with a theoretical edge can become unprofitable after real-world costs
   - India's 30% tax + 1% TDS on crypto makes many marginal strategies unviable
   - Market impact on illiquid prediction market contracts can eliminate profits

### Common Psychological Traps

- **Survivorship bias in success stories:** You only hear from winners; the 97% who lost money are silent
- **Dunning-Kruger effect:** Beginners overestimate their ability to beat markets
- **Sunk cost fallacy:** Continuing to trade a losing strategy because of time invested
- **Gambler's fallacy:** "I'm due for a win" after a losing streak
- **Confirmation bias:** Seeking out success stories while ignoring failure data

---

## 10. Lessons from Real Traders

### Lesson 1: The Edge Is Information, Not Technology
Theo didn't use AI or fancy algorithms. He used **private polling data** and domain expertise. The biggest prediction market win in history came from better information, not better code.

### Lesson 2: The House (Almost) Always Wins
- 97% of day traders lose money
- 80% of Polymarket participants are net losers
- Only 0.51% of Polymarket wallets profit >$1,000
- Only 3-5% of sports bettors are profitable long-term
- 86% of retail forex traders lose money

### Lesson 3: Bots Beat Humans at Execution, Not Strategy
- Bots are excellent at executing a well-defined strategy consistently
- They cannot discover new strategies or adapt to regime changes
- "Human oversight remains critical -- even the most sophisticated AI trading bots require human oversight and strategic direction"

### Lesson 4: Backtests Lie
- The backtest-to-live-trading gap is the #1 killer of retail algo traders
- Always use walk-forward analysis, not just in-sample optimization
- Use survivorship-free datasets
- Account for transaction costs, slippage, and market impact
- If it looks too good to be true, it is

### Lesson 5: Risk Management > Strategy
- Position sizing and risk management determine survival more than entry signals
- Fractional Kelly criterion (0.3-0.5x Kelly) is the empirically supported approach
- Never risk money you cannot afford to lose -- this isn't just a disclaimer, it's the core lesson from every study

### Lesson 6: Specialization Beats Generalization
- Top Polymarket traders specialize (politics, sports, crypto prices)
- Sports betting ML works best when you have deep domain knowledge of specific leagues
- Generic "predict the market with ML" approaches consistently fail

### Lesson 7: The Real Money Is in Infrastructure
- Market makers earned $20M+ on Polymarket in 2024
- Arbitrage bots extracted $40M from Polymarket in one year
- QuantConnect processes $45B+ notional volume monthly (as a platform, not a trader)
- The pick-and-shovel sellers consistently outperform the gold miners

---

## 11. User-Specific Notes

### User 1: H1B/US

**What You Can Legally and Practically Do:**
- Passive stock/ETF investing (safest from immigration perspective)
- Use Kalshi for prediction market trading (CFTC-regulated, $25K position limit per event)
- Build and paper-trade algorithmic strategies (learning + portfolio skill)
- Use QuantConnect or similar platforms for strategy development
- Sports prediction models (for Kalshi sports markets, within position limits)

**What to Avoid:**
- Polymarket (US persons are geo-blocked and restricted)
- Any trading activity that could be construed as self-employment or running a business
- Day trading at high frequency (could look like a job to USCIS)
- Offshore crypto exchanges or unregulated platforms

**Realistic Expectations:**
- Kalshi with domain expertise and careful position sizing: potentially profitable but capped at $25K exposure per event
- Passive index investing: historically 7-10% annual returns
- Building algo trading skills: valuable career asset even if trading itself doesn't profit

**Best Approach:**
1. Start with Kalshi, small positions, in areas of domain expertise
2. Track all P&L meticulously
3. Consult immigration attorney about acceptable trading frequency
4. Treat it as education and skill-building, not primary income

### User 2: India

**What You Can Legally and Practically Do:**
- Trade on SEBI-regulated Indian stock exchanges (NSE, BSE)
- Use domestic crypto exchanges registered with FIU-IND (CoinDCX, WazirX)
- Build ML models for Indian cricket betting (via domestic platforms, if legally structured as skill games)
- Algorithmic trading on Indian markets via platforms like Algomojo
- Develop and sell trading strategies/tools (entrepreneurship path)
- Opinion trading on platforms like Probo (grey area; legal risk exists)

**What to Avoid:**
- Polymarket (banned under PROGA 2025; DPI blocking; bank account freeze risk)
- Converting INR to stablecoins for offshore betting (FEMA violation)
- Any platform not registered with FIU-IND

**Realistic Expectations:**
- Indian stock market algo trading: 5-15% annual returns if done well
- Crypto trading in India: punitive taxation (30% + 1% TDS) makes marginal strategies unviable
- Need a clear, substantial edge to overcome India's tax drag on crypto
- IPL/cricket prediction models could have potential on domestic platforms (Probo) if legal risks are acceptable

**Best Approach:**
1. Focus on Indian stock markets first (better tax treatment than crypto)
2. Build ML skills that are marketable for employment (quant finance, data science)
3. If trading, start with paper trading and small positions
4. Consider the entrepreneurship angle: building trading tools/platforms can be more profitable than trading itself
5. Avoid crypto trading unless edge is very substantial (30% tax floor makes most strategies lose money)

---

## Summary Table: Evidence-Based Verdict

| Activity | Evidence of Profitability | Realistic for Retail? | User 1 (H1B/US) | User 2 (India) |
|---|---|---|---|---|
| Prediction market (information edge) | Strong ($85M case study) | Only with genuine domain expertise | Kalshi only, $25K cap | Restricted/illegal |
| Prediction market arbitrage (bots) | Strong ($40M documented) | Only with technical infrastructure | Not viable (Polymarket blocked) | Not viable (Polymarket blocked) |
| Market making (prediction markets) | Strong ($20M+ in 2024) | Requires capital + sophistication | Possible on Kalshi | Not viable |
| Sports betting with calibrated ML | Moderate (academic studies) | Possible with specialization | Via Kalshi sports markets | Domestic platforms (grey area) |
| Crypto grid/DCA bots | Moderate (15-40% in right conditions) | Yes, but market-dependent | Possible | Possible (high tax drag) |
| Stock algo trading (quantitative) | Moderate (5-20% annual) | Yes, with proper methodology | Yes | Yes (Indian markets) |
| Deep learning stock prediction | Weak (out-of-sample ~50%) | No | Not recommended | Not recommended |
| RL trading (FinRL) | None (no live evidence) | No | Not recommended | Not recommended |
| LSTM time series forecasting | Weak for trading | No | Not recommended | Not recommended |
| Passive index investing | Strong (7-10% historical) | Yes | Best risk-adjusted option | Yes (Indian index funds) |

---

*This document represents research compiled from web sources as of March 2026. Markets evolve; strategies that work today may not work tomorrow. None of this constitutes financial or legal advice. Both users should consult appropriate legal counsel (immigration attorney for User 1, financial/legal advisor for User 2) before engaging in any trading activity.*
