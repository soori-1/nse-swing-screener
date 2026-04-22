import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NSE Swing Breakout Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Sora:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sora', sans-serif;
    }
    .stApp {
        background: #070d1a;
    }
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1a2744 100%);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, #3b82f620 0%, transparent 70%);
        pointer-events: none;
    }
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-subtitle {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 6px;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-card {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 18px 22px;
        text-align: center;
    }
    .metric-number {
        font-size: 2.2rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 6px;
    }
    .breakout-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        border-left: 3px solid #22c55e;
        transition: all 0.2s;
    }
    .breakout-card.no-vol {
        border-left-color: #f59e0b;
    }
    .stock-symbol {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .signal-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-strong {
        background: #14532d;
        color: #4ade80;
        border: 1px solid #22c55e40;
    }
    .badge-weak {
        background: #451a03;
        color: #fbbf24;
        border: 1px solid #f59e0b40;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 28px;
        font-family: 'Sora', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        width: 100%;
        transition: all 0.2s;
        box-shadow: 0 4px 15px #3b82f630;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px #3b82f650;
    }
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stMultiSelect"] label {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .sector-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-left: 8px;
    }
    .timestamp {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #475569;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# WATCHLIST
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
    "PIDILITIND.NS", "BERGEPAINT.NS", "HAVELLS.NS", "VOLTAS.NS", "ITC.NS",
    "PERSISTENT.NS", "MPHASIS.NS", "LTIM.NS", "COFORGE.NS", "ZOMATO.NS",
    "IRCTC.NS", "INDHOTEL.NS", "RVNL.NS", "IRFC.NS", "RECLTD.NS",
    "PFC.NS", "BANKBARODA.NS", "CANBK.NS", "PNB.NS", "FEDERALBNK.NS",
    "IDFCFIRSTB.NS", "INDUSINDBK.NS", "AUBANK.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS",
    "APOLLOHOSP.NS", "FORTIS.NS", "AUROPHARMA.NS", "LUPIN.NS", "TORNTPHARM.NS",
    "TATAPOWER.NS", "ADANIGREEN.NS", "NAUKRI.NS", "INDIGO.NS", "OFSS.NS",
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
}

SECTOR_COLORS = {
    "Banking":"#3b82f6","IT":"#8b5cf6","FMCG":"#f59e0b","Finance":"#10b981",
    "Energy":"#ef4444","Infra":"#06b6d4","Auto":"#f97316","Pharma":"#ec4899",
    "Consumer":"#84cc16","Metal":"#a8a29e","Cement":"#d97706","Telecom":"#0ea5e9",
}

# ─────────────────────────────────────────────────────────────
# CORE LOGIC
# ─────────────────────────────────────────────────────────────
def find_swings(df, lookback=5):
    highs = df['High'].values
    lows  = df['Low'].values
    n     = len(df)
    swing_highs, swing_lows = [], []
    for i in range(lookback, n - lookback):
        if highs[i] == max(highs[i - lookback: i + lookback + 1]):
            swing_highs.append((df.index[i], round(float(highs[i]), 2)))
        if lows[i] == min(lows[i - lookback: i + lookback + 1]):
            swing_lows.append((df.index[i], round(float(lows[i]), 2)))
    return swing_highs, swing_lows


def check_breakout(df, swing_highs, vol_mult=1.2):
    if not swing_highs:
        return False, None, False, 0
    last_swing_date, last_swing_price = swing_highs[-1]
    today_close  = float(df['Close'].iloc[-1])
    today_volume = float(df['Volume'].iloc[-1])
    avg_volume   = float(df['Volume'].iloc[-21:-1].mean())
    vol_ratio    = today_volume / avg_volume if avg_volume > 0 else 0
    is_breakout  = today_close > last_swing_price
    vol_ok       = vol_ratio >= vol_mult
    return is_breakout, last_swing_price, vol_ok, round(vol_ratio, 2)


