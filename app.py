import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
# Define the custom CSS
hide_streamlit_style = """
<style>
/* Hides the top-right menu */
#MainMenu {visibility: hidden;}

/* Hides the 'Made with Streamlit' footer */
footer {visibility: hidden;}

/* Hides the top header line completely */
header {visibility: hidden;}

/* Hides the 'Deploy' button specifically */
.stDeployButton {display:none;}
</style>
"""

# Inject the CSS into the Streamlit app
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
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
}

SECTOR_COLORS = {
    "Banking":"#3b82f6","IT":"#a78bfa","FMCG":"#fb923c","Finance":"#34d399",
    "Energy":"#f87171","Infra":"#22d3ee","Auto":"#f97316","Pharma":"#f472b6",
    "Consumer":"#a3e635","Metal":"#94a3b8","Cement":"#fbbf24","Telecom":"#38bdf8",
}

# ── LOGIC ─────────────────────────────────────────────────────
def find_swings(df, lookback=5):
    highs, lows, n = df['High'].values, df['Low'].values, len(df)
    sh, sl = [], []
    for i in range(lookback, n - lookback):
        if highs[i] == max(highs[i-lookback:i+lookback+1]):
            sh.append((df.index[i], round(float(highs[i]), 2)))
        if lows[i] == min(lows[i-lookback:i+lookback+1]):
            sl.append((df.index[i], round(float(lows[i]), 2)))
    return sh, sl


def check_approaching(df, swing_highs, threshold_pct, vol_mult):
    if not swing_highs:
        return False, None, None, False, 0
    _, last_sh = swing_highs[-1]
    close    = float(df['Close'].iloc[-1])
    vol_now  = float(df['Volume'].iloc[-1])
    vol_avg  = float(df['Volume'].iloc[-21:-1].mean())
    vol_ratio= round(vol_now / vol_avg, 2) if vol_avg > 0 else 0
    if close >= last_sh:          # already broken out — skip
        return False, None, None, False, 0
    gap_pct = round((last_sh - close) / last_sh * 100, 2)
    if gap_pct > threshold_pct:   # too far away — skip
        return False, None, None, False, 0
    return True, last_sh, gap_pct, vol_ratio >= vol_mult, vol_ratio


@st.cache_data(ttl=900, show_spinner=False)
def run_screener(lookback, vol_mult, min_mcap, threshold):
    results = []
    for sym in WATCHLIST:
        try:
            t  = yf.Ticker(sym)
            df = t.history(period="2y", interval="1d")   # full 2-year history
            if df.empty or len(df) < lookback * 2 + 20:
                continue
            mcap_cr = (getattr(t.fast_info, "market_cap", 0) or 0) / 1e7
            if mcap_cr < min_mcap:
                continue
            sh, sl = find_swings(df, lookback)
            ok, last_sh, gap, vol_ok, vol_r = check_approaching(df, sh, threshold, vol_mult)
            if not ok:
                continue
            close   = round(float(df['Close'].iloc[-1]), 2)
            prev    = round(float(df['Close'].iloc[-2]), 2)
            day_chg = round((close - prev) / prev * 100, 2)
            signal  = "HOT" if gap <= 0.5 else "WARM" if gap <= 1.2 else "CLOSE"
            results.append({
                "symbol"   : sym.replace(".NS",""),
                "full_sym" : sym,
                "close"    : close,
                "day_chg"  : day_chg,
                "swing_high": last_sh,
                "sh_date"  : sh[-1][0].strftime("%d %b '%y"),
                "swing_low": sl[-1][1] if sl else None,
                "gap_pct"  : gap,
                "vol_ok"   : vol_ok,
                "vol_ratio": vol_r,
                "mcap_cr"  : round(mcap_cr),
                "sector"   : SECTOR_MAP.get(sym, "Other"),
                "signal"   : signal,
                "sh_list"  : [(d.strftime("%Y-%m-%d"), p) for d, p in sh[-8:]],
                "sl_list"  : [(d.strftime("%Y-%m-%d"), p) for d, p in sl[-8:]],
            })
        except:
            continue
    order = {"HOT":0,"WARM":1,"CLOSE":2}
    return sorted(results, key=lambda x: (order[x["signal"]], x["gap_pct"]))


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
        <span style='color:#2d3f5c'> — volume building up</span>
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
if "results" not in st.session_state:
    st.session_state.results = None

