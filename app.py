import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(
    page_title="Right Horizons — Breakout Watch",
    page_icon="△",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# AESTHETIC — RIGHT HORIZONS (warm editorial financial)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,500;0,9..144,700;1,9..144,400&family=JetBrains+Mono:wght@400;600;700&family=Inter+Tight:wght@400;500;600&display=swap');

:root {
    --paper:     #F5EDE0;
    --paper-2:   #EDE2D1;
    --paper-3:   #E3D5BE;
    --ink:       #1F1611;
    --ink-muted: #5C4B3B;
    --ink-fade:  #8B7355;
    --bronze:    #A87339;
    --bronze-dk: #8B5A27;
    --gold:      #D4A442;
    --olive:     #7A8B3F;
    --crimson:   #B04848;
    --teal:      #4A7A7A;
    --line:      #C9B896;
}

html, body, [class*="css"] { font-family: 'Inter Tight', sans-serif; }
.stApp { background: linear-gradient(180deg,#F5EDE0 0%,#EDE2D1 100%); color: var(--ink); }
.block-container { padding-top:1.5rem !important; padding-bottom:3rem !important; max-width:1400px; }

section[data-testid="stSidebar"] { background:#1F1611 !important; border-right:1px solid var(--bronze-dk) !important; }
section[data-testid="stSidebar"] * { color: var(--paper) !important; }
section[data-testid="stSidebar"] .block-container { padding-top:1rem !important; }

.masthead {
    border-top:3px solid var(--ink); border-bottom:1px solid var(--ink);
    padding:18px 0 12px; margin-bottom:24px; text-align:center; position:relative;
}
.masthead-brand {
    font-family:'Fraunces',serif; font-weight:700; font-size:2.6rem;
    letter-spacing:-1px; color:var(--bronze); line-height:1; margin:0;
}
.masthead-brand span { color:var(--ink); font-style:normal; font-weight:700; }
.masthead-tagline {
    font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:var(--ink-muted);
    text-transform:uppercase; letter-spacing:3.5px; margin-top:6px;
}
.masthead-date { position:absolute; top:20px; right:8px;
    font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:var(--ink-fade); }
.masthead-date-left { position:absolute; top:20px; left:8px;
    font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:var(--ink-fade);
    letter-spacing:1px; }

.stTabs [data-baseweb="tab-list"] {
    gap:28px; border-bottom:1px solid var(--line); background:transparent !important; padding:0 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family:'Fraunces',serif !important; font-weight:500 !important; font-size:1.05rem !important;
    color:var(--ink-muted) !important; background:transparent !important; padding:10px 0 !important;
    border:none !important;
}
.stTabs [aria-selected="true"] {
    color:var(--ink) !important; border-bottom:2px solid var(--bronze) !important; font-weight:700 !important;
}

.kpi-row { display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin-bottom:28px; }
.kpi {
    background:var(--paper-2); border:1px solid var(--line); border-top:3px solid var(--bronze);
    border-radius:2px; padding:18px 18px 16px; transition:transform 0.2s ease,box-shadow 0.2s ease;
}
.kpi:hover { transform:translateY(-2px); box-shadow:0 4px 12px rgba(168,115,57,0.15); }
.kpi-val { font-family:'Fraunces',serif; font-size:2.4rem; font-weight:700; line-height:1; letter-spacing:-1px; }
.kpi-lbl {
    font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:var(--ink-fade);
    text-transform:uppercase; letter-spacing:1.8px; margin-top:10px; font-weight:600;
}

.tbl { background:var(--paper-2); border:1px solid var(--line); border-radius:2px;
    overflow:hidden; margin-bottom:8px; }
.tbl-hdr {
    display:grid;
    grid-template-columns:110px 100px 115px 130px 150px 100px 105px 95px;
    padding:10px 22px; background:var(--paper-3); border-bottom:1px solid var(--line);
}
.tbl-hdr span {
    font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:var(--ink-muted);
    text-transform:uppercase; letter-spacing:1.8px; font-weight:700;
}
.tbl-row {
    display:grid;
    grid-template-columns:110px 100px 115px 130px 150px 100px 105px 95px;
    padding:16px 22px; border-bottom:1px solid var(--line); transition:background 0.15s; align-items:center;
}
.tbl-row:hover { background:var(--paper-3); }
.tbl-row:last-child { border-bottom:none; }
.scroll-body { max-height:520px; overflow-y:auto; }
.scroll-body::-webkit-scrollbar { width:4px; }
.scroll-body::-webkit-scrollbar-track { background:var(--paper-2); }
.scroll-body::-webkit-scrollbar-thumb { background:var(--bronze); }

.sym { font-family:'Fraunces',serif; font-weight:700; font-size:1.02rem; color:var(--ink); letter-spacing:-0.3px; }
.mono { font-family:'JetBrains Mono',monospace; font-size:0.8rem; color:var(--ink-muted); font-weight:500; }

.pill {
    display:inline-block; padding:3px 10px; border-radius:100px;
    font-family:'JetBrains Mono',monospace; font-size:0.62rem; font-weight:700; letter-spacing:0.8px;
}
.pill-hot  { background:#fbe8e9; color:var(--crimson); border:1px solid #e5b8ba; }
.pill-warm { background:#f8ecd0; color:#8B6914; border:1px solid #d4b880; }
.pill-cool { background:#e3ecec; color:var(--teal); border:1px solid #b8cccc; }

.sec {
    display:inline-block; padding:2px 7px; border-radius:2px;
    font-family:'JetBrains Mono',monospace; font-size:0.58rem; font-weight:600;
    letter-spacing:0.6px; text-transform:uppercase;
}

.prox { display:flex; align-items:center; gap:8px; }
.prox-bg { flex:1; height:4px; background:var(--paper-3); border-radius:2px;
    overflow:hidden; border:1px solid var(--line); }
.prox-fill { height:100%; border-radius:2px; }

.section-head {
    font-family:'Fraunces',serif; font-size:1rem; font-style:italic; font-weight:500;
    color:var(--ink); margin:28px 0 14px; display:flex; align-items:baseline; gap:14px;
}
.section-head::after { content:''; flex:1; height:1px; background:var(--line);
    position:relative; top:-6px; }
.section-head-label {
    font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:var(--bronze);
    text-transform:uppercase; letter-spacing:2.5px; font-style:normal; font-weight:700;
}

.chart-wrap { background:var(--paper-2); border:1px solid var(--line); border-radius:2px; padding:6px; }

section[data-testid="stSidebar"] label {
    color:var(--paper-3) !important; font-family:'JetBrains Mono',monospace !important;
    font-size:0.65rem !important; text-transform:uppercase; letter-spacing:1.2px !important; font-weight:600 !important;
}

.stButton > button {
    background:var(--bronze) !important; color:var(--paper) !important;
    border:1px solid var(--bronze-dk) !important; border-radius:2px !important;
    padding:12px 0 !important; font-family:'Fraunces',serif !important; font-weight:700 !important;
    font-size:0.9rem !important; width:100% !important; letter-spacing:1px !important;
    text-transform:uppercase !important; transition:all 0.2s ease !important; margin-top:10px !important;
}
.stButton > button:hover { background:var(--bronze-dk) !important; transform:translateY(-1px);
    box-shadow:0 4px 10px rgba(31,22,17,0.3); }

[data-baseweb="select"] > div {
    background:var(--paper-2) !important; border:1px solid var(--line) !important;
    border-radius:2px !important; font-family:'JetBrains Mono',monospace !important;
}

[data-testid="stMetric"] { background:var(--paper-2); border:1px solid var(--line);
    padding:14px; border-radius:2px; }
[data-testid="stMetricLabel"] {
    font-family:'JetBrains Mono',monospace !important; font-size:0.62rem !important;
    text-transform:uppercase; letter-spacing:1.2px; color:var(--ink-fade) !important;
}
[data-testid="stMetricValue"] {
    font-family:'Fraunces',serif !important; color:var(--ink) !important; font-weight:700 !important;
}

.stAlert {
    background:var(--paper-2) !important; border-left:3px solid var(--bronze) !important;
    color:var(--ink) !important; font-family:'Inter Tight',sans-serif !important;
}

footer { visibility:hidden; }
#MainMenu { visibility:hidden; }

.ornament { text-align:center; color:var(--bronze); font-family:'Fraunces',serif;
    font-style:italic; margin:20px 0; letter-spacing:10px; }

.empty-state { text-align:center; padding:100px 20px; font-family:'Fraunces',serif; }
.empty-state-orn { font-size:3rem; color:var(--line); margin-bottom:16px; }
.empty-state-text { font-style:italic; font-size:1.2rem; color:var(--ink-muted); font-weight:500; }
.empty-state-sub {
    font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:var(--ink-fade);
    margin-top:10px; letter-spacing:1.2px;
}

[data-testid="stDataFrame"] { background:var(--paper-2); border:1px solid var(--line) !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════
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
    "CGPOWER.NS":"CapGoods","SIEMENS.NS":"CapGoods","ABB.NS":"CapGoods",
    "CUMMINSIND.NS":"CapGoods","THERMAX.NS":"CapGoods",
    "TRENT.NS":"Consumer","KALYANKJIL.NS":"Consumer","VBL.NS":"FMCG",
    "KPITTECH.NS":"IT","SUPREMEIND.NS":"Consumer","GRINDWELL.NS":"CapGoods",
    "TIMKEN.NS":"CapGoods","SCHAEFFLER.NS":"CapGoods",
}

SECTOR_COLORS = {
    "Banking":"#4A7A7A","IT":"#7A5A8B","FMCG":"#C47D3E","Finance":"#7A8B3F",
    "Energy":"#B04848","Infra":"#5A7A8B","Auto":"#A85A2E","Pharma":"#8B4A6A",
    "Consumer":"#7A8B3F","Metal":"#6B6B6B","Cement":"#8B6A2E","Telecom":"#4A7A8B",
    "Defence":"#5A4A7A","CapGoods":"#6B7A4A",
}

# ═══════════════════════════════════════════════════════════════
# CMT LOGIC
# ═══════════════════════════════════════════════════════════════
def calculate_atr(df, period=14):
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Close'].shift()).abs()
    lc = (df['Low']  - df['Close'].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-1])

def calculate_adx(df, period=14):
    h, l, c = df['High'], df['Low'], df['Close']
    plus_dm  = h.diff().where((h.diff() > -l.diff()) & (h.diff() > 0), 0)
    minus_dm = (-l.diff()).where((-l.diff() > h.diff()) & (-l.diff() > 0), 0)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr_s = tr.rolling(period).mean()
    pd_  = 100 * plus_dm.rolling(period).mean()  / atr_s
    md_  = 100 * minus_dm.rolling(period).mean() / atr_s
    dx   = 100 * (pd_ - md_).abs() / (pd_ + md_ + 1e-9)
    adx  = dx.rolling(period).mean()
    return float(adx.iloc[-1]) if not adx.empty else 0

def find_swings(df, lookback=10):
    highs, lows, n = df['High'].values, df['Low'].values, len(df)
    sh, sl = [], []
    for i in range(lookback, n - lookback):
        if highs[i] == max(highs[i - lookback: i + lookback + 1]):
            sh.append((df.index[i], round(float(highs[i]), 2)))
        if lows[i] == min(lows[i - lookback: i + lookback + 1]):
            sl.append((df.index[i], round(float(lows[i]), 2)))
    return sh, sl

@st.cache_data(ttl=1800, show_spinner=False)
def get_market_regime():
    try:
        n = yf.Ticker("^NSEI").history(period="6mo")
        if n.empty or len(n) < 50:
            return True, 0
        close = float(n['Close'].iloc[-1])
        ma50  = float(n['Close'].iloc[-50:].mean())
        return close > ma50, round((close - ma50) / ma50 * 100, 2)
    except:
        return True, 0

@st.cache_data(ttl=1800, show_spinner=False)
def get_nifty_return(period_days=63):
    try:
        n = yf.Ticker("^NSEI").history(period="1y")
        if n.empty or len(n) < period_days:
            return 0
        return float((n['Close'].iloc[-1] / n['Close'].iloc[-period_days] - 1) * 100)
    except:
        return 0

def check_rs(df, nifty_ret, period_days=63):
    if len(df) < period_days:
        return False, 0, 0
    ret = float((df['Close'].iloc[-1] / df['Close'].iloc[-period_days] - 1) * 100)
    return ret > nifty_ret, round(ret, 2), round(ret - nifty_ret, 2)

def wyckoff_check(df, sh_idx, lo_idx):
    if lo_idx <= sh_idx:
        return True, 1.0
    seg = df.iloc[sh_idx: lo_idx + 1]
    if len(seg) < 3:
        return True, 1.0
    up = seg[seg['Close'] > seg['Open']]['Volume'].sum()
    dn = seg[seg['Close'] < seg['Open']]['Volume'].sum()
    if dn == 0:
        return True, 2.0
    return (up / dn) >= 0.6, round(float(up / dn), 2)

def tight_base(df, period=15, max_sd_pct=4.0):
    if len(df) < period:
        return True, 0
    c = df['Close'].iloc[-period:]
    sd = float(c.std() / c.mean() * 100)
    return sd <= max_sd_pct, round(sd, 2)

def find_valid_resistance(df, swing_highs, threshold_atr_mult=1.5,
                          min_pullback_pct=5.0, min_sh_age=12, min_pb_age=10):
    if not swing_highs:
        return None
    close    = float(df['Close'].iloc[-1])
    closes   = df['Close'].values
    highs_a  = df['High'].values
    lows_a   = df['Low'].values
    n        = len(df)

    if n >= 50 and close < float(df['Close'].iloc[-50:].mean()) * 0.97:
        return None

    atr = calculate_atr(df)
    if atr == 0 or np.isnan(atr):
        return None

    for sh_date, sh_price in reversed(swing_highs):
        if sh_price <= close:
            continue
        try:
            bar_idx = df.index.get_loc(sh_date)
        except Exception:
            continue
        if (n - 1 - bar_idx) < min_sh_age:
            continue

        post_lows = lows_a[bar_idx + 1:]
        if len(post_lows) == 0:
            continue
        lo_rel = int(np.argmin(post_lows))
        lo_abs = bar_idx + 1 + lo_rel
        lo_val = float(post_lows[lo_rel])
        pb_pct = (sh_price - lo_val) / sh_price * 100
        if pb_pct < min_pullback_pct:
            continue

        if (n - 1 - lo_abs) < min_pb_age:
            continue

        if lo_abs < n - 1:
            hs = highs_a[lo_abs: n - 1]
            if len(hs) > 0 and float(hs.max()) > sh_price * 1.002:
                continue

        if int(np.sum(closes > sh_price * 1.002)) / n > 0.10:
            continue

        win_len = min(120, bar_idx)
        if win_len > 20:
            pre = highs_a[bar_idx - win_len: bar_idx]
            if len(pre) > 0 and float(pre.max()) > sh_price:
                continue

        gap_pts = sh_price - close
        gap_atr = round(gap_pts / atr, 2)
        if gap_atr > threshold_atr_mult:
            continue

        base_ok, base_sd = tight_base(df)
        if not base_ok:
            continue

        wy_ok, wy_ratio = wyckoff_check(df, bar_idx, lo_abs)

        tier = "HOT" if gap_atr <= 0.5 else "WARM" if gap_atr <= 1.0 else "CLOSE"

        return {
            "price":sh_price, "date":sh_date,
            "gap_pct":round(gap_pts/sh_price*100, 2), "gap_atr":gap_atr, "tier":tier,
            "pullback_pct":round(pb_pct, 2), "pullback_low":round(lo_val, 2),
            "base_sd_pct":base_sd, "wyckoff_ok":wy_ok, "wyckoff_ratio":wy_ratio,
            "atr":round(atr, 2),
        }
    return None

@st.cache_data(ttl=900, show_spinner=False)
def run_approaching(lookback, min_mcap, threshold_atr):
    risk_on, _ = get_market_regime()
    nifty_ret = get_nifty_return(63)
    results = []
    for sym in WATCHLIST:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="2y", interval="1d")
            if df.empty or len(df) < 80:
                continue
            mcap_cr = (getattr(t.fast_info, "market_cap", 0) or 0) / 1e7
            if mcap_cr < min_mcap:
                continue
            rs_ok, stock_ret, rs_diff = check_rs(df, nifty_ret)
            if not rs_ok:
                continue
            sh, sl = find_swings(df, lookback)
            r = find_valid_resistance(df, sh, threshold_atr_mult=threshold_atr)
            if not r:
                continue
            close = round(float(df['Close'].iloc[-1]), 2)
            prev  = round(float(df['Close'].iloc[-2]), 2)
            day_chg = round((close - prev) / prev * 100, 2)
            vn = float(df['Volume'].iloc[-1])
            va = float(df['Volume'].iloc[-21:-1].mean())
            vr = round(vn / va, 2) if va > 0 else 0
            adx = round(calculate_adx(df), 1)
            results.append({
                "symbol":sym.replace(".NS",""), "full_sym":sym,
                "close":close, "day_chg":day_chg,
                "swing_high":r["price"], "sh_date":r["date"].strftime("%d %b '%y"),
                "swing_low":sl[-1][1] if sl else None,
                "gap_pct":r["gap_pct"], "gap_atr":r["gap_atr"], "tier":r["tier"],
                "pullback":r["pullback_pct"], "base_sd":r["base_sd_pct"],
                "wyckoff_ok":r["wyckoff_ok"], "wyckoff_ratio":r["wyckoff_ratio"],
                "vol_ratio":vr, "adx":adx, "rs_diff":rs_diff, "stock_ret":stock_ret,
                "mcap_cr":round(mcap_cr), "sector":SECTOR_MAP.get(sym, "Other"),
                "sh_list":[(d.strftime("%Y-%m-%d"), p) for d, p in sh[-8:]],
                "sl_list":[(d.strftime("%Y-%m-%d"), p) for d, p in sl[-8:]],
            })
        except:
            continue
    order = {"HOT":0,"WARM":1,"CLOSE":2}
    return sorted(results, key=lambda x: (order[x["tier"]], x["gap_atr"])), risk_on

@st.cache_data(ttl=900, show_spinner=False)
def run_breakouts(lookback, min_mcap, days_back=5):
    risk_on, _ = get_market_regime()
    nifty_ret = get_nifty_return(63)
    results = []
    for sym in WATCHLIST:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="2y", interval="1d")
            if df.empty or len(df) < 80:
                continue
            mcap_cr = (getattr(t.fast_info, "market_cap", 0) or 0) / 1e7
            if mcap_cr < min_mcap:
                continue
            rs_ok, stock_ret, rs_diff = check_rs(df, nifty_ret)
            if not rs_ok:
                continue
            sh, sl = find_swings(df, lookback)
            n = len(df)
            closes = df['Close'].values
            vols   = df['Volume'].values

            bo_days = None; bo_level = None; bo_date = None; conf = None
            for days_ago in range(1, days_back + 1):
                cidx = n - days_ago
                c_close = float(closes[cidx]); p_close = float(closes[cidx - 1])
                df_s = df.iloc[:cidx]
                sh_s, _ = find_swings(df_s, lookback)
                v = find_valid_resistance(df_s, sh_s, threshold_atr_mult=10.0)
                if not v:
                    continue
                res = v["price"]
                if c_close > res and p_close <= res:
                    next_idx = cidx + 1
                    got = None
                    if next_idx < n and float(closes[next_idx]) > res:
                        got = "2-candle"
                    else:
                        va_ = float(vols[max(0, cidx - 20):cidx].mean())
                        if va_ > 0 and float(vols[cidx]) / va_ >= 1.5:
                            got = "volume"
                    if got is None and days_ago == 1:
                        got = "pending"
                    elif got is None:
                        continue
                    bo_days = days_ago; bo_level = res
                    bo_date = v["date"]; conf = got
                    break
            if bo_days is None:
                continue

            close = round(float(closes[-1]), 2)
            prev  = round(float(closes[-2]), 2)
            day_chg = round((close - prev) / prev * 100, 2)
            bo_pct  = round((close - bo_level) / bo_level * 100, 2)
            lbl = "TODAY" if bo_days == 1 else f"{bo_days}D AGO"
            adx = round(calculate_adx(df), 1)
            vn = float(df['Volume'].iloc[-1]); va = float(df['Volume'].iloc[-21:-1].mean())
            vr = round(vn / va, 2) if va > 0 else 0

            results.append({
                "symbol":sym.replace(".NS",""), "full_sym":sym,
                "close":close, "day_chg":day_chg,
                "broken_sh":bo_level, "sh_date":bo_date.strftime("%d %b '%y") if bo_date else "—",
                "bo_pct":bo_pct, "days_ago":bo_days, "label":lbl, "confirmation":conf,
                "swing_low":sl[-1][1] if sl else None,
                "vol_ratio":vr, "adx":adx, "rs_diff":rs_diff,
                "mcap_cr":round(mcap_cr), "sector":SECTOR_MAP.get(sym, "Other"),
                "sh_list":[(d.strftime("%Y-%m-%d"), p) for d, p in sh[-8:]],
                "sl_list":[(d.strftime("%Y-%m-%d"), p) for d, p in sl[-8:]],
            })
        except:
            continue
    return sorted(results, key=lambda x: (x["days_ago"], -x["bo_pct"])), risk_on


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 18px; border-bottom:1px solid #A87339; margin-bottom:18px'>
        <div style='font-family:Fraunces,serif;font-size:1.4rem;font-weight:700;
                    color:#D4A442; letter-spacing:-0.5px'>△ Right Horizons</div>
        <div style='font-family:JetBrains Mono,monospace; font-size:0.62rem;
                    color:#C9B896; margin-top:6px; letter-spacing:2px; text-transform:uppercase'>
            Breakout Watch · NSE Daily
        </div>
    </div>
    """, unsafe_allow_html=True)

    threshold_atr = st.slider("Gap to SH (ATRs)", 0.3, 3.0, 1.5, 0.1)
    lookback      = st.slider("Swing lookback", 5, 15, 10)
    min_mcap      = st.slider("Min market cap (₹ Cr)", 500, 10000, 500, 250)
    days_back     = st.slider("Breakout window (days)", 1, 10, 5, 1)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    run_btn = st.button("Run Screen")

    st.markdown("""
    <div style='margin-top:26px; padding:14px; background:#2a1f17;
                border:1px solid #A87339; border-radius:2px'>
        <div style='font-family:JetBrains Mono,monospace; font-size:0.58rem;
                    color:#D4A442; text-transform:uppercase; letter-spacing:1.5px;
                    margin-bottom:10px'>Active Filters · CMT Grade</div>
        <div style='font-family:Inter Tight,sans-serif; font-size:0.72rem;
                    color:#E3D5BE; line-height:1.9'>
            ① Nifty regime check<br>
            ② Relative Strength &gt; Nifty<br>
            ③ ATR-normalized distance<br>
            ④ Tight base (SD ≤ 4%)<br>
            ⑤ Wyckoff volume absorption<br>
            ⑥ Level integrity<br>
            ⑦ Chop zone rejection<br>
            ⑧ 2-candle confirmation
        </div>
    </div>
    """, unsafe_allow_html=True)

# MASTHEAD
now = datetime.now()
st.markdown(f"""
<div class="masthead">
    <div class="masthead-date-left">VOL. I · NO. {now.strftime('%j')}</div>
    <div class="masthead-brand">R<span>ight</span> Horizons</div>
    <div class="masthead-tagline">— The Breakout Watch —</div>
    <div class="masthead-date">{now.strftime("%A, %d %B %Y")}</div>
</div>
""", unsafe_allow_html=True)

# SESSION
if "results"   not in st.session_state: st.session_state.results   = None
if "breakouts" not in st.session_state: st.session_state.breakouts = None
if "risk_on"   not in st.session_state: st.session_state.risk_on   = True

if run_btn:
    with st.spinner("Scanning 110 stocks · applying 8 CMT filters..."):
        st.session_state.results,   st.session_state.risk_on = run_approaching(lookback, min_mcap, threshold_atr)
        st.session_state.breakouts, _                         = run_breakouts(lookback, min_mcap, days_back)

if st.session_state.results is None:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-orn">△</div>
        <div class="empty-state-text">Awaiting your instructions</div>
        <div class="empty-state-sub">Configure filters and press Run Screen</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

if not st.session_state.risk_on:
    st.markdown("""
    <div style='background:#fbe8e9; border:1px solid #e5b8ba; border-left:4px solid #B04848;
                padding:14px 20px; border-radius:2px; margin-bottom:20px'>
        <div style='font-family:Fraunces,serif; font-weight:700; color:#B04848; font-size:0.95rem'>
            ⚠ Market Regime: RISK-OFF
        </div>
        <div style='font-family:Inter Tight,sans-serif; font-size:0.78rem; color:#5C4B3B; margin-top:4px'>
            Nifty is trading below its 50-day MA. Breakouts fail more often in such phases.
            Consider waiting for regime confirmation.
        </div>
    </div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Approaching", "Recent Breakouts", "Validate Logic"])

def render_chart(sel):
    try:
        df_c = yf.Ticker(sel["full_sym"]).history(period="1y", interval="1d")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.72, 0.28], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(
            x=df_c.index, open=df_c['Open'], high=df_c['High'],
            low=df_c['Low'], close=df_c['Close'],
            increasing_line_color='#7A8B3F', decreasing_line_color='#B04848',
            increasing_fillcolor='#A3B55A', decreasing_fillcolor='#C46565',
            name="Price", line_width=1), row=1, col=1)
        sh_level = sel.get("swing_high") or sel.get("broken_sh")
        if sh_level:
            label = f"Resistance  ₹{sh_level:,}"
            if sel.get("gap_pct") is not None:
                label += f"  · {sel.get('gap_pct')}% / {sel.get('gap_atr','?')} ATR"
            elif sel.get("bo_pct"):
                label += f"  · broke +{sel['bo_pct']}%"
            fig.add_hline(y=sh_level, line_dash="dash", line_color="#A87339", line_width=1.5,
                annotation_text=label, annotation_position="top left",
                annotation_font=dict(color="#8B5A27", size=11, family="JetBrains Mono"),
                row=1, col=1)
        if sel.get("swing_low"):
            fig.add_hline(y=sel["swing_low"], line_dash="dot", line_color="#4A7A7A", line_width=1.2,
                annotation_text=f"Support  ₹{sel['swing_low']:,}",
                annotation_position="bottom left",
                annotation_font=dict(color="#4A7A7A", size=10, family="JetBrains Mono"),
                row=1, col=1)
        sh_d = [s[0] for s in sel["sh_list"]]; sh_p = [s[1] for s in sel["sh_list"]]
        fig.add_trace(go.Scatter(x=sh_d, y=sh_p, mode='markers',
            marker=dict(color='#A87339', size=7, symbol='triangle-down',
                        line=dict(color='#8B5A27', width=1)),
            name="Swing Highs"), row=1, col=1)
        sl_d = [s[0] for s in sel["sl_list"]]; sl_p = [s[1] for s in sel["sl_list"]]
        fig.add_trace(go.Scatter(x=sl_d, y=sl_p, mode='markers',
            marker=dict(color='#4A7A7A', size=7, symbol='triangle-up',
                        line=dict(color='#2F5555', width=1)),
            name="Swing Lows"), row=1, col=1)
        vol_c = ['rgba(122,139,63,0.5)' if c >= o else 'rgba(176,72,72,0.5)'
                 for c, o in zip(df_c['Close'], df_c['Open'])]
        fig.add_trace(go.Bar(x=df_c.index, y=df_c['Volume'],
            marker_color=vol_c, showlegend=False), row=2, col=1)
        avg_v = df_c['Volume'].rolling(20).mean()
        fig.add_trace(go.Scatter(x=df_c.index, y=avg_v,
            line=dict(color='rgba(168,115,57,0.6)', width=1, dash='dot'),
            showlegend=False), row=2, col=1)
        fig.update_layout(
            height=500, plot_bgcolor='#F5EDE0', paper_bgcolor='#EDE2D1',
            font=dict(family='JetBrains Mono', color='#5C4B3B', size=10),
            xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation='h', y=1.02, x=0, font=dict(size=9),
                        bgcolor='rgba(0,0,0,0)'))
        fig.update_xaxes(gridcolor='#C9B896', zeroline=False, linecolor='#8B7355')
        fig.update_yaxes(gridcolor='#C9B896', zeroline=False, linecolor='#8B7355')
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Chart error: {e}")


# TAB 1 — APPROACHING
with tab1:
    results = st.session_state.results
    total = len(results)
    hot   = sum(1 for r in results if r["tier"] == "HOT")
    warm  = sum(1 for r in results if r["tier"] == "WARM")
    wy    = sum(1 for r in results if r["wyckoff_ok"])
    avg_rs = round(sum(r["rs_diff"] for r in results) / total, 1) if total else 0

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi"><div class="kpi-val" style="color:#A87339">{total}</div>
            <div class="kpi-lbl">Setups</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#B04848">{hot}</div>
            <div class="kpi-lbl">Hot ≤ 0.5 ATR</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#D4A442">{warm}</div>
            <div class="kpi-lbl">Warm ≤ 1.0 ATR</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#7A8B3F">{wy}</div>
            <div class="kpi-lbl">Wyckoff Accumulation</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#4A7A7A">+{avg_rs}%</div>
            <div class="kpi-lbl">Avg RS vs Nifty</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="section-head">
        <span class="section-head-label">Dispatch 01</span>
        Stocks Approaching Resistance
    </div>""", unsafe_allow_html=True)

    if not results:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-orn">∅</div>
            <div class="empty-state-text">No approaching setups</div>
            <div class="empty-state-sub">All 8 CMT filters applied — market may be thin today</div>
        </div>""", unsafe_allow_html=True)
    else:
        rows_html = ""
        for r in results:
            sc = SECTOR_COLORS.get(r["sector"], "#8B7355")
            dc = "#7A8B3F" if r["day_chg"] >= 0 else "#B04848"
            pcls = {"HOT":"pill-hot","WARM":"pill-warm","CLOSE":"pill-cool"}[r["tier"]]
            plbl = {"HOT":"◆ HOT","WARM":"◇ WARM","CLOSE":"◌ CLOSE"}[r["tier"]]
            prox_pct = max(0, min(100, round((1 - r["gap_atr"] / max(threshold_atr, 0.1)) * 100)))
            pcol = "#B04848" if r["tier"]=="HOT" else "#D4A442" if r["tier"]=="WARM" else "#4A7A7A"
            wy_badge = "◉" if r["wyckoff_ok"] else "◎"
            wy_col   = "#7A8B3F" if r["wyckoff_ok"] else "#8B7355"
            rs_col   = "#7A8B3F" if r["rs_diff"] > 5 else "#D4A442" if r["rs_diff"] > 0 else "#8B7355"

            rows_html += f"""
            <div class="tbl-row">
                <span class="sym">{r['symbol']}</span>
                <span><span class="pill {pcls}">{plbl}</span></span>
                <span class="mono">₹{r['close']:,}<br>
                    <span style="font-size:0.7rem;color:{dc};font-weight:600">
                        {'+' if r['day_chg']>=0 else ''}{r['day_chg']}%</span>
                </span>
                <span class="mono">₹{r['swing_high']:,}<br>
                    <span style="font-size:0.65rem;color:#8B7355">{r['sh_date']}</span>
                </span>
                <span>
                    <div class="prox">
                        <div class="prox-bg">
                            <div class="prox-fill" style="width:{prox_pct}%;background:{pcol};
                                box-shadow:0 0 6px {pcol}60"></div>
                        </div>
                        <span style="font-family:JetBrains Mono;font-size:0.72rem;
                                     color:{pcol};min-width:48px;font-weight:600">
                            {r['gap_atr']}σ
                        </span>
                    </div>
                    <div style="font-size:0.6rem; color:#8B7355; font-family:JetBrains Mono;
                                margin-top:3px">
                        {r['gap_pct']}% · pb {r['pullback']}% · base σ{r['base_sd']}%
                    </div>
                </span>
                <span style="font-family:JetBrains Mono;font-size:0.75rem;color:{wy_col}">
                    {wy_badge} {r['vol_ratio']}×
                    <div style="font-size:0.58rem;color:#8B7355;margin-top:2px">
                        U/D {r['wyckoff_ratio']}
                    </div>
                </span>
                <span style="font-family:JetBrains Mono;font-size:0.72rem;color:{rs_col};
                             font-weight:600">
                    {'+' if r['rs_diff']>=0 else ''}{r['rs_diff']}%
                    <div style="font-size:0.58rem;color:#8B7355;font-weight:400;
                                text-transform:uppercase;letter-spacing:0.8px">
                        RS · ADX {r['adx']}
                    </div>
                </span>
                <span>
                    <span class="sec" style="background:{sc}18;color:{sc};border:1px solid {sc}50">
                        {r['sector']}
                    </span>
                    <div style="font-family:JetBrains Mono;font-size:0.6rem;color:#8B7355;margin-top:4px">
                        ₹{r['mcap_cr']:,}Cr
                    </div>
                </span>
            </div>"""

        st.markdown(f"""
        <div class="tbl">
          <div class="tbl-hdr">
            <span>Symbol</span><span>Tier</span><span>Close</span>
            <span>Resistance</span><span>Distance</span>
            <span>Vol / Wyckoff</span><span>RS / ADX</span><span>Sector</span>
          </div>
          <div class="scroll-body">{rows_html}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""<div class="section-head">
            <span class="section-head-label">Visual</span>
            Chart Detail
        </div>""", unsafe_allow_html=True)
        sel_sym = st.selectbox("Select stock", [r["symbol"] for r in results],
                               key="sel_t1", label_visibility="collapsed")
        if sel_sym:
            s = next(r for r in results if r["symbol"] == sel_sym)
            render_chart(s)
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Close",        f"₹{s['close']:,}",       f"{s['day_chg']}%")
            c2.metric("Resistance",   f"₹{s['swing_high']:,}",  f"{s['gap_atr']}σ")
            c3.metric("Pullback",     f"{s['pullback']}%",       f"base σ{s['base_sd']}%")
            c4.metric("RS (3M)",      f"+{s['rs_diff']}%",       f"ADX {s['adx']}")
            c5.metric("Wyckoff",
                      "Accumulation" if s['wyckoff_ok'] else "Weak",
                      f"U/D {s['wyckoff_ratio']}")