@st.cache_data(ttl=900, show_spinner=False)
def run_screener(swing_lookback, vol_multiplier, min_mcap_cr):
    results = []
    for symbol in WATCHLIST:
        try:
            ticker = yf.Ticker(symbol)
            df     = ticker.history(period="6mo", interval="1d")
            if df.empty or len(df) < (swing_lookback * 2 + 10):
                continue
            info = ticker.fast_info
            mcap = getattr(info, "market_cap", 0) or 0
            mcap_cr = mcap / 1e7
            if mcap_cr < min_mcap_cr:
                continue
            swing_highs, swing_lows = find_swings(df, swing_lookback)
            if not swing_highs:
                continue
            is_bo, last_sh, vol_ok, vol_ratio = check_breakout(df, swing_highs, vol_multiplier)
            if not is_bo:
                continue
            close     = round(float(df['Close'].iloc[-1]), 2)
            prev_close= round(float(df['Close'].iloc[-2]), 2)
            day_chg   = round((close - prev_close) / prev_close * 100, 2)
            bo_pct    = round((close - last_sh) / last_sh * 100, 2)
            last_sl   = swing_lows[-1][1] if swing_lows else None
            risk      = round((close - last_sl) / close * 100, 2) if last_sl else None
            hist_slice = df['Close'].iloc[-20:].tolist()
            results.append({
                "symbol"      : symbol.replace(".NS", ""),
                "full_symbol" : symbol,
                "close"       : close,
                "day_chg"     : day_chg,
                "swing_high"  : last_sh,
                "swing_high_date": swing_highs[-1][0].strftime("%d %b"),
                "swing_low"   : last_sl,
                "breakout_pct": bo_pct,
                "vol_confirmed": vol_ok,
                "vol_ratio"   : vol_ratio,
                "mcap_cr"     : round(mcap_cr),
                "sector"      : SECTOR_MAP.get(symbol, "Other"),
                "history"     : hist_slice,
                "all_swing_highs": [(d.strftime("%d %b"), p) for d, p in swing_highs[-5:]],
                "all_swing_lows" : [(d.strftime("%d %b"), p) for d, p in swing_lows[-5:]],
            })
        except:
            continue
    return sorted(results, key=lambda x: (not x["vol_confirmed"], -x["breakout_pct"]))


