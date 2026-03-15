# Prediction Markets: Comprehensive Research Guide

Compiled: 2026-03-14

---

## ⚠️ Important: User-Specific Legal Status

Prediction markets have very different legal status depending on your jurisdiction. Read this section carefully before proceeding.

### **⚠️ User 1 (H1B/US)** — Indian citizen on H1B visa working as an employee in the US

- **CAN legally use Kalshi** (CFTC-regulated, accepts US residents)
- **CAN legally use Polymarket US** (CFTC-regulated)
- Prediction market profits are taxable income in the US
- This is considered passive investment activity — fine on H1B (similar to stock/options trading, no "active business" issues)
- Some states may restrict access to certain platforms (check Kalshi's and Polymarket's state availability lists)

### **⚠️ User 2 (India)** — Indian citizen living in India, currently unemployed

- ❌ **CRITICAL: Prediction markets are largely ILLEGAL in India**
- The Public Gambling Act, 1867 prohibits most forms of betting
- Online betting/gambling is banned or heavily restricted in most Indian states
- Some states (Goa, Sikkim, Meghalaya) have partial exceptions for certain forms of gambling but these don't clearly cover prediction markets
- **Polymarket:** Technically accessible from India (international version, crypto-based) but operates in a **LEGAL GRAY AREA**. Using it could violate Indian gambling laws and RBI forex regulations.
- **Kalshi:** US-only, **NOT available** to Indian residents
- **PredictIt:** US-only
- **Safe alternatives:**
  - Metaculus (no money, purely reputation-based) ✅ Legal
  - Manifold Markets (play money only) ✅ Legal
  - Probo (Indian prediction market app, operates in legal gray area using "opinion trading" framing) ⚠️ Gray area
- **Probo / MPL / similar Indian apps:** Some Indian startups have launched "opinion trading" platforms. Their legal status is uncertain and being debated. DGIPR and state gambling commissions are watching closely.
- Using crypto to access international prediction markets also potentially violates RBI's restrictions on using foreign exchange for prohibited purposes (betting/gambling is a prohibited purpose under FEMA).

---

## 1. What Are Prediction Markets?

### The Basic Concept

A prediction market is a marketplace where people trade contracts whose payouts depend on the outcome of future events. Think of it as a stock market, but instead of trading shares of companies, you trade shares of "will X happen?" The price of each share reflects what the market collectively believes the probability of that event is.

**Simple example:** A market asks "Will it rain in New York on March 20?" If you can buy a "Yes" share for $0.30, the market is collectively estimating a 30% chance of rain. If it does rain, your $0.30 share pays out $1.00 (you profit $0.70). If it doesn't rain, your share is worth $0.00 (you lose $0.30).

### How They Work Mechanically

**Binary outcome markets** are the most common type:

| Concept | Explanation |
|---------|-------------|
| **Binary outcome** | Every market resolves to either YES or NO (1 or 0) |
| **Shares** | You buy "Yes" shares or "No" shares for any market |
| **Price = probability** | A share priced at $0.65 implies a 65% probability |
| **Payout** | Winning shares pay $1.00; losing shares pay $0.00 |
| **Profit** | Your profit = $1.00 minus what you paid (if you win) |
| **Complementary pricing** | Yes + No prices always sum to ~$1.00 (e.g., Yes at $0.65 means No at $0.35) |

**How a trade works step by step:**

1. You see a market: "Will the Fed cut rates in June 2026?"
2. The current price of "Yes" is $0.42 (market says 42% chance)
3. You believe it's more likely than 42%, so you buy 100 "Yes" shares at $0.42 each (cost: $42)
4. If the Fed does cut rates: your shares pay out $1.00 each = $100. Profit = $58
5. If they don't: your shares pay $0.00. Loss = $42
6. You can also sell your shares before the event resolves if the price moves in your favor

**Non-binary markets** also exist:
- **Multi-outcome:** "Who will win the 2028 election?" with separate Yes/No markets for each candidate
- **Scalar/range:** "What will GDP growth be?" with brackets like 0-1%, 1-2%, 2-3%, etc.

### History and Origins

| Year | Milestone |
|------|-----------|
| **1500s-1800s** | Informal political betting markets in Europe; odds on papal elections in the Vatican |
| **1868-1940s** | Wall Street "curb exchanges" openly traded election outcomes; often more accurate than polls |
| **1988** | Iowa Electronic Markets (IEM) launched at University of Iowa — first modern academic prediction market |
| **2001** | DARPA proposed a "Policy Analysis Market" for geopolitical events (cancelled after political controversy) |
| **2003** | TradeSports/InTrade launched in Ireland, became the dominant real-money prediction market |
| **2008** | InTrade accurately predicted 49/50 states in the US presidential election |
| **2012** | InTrade shut down due to regulatory issues with the CFTC |
| **2014** | Augur project started (decentralized prediction market on Ethereum) |
| **2014** | PredictIt launched with CFTC no-action letter for academic research |
| **2020** | Polymarket founded — crypto-native prediction market on Polygon |
| **2020** | Kalshi founded — first CFTC-regulated prediction market exchange |
| **2023** | Manifold Markets gained popularity as a play-money forecasting platform |
| **2024** | Polymarket exploded in popularity during US presidential election, reaching $3.5B+ in trading volume |
| **2025** | Kalshi won legal battle to list election contracts; Polymarket US launched as CFTC-regulated entity |

### How Prices Reflect Probabilities

The mechanism is elegant: market prices aggregate information from all participants into a single probability estimate.

**Why this works:**
- If the true probability of an event is 70%, but the market price is at $0.50, there's a profit opportunity
- Informed traders buy at $0.50, pushing the price up toward $0.70
- Uninformed traders on the other side are willing to sell at $0.50, creating liquidity
- Over time, the price converges toward the "true" probability as more information is incorporated
- This is known as the **Efficient Market Hypothesis** applied to event outcomes

**What moves the price:**
- New information (poll results, news events, expert statements)
- Large trades by informed participants ("whale" activity)
- Changing market sentiment
- Time decay as the event approaches

