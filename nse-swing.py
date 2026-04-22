"""
NSE Swing Breakout Screener — Daily Timeframe
=============================================
- Filters stocks above 500 Cr market cap
- Finds previous swing highs and swing lows on daily candles
- Signals when today's close breaks above the most recent swing high
- Optional: volume confirmation (1.2x average volume)

Install requirements:
    pip install yfinance pandas tabulate
"""

import yfinance as yf
import pandas as pd
from tabulate import tabulate

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────
SWING_LOOKBACK     = 5        # candles on EACH side to confirm swing point
VOLUME_MULTIPLIER  = 1.2      # breakout needs volume > 1.2x 20-day avg
MIN_MARKET_CAP_CR  = 500      # minimum market cap in Crores (₹)
PERIOD             = "6mo"    # how much historical data to pull
INTERVAL           = "1d"     # ← DAILY candles

# ─────────────────────────────────────────────────────────────
# WATCHLIST — Add/replace NSE symbols with .NS suffix
# This is a sample of large/mid caps. Extend as needed.
# ─────────────────────────────────────────────────────────────
WATCHLIST = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BAJFINANCE.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "LT.NS", "HCLTECH.NS", "ASIANPAINT.NS", "WIPRO.NS",
    "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
    "ONGC.NS", "POWERGRID.NS", "NTPC.NS", "TECHM.NS", "BAJAJFINSV.NS",
    "TATAMOTORS.NS", "DRREDDY.NS", "DIVISLAB.NS", "CIPLA.NS", "ADANIPORTS.NS",
    "COALINDIA.NS", "GRASIM.NS", "HINDALCO.NS", "JSWSTEEL.NS", "TATASTEEL.NS",
    "BPCL.NS", "IOC.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "BAJAJ-AUTO.NS",
    "BRITANNIA.NS", "DABUR.NS", "MARICO.NS", "COLPAL.NS", "GODREJCP.NS",
    "PIDILITIND.NS", "BERGEPAINT.NS", "HAVELLS.NS", "VOLTAS.NS", "CROMPTON.NS",
    "MCDOWELL-N.NS", "UBL.NS", "TATACONSUM.NS", "ITC.NS", "OFSS.NS",
    "PERSISTENT.NS", "MPHASIS.NS", "LTIM.NS", "COFORGE.NS", "ZOMATO.NS",
    "NYKAA.NS", "PAYTM.NS", "POLICYBZR.NS", "DELHIVERY.NS", "IRCTC.NS",
    "INDHOTEL.NS", "LEMONTREE.NS", "RVNL.NS", "IRFC.NS", "RECLTD.NS",
    "PFC.NS", "BANKBARODA.NS", "CANBK.NS", "PNB.NS", "FEDERALBNK.NS",
    "IDFCFIRSTB.NS", "BANDHANBNK.NS", "RBLBANK.NS", "INDUSINDBK.NS", "AUBANK.NS",
    "CHOLAFIN.NS", "M&MFIN.NS", "SHRIRAMFIN.NS", "MUTHOOTFIN.NS", "LICHSGFIN.NS",
    "APOLLOHOSP.NS", "FORTIS.NS", "MAXHEALTH.NS", "LALPATHLAB.NS", "METROPOLIS.NS",
    "AUROPHARMA.NS", "LUPIN.NS", "TORNTPHARM.NS", "ALKEM.NS", "IPCALAB.NS",
    "GMRINFRA.NS", "NAUKRI.NS", "INDIGO.NS", "SPICEJET.NS", "MFSL.NS",
    "TATAPOWER.NS", "ADANIGREEN.NS", "ADANIENT.NS", "ADANITRANS.NS", "CESC.NS",
]

# ─────────────────────────────────────────────────────────────
# STEP 1 — Detect swing highs and swing lows
# ─────────────────────────────────────────────────────────────
def find_swings(df, lookback=SWING_LOOKBACK):
    """
    A swing HIGH at index i means:
        df['High'][i] is greater than all highs in [i-lookback : i] and [i : i+lookback]

    A swing LOW at index i means:
        df['Low'][i] is less than all lows in [i-lookback : i] and [i : i+lookback]
    """
    swing_highs = []
    swing_lows  = []

    highs = df['High'].values
    lows  = df['Low'].values
    n     = len(df)

    for i in range(lookback, n - lookback):
        # Swing High check
        if highs[i] == max(highs[i - lookback : i + lookback + 1]):
            swing_highs.append((df.index[i], highs[i]))

        # Swing Low check
        if lows[i] == min(lows[i - lookback : i + lookback + 1]):
            swing_lows.append((df.index[i], lows[i]))

    return swing_highs, swing_lows


