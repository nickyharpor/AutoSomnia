# 🌙 AutoSomnia

**Close your eyes and let AutoSomnia trade for you.**

*An AI-powered Web3 trading bot that manages your cryptocurrency portfolio while you sleep.*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Web3](https://img.shields.io/badge/Web3-EVM_Compatible-orange.svg)](https://web3py.readthedocs.io)
[![Telegram](https://img.shields.io/badge/Telegram-Bot_API-blue.svg)](https://core.telegram.org/bots/api)

---

## 🚀 Overview

AutoSomnia is a comprehensive Web3 trading automation platform that combines AI-powered market analysis with seamless account management. Built for the Somnia blockchain ecosystem, it provides users with intelligent trading suggestions and automated portfolio management through an intuitive Telegram bot interface.

## 🤖 Telegram Bot

https://t.me/autosomnia_bot

## 💻 Pitch Deck

https://gamma.app/docs/AutoSomnia-x3lbsffz3yuwgkn

### 🎯 Key Features

- **🤖 AI-Powered Trading Suggestions**: Leverages Google Gemini AI for intelligent market analysis
- **💼 Web3 Account Management**: Create, import, and manage EVM-compatible wallets
- **💸 Automated Transactions**: Send SOMI and ERC-20 tokens with MAX amount support
- **📊 Real-time Market Data**: Integration with CoinGecko API for live price feeds
- **🔐 Secure Storage**: MongoDB-based account management with encrypted private keys
- **📱 Telegram Interface**: User-friendly bot commands for all operations

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Telegram Bot  │────│   FastAPI App   │────│   Blockchain     │
│                 │    │                 │    │                  │
│ • User Commands │    │ • REST API      │    │ • Somnia         │
│ • AI Responses  │    │ • Account Mgmt  │    │ • EVM Chains     │
│ • Notifications │    │ • Transactions  │    │ • Smart Contracts│
└─────────────────┘    └─────────────────┘    └──────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │    Database     │              │
         └──────────────│                 │──────────────┘
                        │ • MongoDB       │
                        │ • User Accounts │
                        │ • Transaction   │
                        │   History       │
                        └─────────────────┘
```

### 🛠️ Tech Stack

**Backend:**
- **FastAPI** - High-performance async web framework
- **Web3.py** - Ethereum blockchain interaction
- **MongoDB** - Document database for account storage
- **Pydantic** - Data validation and serialization

**AI & External APIs:**
- **Google Gemini AI** - Advanced language model for trading analysis
- **CoinGecko API** - Real-time cryptocurrency market data
- **Telegram Bot API** - User interface and notifications

**Blockchain:**
- **Somnia Network** - Primary blockchain integration
- **EVM Compatibility** - Support for Ethereum-based chains
- **Web3 Standards** - ERC-20 tokens, standard transactions

---

## 🎮 Bot Commands

### 💼 Account Management
```
/new_account          - Create a new Web3 wallet
/account_info         - View your account details and balances
/withdraw_funds <to>  - Send all SOMI to specified address
/withdraw_funds <to> <token> - Send all tokens to address
```

### 📈 Trading Features
```
/suggest_exchange     - Get AI-powered trading recommendations
/buy_usd <amount>     - Manually buy USDT
/sell_usd <amount>    - Manually sell USDT
/auto_exchange_on     - Enable automated trading
/auto_exchange_off    - Disable automated trading
```

### ℹ️ General
```
/start               - Welcome message and bot introduction
/help                - Show available commands
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB instance
- Telegram Bot Token
- Google Gemini API Key
- CoinGecko API Key

### 1. Clone the Repository
```bash
git clone https://github.com/nickyharpor/AutoSomnia.git
cd AutoSomnia
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` in the root directory and fill in the values. 

### 4. Start the Services

**Start the FastAPI Backend:**
```bash
python app/main.py
```

**Start the Telegram Bot:**
```bash
cd bot
python bot.py
```

### 5. Interact with the Bot
1. Find your bot on Telegram
2. Send `/start` to begin
3. Use `/new_account` to create your first wallet
4. Try `/suggest_exchange` for AI trading advice

---

## 🔧 API Documentation

The FastAPI backend provides comprehensive REST endpoints:

### 🔗 Interactive API Docs
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 📋 Key Endpoints

**Account Management:**
- `POST /account/create` - Create new Web3 account
- `GET /account/balance/{address}` - Get ETH balance
- `GET /account/portfolio/{address}` - Get complete portfolio
- `POST /account/send-eth` - Send ETH transactions
- `POST /account/send-token` - Send ERC-20 tokens
- `DELETE /account/remove/{address}` - Remove single account
- `DELETE /account/remove-user/{user_id}` - Remove user and all their accounts

**Exchange Operations:**
- `GET /exchange/weth-address` - Get WETH token address
- `GET /exchange/factory-address` - Get factory contract address
- `POST /exchange/quote` - Get quote for token pairs
- `POST /exchange/amounts-out` - Calculate swap outputs
- `POST /exchange/swap-exact-tokens-for-tokens` - Execute token swaps

**Exchange Operations:**
- `GET /exchange/amounts-out` - Calculate swap outputs
- `GET /exhange/quote` - Get quote for token pairs
- `POST /exchange/swap-exact-tokens-for-tokens` - Execute token swaps
- `POST /exchange/swap-exact-eth-for-tokens` - Execute SOMA to token swaps
- `POST /exchange/swap-exact-tokens-for-eth` - Execute token to SOMA swaps

**Health & Monitoring:**
- `GET /health` - Application health check
- `GET /account/health` - Account service status monitoring
- `GET /exchange/health` - Exchange service status monitoring

---

## 🧠 AI Trading Intelligence

AutoSomnia's AI system analyzes multiple market factors:

### 📊 Data Sources
- **Real-time Prices** - Live cryptocurrency prices from CoinGecko
- **Market Trends** - 24-hour price changes and volume data
- **Technical Indicators** - Price momentum and volatility analysis

### 🎯 AI Analysis
- **Market Sentiment** - Evaluates current market conditions
- **Risk Assessment** - Considers volatility and market risks
- **Timing Recommendations** - Suggests optimal entry/exit points
- **Portfolio Balance** - Advises on asset allocation strategies

### 💡 Trading Suggestions
The AI provides actionable recommendations:
- **Buy Signals** - When to acquire specific assets
- **Sell Signals** - When to take profits or cut losses
- **Hold Advice** - When to maintain current positions
- **Risk Warnings** - Alerts about high-risk market conditions

---

## 🔒 Security Features

### 🛡️ Account Security
- **Encrypted Storage** - Private keys stored securely in MongoDB
- **Mnemonic Generation** - BIP-39 compliant seed phrases
- **Address Validation** - Comprehensive input validation
- **Transaction Verification** - Multi-layer transaction checks

### 🔐 API Security
- **Request Validation** - Pydantic models for all inputs
- **Error Handling** - Secure error responses without data leakage
- **Rate Limiting** - Protection against API abuse
- **CORS Configuration** - Controlled cross-origin access

### 🚨 Best Practices
- **Never store private keys in logs**
- **Validate all blockchain addresses**
- **Implement proper error handling**
- **Use secure random number generation**

---

## 🏆 Highlights

### 🎯 Innovation Points
- **AI-Driven Trading** - First Web3 bot with integrated AI market analysis
- **Seamless UX** - Complex blockchain operations simplified to chat commands
- **Multi-Chain Ready** - Built for Somnia with broader EVM compatibility
- **Production Ready** - Comprehensive error handling and security measures

### 🛠️ Technical Excellence
- **Modern Architecture** - Async FastAPI with proper separation of concerns
- **Robust Database** - MongoDB with optimized queries and indexing
- **Comprehensive API** - Full REST API with interactive documentation
- **Quality Code** - Type hints, validation, and extensive error handling

### 🌍 Real-World Impact
- **Accessibility** - Makes DeFi accessible to non-technical users
- **Automation** - Reduces manual trading effort and human error
- **Education** - Teaches users about market dynamics through AI insights
- **Community** - Telegram-based interface encourages user engagement

---

## 🔮 Future Roadmap

### Phase 1: Core Enhancement
- [ ] Advanced portfolio analytics
- [ ] Copy trading
- [ ] Custom trading strategies
- [ ] Enhanced security features

### Phase 2: Web-based Frontend
- [ ] Design
- [ ] React implementation
- [ ] Test and deploy

### Phase 3: Ecosystem Expansion
- [ ] Multi-chain support (Polygon, BSC, Arbitrum)
- [ ] DeFi protocol integrations
- [ ] Social trading features

### Phase 4: Enterprise Features
- [ ] Team account management
- [ ] Advanced analytics dashboard
- [ ] API for third-party integrations
- [ ] White-label solutions

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### 🐛 Bug Reports
- Use GitHub Issues to report bugs
- Include detailed reproduction steps
- Provide environment information

### 💡 Feature Requests
- Suggest new features via GitHub Issues
- Explain the use case and benefits
- Consider implementation complexity

### 🔧 Development

```bash
# Fork the repository
git clone https://github.com/nickyharpor/AutoSomnia.git

# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes and commit
git commit -m "Add amazing feature"

# Push to your fork and create a Pull Request
git push origin feature/amazing-feature
```

---

## 📞 Contact & Support

- **GitHub**: [AutoSomnia Repository](https://github.com/nickyharpor/AutoSomnia.git)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/nickyharpor/AutoSomnia/issues)


