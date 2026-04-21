# 🤖 Binance Futures Testnet Trading Bot

A clean, modular Python CLI application to place orders on **Binance Futures Testnet (USDT-M)**.
Built as part of the Python Developer Intern assignment.

---

## 📌 Features

* ✅ MARKET orders (BUY / SELL)
* ✅ LIMIT orders (BUY / SELL)
* ⭐ STOP_MARKET order (bonus feature)
* ✅ CLI interface using argparse
* ✅ Strong input validation with clear error messages
* ✅ Structured logging (requests, responses, errors)
* ✅ Clean code separation (client / orders / validators / CLI)
* ✅ Error handling (API, validation, network)

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── client.py
│   ├── orders.py
│   ├── validators.py
│   ├── logging_config.py
├── logs/
│   ├── sample_market.log
│   ├── sample_limit.log
├── cli.py
├── requirements.txt
├── README.md
├── .env.example
```

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Configure API keys

Create a `.env` file:

```
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_secret_key
```

👉 Use Binance Futures Testnet
https://testnet.binancefuture.com

---

## 🚀 Usage

### ▶️ Market Order

```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

---

### ▶️ Limit Order

```bash
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 75000
```

---

### ▶️ Stop Market Order (Bonus)

```bash
python cli.py place --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --price 70000
```

---

## 📊 Example Output

```
📋 ORDER REQUEST SUMMARY
Symbol     : BTCUSDT
Side       : BUY
Type       : MARKET
Quantity   : 0.001

✅ ORDER RESPONSE
Order ID   : 13056949236
Status     : NEW
Executed Qty: 0.0000
Avg Price  : 0.00
```

---

## 📝 Logging

Logs are stored in:

```
logs/trading_bot_YYYYMMDD.log
```

Includes:

* API request details
* API responses
* Errors and failures

---

## ⚠️ Assumptions

* Uses **Binance Futures Testnet only**
* No real money involved
* Orders may remain `NEW` due to testnet behavior
* User provides valid quantity and symbol

---

## ⭐ Bonus Implemented

* STOP_MARKET order support
* Advanced validation using live market price

---

## 📦 Requirements

* Python 3.x
* requests
* python-dotenv

---

## ✅ Submission Checklist

* ✔ MARKET order working
* ✔ LIMIT order working
* ✔ Logs included (market + limit)
* ✔ Clean code structure
* ✔ README with setup + usage

---

## 🏁 Conclusion

This project demonstrates:

* API integration
* CLI design
* Error handling
* Logging practices
* Clean architecture

---