# ─────────────────────────────────────────────────────────────
# STEP 2 — Check for breakout signal
# ─────────────────────────────────────────────────────────────
def check_breakout(df, swing_highs):
    """
    Breakout = Today's CLOSE is above the most recent confirmed swing high.
    Volume confirmation = Today's volume > 1.2x the 20-day average volume.
    """
    if not swing_highs:
        return False, None, False

    # Most recent swing high (last item in list)
    last_swing_date, last_swing_price = swing_highs[-1]

    today_close  = df['Close'].iloc[-1]
    today_volume = df['Volume'].iloc[-1]
    avg_volume   = df['Volume'].iloc[-21:-1].mean()   # 20-day avg (excluding today)

    is_breakout        = today_close > last_swing_price
    volume_confirmed   = today_volume > (avg_volume * VOLUME_MULTIPLIER)

    return is_breakout, last_swing_price, volume_confirmed


# ─────────────────────────────────────────────────────────────
# STEP 3 — Market cap filter (> 500 Cr)
# ─────────────────────────────────────────────────────────────
def get_market_cap_cr(ticker_info):
    """
    yfinance returns marketCap in absolute ₹ (or USD for some).
    We divide by 1 Crore (10,000,000) to convert.
    """
    mcap = ticker_info.get("marketCap", 0)
    if mcap:
        return mcap / 1e7    # 1 Crore = 10 million = 1e7
    return 0


# ─────────────────────────────────────────────────────────────
# STEP 4 — Run the screener
# ─────────────────────────────────────────────────────────────
def run_screener():
    results = []
    skipped = []

    print(f"\n🔍 Scanning {len(WATCHLIST)} stocks on DAILY timeframe...\n")

    for symbol in WATCHLIST:
        try:
            ticker = yf.Ticker(symbol)
            df     = ticker.history(period=PERIOD, interval=INTERVAL)

            if df.empty or len(df) < (SWING_LOOKBACK * 2 + 5):
                skipped.append(symbol)
                continue

            # Market cap filter
            info   = ticker.info
            mcap   = get_market_cap_cr(info)
            if mcap < MIN_MARKET_CAP_CR:
                continue

            # Find swings
            swing_highs, swing_lows = find_swings(df)

            if not swing_highs:
                continue

            # Check breakout
            is_breakout, last_swing_high, vol_confirmed = check_breakout(df, swing_highs)

            if not is_breakout:
                continue

            # Collect result
            today_close = round(df['Close'].iloc[-1], 2)
            last_swing_low = swing_lows[-1][1] if swing_lows else None
            swing_high_date = swing_highs[-1][0].strftime("%d-%b-%Y")

            results.append({
                "Symbol"           : symbol.replace(".NS", ""),
                "Close (₹)"        : today_close,
                "Swing High (₹)"   : round(last_swing_high, 2),
                "Swing High Date"  : swing_high_date,
                "Swing Low (₹)"    : round(last_swing_low, 2) if last_swing_low else "N/A",
                "Vol Confirmed"    : "✅ YES" if vol_confirmed else "⚠️  NO",
                "Mkt Cap (Cr)"     : f"₹{round(mcap):,}",
            })

        except Exception as e:
            skipped.append(f"{symbol} ({e})")
            continue

    return results, skipped


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results, skipped = run_screener()

    print("\n" + "="*80)
    print("  📈  NSE SWING BREAKOUT SCREENER — DAILY  |  >500 Cr Market Cap")
    print("="*80)

    if results:
        df_out = pd.DataFrame(results)
        print(tabulate(df_out, headers="keys", tablefmt="rounded_outline", showindex=False))
        print(f"\n✅ {len(results)} breakout(s) found out of {len(WATCHLIST)} stocks scanned.")
    else:
        print("\n❌ No breakouts found today. Markets may be consolidating.")

    if skipped:
        print(f"\n⚠️  Skipped {len(skipped)} symbol(s): {', '.join(skipped[:5])}{'...' if len(skipped) > 5 else ''}")

    print("\n📌 LEGEND:")
    print("  Swing High  = Recent local peak (resistance level)")
    print("  Swing Low   = Recent local trough (support level)")
    print("  Vol Confirmed ✅ = Today's volume > 1.2x 20-day average (stronger signal)")
    print("  Vol Confirmed ⚠️  = Breakout without volume — treat with caution\n")