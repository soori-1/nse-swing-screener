# 📈 NSE Swing Breakout Screener

A real-time end-of-day screener for Indian stocks that detects **swing breakouts** on the daily timeframe.

## Features
- 🔍 Scans 80+ NSE large/mid-cap stocks (>₹500 Cr market cap)
- 📊 Detects swing highs and swing lows automatically
- ✅ Volume confirmation filter (1.2× average)
- 📈 Interactive candlestick charts with swing levels plotted
- 🎨 Dark-mode dashboard with sector breakdown

## How it works
1. **Swing High** = candle whose high is higher than N candles on both sides
2. **Swing Low** = candle whose low is lower than N candles on both sides  
3. **Breakout** = today's close > most recent swing high
4. **Volume Confirmation** = today's volume > 1.2× 20-day average

## Deploy to Streamlit Cloud (Free)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nse-swing-screener.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repo → branch: `main` → file: `app.py`
5. Click **Deploy** — done! 🚀

Your app will be live at:
`https://YOUR_USERNAME-nse-swing-screener-app-XXXXX.streamlit.app`

## Local Setup
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Disclaimer
For educational purposes only. Not financial advice.