def make_candlestick_chart(symbol, swing_highs, swing_lows):
    try:
        df = yf.Ticker(f"{symbol}.NS").history(period="3mo", interval="1d")
        if df.empty:
            return None
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.72, 0.28], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            increasing_line_color='#22c55e', decreasing_line_color='#ef4444',
            increasing_fillcolor='#22c55e', decreasing_fillcolor='#ef4444',
            name="Price", line_width=1
        ), row=1, col=1)

        sh_dates = [s[0] for s in swing_highs[-5:]]
        sh_prices= [s[1] for s in swing_highs[-5:]]
        fig.add_trace(go.Scatter(
            x=[df.index[df.index.get_loc(d, method='nearest')] for d in [df.index[-1]][:1]],
            y=sh_prices[-1:],
            mode='lines',
            line=dict(color='#f59e0b', width=1.5, dash='dash'),
            name=f"Swing High ₹{sh_prices[-1] if sh_prices else ''}",
        ), row=1, col=1)

        if swing_lows:
            sl_prices = [s[1] for s in swing_lows[-3:]]
            fig.add_trace(go.Scatter(
                x=[df.index[0], df.index[-1]],
                y=[sl_prices[-1], sl_prices[-1]],
                mode='lines',
                line=dict(color='#3b82f6', width=1.5, dash='dot'),
                name=f"Swing Low ₹{sl_prices[-1]}",
            ), row=1, col=1)

        colors = ['#22c55e' if v >= df['Volume'].mean() else '#475569' for v in df['Volume']]
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'], marker_color=colors,
            name="Volume", showlegend=False
        ), row=2, col=1)

        fig.update_layout(
            height=480,
            plot_bgcolor='#0f172a', paper_bgcolor='#0f172a',
            font=dict(family='JetBrains Mono', color='#94a3b8', size=11),
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation='h', y=1.02, font=dict(size=10),
                        bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)'),
        )
        fig.update_xaxes(gridcolor='#1e293b', showgrid=True, zeroline=False)
        fig.update_yaxes(gridcolor='#1e293b', showgrid=True, zeroline=False)
        return fig
    except:
        return None


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px'>
        <div style='font-size:2rem'>📈</div>
        <div style='font-weight:700; color:#e2e8f0; font-size:1rem; letter-spacing:-0.3px'>NSE Screener</div>
        <div style='color:#475569; font-size:0.72rem; font-family:JetBrains Mono'>Swing Breakout · Daily</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    swing_lookback = st.slider("Swing Lookback (candles)", 3, 10, 5,
        help="Number of candles on each side to confirm a swing point")
    vol_multiplier = st.slider("Volume Multiplier", 1.0, 3.0, 1.2, 0.1,
        help="Breakout volume must exceed X × 20-day average")
    min_mcap = st.slider("Min Market Cap (₹ Cr)", 500, 5000, 500, 100)
    vol_filter = st.checkbox("Show only volume-confirmed", value=False)

    st.divider()

    run_btn = st.button("🔍  Run Screener")

    st.markdown("""
    <div style='margin-top:24px; padding:14px; background:#0f172a; border-radius:10px; border:1px solid #1e293b'>
        <div style='color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px'>Legend</div>
        <div style='font-size:0.78rem; color:#94a3b8; line-height:2'>
            🟢 <b>Strong</b> — Vol confirmed<br>
            🟡 <b>Weak</b> — No vol confirm<br>
            📊 <b>Swing High</b> — Resistance<br>
            📉 <b>Swing Low</b> — Support
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <div class="main-title">📈 NSE Swing Breakout Screener</div>
    <div class="main-subtitle">
        Daily Timeframe · >₹{min_mcap} Cr Market Cap · 
        Lookback: {swing_lookback} candles · Vol: {vol_multiplier}x
    </div>
    <div class="timestamp" style="margin-top:8px">
        Last run: {datetime.now().strftime("%d %b %Y, %I:%M %p IST")}
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None

if run_btn:
    with st.spinner("🔍 Scanning NSE stocks... this takes ~60 seconds"):
        st.session_state.results = run_screener(swing_lookback, vol_multiplier, min_mcap)

if st.session_state.results is None:
    st.markdown("""
    <div style='text-align:center; padding:80px 20px; color:#334155'>
        <div style='font-size:4rem; margin-bottom:16px'>🎯</div>
        <div style='font-size:1.3rem; font-weight:600; color:#475569'>Ready to scan</div>
        <div style='font-size:0.85rem; margin-top:8px'>
            Adjust parameters in the sidebar and click <b>Run Screener</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

results = st.session_state.results
if vol_filter:
    results = [r for r in results if r["vol_confirmed"]]

# ─────────────────────────────────────────────────────────────
# METRICS ROW
# ─────────────────────────────────────────────────────────────
total      = len(results)
strong     = sum(1 for r in results if r["vol_confirmed"])
weak       = total - strong
sectors    = len(set(r["sector"] for r in results))
avg_bo_pct = round(sum(r["breakout_pct"] for r in results) / total, 2) if total else 0

c1, c2, c3, c4, c5 = st.columns(5)
for col, num, label, color in [
    (c1, total,    "Breakouts Found",    "#3b82f6"),
    (c2, strong,   "Vol Confirmed ✅",   "#22c55e"),
    (c3, weak,     "Weak Signal ⚠️",    "#f59e0b"),
    (c4, sectors,  "Sectors",            "#8b5cf6"),
    (c5, f"+{avg_bo_pct}%", "Avg Breakout", "#10b981"),
]:
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-number" style="color:{color}">{num}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SECTOR DISTRIBUTION CHART
# ─────────────────────────────────────────────────────────────
if results:
    sector_counts = {}
    for r in results:
        sector_counts[r["sector"]] = sector_counts.get(r["sector"], 0) + 1

    col_chart, col_list = st.columns([1, 2])

    with col_chart:
        fig_pie = go.Figure(go.Pie(
            labels=list(sector_counts.keys()),
            values=list(sector_counts.values()),
            hole=0.55,
            marker=dict(colors=[SECTOR_COLORS.get(s, "#64748b") for s in sector_counts.keys()],
                        line=dict(color='#0f172a', width=2)),
            textfont=dict(family='JetBrains Mono', size=11),
        ))
        fig_pie.update_layout(
            height=260,
            showlegend=True,
            legend=dict(font=dict(size=10, family='JetBrains Mono'), bgcolor='rgba(0,0,0,0)'),
            plot_bgcolor='#0f172a', paper_bgcolor='#0f172a',
            font=dict(color='#94a3b8'),
            margin=dict(l=0, r=0, t=0, b=0),
            annotations=[dict(text=f"<b>{total}</b><br>stocks", x=0.5, y=0.5,
                              font=dict(size=14, color='#e2e8f0', family='JetBrains Mono'),
                              showarrow=False)]
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with col_list:
        # Breakout % bar chart
        syms = [r["symbol"] for r in results[:12]]
        bpcts = [r["breakout_pct"] for r in results[:12]]
        colors_bar = ["#22c55e" if r["vol_confirmed"] else "#f59e0b" for r in results[:12]]

        fig_bar = go.Figure(go.Bar(
            y=syms[::-1], x=bpcts[::-1], orientation='h',
            marker=dict(color=colors_bar[::-1],
                        line=dict(color='rgba(0,0,0,0)')),
            text=[f"+{p}%" for p in bpcts[::-1]],
            textposition='outside',
            textfont=dict(family='JetBrains Mono', size=10, color='#94a3b8'),
        ))
        fig_bar.update_layout(
            height=260,
            plot_bgcolor='#0f172a', paper_bgcolor='#0f172a',
            font=dict(color='#94a3b8', family='JetBrains Mono', size=10),
            margin=dict(l=10, r=60, t=0, b=0),
            xaxis=dict(gridcolor='#1e293b', zeroline=False, showticklabels=False),
            yaxis=dict(gridcolor='rgba(0,0,0,0)'),
            bargap=0.3,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

st.divider()

# ─────────────────────────────────────────────────────────────
# STOCK CARDS + CHART DETAIL
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='font-size:0.75rem; color:#475569; text-transform:uppercase;
            letter-spacing:1.5px; font-weight:600; margin-bottom:14px'>
    🔥 Breakout Signals — Click a stock to view chart
</div>
""", unsafe_allow_html=True)

if not results:
    st.info("No breakouts found. Try lowering the volume multiplier or market cap filter.")
else:
    selected = st.session_state.get("selected_stock", None)

    for r in results:
        sec_color = SECTOR_COLORS.get(r["sector"], "#64748b")
        badge_class = "badge-strong" if r["vol_confirmed"] else "badge-weak"
        badge_text  = "✅ Strong Signal" if r["vol_confirmed"] else "⚠️ Weak Signal"
        day_color   = "#22c55e" if r["day_chg"] >= 0 else "#ef4444"
        border_col  = "#22c55e" if r["vol_confirmed"] else "#f59e0b"

        col_card, col_btn = st.columns([6, 1])
        with col_card:
            st.markdown(f"""
            <div class="breakout-card {'no-vol' if not r['vol_confirmed'] else ''}"
                 style="border-left-color:{border_col}">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px">
                    <div style="display:flex; align-items:center; gap:10px">
                        <span class="stock-symbol">{r['symbol']}</span>
                        <span class="sector-tag" style="background:{sec_color}20; color:{sec_color}; border:1px solid {sec_color}40">
                            {r['sector']}
                        </span>
                        <span class="signal-badge {badge_class}">{badge_text}</span>
                    </div>
                    <div style="display:flex; gap:24px; align-items:center">
                        <div style="text-align:right">
                            <div style="font-family:'JetBrains Mono'; font-size:1.1rem; color:#e2e8f0; font-weight:700">
                                ₹{r['close']:,}
                            </div>
                            <div style="font-size:0.75rem; color:{day_color}">
                                {'+' if r['day_chg'] >= 0 else ''}{r['day_chg']}% today
                            </div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.5px">Swing High</div>
                            <div style="font-family:'JetBrains Mono'; font-size:0.85rem; color:#f59e0b">₹{r['swing_high']:,}</div>
                            <div style="font-size:0.6rem; color:#475569">{r['swing_high_date']}</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.5px">Swing Low</div>
                            <div style="font-family:'JetBrains Mono'; font-size:0.85rem; color:#3b82f6">
                                {'₹' + str(r['swing_low']) if r['swing_low'] else 'N/A'}
                            </div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.5px">Breakout</div>
                            <div style="font-family:'JetBrains Mono'; font-size:0.85rem; color:#22c55e; font-weight:700">
                                +{r['breakout_pct']}%
                            </div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.5px">Vol Ratio</div>
                            <div style="font-family:'JetBrains Mono'; font-size:0.85rem; color:{'#22c55e' if r['vol_confirmed'] else '#f59e0b'}">
                                {r['vol_ratio']}x
                            </div>
                        </div>
                        <div style="text-align:right">
                            <div style="font-size:0.65rem; color:#64748b">Mkt Cap</div>
                            <div style="font-size:0.78rem; color:#94a3b8">₹{r['mcap_cr']:,} Cr</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            if st.button("📊 Chart", key=f"btn_{r['symbol']}"):
                st.session_state.selected_stock = r['symbol'] if selected != r['symbol'] else None
                st.rerun()

        # Expanded chart
        if st.session_state.get("selected_stock") == r["symbol"]:
            with st.container():
                ticker_obj = yf.Ticker(f"{r['symbol']}.NS")
                df_full    = ticker_obj.history(period="3mo", interval="1d")
                if not df_full.empty:
                    sh_list = [(pd.Timestamp(d, tz='UTC'), p) for d, p in r["all_swing_highs"]]
                    sl_list = [(pd.Timestamp(d, tz='UTC'), p) for d, p in r["all_swing_lows"]]
                    fig = make_candlestick_chart(r["symbol"], sh_list, sl_list)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    # Mini stats row
                    s1, s2, s3, s4 = st.columns(4)
                    s1.metric("Current Close", f"₹{r['close']:,}", f"{r['day_chg']}%")
                    s2.metric("Swing High", f"₹{r['swing_high']:,}", f"Broke +{r['breakout_pct']}%")
                    s3.metric("Swing Low (Support)", f"₹{r['swing_low']:,}" if r['swing_low'] else "N/A")
                    s4.metric("Volume Ratio", f"{r['vol_ratio']}x", "Confirmed ✅" if r['vol_confirmed'] else "Not confirmed ⚠️")
            st.markdown("---")

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center; padding:24px; color:#1e293b; font-size:0.72rem;
            font-family:JetBrains Mono; margin-top:40px; border-top:1px solid #0f172a'>
    NSE Swing Breakout Screener · Data via Yahoo Finance · Not financial advice<br>
    {len(WATCHLIST)} stocks scanned · Refreshes every 15 min on re-run
</div>
""", unsafe_allow_html=True)