### Prediction Markets vs. Traditional Gambling

| Aspect | Prediction Markets | Traditional Betting/Gambling |
|--------|-------------------|------------------------------|
| **Purpose** | Information aggregation, price discovery | Entertainment, house profit |
| **Odds setter** | The crowd (market participants) | The bookmaker/house |
| **House edge** | Minimal or zero (just trading fees) | Built-in margin (vig/juice), typically 5-15% |
| **Continuous trading** | Yes — buy/sell anytime before resolution | Usually locked in once placed |
| **Sell before outcome** | Yes — can exit your position early | No (usually) |
| **Skill vs luck** | Rewards research and analysis | Varies; house always has edge |
| **Information value** | Prices are considered useful forecasts | Odds reflect bookmaker risk management |
| **Regulatory view** | Increasingly treated as financial instruments | Regulated as gambling |

### The "Wisdom of Crowds" Argument

Prediction markets are considered one of the best implementations of the "wisdom of crowds" concept (from James Surowiecki's 2004 book):

- **Diversity of opinion:** Participants come from different backgrounds with different information sources
- **Independence:** Each trader makes their own assessment (not following a leader)
- **Decentralization:** No single authority sets the price
- **Aggregation:** The market price mechanism combines all individual estimates into one number
- **Financial incentive:** Real money (or reputation) on the line motivates honest, well-researched opinions — no cost to lying in a poll, but it costs money to be wrong in a market

**Empirical accuracy:** Studies have shown prediction markets outperform polls, expert panels, and even internal corporate forecasts. In the 2024 US election, Polymarket's prices were more accurate than major polling aggregates in predicting state-level outcomes.

---

## 2. Major Prediction Market Platforms

### Polymarket

**Overview:** The world's largest prediction market by volume. Crypto-native, built on Polygon blockchain.

| Detail | Info |
|--------|------|
| **Founded** | 2020 |
| **Based in** | New York, NY |
| **Blockchain** | Polygon (Ethereum L2) |
| **Currency** | USDC (USD stablecoin) |
| **US availability** | Polymarket US operates as a CFTC-regulated Designated Contract Market (DCM) via QCX LLC; international version operates separately |
| **2024 election volume** | $3.5B+ traded |
| **Deposit methods** | Crypto (USDC on Polygon, Ethereum, or other chains via bridge); credit/debit card via onramp partners |
| **Minimum trade** | ~$1 |

**How Polymarket works:**
- Uses a Central Limit Order Book (CLOB) for matching trades — similar to a traditional stock exchange
- Shares are tokenized using the Conditional Token Framework (CTF) on Polygon
- Trades are gasless (Polymarket covers gas fees for users)
- Supports limit orders (set your price) and market orders (buy at current price)
- Real-time WebSocket feeds available for price streaming

**Fee structure:**
- No fees to create an account or deposit
- Trading fees are minimal — Polymarket charges no explicit trading fees on most markets
- A Maker Rebate Program pays daily USDC rebates to liquidity providers
- Withdrawal fees are gas costs to bridge USDC back to Ethereum mainnet

**What you can bet on:**
- Politics (elections, policy, appointments)
- Crypto (BTC/ETH price targets, protocol events)
- Sports (NFL, NBA, soccer, tennis)
- Pop culture (Oscars, TV shows, celebrity events)
- Science & tech (AI milestones, space events)
- Economics (Fed rates, inflation, GDP)
- Weather and climate events
- Geopolitics (wars, treaties, sanctions)

**Strengths:** Deepest liquidity, widest market selection, strong API/developer tools, gasless UX
**Weaknesses:** Crypto-only deposits (friction for non-crypto users), international version unregulated, past CFTC settlement ($1.4M fine in 2022)

> **⚠️ User 1 (H1B/US):** ✅ Can use Polymarket US (CFTC-regulated version). Fully legal as passive investment activity on H1B.
>
> **⚠️ User 2 (India):** ⚠️ International version is technically accessible (crypto-based, no KYC restrictions by geography) but operates in a **legal gray area** in India. Using it could violate the Public Gambling Act and RBI forex/FEMA regulations. Proceed with caution — or avoid real-money trading entirely.

---

### Kalshi

**Overview:** The first fully CFTC-regulated prediction market exchange in the US. Treats event contracts as financial derivatives.

| Detail | Info |
|--------|------|
| **Founded** | 2020 |
| **Based in** | New York, NY |
| **Regulated by** | CFTC (Designated Contract Market) |
| **Currency** | USD (fiat) |
| **US availability** | Fully legal for US residents (except in certain restricted states) |
| **Deposit methods** | Bank transfer (ACH), wire transfer, debit card |
| **Contract type** | Event contracts with $1 max payout |

**How Kalshi works:**
- Operates like a traditional exchange with an order book
- Contracts are "event contracts" — binary yes/no outcomes
- Each contract pays $1 if the outcome occurs, $0 if not
- Prices reflect probabilities (e.g., $0.72 = 72% implied probability)
- Supports limit and market orders
- Provides a demo/paper trading environment for practice

**Fee structure:**
- Transaction fees: typically 1-7 cents per contract depending on the contract price
- No fees for deposits via ACH
- Fees are charged only when you enter a position (not when you exit or when the market resolves)
- Fee discounts available for high-volume traders

**Available markets:**
- Economics (CPI, GDP, unemployment, Fed rate decisions)
- Politics (election outcomes, policy decisions, congressional votes)
- Weather (temperature records, hurricane landfalls)
- Company events (earnings, IPOs, product launches)
- Financial (S&P 500 ranges, oil prices, Treasury yields)
- Culture and current events

**Strengths:** Fully US-regulated (CFTC), fiat deposits (no crypto needed), strong legal standing, transparent resolution rules
**Weaknesses:** Smaller liquidity than Polymarket, fewer market categories, some states excluded, less flexible market creation

> **⚠️ User 1 (H1B/US):** ✅ Fully legal. Easiest onramp for US-based users — fiat deposits via ACH, no crypto needed. Passive investment activity is fine on H1B.
>
> **⚠️ User 2 (India):** ❌ US-only platform. Not available to Indian residents. Cannot create an account.

---

### Metaculus

**Overview:** A reputation-based forecasting platform. No real money — instead uses track record and peer comparison to motivate accuracy.

| Detail | Info |
|--------|------|
| **Founded** | 2015 |
| **Type** | Forecasting platform (no money) |
| **Currency** | Reputation points / track record score |
| **Availability** | Global, free |
| **Focus** | Science, technology, AI, geopolitics, existential risk |

**How Metaculus works:**
- Users submit probability estimates (not trades) on questions
- Each user has a calibration score tracking how accurate their predictions are over time
- The "community prediction" is the aggregate of all users' estimates (similar to a market price)
- The "Metaculus prediction" uses a proprietary weighted algorithm emphasizing historically accurate forecasters
- Questions can be binary (yes/no) or continuous (numeric range)
- No order book — you simply submit your estimate

**Key features:**
- Tournaments and competitions for forecasters
- Extensive question categorization (AI, biosecurity, nuclear risk, economics)
- Open API for accessing community predictions
- Used by policymakers and researchers for calibrated forecasts
- Strong community of "superforecasters" (people with demonstrated predictive accuracy)

**Strengths:** Focused on calibration and accuracy, no financial barrier to entry, attracts domain experts, strong on long-term and existential-risk questions
**Weaknesses:** No financial incentive (less skin in the game), smaller user base, predictions can be slow to update vs. real-money markets

> **⚠️ User 1 (H1B/US):** ✅ Fully legal. No money involved — purely reputation-based. Great for calibration practice.
>
> **⚠️ User 2 (India):** ✅ Fully legal. No money involved. Accessible globally. Excellent starting point for building forecasting skills.

---

### Manifold Markets

**Overview:** A social prediction market using play money, where anyone can create a market on any topic.

| Detail | Info |
|--------|------|
| **Founded** | 2022 |
| **Type** | Play-money prediction market |
| **Currency** | Mana (M) — play money, cannot be cashed out |
| **Starting balance** | M1,000 free for new users |
| **Availability** | Global, free |

**How Manifold works:**
- Anyone can create a market on any topic — no approval needed
- Uses an Automated Market Maker (AMM) for liquidity (like Uniswap for predictions)
- Users trade with Mana (play money), so no regulatory barriers
- Market creators set resolution criteria and resolve their own markets
- Calibration: Manifold's aggregate predictions have been shown to be within 4 percentage points of actual outcomes on average

**Key features:**
- Community-driven market creation (any topic imaginable)
- Social features (comments, follows, groups)
- Leagues and competitions
- API available for developers
- Prediction accuracy competitive with real-money markets (outperformed some during 2022 midterms)

**Strengths:** Zero financial risk, unlimited market creation, strong community, good for niche/personal questions, strong accuracy despite being play money
**Weaknesses:** No real money = less incentive for deep research, play money can lead to less serious participation, market creator resolves (potential bias)

> **⚠️ User 1 (H1B/US):** ✅ Fully legal. Play money only. Great for practicing strategies with zero financial risk.
>
> **⚠️ User 2 (India):** ✅ Fully legal. Play money only. Accessible globally. Ideal for building prediction skills and testing strategies without legal risk.

---

### PredictIt

**Overview:** A political prediction market operating under a CFTC no-action letter for academic research.

| Detail | Info |
|--------|------|
| **Founded** | 2014 |
| **Operated by** | Victoria University of Wellington (New Zealand) |
| **Regulated by** | CFTC no-action letter (limited exemption) |
| **Currency** | USD |
| **Availability** | US residents (with restrictions) |

**How PredictIt works:**
- Trades binary event contracts on political events
- Share prices range from $0.01 to $0.99 (representing 1-99% probability)
- Maximum investment: $850 per contract per trader (regulatory limit)
- Maximum traders: 5,000 per market (regulatory limit)

**Fee structure:**
- 10% fee on profits (not on the trade amount)
- 5% withdrawal fee
- These fees are notably higher than other platforms

**Current status:**
- CFTC issued a wind-down order in 2022, but PredictIt won a court injunction allowing continued operation
- Future uncertain — operating under legal limbo
- Limited market selection compared to newer platforms

**Strengths:** Real USD, US-legal (under no-action letter), established track record on political markets
**Weaknesses:** High fees (10% profit + 5% withdrawal), $850 position limits, limited to 5,000 traders per market, uncertain regulatory future, limited market categories

> **⚠️ User 1 (H1B/US):** ✅ Legal (limited). Operates under a CFTC no-action letter. $850 position caps and high fees make it less attractive than Kalshi/Polymarket US, but still a viable option for political markets.
>
> **⚠️ User 2 (India):** ❌ US-only platform. Not available to Indian residents.

---

### Augur

**Overview:** A decentralized prediction market protocol on Ethereum. Fully permissionless — no central authority.

| Detail | Info |
|--------|------|
| **Founded** | 2014 (launched 2018) |
| **Type** | Decentralized protocol (no company controls it) |
| **Blockchain** | Ethereum |
| **Currency** | ETH / DAI |
| **Token** | REP (Augur reputation token used for dispute resolution) |

**How Augur works:**
- Anyone can create a market, and anyone can trade
- Uses smart contracts for all operations (no intermediary)
- Market resolution is decentralized — REP token holders vote on outcomes
- Dispute resolution system: if someone disagrees with a resolution, they can stake REP to challenge it
- No KYC or account required — just a crypto wallet

**Strengths:** Fully decentralized (censorship-resistant), permissionless, no KYC, theoretically unlimited markets
**Weaknesses:** Poor UX, very low liquidity, high gas fees on Ethereum, complex for beginners, slow market resolution, limited adoption

> **⚠️ User 1 (H1B/US):** ⚠️ Legal gray area. Decentralized and unregulated — no CFTC oversight. Using it is not explicitly illegal but lacks the regulatory protections of Kalshi/Polymarket US. Low liquidity makes it impractical regardless.
>
> **⚠️ User 2 (India):** ⚠️ Legal gray area. Decentralized and permissionless (no geographic restrictions), but using real crypto (ETH/DAI) for betting likely violates Indian gambling laws and FEMA forex regulations. The decentralized nature does not provide legal protection.

---

### Platform Comparison Matrix

| Feature | Polymarket | Kalshi | Metaculus | Manifold | PredictIt | Augur |
|---------|-----------|--------|-----------|----------|-----------|-------|
| **Real money** | Yes (USDC) | Yes (USD) | No | No (Mana) | Yes (USD) | Yes (ETH/DAI) |
| **US legal** | Yes (regulated US entity) | Yes (CFTC) | N/A | N/A | Yes (limited) | Gray area |
| **Regulation** | CFTC (US entity) | CFTC | None needed | None needed | CFTC no-action | None (decentralized) |
| **Crypto required** | Yes | No | No | No | No | Yes |
| **Liquidity** | Very high | Medium | N/A | Low (play money) | Low | Very low |
| **Market variety** | Very wide | Wide | Wide | Unlimited | Politics only | Unlimited |
| **Anyone can create markets** | No | No | Limited | Yes | No | Yes |
| **Fees** | Very low | Low-medium | Free | Free | High | Gas fees |
| **Best for** | Serious trading | US-regulated trading | Calibration practice | Casual forecasting | Political junkies | Crypto purists |

---

## 3. Types of Markets

### Political Events

The most popular and heavily traded category across all platforms.

- **Elections:** Presidential, congressional, gubernatorial, international elections
- **Policy decisions:** Will X bill pass? Will the debt ceiling be raised?
- **Appointments:** Supreme Court nominees, cabinet positions, Fed chair
- **Geopolitics:** Will countries sign treaties? Will sanctions be imposed?
- **Example:** "Will the Republican nominee win the 2028 presidential election?" — typically attracts the highest volume

**Why political markets are popular:** High public interest, abundant information sources (polls, pundit analysis, historical data), and events with clear resolution criteria.

### Sports

Prediction markets overlap somewhat with traditional sports betting but offer continuous trading.

- **Game outcomes:** Who will win specific matchups
- **Season/tournament outcomes:** Championship winners, MVP awards
- **Player-specific:** Will Player X be traded? Will they break a record?
- **Polymarket sports markets** operate differently from traditional sportsbooks — you trade shares rather than placing fixed bets, and can exit positions before the event

### Crypto and Digital Assets

Particularly popular on Polymarket due to the crypto-native user base.

- **Price targets:** "Will Bitcoin exceed $150K by December 2026?"
- **Protocol events:** Will Ethereum complete its next upgrade on time?
- **Regulatory:** Will the SEC approve X ETF?
- **Adoption milestones:** Will a Fortune 500 company add BTC to its balance sheet?
- **DeFi events:** Will a specific protocol be hacked?

### Economics and Financial Events

High-value markets that attract sophisticated traders.

- **Federal Reserve:** Rate decisions, FOMC meeting outcomes
- **Inflation:** CPI prints, inflation rate ranges
- **Employment:** Jobs report numbers, unemployment rate
- **GDP:** Growth rate brackets
- **Corporate:** Earnings beats/misses, IPO pricing
- **Commodities:** Oil price ranges, gold targets

**Why these matter:** These markets are often the closest to traditional financial derivatives and attract traders with genuine information edges.

### Science and Technology

- **AI milestones:** Will GPT-5 be released by X date? Will AI pass specific benchmarks?
- **Space:** SpaceX Starship milestones, NASA missions
- **Climate:** Temperature records, extreme weather events
- **Medical:** Drug approvals (FDA), pandemic developments
- **Tech industry:** Product launches, acquisitions, antitrust rulings

### Entertainment and Culture

- **Awards:** Oscars, Emmys, Grammy predictions
- **Movies/TV:** Box office performance, show renewals/cancellations
- **Celebrity:** Public events, announcements
- **Viral events:** Internet culture milestones

### Weather

Particularly developed on Kalshi, which has CFTC approval for weather contracts.

- **Temperature:** Will the temperature exceed X degrees in Y city?
- **Hurricanes:** Named storm counts, landfall predictions
- **Precipitation:** Snowfall and rainfall records
- **Climate records:** Hottest year, sea ice extent

---

## 4. Strategies for Prediction Markets

### Strategy 1: Information Edge / Research-Based Trading

The most fundamental strategy. You profit by knowing more than the market average.

**How it works:**
1. Find a market where you have specialized knowledge or can research more deeply than typical participants
2. Assess whether the market price (implied probability) is too high or too low
3. Buy if underpriced, sell/short if overpriced
4. Wait for the market to correct toward the true probability, or for the event to resolve

**Example:** A market prices "Will FDA approve Drug X?" at 40%. You've read the Phase 3 trial data, know the advisory committee voted 10-2 in favor, and historical approval rates after such votes are ~90%. You buy at $0.40 and expect to collect $1.00.

**Information sources:**
- Primary sources (government data, SEC filings, academic papers)
- Domain-specific news and publications
- Expert analysis and interviews
- Historical base rates for similar events
- Statistical models (polling aggregators, economic forecasts)

### Strategy 2: Arbitrage Between Platforms

Different platforms sometimes price the same event differently, creating risk-free profit opportunities.

**How it works:**
1. The same event is listed on Polymarket at $0.60 (Yes) and Kalshi at $0.55 (Yes)
2. Buy "Yes" on Kalshi at $0.55 and buy "No" on Polymarket at $0.40
3. Total cost: $0.95. Guaranteed payout: $1.00 (one of your positions always wins)
4. Risk-free profit: $0.05 per share

**Considerations:**
- Fees can eat into arbitrage profits
- Resolution criteria may differ slightly between platforms
- Capital is tied up until the event resolves
- Opportunities are typically small and short-lived (others spot them too)
- Different settlement currencies (USDC vs USD) add currency risk

### Strategy 3: Market Making

Provide liquidity by placing both buy and sell orders, profiting from the spread.

**How it works:**
1. Place a buy (bid) order at $0.48 and a sell (ask) order at $0.52 on the same market
2. When both orders fill, you've bought at $0.48 and sold at $0.52 = $0.04 profit
3. Repeat continuously, adjusting prices as the market moves

**Requirements:**
- Significant capital to maintain multiple positions
- Automated trading system (manual market making is impractical)
- Understanding of inventory risk management
- API access to the trading platform
- Polymarket offers maker rebates, incentivizing this strategy

**Risks:** If the market moves strongly in one direction, you can be left holding a losing position ("adverse selection").

### Strategy 4: Following Smart Money / Whale Tracking

Monitor large traders' positions and follow their bets.

**How it works:**
1. Track large orders on Polymarket using blockchain data (all trades are on-chain)
2. Identify wallets that have historically been accurate
3. When a known accurate whale takes a large position, consider following
4. Use on-chain analytics tools to monitor wallet activity

**Tools:**
- Polymarket CLOB API for real-time order flow
- Polygon block explorers (Polygonscan) for on-chain transaction data
- Third-party analytics dashboards that track whale wallets
- Polymarket leaderboard for identifying top traders

**Caution:** Whales can be wrong; they may also be hedging other positions; front-running whales can move the price against you before you enter.

### Strategy 5: News-Based Trading (Event-Driven)

Trade immediately when breaking news changes the probability of an event.

**How it works:**
1. Set up alerts for news related to open markets
2. When breaking news hits, quickly assess its impact on market probabilities
3. Trade before the market fully adjusts to the new information
4. Speed matters — prices adjust within minutes on liquid markets

**Example:** A surprise jobs report comes in much stronger than expected. You immediately buy "No" on "Will the Fed cut rates this month?" before the market fully adjusts.

**Requirements:**
- Fast news sources (newswires, Twitter/X, specialized feeds)
- Pre-analyzed decision trees (if X happens, I trade Y)
- Quick access to trading platforms (API preferred over manual)
- Understanding of how specific news impacts specific markets

### Strategy 6: Using AI for Information Synthesis

Leverage AI tools to process large amounts of information and identify market mispricings.

**How it works:**
1. Use Claude or other LLMs to research the background of specific markets
2. Have AI synthesize information from multiple sources
3. Use AI to analyze historical base rates for similar events
4. Build automated pipelines that monitor relevant information sources

**Practical applications:**
- "Summarize all recent polling data for this election market"
- "What is the historical base rate for FDA drug approvals with these characteristics?"
- "Analyze the last 10 Fed meetings and their relationship to the current economic data"
- "Monitor these 5 news sources for any mention of topics related to my open positions"

### User-Specific Strategy Notes

> **⚠️ User 1 (H1B/US):** All strategies above are viable. Cross-platform arbitrage between Kalshi and Polymarket US is legal and one of the lowest-risk approaches. Information edge trading, market making, and news-based trading are all accessible. All prediction market profits must be reported on your US tax return.

> **⚠️ User 2 (India):** Most strategies involving real money are **not legally viable** from India. However, User 2 **CAN** practice on Manifold Markets (play money) and Metaculus (reputation). Building research skills, probability assessment, and calibration is valuable even without real money. These skills transfer directly to other domains (stock market analysis, business decision-making, career planning). If the legal landscape changes in India, you will be ready to deploy these skills for real money.

---

## 5. How AI/Claude Can Help with Prediction Markets

### Research and Information Synthesis

AI is exceptionally well-suited for the information-gathering phase of prediction market trading.

**What Claude can do:**
- **Summarize complex topics:** "Explain the current state of the US-China trade relationship and how it might affect this market"
- **Analyze primary sources:** Feed in government reports, earnings transcripts, or academic papers and get key takeaways
- **Historical analysis:** "What has happened historically when the yield curve inverted? How did the Fed respond?"
- **Multi-source synthesis:** Combine information from polls, expert opinions, statistical models, and news reports into a coherent probability estimate
- **Identify blind spots:** "What are the strongest arguments against my current position?"

### Probability Assessment

**What Claude can do:**
- Help calibrate probability estimates using reference class forecasting
- Identify relevant base rates ("What percentage of incumbent presidents win re-election?")
- Walk through structured decision analysis (decision trees, scenario planning)
- Challenge your reasoning by steelmanning the opposing view
- Compare your estimate to historical prediction market accuracy on similar events

**Example prompt:** "I'm considering a market on whether the Fed will cut rates in June. The current price is 45%. Walk me through the key factors I should consider, relevant base rates, and give me your analysis of whether 45% seems well-calibrated."

### News Monitoring and Alerting

**Building with Claude:**
- Create automated pipelines that scrape and summarize relevant news
- Set up RSS feed monitoring with AI-powered relevance filtering
- Build daily briefings summarizing developments related to your open positions
- Use Claude to assess the significance of breaking news ("On a scale of 1-10, how much does this news change the probability of X?")

### Automated Monitoring Tools

**What you can build:**
- **Market scanner:** Monitor Polymarket/Kalshi APIs for new markets, large price movements, or volume spikes
- **Arbitrage detector:** Compare prices across platforms for the same events and alert when spreads exist
- **Resolution tracker:** Monitor markets approaching resolution and assess whether current prices seem accurate
- **Portfolio dashboard:** Track your open positions, P&L, and exposure across platforms

**Example architecture:**
```
[News APIs / RSS Feeds] --> [Claude Analysis] --> [Signal Generation]
[Polymarket API] --> [Market Data Collector] --> [Price/Volume Monitoring]
[Kalshi API] --> [Market Data Collector] --> [Arbitrage Detection]
                                              --> [Dashboard / Alerts]
```

### Evaluating Arguments

**What Claude can do:**
- Present balanced pro/con analysis for any market outcome
- Identify the strongest arguments on each side
- Flag potential biases in your reasoning
- Suggest information you might be missing
- Analyze the track record of specific pundits or experts whose views might influence your assessment

### Limitations to Be Aware Of

- Claude cannot access real-time data without tool use — it does not know current market prices
- Claude's knowledge has a training cutoff and may not reflect very recent events
- AI probability estimates are informative but not authoritative — they should be one input among many
- Claude should not be used as the sole basis for trading decisions

---

## 6. Tools and APIs

### Polymarket API / CLOB API

The most comprehensive prediction market API available.

**Architecture:**
- **Central Limit Order Book (CLOB):** Exchange-style matching engine
- **Blockchain:** Polygon network for settlement
- **Token standard:** Conditional Token Framework (CTF)

**Key endpoints:**
- Market data: Order books, price history, trade history, market metadata
- Trading: Create/cancel orders, get positions, trade history
- Account: User profiles, leaderboards, activity
- WebSocket: Real-time order book updates, price feeds, trade streams

**SDK availability:**
- TypeScript: `@polymarket/clob-client`
- Python: `py-clob-client`
- Rust: `polymarket-client-sdk`

**API documentation:** https://docs.polymarket.com

**Rate limits:** Apply; specific limits documented in API reference

**Authentication:** API keys required for trading; market data endpoints may be publicly accessible

**Example (Python):**
```python
from py_clob_client.client import ClobClient

client = ClobClient(
    host="https://clob.polymarket.com",
    key=api_key,
    chain_id=137  # Polygon
)

# Get market data
markets = client.get_markets()

# Get order book for a specific market
orderbook = client.get_order_book(token_id="YOUR_TOKEN_ID")

# Place an order
order = client.create_order(
    token_id="YOUR_TOKEN_ID",
    price=0.50,
    size=100,
    side="BUY"
)
```

### Kalshi API

**Architecture:**
- Traditional exchange order book
- REST API + WebSocket for real-time data
- Demo environment available for testing

**Key capabilities:**
- Market data: Available events, order books, trade history
- Trading: Place/cancel orders, manage positions
- Portfolio: Track positions and P&L
- WebSocket: Real-time market data streaming

**API documentation:** https://docs.kalshi.com

**Authentication:** API keys generated from Kalshi account; Developer Agreement required

**Specification:** OpenAPI spec available at https://docs.kalshi.com/openapi.yaml

**Demo environment:** Available for paper trading and API testing without real money

### Metaculus API

- Public API for accessing community predictions
- Endpoints for question data, predictions, and user scores
- Useful for comparing Metaculus community forecasts against market prices
- Documentation available at Metaculus developer resources

### Manifold Markets API

- Open API for market data and trading (with Mana)
- Endpoints: list markets, get market details, place bets, create markets
- Useful for prototyping trading strategies with zero financial risk
- Well-documented and permissive rate limits

### Data Sources for Research

| Source | What It Provides | Use Case |
|--------|-----------------|----------|
| **Polling aggregators** (538, RCP, Silver Bulletin) | Election polls, model forecasts | Political markets |
| **FRED (Federal Reserve Economic Data)** | Economic indicators, historical data | Economic markets |
| **BLS (Bureau of Labor Statistics)** | Employment, CPI, inflation data | Jobs/inflation markets |
| **CME FedWatch** | Fed funds futures implied probabilities | Fed rate markets |
| **CoinGecko / CoinMarketCap** | Crypto prices and market data | Crypto markets |
| **SEC EDGAR** | Corporate filings, earnings reports | Company event markets |
| **Weather.gov / NOAA** | Weather data and forecasts | Weather markets |
| **PubMed / ClinicalTrials.gov** | Medical research and trial data | FDA approval markets |
| **Twitter/X** | Breaking news, expert commentary | All markets (news-based trading) |
| **Newswires (Reuters, AP)** | Breaking news | Event-driven trading |

### Building Your Own Tools

**Recommended stack for a prediction market monitoring system:**

```
Language: Python (best ecosystem for data/APIs)
API calls: requests / httpx / aiohttp
Data storage: SQLite or PostgreSQL
Scheduling: cron jobs or APScheduler
Notifications: Telegram Bot API, Discord webhooks, or email
Visualization: Streamlit or Grafana
AI integration: Anthropic API (Claude) for analysis
```

**Key scripts to build:**
1. **Market data collector** — polls Polymarket/Kalshi APIs on a schedule, stores prices and volumes
2. **Arbitrage scanner** — compares prices across platforms for matching markets
3. **News monitor** — watches RSS feeds and uses Claude to assess relevance to open markets
4. **Position tracker** — aggregates your positions across platforms into a unified dashboard
5. **Alert system** — notifies you when prices move beyond thresholds or when new relevant markets open

### User-Specific API Notes

> **⚠️ User 1 (H1B/US):** Full access to all APIs listed above for both data analysis and live trading. Kalshi provides a demo environment for testing before trading real money.

> **⚠️ User 2 (India):** Can use Polymarket API and Manifold API for **data analysis, monitoring, and building tools** — even if not trading. Building analytical tools is legal; placing bets may not be. Metaculus API is fully legal to use. This is a valuable path: build market analysis tools, arbitrage detectors, and monitoring dashboards as portfolio projects or as preparation for when legal access becomes available. The technical skills (API integration, data analysis, probability modeling) are transferable and marketable.

---

## 7. Risks and Considerations

### Legal and Regulatory Landscape

**United States:**
- Prediction markets are regulated as derivatives by the CFTC (Commodity Futures Trading Commission)
- Kalshi is the primary CFTC-regulated exchange (DCM status)
- Polymarket US operates as a CFTC-regulated Designated Contract Market
- PredictIt operates under a no-action letter (limited exemption, future uncertain)
- State-level gambling laws may also apply — not all prediction markets are legal in all states
- The CFTC has historically taken enforcement actions against unregistered prediction markets (Polymarket paid a $1.4M settlement in 2022 before becoming regulated)
- Election markets were long prohibited but Kalshi won a landmark court case in 2024 allowing election contracts

**International:**
- Polymarket's international platform operates without CFTC regulation
- Most countries have unclear or no specific regulation for prediction markets
- Some jurisdictions classify them as gambling (UK, where they need a gambling license)
- EU's MiCA regulation may affect crypto-based prediction markets
- Offshore platforms (like the original InTrade from Ireland) have historically operated in regulatory gray areas

**⚠️ User 2 (India) — Detailed India-Specific Legal Analysis:**

- **Public Gambling Act, 1867:** The primary central law prohibiting gambling and betting in India. Most forms of wagering on uncertain outcomes are illegal. Prediction markets likely fall under this prohibition.
- **State-level gambling acts:** Gambling is a state subject in India. Most states have their own gambling/betting acts that are stricter than the central law. Maharashtra, Tamil Nadu, Andhra Pradesh, Telangana, and Karnataka have explicitly banned online gambling/betting. A few states (Goa, Sikkim, Meghalaya) have partial exceptions for certain forms of gambling, but these don't clearly cover prediction markets.
- **Information Technology Act, 2000:** While not specifically targeting prediction markets, online gambling platforms can be blocked under IT Act provisions. The government has the power to block websites and apps under Section 69A.
- **FEMA (Foreign Exchange Management Act):** Using foreign exchange (including crypto) for gambling/betting is a **prohibited purpose** under FEMA. This means using crypto to access international prediction markets like Polymarket potentially violates FEMA, separate from gambling law violations.
- **RBI and cryptocurrency:** The RBI's 2018 circular banning banks from facilitating crypto transactions was overturned by the Supreme Court in 2020 (Internet and Mobile Association of India v. RBI). However, new regulations are under discussion, and the government has imposed a 30% tax on crypto gains plus 1% TDS (Tax Deducted at Source) on crypto transactions. Using crypto for prohibited purposes (gambling) remains problematic.
- **"Games of skill" vs. "games of chance":** Indian law generally exempts "games of skill" from gambling prohibitions (the Supreme Court has upheld this for fantasy sports like Dream11). Prediction markets could arguably fall under either category — they reward research and analysis (skill) but outcomes are inherently uncertain (chance). This legal distinction is being actively debated for prediction market apps.
- **Indian prediction market apps (Probo, Traffic):** Some Indian startups have launched "opinion trading" platforms, framing themselves as distinct from gambling. Probo specifically uses "opinion trading" language to distinguish from betting. Their legal status is uncertain and actively debated. DGIPR and state gambling commissions are monitoring these platforms closely.
- **Potential penalties:** Violations of the Public Gambling Act can result in fines and imprisonment (varies by state — typically fines of a few hundred to a few thousand rupees and imprisonment up to 3 months for a first offense, more for repeat offenses). FEMA violations can result in penalties up to three times the amount involved.

**Key takeaway:** If you are in the US, use Kalshi or Polymarket US for legal certainty. If you are in India, stick to free/play-money platforms (Metaculus, Manifold) and avoid real-money prediction markets until the legal framework clarifies.

### Liquidity Risks

- **Thin markets:** Many prediction markets have low liquidity — you may not be able to buy or sell at the price you want
- **Slippage:** Large orders in illiquid markets will move the price against you
- **Locked capital:** Your money is tied up until the market resolves (which could be months or years)
- **Wide spreads:** Illiquid markets have large bid-ask spreads, meaning you lose money just entering and exiting
- **Exit risk:** You may not be able to sell your position before resolution if there are no buyers

**Mitigation:** Stick to high-volume markets, use limit orders (not market orders), size positions appropriately, and don't put money into long-dated markets that you might need back soon.

### Resolution Disputes

- **Ambiguous resolution criteria:** "Will X happen?" can be interpreted differently by different people
- **Edge cases:** Events that partially happen or happen in an unexpected way
- **Resolution source disagreements:** What if the designated resolution source (e.g., a specific news outlet) reports incorrectly?
- **Platform risk:** The platform itself decides resolution — and their decision is typically final

**Examples of disputes:**
- Polymarket has had controversial resolutions where the outcome was technically ambiguous
- Augur's decentralized resolution (REP token voting) has been manipulated in the past
- PredictIt has faced disputes over political market resolutions

**Mitigation:** Read the resolution criteria carefully before trading. Avoid markets with vague or debatable resolution conditions. Factor resolution risk into your position sizing.

### Smart Contract Risks (Crypto Platforms)

- **Smart contract bugs:** A bug in Polymarket's or Augur's contracts could lead to loss of funds
- **Bridge risks:** Moving assets between blockchains (e.g., Ethereum to Polygon) involves bridge smart contracts that have been exploited before
- **Oracle risks:** Prediction markets rely on "oracles" (external data feeds) to determine outcomes — oracle manipulation is a known attack vector
- **Wallet security:** You are responsible for securing your own crypto wallet (seed phrase, hardware wallet)

**Mitigation:** Use established platforms with audited contracts, don't keep more funds on-platform than you are actively trading, use hardware wallets for large amounts.

### Financial Risks

- **Total loss:** You can lose 100% of what you put into any single market
- **Correlation risk:** Multiple markets may be correlated (e.g., all your political bets go wrong in the same election)
- **Opportunity cost:** Capital locked in prediction markets could be earning returns elsewhere
- **Overconfidence:** The biggest risk — believing you know better than the market when you don't
- **Addiction risk:** The dopamine feedback loop of prediction markets can be similar to gambling

**Mitigation:** Never bet more than you can afford to lose. Diversify across markets and platforms. Keep a trading journal to track your accuracy. Set loss limits.

### Tax Implications

**United States:**
- Prediction market profits are generally taxable
- Kalshi issues 1099 forms for US taxpayers
- Polymarket (crypto) — gains are treated as either short-term or long-term capital gains depending on holding period
- Losses may be deductible (subject to wash sale rules and gambling loss limitations — classification is still evolving)
- The IRS has not issued comprehensive guidance specific to prediction markets; treatment may vary

**Record keeping:**
- Track all trades, deposits, withdrawals, and profits/losses
- Kalshi provides built-in tax reporting
- For Polymarket/crypto platforms, use crypto tax software (Koinly, CoinTracker, etc.)
- Consult a tax professional — this area is evolving rapidly

**International:**
- Tax treatment varies by country
- Some countries may treat prediction market gains as gambling winnings (possibly tax-free in some jurisdictions, e.g., UK)
- Others may treat them as capital gains or miscellaneous income

---

## 8. Getting Started: Practical Recommendations

### For Absolute Beginners

1. **Start with play money:** Use Manifold Markets (free, no risk) to learn how prediction markets work and practice trading
2. **Practice calibration:** Use Metaculus to train your ability to estimate probabilities accurately
3. **Read resolution criteria:** Before any trade, always read the full resolution rules
4. **Start small:** When you move to real money, start with amounts you are completely comfortable losing ($20-$50)
5. **Focus on what you know:** Trade in areas where you have genuine knowledge or can research effectively
6. **Track your performance:** Keep a spreadsheet of your trades, your reasoning, and your results

### Recommended Progression

```
Phase 1: Learn (Week 1-4)
  - Create a Manifold Markets account
  - Make 20-30 play-money trades
  - Create a Metaculus account and make forecasts
  - Read prediction market communities (Reddit r/polymarket, Twitter/X)

Phase 2: Small Real Money (Month 2-3)
  - Create a Kalshi account (if in the US) — easiest fiat onramp
  - Deposit $50-$100
  - Make 5-10 trades in areas you understand
  - Track your results carefully

Phase 3: Scale Up (Month 3+)
  - If profitable and comfortable, consider Polymarket for deeper liquidity
  - Set up API access and start building monitoring tools
  - Develop a systematic approach to finding mispricings
  - Diversify across market categories
```

### **⚠️ User 1 (H1B/US) — Getting Started Path**

```
Phase 1: Practice (Week 1-2)
  - Manifold Markets + Metaculus (free, no risk)
  - Learn market mechanics, practice probability assessment
  - Build calibration skills

Phase 2: First Real Money (Week 3-4)
  - Kalshi — $50-$100 to start
  - Easiest fiat onramp (ACH bank transfer, no crypto needed)
  - Use Kalshi's demo environment first if available
  - Focus on markets you understand (economics, politics, tech)

Phase 3: Scale and Diversify (Month 2+)
  - Polymarket US for deeper liquidity and wider market selection
  - Cross-platform arbitrage between Kalshi and Polymarket US
  - Build API-based monitoring tools
  - All profits reported on US tax return (Kalshi issues 1099 forms)
```

### **⚠️ User 2 (India) — Getting Started Path**

```
Phase 1: Legal Practice Only (Ongoing)
  - Manifold Markets + Metaculus ONLY (legal, free, no regulatory risk)
  - Focus on building calibration, research, and probability assessment skills
  - Participate in Metaculus tournaments for reputation
  - These skills are valuable for stock market analysis, career decisions,
    and business planning — even without prediction market trading

Phase 2: Build Analytical Tools (Month 2+)
  - Use Polymarket API, Manifold API, and Metaculus API for data analysis
  - Build market monitoring dashboards, arbitrage detectors, price trackers
  - This is legal — you are analyzing data, not placing bets
  - These tools can serve as portfolio projects for employment

Phase 3: DO NOT Use Real-Money Prediction Markets
  - Do NOT use real-money prediction markets until Indian legal framework
    clarifies
  - Indian "opinion trading" apps (Probo, Traffic) exist but operate in
    a legal gray area — use at your own risk

Alternative Path:
  - Focus on stock market and crypto trading through LEGAL Indian platforms
    instead (Zerodha, Groww, WazirX, CoinDCX)
  - The analytical and probability skills from Phase 1-2 transfer directly
    to stock/crypto trading

Future Consideration:
  - If prediction markets become legal in India (bills have been proposed
    occasionally), be ready with skills built in Phase 1-2
  - Monitor developments in India's gambling law reform and the legal
    status of opinion trading platforms
```

### Key Metrics to Track

| Metric | What It Tells You |
|--------|-------------------|
| **Win rate** | Percentage of markets where you profited |
| **Brier score** | Statistical measure of prediction accuracy (lower = better) |
| **ROI** | Return on investment across all trades |
| **Calibration** | When you say 70%, does it happen ~70% of the time? |
| **Average edge** | Average difference between your entry price and resolution price |
| **Holding period** | How long your capital is tied up |

---

## 9. Resources and Further Reading

### Communities
- **Reddit:** r/polymarket, r/kalshi, r/predictionmarkets
- **Twitter/X:** Follow @Polymarket, @Kalshi, @Metaculus, @ManifoldMarkets
- **Discord:** Most platforms maintain Discord servers for community discussion
- **Forecasting community:** Good Judgment Open (Philip Tetlock's superforecaster project)

### Books and Academic Resources
- *Superforecasting* by Philip Tetlock — the foundational text on calibrated prediction
- *The Wisdom of Crowds* by James Surowiecki — why groups outperform individuals
- *Prediction Machines* by Ajay Agrawal — AI and prediction economics
- Robin Hanson's academic papers on prediction markets (George Mason University)
- Arrow et al., "The Promise of Prediction Markets" (Science, 2008)

### Key Concepts to Learn
- **Calibration:** Being well-calibrated means your probability estimates match actual frequencies
- **Base rates:** The historical frequency of similar events (essential for good forecasts)
- **Reference class forecasting:** Predicting by looking at how similar situations have resolved
- **Expected value (EV):** Price x Probability of winning — always think in terms of EV, not individual outcomes
- **Kelly criterion:** Mathematical formula for optimal bet sizing based on your edge and bankroll
- **Brier score:** Standard metric for evaluating prediction accuracy (0 = perfect, 1 = worst possible)

---

*This document covers the landscape as of early 2026. Prediction markets are evolving rapidly — regulatory frameworks, platform features, and available markets change frequently. Always verify current platform terms, fees, and legal status before trading.*
