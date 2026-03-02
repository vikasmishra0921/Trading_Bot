# Binance Futures Testnet Trading Bot

A production-quality Python CLI trading bot for the [Binance Futures Testnet (USDT-M)](https://testnet.binancefuture.com).  
Supports **MARKET** and **LIMIT** orders with both a classic CLI interface and an interactive guided mode.

---

## Project Structure

```
trading_bot/
├── cli.py              # Entry point — argparse CLI + interactive mode
├── client.py           # Binance client factory
├── orders.py           # Order placement + response formatting
├── validators.py       # All input validation logic
├── logging_config.py   # Structured logging (file + console)
├── requirements.txt
├── .env.example
├── .env                # ← you create this (not committed)
└── logs/
    └── trading.log     # Auto-created on first run
```

---

## Setup

### 1. Clone / copy the project

```bash
cd trading_bot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

Get your Testnet API key from [https://testnet.binancefuture.com](https://testnet.binancefuture.com).

```bash
cp .env.example .env
```

Edit `.env`:

```env
API_KEY=your_testnet_api_key_here
API_SECRET=your_testnet_api_secret_here
```

---

## Usage

### Interactive Mode (no arguments)

```bash
python cli.py
```

The bot will prompt you step-by-step:

```
╔══════════════════════════════════════════╗
║   Binance Futures Testnet — Trading Bot  ║
║           Interactive Mode               ║
╚══════════════════════════════════════════╝

  Symbol  [e.g. BTCUSDT]: BTCUSDT
  Side  [BUY / SELL]: BUY
  Order type  [MARKET / LIMIT]: LIMIT
  Quantity  [e.g. 0.01]: 0.01
  Price  [e.g. 42000.50]: 40000

┌─── Order Summary ────────────────────────
│  Symbol     : BTCUSDT
│  Side       : BUY
│  Type       : LIMIT
│  Quantity   : 0.01
│  Price      : 40000
└───────────────────────────────────────────

  Confirm order? [y/N]: y

  Placing order…

  ✓  Order placed successfully!

┌─── Order Response ───────────────────────
│  Order ID   : 123456789
│  Symbol     : BTCUSDT
│  Side       : BUY
│  Type       : LIMIT
│  Status     : NEW
│  Qty        : 0.01
│  Avg Price  : 40000
└───────────────────────────────────────────
```

---

### CLI Mode (all arguments supplied)

**Market Buy:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit Sell:**
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.5 --price 3200
```

**Skip confirmation prompt:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01 --yes
```

---

### Help

```bash
python cli.py --help
```

---

## Logging

All activity is logged to `logs/trading.log` with timestamps and severity levels.  
Console output shows only warnings and above (human UX uses `print`).

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing / invalid input | Clear validation message; re-prompts in interactive mode |
| Missing API credentials | Immediate error with instructions |
| Binance API rejection | Error message with reason from exchange |
| Network failure / timeout | Graceful error; logged for diagnosis |
| User cancels (`Ctrl-C`) | Clean exit message |

---

## Notes

- This bot targets the **Futures Testnet** — no real funds are involved.
- Do **not** commit your `.env` file.
- Tested with `python-binance==1.0.19`.
