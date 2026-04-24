import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(
    page_title="NSE Breakout Watch",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0a0f1e; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
section[data-testid="stSidebar"] {
    background: #0d1424 !important;
    border-right: 1px solid #1a2540 !important;
}

.kpi-row { display: flex; gap: 12px; margin-bottom: 24px; }
.kpi {
    flex: 1; background: #111827;
    border: 1px solid #1f2d47; border-radius: 10px;
    padding: 18px 16px; text-align: center;
}
.kpi-val { font-family: 'IBM Plex Mono', monospace; font-size: 1.9rem; font-weight: 600; line-height: 1.1; }
.kpi-lbl { font-size: 0.68rem; color: #4b5e7e; text-transform: uppercase; letter-spacing: 1.2px; margin-top: 5px; }

.tbl-wrap { background: #0d1424; border: 1px solid #1a2540; border-radius: 12px; overflow: hidden; }
.tbl-header {
    display: grid;
    grid-template-columns: 100px 90px 110px 120px 140px 80px 80px 90px;
    padding: 10px 20px;
    border-bottom: 1px solid #1a2540;
    gap: 0;
}
.tbl-row {
    display: grid;
    grid-template-columns: 100px 90px 110px 120px 140px 80px 80px 90px;
    padding: 14px 20px;
    border-bottom: 1px solid #0f1825;
    gap: 0;
    transition: background 0.15s;
}
.tbl-row:hover { background: #111827; }
.tbl-row:last-child { border-bottom: none; }
.col-hdr { font-size: 0.62rem; color: #2d3f5c; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
.sym { font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 0.9rem; color: #e2e8f0; }
.mono { font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; color: #94a3b8; }
.scroll-body { max-height: 500px; overflow-y: auto; }
.scroll-body::-webkit-scrollbar { width: 3px; }
.scroll-body::-webkit-scrollbar-thumb { background: #1f2d47; border-radius: 2px; }

.pill { display: inline-block; padding: 3px 9px; border-radius: 20px; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.3px; }
.pill-hot  { background: #0d2a1a; color: #4ade80; border: 1px solid #22c55e30; }
.pill-warm { background: #251a05; color: #fbbf24; border: 1px solid #f59e0b30; }
.pill-cool { background: #0a1b30; color: #60a5fa; border: 1px solid #3b82f630; }

.sec-badge { display:inline-block; padding:2px 7px; border-radius:4px; font-size:0.6rem; font-weight:600; text-transform:uppercase; letter-spacing:0.4px; }

.prox-wrap { display: flex; align-items: center; gap: 7px; }
.prox-bg { flex:1; height:5px; background:#1a2540; border-radius:3px; overflow:hidden; }
.prox-fill { height:100%; border-radius:3px; }

.sec-head {
    font-size: 0.65rem; color: #2d3f5c; text-transform: uppercase;
    letter-spacing: 1.5px; font-weight: 600; margin: 24px 0 12px;
    display: flex; align-items: center; gap: 10px;
}
.sec-head::after { content:''; flex:1; height:1px; background:#1a2540; }

.chart-wrap { background:#0d1424; border:1px solid #1a2540; border-radius:12px; padding:4px; margin-top:4px; }

div[data-testid="stSlider"] label { color:#4b5e7e !important; font-size:0.7rem !important; text-transform:uppercase; letter-spacing:0.8px; }
.stButton > button {
    background: #1d4ed8; color: white; border: none; border-radius: 8px;
    padding: 10px 0; font-family: 'DM Sans', sans-serif; font-weight: 600;
    font-size: 0.88rem; width: 100%; margin-top: 8px;
}
.stButton > button:hover { background: #2563eb; }
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────
WATCHLIST = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","SBIN.NS","BAJFINANCE.NS","BHARTIARTL.NS","KOTAKBANK.NS",
    "AXISBANK.NS","LT.NS","HCLTECH.NS","ASIANPAINT.NS","WIPRO.NS",
    "MARUTI.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS",
    "ONGC.NS","POWERGRID.NS","NTPC.NS","TECHM.NS","BAJAJFINSV.NS",
    "TATAMOTORS.NS","DRREDDY.NS","DIVISLAB.NS","CIPLA.NS","ADANIPORTS.NS",
    "COALINDIA.NS","GRASIM.NS","HINDALCO.NS","JSWSTEEL.NS","TATASTEEL.NS",
    "BPCL.NS","IOC.NS","HEROMOTOCO.NS","EICHERMOT.NS","BAJAJ-AUTO.NS",
    "BRITANNIA.NS","DABUR.NS","MARICO.NS","COLPAL.NS","GODREJCP.NS",
    "PIDILITIND.NS","BERGEPAINT.NS","HAVELLS.NS","VOLTAS.NS","ITC.NS",
    "PERSISTENT.NS","MPHASIS.NS","LTIM.NS","COFORGE.NS","ZOMATO.NS",
    "IRCTC.NS","INDHOTEL.NS","RVNL.NS","IRFC.NS","RECLTD.NS",
    "PFC.NS","BANKBARODA.NS","CANBK.NS","PNB.NS","FEDERALBNK.NS",
    "IDFCFIRSTB.NS","INDUSINDBK.NS","AUBANK.NS","CHOLAFIN.NS","MUTHOOTFIN.NS",
    "APOLLOHOSP.NS","FORTIS.NS","AUROPHARMA.NS","LUPIN.NS","TORNTPHARM.NS",
    "TATAPOWER.NS","ADANIGREEN.NS","NAUKRI.NS","INDIGO.NS","OFSS.NS",
    "DIXON.NS","TATACONSUM.NS","MOTHERSON.NS","BALKRISIND.NS","DMART.NS",
    "ABCAPITAL.NS","MFSL.NS","SBICARD.NS","HDFCAMC.NS","NIPPONLIFE.NS",
    "ANGELONE.NS","ICICIPRULI.NS","HDFCLIFE.NS","360ONE.NS","MOTILALOFS.NS",
    "ICICIGI.NS","STARHEALTH.NS","NUVAMA.NS","HAL.NS","BEL.NS","BHEL.NS",
    "COCHINSHIP.NS","CGPOWER.NS","SIEMENS.NS","ABB.NS","CUMMINSIND.NS",
    "THERMAX.NS","TRENT.NS","KALYANKJIL.NS","VBL.NS","KPITTECH.NS",
    "SUPREMEIND.NS","GRINDWELL.NS","TIMKEN.NS","SCHAEFFLER.NS",
]

SECTOR_MAP = {
    "RELIANCE.NS":"Energy","TCS.NS":"IT","HDFCBANK.NS":"Banking","INFY.NS":"IT",
    "ICICIBANK.NS":"Banking","HINDUNILVR.NS":"FMCG","SBIN.NS":"Banking",
    "BAJFINANCE.NS":"Finance","BHARTIARTL.NS":"Telecom","KOTAKBANK.NS":"Banking",
    "AXISBANK.NS":"Banking","LT.NS":"Infra","HCLTECH.NS":"IT","ASIANPAINT.NS":"Consumer",
    "WIPRO.NS":"IT","MARUTI.NS":"Auto","SUNPHARMA.NS":"Pharma","TITAN.NS":"Consumer",
    "ULTRACEMCO.NS":"Cement","NESTLEIND.NS":"FMCG","ONGC.NS":"Energy",
    "POWERGRID.NS":"Energy","NTPC.NS":"Energy","TECHM.NS":"IT","BAJAJFINSV.NS":"Finance",
    "TATAMOTORS.NS":"Auto","DRREDDY.NS":"Pharma","DIVISLAB.NS":"Pharma",
    "CIPLA.NS":"Pharma","ADANIPORTS.NS":"Infra","COALINDIA.NS":"Energy",
    "GRASIM.NS":"Cement","HINDALCO.NS":"Metal","JSWSTEEL.NS":"Metal",
    "TATASTEEL.NS":"Metal","BPCL.NS":"Energy","IOC.NS":"Energy","HEROMOTOCO.NS":"Auto",
    "EICHERMOT.NS":"Auto","BAJAJ-AUTO.NS":"Auto","BRITANNIA.NS":"FMCG",
    "DABUR.NS":"FMCG","MARICO.NS":"FMCG","COLPAL.NS":"FMCG","GODREJCP.NS":"FMCG",
    "PIDILITIND.NS":"Consumer","BERGEPAINT.NS":"Consumer","HAVELLS.NS":"Consumer",
    "VOLTAS.NS":"Consumer","ITC.NS":"FMCG","PERSISTENT.NS":"IT","MPHASIS.NS":"IT",
    "LTIM.NS":"IT","COFORGE.NS":"IT","ZOMATO.NS":"Consumer","IRCTC.NS":"Consumer",
    "INDHOTEL.NS":"Consumer","RVNL.NS":"Infra","IRFC.NS":"Finance","RECLTD.NS":"Finance",
    "PFC.NS":"Finance","BANKBARODA.NS":"Banking","CANBK.NS":"Banking","PNB.NS":"Banking",
    "FEDERALBNK.NS":"Banking","IDFCFIRSTB.NS":"Banking","INDUSINDBK.NS":"Banking",
    "AUBANK.NS":"Banking","CHOLAFIN.NS":"Finance","MUTHOOTFIN.NS":"Finance",
    "APOLLOHOSP.NS":"Pharma","FORTIS.NS":"Pharma","AUROPHARMA.NS":"Pharma",
    "LUPIN.NS":"Pharma","TORNTPHARM.NS":"Pharma","TATAPOWER.NS":"Energy",
    "ADANIGREEN.NS":"Energy","NAUKRI.NS":"IT","INDIGO.NS":"Consumer","OFSS.NS":"IT",
    "DIXON.NS":"Consumer","TATACONSUM.NS":"FMCG","MOTHERSON.NS":"Auto",
    "BALKRISIND.NS":"Auto","DMART.NS":"Consumer","ABCAPITAL.NS":"Finance",
    "MFSL.NS":"Finance","SBICARD.NS":"Finance","HDFCAMC.NS":"Finance","NIPPONLIFE.NS":"Finance",
    "ANGELONE.NS":"Finance","ICICIPRULI.NS":"Finance","HDFCLIFE.NS":"Finance",
    "360ONE.NS":"Finance","MOTILALOFS.NS":"Finance","ICICIGI.NS":"Finance",
    "STARHEALTH.NS":"Finance","NUVAMA.NS":"Finance",
    "HAL.NS":"Defence","BEL.NS":"Defence","BHEL.NS":"Infra","COCHINSHIP.NS":"Defence",
    "CGPOWER.NS":"Capital Goods","SIEMENS.NS":"Capital Goods","ABB.NS":"Capital Goods",
    "CUMMINSIND.NS":"Capital Goods","THERMAX.NS":"Capital Goods",
    "TRENT.NS":"Consumer","KALYANKJIL.NS":"Consumer","VBL.NS":"FMCG",
    "KPITTECH.NS":"IT","SUPREMEIND.NS":"Consumer","GRINDWELL.NS":"Capital Goods",
    "TIMKEN.NS":"Capital Goods","SCHAEFFLER.NS":"Capital Goods",
}

SECTOR_COLORS = {
    "Banking":"#3b82f6","IT":"#a78bfa","FMCG":"#fb923c","Finance":"#34d399",
    "Energy":"#f87171","Infra":"#22d3ee","Auto":"#f97316","Pharma":"#f472b6",
    "Consumer":"#a3e635","Metal":"#94a3b8","Cement":"#fbbf24","Telecom":"#38bdf8","Defence":"#e879f9","Capital Goods":"#67e8f9",
}

# ── LOGIC ─────────────────────────────────────────────────────
def find_swings(df, lookback=10):
    """
    Pure swing detection: a swing high at index i means df['High'][i]
    is strictly greater than all highs in the window [i-lookback .. i+lookback].
    Returns list of (date, price) tuples sorted oldest → newest.
    """
    highs, lows, n = df['High'].values, df['Low'].values, len(df)
    sh, sl = [], []
    for i in range(lookback, n - lookback):
        if highs[i] == max(highs[i - lookback: i + lookback + 1]):
            sh.append((df.index[i], round(float(highs[i]), 2)))
        if lows[i] == min(lows[i - lookback: i + lookback + 1]):
            sl.append((df.index[i], round(float(lows[i]), 2)))
    return sh, sl


def find_valid_resistance(df, swing_highs, threshold_pct,
                          min_pullback_pct=5.0, min_sh_age_candles=10):
    """
    CMT-validated pre-breakout resistance detection.

    A swing high is valid resistance ONLY when ALL five conditions hold:

    CONDITION 1 — Prior rejection (the most important rule):
        After the swing high was formed, price must have pulled back AT LEAST
        min_pullback_pct% below that high. This proves market rejected price there.

    CONDITION 2 — Below resistance now:
        Current close < swing high. Gap <= threshold_pct%.

    CONDITION 3 — Uptrend context:
        Close > 50MA * 0.97. We only trade breakouts in rising stocks.

    CONDITION 4 — Age confirmation:
        Swing high must be at least min_sh_age_candles old (not forming now).

    CONDITION 5 — INTEGRITY (the new rule that fixes DIXON + DRREDDY):
        Since price pulled back from SH to its lowest point, price must NOT
        have traded ABOVE the swing high level at any point before today.
        If price already pierced above SH and came back down, this level is
        no longer a clean pre-breakout resistance — it is a chop zone.

        Specifically: between the pullback low and today, no HIGH may exceed
        the swing high price.

    CONDITION 6 — Meaningful proximity (avoid distant highs):
        The swing high must be within 15% of the current 60-day high.
        Filters out irrelevant ancient highs when price has already rallied past.

    Returns: (valid, resistance_price, gap_pct, sh_date)
    """
    if not swing_highs:
        return False, None, None, None

    close     = float(df['Close'].iloc[-1])
    closes    = df['Close'].values
    highs_arr = df['High'].values
    lows_arr  = df['Low'].values
    n         = len(df)

    # Condition 3: Uptrend filter
    if n >= 50:
        ma50 = float(df['Close'].iloc[-50:].mean())
        if close < ma50 * 0.97:
            return False, None, None, None

    # Reference for Condition 6
    high_60d = float(df['High'].iloc[-60:].max()) if n >= 60 else float(df['High'].max())

    best_sh   = None
    best_date = None

    # Walk from most recent swing high backwards
    for sh_date, sh_price in reversed(swing_highs):
        # Condition 2a: must still be above current close
        if sh_price <= close:
            continue

        try:
            bar_idx = df.index.get_loc(sh_date)
        except Exception:
            continue

        # Condition 4: age confirmation
        if (n - 1 - bar_idx) < min_sh_age_candles:
            continue

        # Condition 1: pullback after SH
        post_sh_closes = closes[bar_idx + 1:]
        post_sh_lows   = lows_arr[bar_idx + 1:]
        if len(post_sh_closes) == 0:
            continue

        lowest_after_idx_rel = int(np.argmin(post_sh_lows))
        lowest_after_idx     = bar_idx + 1 + lowest_after_idx_rel
        lowest_after         = float(post_sh_lows[lowest_after_idx_rel])
        pullback_pct         = (sh_price - lowest_after) / sh_price * 100

        if pullback_pct < min_pullback_pct:
            continue

        # ════════════════════════════════════════════════════════
        # CONDITION 5 — INTEGRITY (after pullback to now, no piercing)
        # ════════════════════════════════════════════════════════
        if lowest_after_idx < n - 1:
            highs_since_low = highs_arr[lowest_after_idx: n - 1]
            if len(highs_since_low) > 0:
                max_high_since_low = float(highs_since_low.max())
                if max_high_since_low > sh_price * 1.002:
                    continue

        # ════════════════════════════════════════════════════════
        # CONDITION 6 — CLEAN LEVEL CHECK (FIXES ULTRACEMCO)
        # The level must not be a chop-zone pivot. Count how many
        # times in the WHOLE history price has closed above sh_price.
        # If > 10% of candles closed above, it's a range boundary, not
        # a clean resistance — reject.
        # ════════════════════════════════════════════════════════
        closes_above = int(np.sum(closes > sh_price * 1.002))
        close_above_ratio = closes_above / n
        if close_above_ratio > 0.10:     # more than 10% of bars closed above
            continue

        # ════════════════════════════════════════════════════════
        # CONDITION 7 — MUST BE A DOMINANT HIGH
        # The swing high should be the HIGHEST point in at least the
        # last 120 candles (6 months). This eliminates mid-range pivots
        # that were just local highs inside a sideways pattern.
        # ════════════════════════════════════════════════════════
        window_len = min(120, bar_idx)
        if window_len > 20:
            pre_sh_highs = highs_arr[bar_idx - window_len: bar_idx]
            if len(pre_sh_highs) > 0 and float(pre_sh_highs.max()) > sh_price:
                continue   # there was an even higher high recently — skip

        # Condition 8: meaningful proximity (within 15% of 60d high)
        if sh_price < high_60d * 0.85:
            continue

        # Condition 2b: gap within threshold
        gap_pct = round((sh_price - close) / sh_price * 100, 2)
        if gap_pct > threshold_pct:
            continue

        # All conditions passed
        best_sh   = sh_price
        best_date = sh_date
        break

    if best_sh is None:
        return False, None, None, None

    gap_pct = round((best_sh - close) / best_sh * 100, 2)
    return True, best_sh, gap_pct, best_date


def get_vol_info(df, vol_mult):
    vol_now  = float(df['Volume'].iloc[-1])
    vol_avg  = float(df['Volume'].iloc[-21:-1].mean())
    vol_ratio= round(vol_now / vol_avg, 2) if vol_avg > 0 else 0
    return vol_ratio >= vol_mult, vol_ratio


@st.cache_data(ttl=900, show_spinner=False)
def run_screener(lookback, vol_mult, min_mcap, threshold):
    results = []
    for sym in WATCHLIST:
        try:
            t  = yf.Ticker(sym)
            df = t.history(period="2y", interval="1d")
            if df.empty or len(df) < lookback * 2 + 30:
                continue
            mcap_cr = (getattr(t.fast_info, "market_cap", 0) or 0) / 1e7
            if mcap_cr < min_mcap:
                continue

            sh, sl = find_swings(df, lookback)
            ok, res_price, gap, sh_date = find_valid_resistance(
                df, sh, threshold, min_pullback_pct=5.0, min_sh_age_candles=lookback + 2
            )
            if not ok:
                continue

            vol_ok, vol_r = get_vol_info(df, vol_mult)
            close   = round(float(df['Close'].iloc[-1]), 2)
            prev    = round(float(df['Close'].iloc[-2]), 2)
            day_chg = round((close - prev) / prev * 100, 2)
            signal  = "HOT" if gap <= 0.5 else "WARM" if gap <= 1.2 else "CLOSE"

            results.append({
                "symbol"    : sym.replace(".NS",""),
                "full_sym"  : sym,
                "close"     : close,
                "day_chg"   : day_chg,
                "swing_high": res_price,
                "sh_date"   : sh_date.strftime("%d %b '%y"),
                "swing_low" : sl[-1][1] if sl else None,
                "gap_pct"   : gap,
                "vol_ok"    : vol_ok,
                "vol_ratio" : vol_r,
                "mcap_cr"   : round(mcap_cr),
                "sector"    : SECTOR_MAP.get(sym, "Other"),
                "signal"    : signal,
                "sh_list"   : [(d.strftime("%Y-%m-%d"), p) for d, p in sh[-8:]],
                "sl_list"   : [(d.strftime("%Y-%m-%d"), p) for d, p in sl[-8:]],
            })
        except:
            continue
    order = {"HOT":0,"WARM":1,"CLOSE":2}
    return sorted(results, key=lambda x: (order[x["signal"]], x["gap_pct"]))


@st.cache_data(ttl=900, show_spinner=False)
def run_recent_breakouts(lookback, vol_mult, min_mcap, days_back=5):
    """
    Finds stocks that:
    1. Had a valid resistance level (swing high WITH prior pullback >= 5%)
    2. Closed above that resistance within the last `days_back` candles
    3. Are in an uptrend (above 50MA)
    """
    results = []
    for sym in WATCHLIST:
        try:
            t  = yf.Ticker(sym)
            df = t.history(period="2y", interval="1d")
            if df.empty or len(df) < lookback * 2 + 30:
                continue
            mcap_cr = (getattr(t.fast_info, "market_cap", 0) or 0) / 1e7
            if mcap_cr < min_mcap:
                continue

            sh, sl = find_swings(df, lookback)
            if not sh:
                continue

            closes    = df['Close'].values
            n         = len(df)
            today_close = float(closes[-1])

            # Uptrend filter
            if n >= 50:
                ma50 = float(df['Close'].iloc[-50:].mean())
                if today_close < ma50 * 0.97:
                    continue

            # For each of the last days_back candles, check if it broke a valid resistance
            breakout_found    = False
            breakout_days_ago = None
            broken_level      = None
            broken_sh_date    = None

            for days_ago in range(1, days_back + 1):
                candle_idx   = n - days_ago
                candle_close = float(closes[candle_idx])
                prev_close   = float(closes[candle_idx - 1])

                # Build a df slice UP TO the candle before this one
                df_slice = df.iloc[:candle_idx]
                sh_slice, _ = find_swings(df_slice, lookback)

                # Find a valid resistance in the history before this candle
                ok, res_price, _, res_date = find_valid_resistance(
                    df_slice, sh_slice, threshold_pct=50,   # wide threshold — we just need the level
                    min_pullback_pct=5.0, min_sh_age_candles=lookback + 2
                )
                if not ok:
                    continue

                # Fresh breakout: this candle closed above resistance, previous candle was below
                if candle_close > res_price and prev_close <= res_price:
                    breakout_found    = True
                    breakout_days_ago = days_ago
                    broken_level      = res_price
                    broken_sh_date    = res_date
                    break

            if not breakout_found:
                continue

            vol_ok, vol_r = get_vol_info(df, vol_mult)
            close   = round(today_close, 2)
            prev    = round(float(closes[-2]), 2)
            day_chg = round((close - prev) / prev * 100, 2)
            bo_pct  = round((close - broken_level) / broken_level * 100, 2)
            label   = "TODAY" if breakout_days_ago == 1 else f"{breakout_days_ago}D AGO"

            results.append({
                "symbol"    : sym.replace(".NS",""),
                "full_sym"  : sym,
                "close"     : close,
                "day_chg"   : day_chg,
                "broken_sh" : broken_level,
                "sh_date"   : broken_sh_date.strftime("%d %b '%y") if broken_sh_date else "—",
                "bo_pct"    : bo_pct,
                "days_ago"  : breakout_days_ago,
                "label"     : label,
                "swing_low" : sl[-1][1] if sl else None,
                "vol_ratio" : vol_r,
                "vol_ok"    : vol_ok,
                "mcap_cr"   : round(mcap_cr),
                "sector"    : SECTOR_MAP.get(sym, "Other"),
                "sh_list"   : [(d.strftime("%Y-%m-%d"), p) for d, p in sh[-8:]],
                "sl_list"   : [(d.strftime("%Y-%m-%d"), p) for d, p in sl[-8:]],
            })
        except:
            continue
    return sorted(results, key=lambda x: (x["days_ago"], -x["bo_pct"]))



# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:14px 0 18px; border-bottom:1px solid #1a2540; margin-bottom:18px'>
        <div style='font-size:1.05rem; font-weight:700; color:#e2e8f0'>🎯 Breakout Watch</div>
        <div style='font-size:0.7rem; color:#2d3f5c; font-family:IBM Plex Mono; margin-top:3px'>
            Pre-breakout · Daily · NSE
        </div>
    </div>
    """, unsafe_allow_html=True)

    threshold = st.slider("Gap to swing high (%)", 0.3, 5.0, 2.0, 0.1,
        help="Only show stocks within X% BELOW their swing high — not yet broken out")
    lookback  = st.slider("Swing lookback (candles)", 3, 15, 5,
        help="Candles on each side to confirm a swing point")
    vol_mult  = st.slider("Volume buildup multiplier", 1.0, 3.0, 1.2, 0.1)
    min_mcap  = st.slider("Min market cap (₹ Cr)", 500, 10000, 500, 250)
    vol_only  = st.checkbox("Only with volume buildup", value=False)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    run_btn = st.button("🔍  Scan Now")

    days_back = st.slider("Recent breakout window (days)", 1, 10, 5, 1,
        help="How many days back to scan for confirmed breakouts")

    st.markdown("""
    <div style='margin-top:24px; padding:14px; background:#080d1a;
                border:1px solid #1a2540; border-radius:8px; font-size:0.72rem; line-height:2.1'>
        <div style='color:#1f2d47; font-size:0.6rem; text-transform:uppercase;
                    letter-spacing:1px; margin-bottom:6px'>Signal guide</div>
        <span style='color:#4ade80; font-weight:700'>HOT</span>
        <span style='color:#2d3f5c'> — within 0.5% of swing high</span><br>
        <span style='color:#fbbf24; font-weight:700'>WARM</span>
        <span style='color:#2d3f5c'> — 0.5 – 1.2% below</span><br>
        <span style='color:#60a5fa; font-weight:700'>CLOSE</span>
        <span style='color:#2d3f5c'> — 1.2 – 2% below</span><br>
        <span style='color:#34d399'>↑ Vol</span>
        <span style='color:#2d3f5c'> — volume building up</span><br>
        <span style='color:#e879f9; font-weight:700'>TODAY</span>
        <span style='color:#2d3f5c'> — broke out today</span><br>
        <span style='color:#fb923c; font-weight:700'>Xd AGO</span>
        <span style='color:#2d3f5c'> — broke out X days back</span>
    </div>
    """, unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-bottom:20px'>
    <div style='font-size:1.5rem; font-weight:700; color:#e2e8f0; letter-spacing:-0.5px'>
        🎯 NSE Breakout Watch
    </div>
    <div style='font-size:0.76rem; color:#2d3f5c; font-family:IBM Plex Mono; margin-top:5px'>
        Stocks approaching swing high resistance &nbsp;·&nbsp; Daily &nbsp;·&nbsp;
        2-year history &nbsp;·&nbsp; {datetime.now().strftime("%d %b %Y  %I:%M %p")}
    </div>
</div>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────
if "results"   not in st.session_state: st.session_state.results   = None
if "breakouts" not in st.session_state: st.session_state.breakouts = None

if run_btn:
    with st.spinner("Scanning stocks · 2Y daily data · this takes ~90 sec…"):
        st.session_state.results   = run_screener(lookback, vol_mult, min_mcap, threshold)
        st.session_state.breakouts = run_recent_breakouts(lookback, vol_mult, min_mcap, days_back)

if st.session_state.results is None:
    st.markdown("""
    <div style='text-align:center; padding:100px 20px'>
        <div style='font-size:3rem; opacity:0.15; margin-bottom:14px'>🎯</div>
        <div style='color:#1a2540; font-size:1rem; font-weight:600'>
            Configure parameters and click Scan Now
        </div>
        <div style='color:#0f1825; font-size:0.8rem; margin-top:6px'>
            Tab 1: Stocks approaching swing high &nbsp;·&nbsp; Tab 2: Recent confirmed breakouts
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎯  Approaching Breakout", "🚀  Recent Breakouts", "🧪  Backtest"])

# helper to render a candlestick chart for any stock dict
def render_chart(sel, key_prefix=""):
    try:
        df_c = yf.Ticker(sel["full_sym"]).history(period="1y", interval="1d")
        fig  = make_subplots(rows=2, cols=1, shared_xaxes=True,
                             row_heights=[0.72, 0.28], vertical_spacing=0.02)
        fig.add_trace(go.Candlestick(
            x=df_c.index, open=df_c['Open'], high=df_c['High'],
            low=df_c['Low'], close=df_c['Close'],
            increasing_line_color='#4ade80', decreasing_line_color='#f87171',
            increasing_fillcolor='#4ade80',  decreasing_fillcolor='#f87171',
            name="Price", line_width=1,
        ), row=1, col=1)

        sh_level = sel.get("swing_high") or sel.get("broken_sh")
        if sh_level:
            label = f"Swing High  ₹{sh_level:,}"
            if sel.get("gap_pct"):
                label += f"  ← {sel['gap_pct']}% away"
            elif sel.get("bo_pct"):
                label += f"  ↑ broke +{sel['bo_pct']}%"
            fig.add_hline(y=sh_level, line_dash="dash", line_color="#fbbf24", line_width=1.5,
                annotation_text=label, annotation_position="top left",
                annotation_font=dict(color="#fbbf24", size=11, family="IBM Plex Mono"),
                row=1, col=1)

        if sel.get("swing_low"):
            fig.add_hline(y=sel["swing_low"], line_dash="dot", line_color="#60a5fa", line_width=1.2,
                annotation_text=f"Swing Low  ₹{sel['swing_low']:,}",
                annotation_position="bottom left",
                annotation_font=dict(color="#60a5fa", size=11, family="IBM Plex Mono"),
                row=1, col=1)

        sh_d = [s[0] for s in sel["sh_list"]]; sh_p = [s[1] for s in sel["sh_list"]]
        sl_d = [s[0] for s in sel["sl_list"]]; sl_p = [s[1] for s in sel["sl_list"]]
        fig.add_trace(go.Scatter(x=sh_d, y=sh_p, mode='markers',
            marker=dict(color='#fbbf24', size=8, symbol='triangle-down'), name="Swing Highs"), row=1, col=1)
        fig.add_trace(go.Scatter(x=sl_d, y=sl_p, mode='markers',
            marker=dict(color='#60a5fa', size=8, symbol='triangle-up'),  name="Swing Lows"),  row=1, col=1)

        vol_c = ['rgba(74,222,128,0.33)' if c >= o else 'rgba(248,113,113,0.33)'
                 for c, o in zip(df_c['Close'], df_c['Open'])]
        fig.add_trace(go.Bar(x=df_c.index, y=df_c['Volume'], marker_color=vol_c, showlegend=False), row=2, col=1)
        avg_v = df_c['Volume'].rolling(20).mean()
        fig.add_trace(go.Scatter(x=df_c.index, y=avg_v,
            line=dict(color='rgba(251,191,36,0.31)', width=1, dash='dot'), showlegend=False), row=2, col=1)

        fig.update_layout(height=500, plot_bgcolor='#0a0f1e', paper_bgcolor='#0d1424',
            font=dict(family='IBM Plex Mono', color='#4b5e7e', size=10),
            xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=16, b=10),
            legend=dict(orientation='h', y=1.02, x=0, font=dict(size=10), bgcolor='rgba(0,0,0,0)'))
        fig.update_xaxes(gridcolor='#111827', zeroline=False)
        fig.update_yaxes(gridcolor='#111827', zeroline=False)

        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Chart error: {e}")


# ════════════════════════════════════════════════════════════
# TAB 1 — Approaching Breakout
# ════════════════════════════════════════════════════════════
with tab1:
    results = st.session_state.results
    if vol_only:
        results = [r for r in results if r["vol_ok"]]

    total   = len(results)
    hot     = sum(1 for r in results if r["signal"] == "HOT")
    warm    = sum(1 for r in results if r["signal"] == "WARM")
    vol_b   = sum(1 for r in results if r["vol_ok"])
    avg_gap = round(sum(r["gap_pct"] for r in results) / total, 2) if total else 0

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi"><div class="kpi-val" style="color:#60a5fa">{total}</div>
            <div class="kpi-lbl">Setups Found</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#4ade80">{hot}</div>
            <div class="kpi-lbl">Hot &lt;0.5%</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#fbbf24">{warm}</div>
            <div class="kpi-lbl">Warm &lt;1.2%</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#34d399">{vol_b}</div>
            <div class="kpi-lbl">Vol Building</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#a78bfa">{avg_gap}%</div>
            <div class="kpi-lbl">Avg Gap</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-head">Pre-Breakout Setups</div>', unsafe_allow_html=True)

    if not results:
        st.markdown("""<div style='text-align:center;padding:50px;color:#1f2d47'>
            No setups match. Try raising the gap threshold.</div>""", unsafe_allow_html=True)
    else:
        rows_html = ""
        for r in results:
            sc   = SECTOR_COLORS.get(r["sector"], "#64748b")
            dc   = "#4ade80" if r["day_chg"] >= 0 else "#f87171"
            pcls = {"HOT":"pill-hot","WARM":"pill-warm","CLOSE":"pill-cool"}[r["signal"]]
            plbl = {"HOT":"🔴 HOT","WARM":"🟡 WARM","CLOSE":"🔵 CLOSE"}[r["signal"]]
            prox = round((1 - r["gap_pct"] / threshold) * 100)
            pcol = "#4ade80" if r["signal"]=="HOT" else "#fbbf24" if r["signal"]=="WARM" else "#60a5fa"
            vc   = "#34d399" if r["vol_ok"] else "#2d3f5c"
            vlbl = f"{'↑ ' if r['vol_ok'] else ''}{r['vol_ratio']}x"
            rows_html += f"""
            <div class="tbl-row">
                <span class="sym">{r['symbol']}</span>
                <span><span class="pill {pcls}">{plbl}</span></span>
                <span class="mono">₹{r['close']:,}<span style="font-size:.65rem;color:{dc}"> {'+' if r['day_chg']>=0 else ''}{r['day_chg']}%</span></span>
                <span class="mono">₹{r['swing_high']:,}<span style="display:block;font-size:.6rem;color:#2d3f5c">{r['sh_date']}</span></span>
                <span><div class="prox-wrap"><div class="prox-bg"><div class="prox-fill" style="width:{prox}%;background:{pcol};box-shadow:0 0 5px {pcol}50"></div></div>
                <span style="font-family:IBM Plex Mono;font-size:.75rem;color:{pcol};min-width:38px">{r['gap_pct']}%</span></div></span>
                <span style="font-family:IBM Plex Mono;font-size:.78rem;color:{vc}">{vlbl}</span>
                <span><span class="sec-badge" style="background:{sc}18;color:{sc};border:1px solid {sc}30">{r['sector']}</span></span>
                <span style="font-family:IBM Plex Mono;font-size:.7rem;color:#2d3f5c">₹{r['mcap_cr']:,}Cr</span>
            </div>"""

        st.markdown(f"""
        <div class="tbl-wrap">
          <div class="tbl-header">
            <span class="col-hdr">Symbol</span><span class="col-hdr">Signal</span>
            <span class="col-hdr">Close</span><span class="col-hdr">Swing High</span>
            <span class="col-hdr">Gap to High</span><span class="col-hdr">Volume</span>
            <span class="col-hdr">Sector</span><span class="col-hdr">Mkt Cap</span>
          </div>
          <div class="scroll-body">{rows_html}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sec-head">Chart View</div>', unsafe_allow_html=True)
        sel1 = st.selectbox("Pick a stock", [r["symbol"] for r in results],
                            key="sel_tab1", label_visibility="collapsed")
        if sel1:
            s = next(r for r in results if r["symbol"] == sel1)
            render_chart(s, "t1")
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Close",       f"₹{s['close']:,}",        f"{s['day_chg']}% today")
            c2.metric("Swing High",  f"₹{s['swing_high']:,}",   f"Set {s['sh_date']}")
            c3.metric("Gap to High", f"{s['gap_pct']}%",          s["signal"])
            c4.metric("Swing Low",   f"₹{s['swing_low']:,}" if s['swing_low'] else "—")
            c5.metric("Volume",      f"{s['vol_ratio']}x",        "Building ↑" if s['vol_ok'] else "Normal")


# ════════════════════════════════════════════════════════════
# TAB 2 — Recent Breakouts
# ════════════════════════════════════════════════════════════
with tab2:
    bos = st.session_state.breakouts or []

    total_b  = len(bos)
    today_b  = sum(1 for b in bos if b["days_ago"] == 1)
    vol_b2   = sum(1 for b in bos if b["vol_ok"])
    avg_bo   = round(sum(b["bo_pct"] for b in bos) / total_b, 2) if total_b else 0

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi"><div class="kpi-val" style="color:#e879f9">{total_b}</div>
            <div class="kpi-lbl">Recent Breakouts</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#4ade80">{today_b}</div>
            <div class="kpi-lbl">Today</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#fb923c">{total_b - today_b}</div>
            <div class="kpi-lbl">Last {days_back} Days</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#34d399">{vol_b2}</div>
            <div class="kpi-lbl">Vol Confirmed</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#a78bfa">+{avg_bo}%</div>
            <div class="kpi-lbl">Avg Breakout</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-head">Confirmed Breakouts</div>', unsafe_allow_html=True)

    if not bos:
        st.markdown("""<div style='text-align:center;padding:50px;color:#1f2d47'>
            No recent breakouts found. Try increasing the breakout window in the sidebar.</div>""",
            unsafe_allow_html=True)
    else:
        bo_rows = ""
        for b in bos:
            sc   = SECTOR_COLORS.get(b["sector"], "#64748b")
            dc   = "#4ade80" if b["day_chg"] >= 0 else "#f87171"
            vc   = "#34d399" if b["vol_ok"] else "#2d3f5c"
            vlbl = f"{'↑ ' if b['vol_ok'] else ''}{b['vol_ratio']}x"
            day_col  = "#4ade80" if b["days_ago"] == 1 else "#fb923c"
            day_pill = f"pill-hot" if b["days_ago"] == 1 else "pill-warm"
            bo_rows += f"""
            <div class="tbl-row">
                <span class="sym">{b['symbol']}</span>
                <span><span class="pill {day_pill}">{b['label']}</span></span>
                <span class="mono">₹{b['close']:,}<span style="font-size:.65rem;color:{dc}"> {'+' if b['day_chg']>=0 else ''}{b['day_chg']}%</span></span>
                <span class="mono">₹{b['broken_sh']:,}<span style="display:block;font-size:.6rem;color:#2d3f5c">resistance broken</span></span>
                <span style="font-family:IBM Plex Mono;font-size:.85rem;color:#4ade80;font-weight:600">+{b['bo_pct']}%</span>
                <span style="font-family:IBM Plex Mono;font-size:.78rem;color:{vc}">{vlbl}</span>
                <span><span class="sec-badge" style="background:{sc}18;color:{sc};border:1px solid {sc}30">{b['sector']}</span></span>
                <span style="font-family:IBM Plex Mono;font-size:.7rem;color:#2d3f5c">₹{b['mcap_cr']:,}Cr</span>
            </div>"""

        st.markdown(f"""
        <div class="tbl-wrap">
          <div class="tbl-header">
            <span class="col-hdr">Symbol</span><span class="col-hdr">When</span>
            <span class="col-hdr">Close</span><span class="col-hdr">Broken Level</span>
            <span class="col-hdr">Breakout %</span><span class="col-hdr">Volume</span>
            <span class="col-hdr">Sector</span><span class="col-hdr">Mkt Cap</span>
          </div>
          <div class="scroll-body">{bo_rows}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sec-head">Chart View</div>', unsafe_allow_html=True)
        sel2 = st.selectbox("Pick a stock", [b["symbol"] for b in bos],
                            key="sel_tab2", label_visibility="collapsed")
        if sel2:
            b = next(x for x in bos if x["symbol"] == sel2)
            render_chart(b, "t2")
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Close",          f"₹{b['close']:,}",       f"{b['day_chg']}% today")
            c2.metric("Broken Swing High", f"₹{b['broken_sh']:,}")
            c3.metric("Breakout",       f"+{b['bo_pct']}%",        b["label"])
            c4.metric("Swing Low",      f"₹{b['swing_low']:,}" if b['swing_low'] else "—")
            c5.metric("Volume",         f"{b['vol_ratio']}x",      "Confirmed ✅" if b['vol_ok'] else "Normal")


# ════════════════════════════════════════════════════════════
# TAB 3 — Logic Validator (does the screener correctly spot breakouts?)
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div style='background:#0d1424;border:1px solid #1a2540;border-radius:10px;
                padding:16px 20px;margin-bottom:20px'>
        <div style='font-size:0.95rem;font-weight:600;color:#e2e8f0;margin-bottom:6px'>
            🧪 Logic Validator
        </div>
        <div style='font-size:0.78rem;color:#4b5e7e;line-height:1.6'>
            Pick any stock. The engine walks through 2 years of daily history and shows
            EVERY point where the screener would have flagged a valid swing breakout.
            You can then verify visually on the chart: did price actually break out?
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------- Simple inputs — just pick a stock ----------
    all_symbols = sorted([s.replace(".NS", "") for s in WATCHLIST])
    bt_symbol = st.selectbox("Stock to validate",
                             all_symbols, key="bt_sym",
                             index=all_symbols.index("TITAN") if "TITAN" in all_symbols else 0)
    bt_run = st.button("▶️  Validate", key="bt_btn")

    # ---------- Logic helper ----------
    def bt_validate(df, sh_idx, sh_price, min_pb=5.0):
        closes_after = df['Close'].values[sh_idx + 1:]
        lows_after   = df['Low'].values[sh_idx + 1:]
        highs_all    = df['High'].values
        closes_all   = df['Close'].values
        n = len(df)
        if len(closes_after) == 0:
            return False, 0, sh_price, "no_data"
        lo_rel = int(np.argmin(lows_after))
        lo_val = float(lows_after[lo_rel])
        pb_pct = (sh_price - lo_val) / sh_price * 100
        if pb_pct < min_pb:
            return False, round(pb_pct, 2), round(lo_val, 2), "no_pullback"
        lo_abs = sh_idx + 1 + lo_rel
        if lo_abs < n - 1:
            hs = highs_all[lo_abs: n - 1]
            if len(hs) > 0 and float(hs.max()) > sh_price * 1.002:
                return False, round(pb_pct, 2), round(lo_val, 2), "pierced"
        if np.sum(closes_all > sh_price * 1.002) / n > 0.10:
            return False, round(pb_pct, 2), round(lo_val, 2), "chop_zone"
        win_len = min(120, sh_idx)
        if win_len > 20:
            pre = highs_all[sh_idx - win_len: sh_idx]
            if len(pre) > 0 and float(pre.max()) > sh_price:
                return False, round(pb_pct, 2), round(lo_val, 2), "not_dominant"
        return True, round(pb_pct, 2), round(lo_val, 2), "valid"

    if bt_run:
        with st.spinner(f"Walking through 2Y history of {bt_symbol}..."):
            try:
                df = yf.Ticker(f"{bt_symbol}.NS").history(period="2y", interval="1d")
                if df.empty:
                    st.error("Could not fetch data for this symbol.")
                    st.stop()

                sh_all, sl_all = find_swings(df, lookback)

                # Walk forward — find every historical breakout signal
                signals = []
                checked = set()
                min_bars = lookback * 2 + 30
                closes_arr = df['Close'].values

                for i in range(min_bars, len(df)):
                    df_s = df.iloc[:i]
                    sh_s, _ = find_swings(df_s, lookback)
                    close_now  = float(df_s['Close'].iloc[-1])
                    prev_close = float(df_s['Close'].iloc[-2])

                    if i >= 50:
                        ma50 = float(df_s['Close'].iloc[-50:].mean())
                        if close_now < ma50 * 0.97:
                            continue

                    for sh_date, sh_price in reversed(sh_s):
                        key = round(sh_price, 1)
                        if key in checked:
                            continue
                        try:
                            bidx = df_s.index.get_loc(sh_date)
                        except:
                            continue
                        if (i - 1) - bidx < lookback + 2:
                            continue
                        ok, pb, _, _ = bt_validate(df_s, bidx, sh_price)
                        if not ok:
                            continue
                        # fresh breakout: prev candle below, current above
                        if prev_close <= sh_price < close_now:
                            checked.add(key)
                            # Check what happened over next 10 days for visual sanity
                            future_10 = closes_arr[i: i + 10]
                            if len(future_10) > 0:
                                max_gain = round((future_10.max() - sh_price) / sh_price * 100, 2)
                                min_draw = round((future_10.min() - sh_price) / sh_price * 100, 2)
                                final_chg = round((future_10[-1] - sh_price) / sh_price * 100, 2)

                                if max_gain >= 3:
                                    followup = f"✅ Real breakout (+{max_gain}% within 10d)"
                                    tag = "real"
                                elif max_gain >= 1:
                                    followup = f"⚠️ Weak follow-through (+{max_gain}% max)"
                                    tag = "weak"
                                else:
                                    followup = f"❌ False breakout ({min_draw}% to {max_gain}%)"
                                    tag = "false"
                            else:
                                followup = "⏳ Too recent"
                                tag = "recent"

                            signals.append({
                                "Breakout Date": df_s.index[-1].strftime("%d %b '%y"),
                                "Broke Above":   f"₹{sh_price:,}",
                                "Resistance Set": sh_date.strftime("%d %b '%y"),
                                "Pullback %":    f"{pb}%",
                                "Entry Close":   f"₹{round(close_now,2):,}",
                                "What Happened": followup,
                                "_tag":          tag,
                            })
                            break

                # --- SUMMARY OF LOGIC QUALITY ---
                total_signals = len(signals)
                real    = sum(1 for s in signals if s["_tag"] == "real")
                weak    = sum(1 for s in signals if s["_tag"] == "weak")
                false   = sum(1 for s in signals if s["_tag"] == "false")

                accuracy = round(real / total_signals * 100, 1) if total_signals else 0
                if accuracy >= 70:
                    verdict, vc = "LOGIC IS SOLID", "#4ade80"
                elif accuracy >= 50:
                    verdict, vc = "LOGIC IS DECENT", "#fbbf24"
                elif total_signals == 0:
                    verdict, vc = "NO BREAKOUTS IN 2Y", "#64748b"
                else:
                    verdict, vc = "LOGIC NEEDS WORK", "#f87171"

                st.markdown('<div class="sec-head">Signal Accuracy</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="kpi-row">
                    <div class="kpi"><div class="kpi-val" style="color:#60a5fa">{total_signals}</div>
                        <div class="kpi-lbl">Breakouts Detected</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:#4ade80">{real}</div>
                        <div class="kpi-lbl">Real (followed through)</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:#fbbf24">{weak}</div>
                        <div class="kpi-lbl">Weak follow-through</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:#f87171">{false}</div>
                        <div class="kpi-lbl">False breakouts</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:{vc}">{accuracy}%</div>
                        <div class="kpi-lbl">{verdict}</div></div>
                </div>
                """, unsafe_allow_html=True)

                # --- DETAILED SIGNALS TABLE ---
                st.markdown('<div class="sec-head">Every Breakout the Screener Would Have Caught</div>',
                            unsafe_allow_html=True)
                if signals:
                    for s in signals:
                        s.pop("_tag", None)
                    df_sig = pd.DataFrame(signals)
                    st.dataframe(df_sig, use_container_width=True, hide_index=True,
                                 height=min(500, 42 * len(signals) + 45))
                else:
                    st.info("No breakouts detected. This stock had no clean swing setups in 2Y.")

                # --- CHART WITH SIGNALS PLOTTED ---
                if signals:
                    st.markdown('<div class="sec-head">Visual Check — Breakouts on Chart</div>',
                                unsafe_allow_html=True)
                    fig = make_subplots(rows=1, cols=1)
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'],
                        increasing_line_color='#4ade80', decreasing_line_color='#f87171',
                        increasing_fillcolor='#4ade80', decreasing_fillcolor='#f87171',
                        name="Price", line_width=1,
                    ))
                    # Plot breakout points as markers
                    bo_dates = []
                    bo_prices= []
                    bo_colors= []
                    for s in signals:
                        try:
                            dt = datetime.strptime(s["Breakout Date"], "%d %b '%y")
                            bo_dates.append(dt)
                            bo_prices.append(float(s["Broke Above"].replace("₹","").replace(",","")))
                            if "Real" in s["What Happened"]:
                                bo_colors.append('#4ade80')
                            elif "Weak" in s["What Happened"]:
                                bo_colors.append('#fbbf24')
                            else:
                                bo_colors.append('#f87171')
                        except:
                            continue
                    if bo_dates:
                        fig.add_trace(go.Scatter(
                            x=bo_dates, y=bo_prices, mode='markers',
                            marker=dict(symbol='star', size=14, color=bo_colors,
                                        line=dict(color='white', width=1)),
                            name="Breakout signals",
                        ))
                    fig.update_layout(
                        height=480, plot_bgcolor='#0a0f1e', paper_bgcolor='#0d1424',
                        font=dict(family='IBM Plex Mono', color='#4b5e7e', size=10),
                        xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10),
                        showlegend=False,
                    )
                    fig.update_xaxes(gridcolor='#111827', zeroline=False)
                    fig.update_yaxes(gridcolor='#111827', zeroline=False)
                    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("""
                    <div style='font-size:0.72rem;color:#4b5e7e;margin-top:8px;line-height:1.7'>
                        ⭐ Green stars = real breakouts (price ran +3% within 10 days)<br>
                        ⭐ Yellow stars = weak follow-through<br>
                        ⭐ Red stars = false breakouts (failed within 10 days)
                    </div>""", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Validation failed: {e}")

st.markdown("""
<div style='text-align:center;margin-top:48px;padding-top:18px;border-top:1px solid #0d1424;
            font-size:0.62rem;color:#0f1825;font-family:IBM Plex Mono'>
    NSE Breakout Watch · Yahoo Finance · 2Y daily · Not financial advice
</div>""", unsafe_allow_html=True)