if run_btn:
    with st.spinner("Scanning 90 stocks · 2Y daily data · this takes ~90 sec…"):
        st.session_state.results = run_screener(lookback, vol_mult, min_mcap, threshold)

if st.session_state.results is None:
    st.markdown("""
    <div style='text-align:center; padding:100px 20px'>
        <div style='font-size:3rem; opacity:0.15; margin-bottom:14px'>🎯</div>
        <div style='color:#1a2540; font-size:1rem; font-weight:600'>
            Configure parameters and click Scan Now
        </div>
        <div style='color:#0f1825; font-size:0.8rem; margin-top:6px'>
            Finds stocks that are close to — but have NOT yet broken — their swing high
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

results = st.session_state.results
if vol_only:
    results = [r for r in results if r["vol_ok"]]

# ── KPIs ──────────────────────────────────────────────────────
total  = len(results)
hot    = sum(1 for r in results if r["signal"] == "HOT")
warm   = sum(1 for r in results if r["signal"] == "WARM")
vol_b  = sum(1 for r in results if r["vol_ok"])
avg_gap= round(sum(r["gap_pct"] for r in results) / total, 2) if total else 0

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

# ── TABLE ─────────────────────────────────────────────────────
st.markdown('<div class="sec-head">Pre-Breakout Setups</div>', unsafe_allow_html=True)

if not results:
    st.markdown("""
    <div style='text-align:center; padding:50px; color:#1f2d47'>
        No setups match. Try raising the gap threshold or lowering market cap.
    </div>""", unsafe_allow_html=True)
    st.stop()

rows_html = ""
for r in results:
    sc      = SECTOR_COLORS.get(r["sector"], "#64748b")
    dc      = "#4ade80" if r["day_chg"] >= 0 else "#f87171"
    pcls    = {"HOT":"pill-hot","WARM":"pill-warm","CLOSE":"pill-cool"}[r["signal"]]
    plbl    = {"HOT":"🔴 HOT","WARM":"🟡 WARM","CLOSE":"🔵 CLOSE"}[r["signal"]]
    prox    = round((1 - r["gap_pct"] / threshold) * 100)
    pcol    = "#4ade80" if r["signal"]=="HOT" else "#fbbf24" if r["signal"]=="WARM" else "#60a5fa"
    vc      = "#34d399" if r["vol_ok"] else "#2d3f5c"
    vlbl    = f"{'↑ ' if r['vol_ok'] else ''}{r['vol_ratio']}x"

    rows_html += f"""
    <div class="tbl-row">
        <span class="sym">{r['symbol']}</span>
        <span><span class="pill {pcls}">{plbl}</span></span>
        <span class="mono">₹{r['close']:,}
            <span style="font-size:.65rem;color:{dc}"> {'+' if r['day_chg']>=0 else ''}{r['day_chg']}%</span>
        </span>
        <span class="mono">₹{r['swing_high']:,}
            <span style="display:block;font-size:.6rem;color:#2d3f5c">{r['sh_date']}</span>
        </span>
        <span>
            <div class="prox-wrap">
                <div class="prox-bg">
                    <div class="prox-fill" style="width:{prox}%;background:{pcol};box-shadow:0 0 5px {pcol}50"></div>
                </div>
                <span style="font-family:IBM Plex Mono;font-size:.75rem;color:{pcol};min-width:38px">{r['gap_pct']}%</span>
            </div>
        </span>
        <span style="font-family:IBM Plex Mono;font-size:.78rem;color:{vc}">{vlbl}</span>
        <span><span class="sec-badge" style="background:{sc}18;color:{sc};border:1px solid {sc}30">{r['sector']}</span></span>
        <span style="font-family:IBM Plex Mono;font-size:.7rem;color:#2d3f5c">₹{r['mcap_cr']:,}Cr</span>
    </div>"""

st.markdown(f"""
<div class="tbl-wrap">
  <div class="tbl-header">
    <span class="col-hdr">Symbol</span>
    <span class="col-hdr">Signal</span>
    <span class="col-hdr">Close</span>
    <span class="col-hdr">Swing High</span>
    <span class="col-hdr">Gap to High</span>
    <span class="col-hdr">Volume</span>
    <span class="col-hdr">Sector</span>
    <span class="col-hdr">Mkt Cap</span>
  </div>
  <div class="scroll-body">{rows_html}</div>
</div>
""", unsafe_allow_html=True)

# ── CHART ─────────────────────────────────────────────────────
st.markdown('<div class="sec-head">Chart View</div>', unsafe_allow_html=True)

sel_sym = st.selectbox("Pick a stock", [r["symbol"] for r in results], label_visibility="collapsed")

if sel_sym:
    sel = next(r for r in results if r["symbol"] == sel_sym)
    try:
        df_c = yf.Ticker(sel["full_sym"]).history(period="1y", interval="1d")

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.72, 0.28], vertical_spacing=0.02)

        fig.add_trace(go.Candlestick(
            x=df_c.index, open=df_c['Open'], high=df_c['High'],
            low=df_c['Low'], close=df_c['Close'],
            increasing_line_color='#4ade80', decreasing_line_color='#f87171',
            increasing_fillcolor='#4ade80',  decreasing_fillcolor='#f87171',
            name="Price", line_width=1,
        ), row=1, col=1)

        # Swing high horizontal line
        fig.add_hline(y=sel["swing_high"], line_dash="dash", line_color="#fbbf24", line_width=1.5,
            annotation_text=f"Swing High  ₹{sel['swing_high']:,}  ← {sel['gap_pct']}% away",
            annotation_position="top left",
            annotation_font=dict(color="#fbbf24", size=11, family="IBM Plex Mono"),
            row=1, col=1)

        if sel["swing_low"]:
            fig.add_hline(y=sel["swing_low"], line_dash="dot", line_color="#60a5fa", line_width=1.2,
                annotation_text=f"Swing Low  ₹{sel['swing_low']:,}",
                annotation_position="bottom left",
                annotation_font=dict(color="#60a5fa", size=11, family="IBM Plex Mono"),
                row=1, col=1)

        # Swing high markers
        sh_d = [s[0] for s in sel["sh_list"]]
        sh_p = [s[1] for s in sel["sh_list"]]
        fig.add_trace(go.Scatter(x=sh_d, y=sh_p, mode='markers',
            marker=dict(color='#fbbf24', size=8, symbol='triangle-down'),
            name="Swing Highs"), row=1, col=1)

        sl_d = [s[0] for s in sel["sl_list"]]
        sl_p = [s[1] for s in sel["sl_list"]]
        fig.add_trace(go.Scatter(x=sl_d, y=sl_p, mode='markers',
            marker=dict(color='#60a5fa', size=8, symbol='triangle-up'),
            name="Swing Lows"), row=1, col=1)

        vol_c = ['#4ade8055' if c >= o else '#f8717155'
                 for c, o in zip(df_c['Close'], df_c['Open'])]
        fig.add_trace(go.Bar(x=df_c.index, y=df_c['Volume'],
            marker_color=vol_c, showlegend=False), row=2, col=1)

        avg_v = df_c['Volume'].rolling(20).mean()
        fig.add_trace(go.Scatter(x=df_c.index, y=avg_v,
            line=dict(color='#fbbf2450', width=1, dash='dot'),
            showlegend=False), row=2, col=1)

        fig.update_layout(
            height=500, plot_bgcolor='#0a0f1e', paper_bgcolor='#0d1424',
            font=dict(family='IBM Plex Mono', color='#4b5e7e', size=10),
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=16, b=10),
            legend=dict(orientation='h', y=1.02, x=0,
                        font=dict(size=10), bgcolor='rgba(0,0,0,0)'),
        )
        fig.update_xaxes(gridcolor='#111827', zeroline=False)
        fig.update_yaxes(gridcolor='#111827', zeroline=False)

        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Close",        f"₹{sel['close']:,}",       f"{sel['day_chg']}% today")
        c2.metric("Swing High",   f"₹{sel['swing_high']:,}",  f"Set {sel['sh_date']}")
        c3.metric("Gap to High",  f"{sel['gap_pct']}%",        sel["signal"])
        c4.metric("Swing Low",    f"₹{sel['swing_low']:,}" if sel['swing_low'] else "—")
        c5.metric("Volume",       f"{sel['vol_ratio']}x",      "Building ↑" if sel['vol_ok'] else "Normal")

    except Exception as e:
        st.error(f"Chart error: {e}")

st.markdown("""
<div style='text-align:center;margin-top:48px;padding-top:18px;border-top:1px solid #0d1424;
            font-size:0.62rem;color:#0f1825;font-family:IBM Plex Mono'>
    NSE Breakout Watch · Yahoo Finance · 2Y daily · Not financial advice
</div>""", unsafe_allow_html=True)