# TAB 2 — RECENT BREAKOUTS
with tab2:
    bos = st.session_state.breakouts or []
    total_b = len(bos)
    today_b = sum(1 for b in bos if b["days_ago"] == 1)
    conf_b  = sum(1 for b in bos if b["confirmation"] in ("2-candle","volume"))
    avg_bo  = round(sum(b["bo_pct"] for b in bos) / total_b, 2) if total_b else 0

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi"><div class="kpi-val" style="color:#A87339">{total_b}</div>
            <div class="kpi-lbl">Breakouts</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#B04848">{today_b}</div>
            <div class="kpi-lbl">Today</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#D4A442">{total_b - today_b}</div>
            <div class="kpi-lbl">Last {days_back}d</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#7A8B3F">{conf_b}</div>
            <div class="kpi-lbl">Confirmed</div></div>
        <div class="kpi"><div class="kpi-val" style="color:#4A7A7A">+{avg_bo}%</div>
            <div class="kpi-lbl">Avg Breakout</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="section-head">
        <span class="section-head-label">Dispatch 02</span>
        Confirmed Breakouts
    </div>""", unsafe_allow_html=True)

    if not bos:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-orn">∅</div>
            <div class="empty-state-text">No confirmed breakouts</div>
            <div class="empty-state-sub">Requires 2-candle hold or 1.5× volume</div>
        </div>""", unsafe_allow_html=True)
    else:
        bo_html = ""
        for b in bos:
            sc = SECTOR_COLORS.get(b["sector"], "#8B7355")
            dc = "#7A8B3F" if b["day_chg"] >= 0 else "#B04848"
            day_pill = "pill-hot" if b["days_ago"]==1 else "pill-warm"
            conf = b["confirmation"]
            conf_badge = "◉ 2-candle" if conf == "2-candle" else "◉ volume" if conf == "volume" else "◎ pending"
            conf_col = "#7A8B3F" if conf != "pending" else "#D4A442"
            rs_col = "#7A8B3F" if b["rs_diff"] > 5 else "#D4A442" if b["rs_diff"] > 0 else "#8B7355"

            bo_html += f"""
            <div class="tbl-row">
                <span class="sym">{b['symbol']}</span>
                <span><span class="pill {day_pill}">{b['label']}</span></span>
                <span class="mono">₹{b['close']:,}<br>
                    <span style="font-size:0.7rem;color:{dc};font-weight:600">
                        {'+' if b['day_chg']>=0 else ''}{b['day_chg']}%</span>
                </span>
                <span class="mono">₹{b['broken_sh']:,}<br>
                    <span style="font-size:0.6rem;color:#8B7355">set {b['sh_date']}</span>
                </span>
                <span style="font-family:Fraunces,serif; font-size:1rem; color:#7A8B3F; font-weight:700">
                    +{b['bo_pct']}%
                    <div style="font-family:JetBrains Mono;font-size:0.62rem;
                                color:{conf_col};font-weight:600;margin-top:2px">{conf_badge}</div>
                </span>
                <span style="font-family:JetBrains Mono;font-size:0.75rem">
                    {b['vol_ratio']}×
                    <div style="font-size:0.58rem;color:#8B7355;margin-top:2px">ADX {b['adx']}</div>
                </span>
                <span style="font-family:JetBrains Mono;font-size:0.72rem;color:{rs_col};
                             font-weight:600">
                    +{b['rs_diff']}%
                    <div style="font-size:0.58rem;color:#8B7355;font-weight:400;
                                text-transform:uppercase;letter-spacing:0.8px">RS</div>
                </span>
                <span>
                    <span class="sec" style="background:{sc}18;color:{sc};border:1px solid {sc}50">
                        {b['sector']}
                    </span>
                    <div style="font-family:JetBrains Mono;font-size:0.6rem;color:#8B7355;margin-top:4px">
                        ₹{b['mcap_cr']:,}Cr
                    </div>
                </span>
            </div>"""

        st.markdown(f"""
        <div class="tbl">
          <div class="tbl-hdr">
            <span>Symbol</span><span>When</span><span>Close</span>
            <span>Broken Level</span><span>Breakout</span>
            <span>Volume</span><span>RS</span><span>Sector</span>
          </div>
          <div class="scroll-body">{bo_html}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""<div class="section-head">
            <span class="section-head-label">Visual</span>
            Chart Detail
        </div>""", unsafe_allow_html=True)
        sel2 = st.selectbox("Select stock", [b["symbol"] for b in bos],
                            key="sel_t2", label_visibility="collapsed")
        if sel2:
            b = next(x for x in bos if x["symbol"] == sel2)
            render_chart(b)
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Close",       f"₹{b['close']:,}",       f"{b['day_chg']}%")
            c2.metric("Broke",       f"₹{b['broken_sh']:,}",   b['label'])
            c3.metric("Breakout",    f"+{b['bo_pct']}%",        b["confirmation"])
            c4.metric("Volume",      f"{b['vol_ratio']}×",      f"ADX {b['adx']}")
            c5.metric("RS (3M)",     f"+{b['rs_diff']}%")


# TAB 3 — VALIDATE
with tab3:
    st.markdown("""
    <div style='background:#EDE2D1;border:1px solid #C9B896;border-left:3px solid #A87339;
                border-radius:2px;padding:18px 22px;margin-bottom:24px'>
        <div style='font-family:Fraunces,serif;font-size:1.05rem;font-weight:700;
                    color:#1F1611;font-style:italic;margin-bottom:8px'>
            Validating the Screener's Historical Accuracy
        </div>
        <div style='font-family:Inter Tight,sans-serif;font-size:0.82rem;
                    color:#5C4B3B;line-height:1.7'>
            Select any stock. The engine walks through 2 years of history, flags every
            breakout the screener would have caught, and marks each as <b>Real</b>,
            <b>Weak</b>, or <b>False</b>.
        </div>
    </div>""", unsafe_allow_html=True)

    all_symbols = sorted([s.replace(".NS", "") for s in WATCHLIST])
    bt_symbol = st.selectbox("Stock to validate", all_symbols, key="bt_sym",
                             index=all_symbols.index("TITAN") if "TITAN" in all_symbols else 0)
    bt_run = st.button("Validate", key="bt_btn")

    if bt_run:
        with st.spinner(f"Walking through 2 years of {bt_symbol}..."):
            try:
                df = yf.Ticker(f"{bt_symbol}.NS").history(period="2y", interval="1d")
                if df.empty:
                    st.error("No data available.")
                    st.stop()
                signals = []
                checked = set()
                closes  = df['Close'].values
                min_bars = lookback * 2 + 30
                for i in range(min_bars, len(df)):
                    df_s = df.iloc[:i]
                    sh_s, _ = find_swings(df_s, lookback)
                    close_now  = float(df_s['Close'].iloc[-1])
                    prev_close = float(df_s['Close'].iloc[-2])
                    if i >= 50:
                        ma50 = float(df_s['Close'].iloc[-50:].mean())
                        if close_now < ma50 * 0.97:
                            continue
                    val = find_valid_resistance(df_s, sh_s, threshold_atr_mult=10.0)
                    if not val:
                        continue
                    sh_price = val["price"]; key = round(sh_price, 1)
                    if key in checked:
                        continue
                    if prev_close <= sh_price < close_now:
                        checked.add(key)
                        future = closes[i: i + 10]
                        if len(future) > 0:
                            max_gain = round((future.max() - sh_price) / sh_price * 100, 2)
                            min_draw = round((future.min() - sh_price) / sh_price * 100, 2)
                            if max_gain >= 3:
                                result, tag = f"Real breakout (+{max_gain}% within 10d)", "real"
                            elif max_gain >= 1:
                                result, tag = f"Weak follow-through (peak +{max_gain}%)", "weak"
                            else:
                                result, tag = f"False breakout ({min_draw}% to +{max_gain}%)", "false"
                        else:
                            result, tag = "Too recent", "recent"
                        signals.append({
                            "Date":df_s.index[-1].strftime("%d %b '%y"),
                            "Broke Above":f"₹{sh_price:,}",
                            "Set On":val["date"].strftime("%d %b '%y"),
                            "Pullback":f"{val['pullback_pct']}%",
                            "Gap (ATR)":f"{val['gap_atr']}σ",
                            "Base SD":f"{val['base_sd_pct']}%",
                            "Outcome":result, "_tag":tag,
                        })

                total = len(signals)
                real  = sum(1 for s in signals if s["_tag"] == "real")
                weak  = sum(1 for s in signals if s["_tag"] == "weak")
                false = sum(1 for s in signals if s["_tag"] == "false")
                acc   = round(real / total * 100, 1) if total else 0

                if acc >= 70:   verdict, vc = "LOGIC IS SOLID",    "#7A8B3F"
                elif acc >= 50: verdict, vc = "LOGIC IS DECENT",   "#D4A442"
                elif total==0:  verdict, vc = "NO BREAKOUTS IN 2Y","#8B7355"
                else:           verdict, vc = "LOGIC NEEDS WORK",  "#B04848"

                st.markdown("""<div class="section-head">
                    <span class="section-head-label">Report</span>
                    Signal Accuracy
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div class="kpi-row">
                    <div class="kpi"><div class="kpi-val" style="color:#A87339">{total}</div>
                        <div class="kpi-lbl">Detected</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:#7A8B3F">{real}</div>
                        <div class="kpi-lbl">Real</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:#D4A442">{weak}</div>
                        <div class="kpi-lbl">Weak</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:#B04848">{false}</div>
                        <div class="kpi-lbl">False</div></div>
                    <div class="kpi"><div class="kpi-val" style="color:{vc}">{acc}%</div>
                        <div class="kpi-lbl">{verdict}</div></div>
                </div>""", unsafe_allow_html=True)

                if signals:
                    st.markdown("""<div class="section-head">
                        <span class="section-head-label">Detail</span>
                        Every Historical Breakout
                    </div>""", unsafe_allow_html=True)
                    for s in signals: s.pop("_tag", None)
                    df_sig = pd.DataFrame(signals)
                    st.dataframe(df_sig, use_container_width=True, hide_index=True,
                                 height=min(500, 42 * len(signals) + 45))

                    st.markdown("""<div class="section-head">
                        <span class="section-head-label">Visual</span>
                        Breakouts Plotted on Chart
                    </div>""", unsafe_allow_html=True)
                    fig = make_subplots(rows=1, cols=1)
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'],
                        increasing_line_color='#7A8B3F', decreasing_line_color='#B04848',
                        increasing_fillcolor='#A3B55A', decreasing_fillcolor='#C46565',
                        name="Price", line_width=1))
                    bo_dates, bo_prices, bo_colors = [], [], []
                    for s in signals:
                        try:
                            dt = datetime.strptime(s["Date"], "%d %b '%y")
                            bo_dates.append(dt)
                            bo_prices.append(float(s["Broke Above"].replace("₹","").replace(",","")))
                            if "Real" in s["Outcome"]:    bo_colors.append('#7A8B3F')
                            elif "Weak" in s["Outcome"]: bo_colors.append('#D4A442')
                            else:                          bo_colors.append('#B04848')
                        except:
                            continue
                    if bo_dates:
                        fig.add_trace(go.Scatter(
                            x=bo_dates, y=bo_prices, mode='markers',
                            marker=dict(symbol='diamond', size=14, color=bo_colors,
                                        line=dict(color='#1F1611', width=1)),
                            name="Signals"))
                    fig.update_layout(
                        height=480, plot_bgcolor='#F5EDE0', paper_bgcolor='#EDE2D1',
                        font=dict(family='JetBrains Mono', color='#5C4B3B', size=10),
                        xaxis_rangeslider_visible=False, showlegend=False,
                        margin=dict(l=10, r=10, t=10, b=10))
                    fig.update_xaxes(gridcolor='#C9B896', zeroline=False)
                    fig.update_yaxes(gridcolor='#C9B896', zeroline=False)
                    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True,
                                    config={"displayModeBar": False})
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("""
                    <div style='font-family:JetBrains Mono,monospace; font-size:0.68rem;
                                color:#8B7355;margin-top:10px;line-height:2;letter-spacing:0.5px'>
                        ◆ OLIVE — real (≥3% in 10d)  &nbsp;·&nbsp;
                        ◆ GOLD — weak follow-through  &nbsp;·&nbsp;
                        ◆ CRIMSON — false breakout
                    </div>""", unsafe_allow_html=True)
                else:
                    st.info("No breakouts detected — the stock had no clean setups in 2 years.")

            except Exception as e:
                st.error(f"Validation failed: {e}")


# Footer
st.markdown("""
<div class="ornament">※ · ※ · ※</div>
<div style='text-align:center; font-family:Fraunces,serif; font-style:italic;
            color:#8B7355; font-size:0.75rem; padding:14px 0 24px'>
    Right Horizons Breakout Watch · Yahoo Finance data ·
    <span style='font-family:JetBrains Mono,monospace; font-size:0.62rem;
                 letter-spacing:1px; text-transform:uppercase'>
        Not Financial Advice
    </span>
</div>""", unsafe_allow_html=True)
