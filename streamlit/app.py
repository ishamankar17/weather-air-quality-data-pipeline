import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from google.cloud import bigquery
from plotly.subplots import make_subplots

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Pune Weather & Air Quality Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# HTML HELPER

def html(snippet: str) -> str:
    return " ".join(line.strip() for line in snippet.splitlines() if line.strip())


# =========================================================
# COLOUR SYSTEM
# =========================================================
BG = "#F3F6FB"
PANEL = "#FFFFFF"
TEXT = "#1B2437"
MUTED = "#6B7791"
GRID = "rgba(100,116,139,0.18)"
BORDER = "rgba(15,23,42,0.09)"

C_TEMP = "#FF7A59"
C_HUM = "#4DA3FF"
C_AQI = "#A78BFA"
C_PM25 = "#FF4D6D"
C_PM10 = "#FFC145"
C_WIND = "#2EC4B6"
C_RAIN = "#3A86FF"

AQI_ORDER = ["Good", "Fair", "Moderate", "Poor", "Very Poor", "Extremely Poor"]
AQI_COLORS = ["#2ecc71", "#a3d977", "#f1c40f", "#e67e22", "#e74c3c", "#8e44ad"]

CHART_H = 215


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    html(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(180deg, #EAF1FB 0%, {BG} 45%);
            color: {TEXT};
        }}
        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stToolbar"], [data-testid="stDecoration"], footer {{
            display: none !important;
        }}
        .block-container {{
            padding: 1.6rem 2rem 0.6rem 2rem;
            max-width: 100%;
        }}
        [data-testid="stVerticalBlock"] {{ gap: 0.7rem; }}
        [data-testid="stHorizontalBlock"] {{ gap: 0.9rem; }}

        .title-row {{ display: flex; align-items: center; gap: 14px; }}
        .title-icon {{ font-size: 2.1rem; }}
        .app-title {{
            font-size: 1.75rem; font-weight: 800; margin: 0; line-height: 1.15;
            background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 55%, #7C3AED 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .app-sub {{ color: {MUTED}; font-size: 0.82rem; margin: 2px 0 0 0; }}
        .badge {{
            display: inline-block; padding: 1px 9px; margin-right: 6px;
            border-radius: 20px; background: rgba(46,196,182,0.15);
            color: #0F8F84; font-size: 0.72rem; font-weight: 600;
        }}
        .badge-filter {{ background: rgba(245,158,11,0.18); color: #B45309; }}

        .kpi {{
            position: relative; overflow: hidden; height: 98px;
            background: {PANEL}; border: 1px solid {BORDER};
            box-shadow: 0 2px 8px rgba(15,23,42,0.06);
            border-radius: 14px; padding: 12px 16px;
        }}
        .kpi::before {{
            content: ""; position: absolute; left: 0; top: 0; right: 0;
            height: 3px; background: var(--accent);
        }}
        .kpi-icon {{ position: absolute; right: 14px; top: 12px; font-size: 1.35rem; opacity: .9; }}
        .kpi-label {{ font-size: 0.7rem; color: {MUTED}; text-transform: uppercase; letter-spacing: .07em; }}
        .kpi-value {{ font-size: 1.7rem; font-weight: 800; line-height: 1.2; color: {TEXT}; }}
        .kpi-sub {{ font-size: 0.72rem; color: {MUTED}; }}

        [class*="st-key-panel"] {{
            background: {PANEL}; border: 1px solid {BORDER};
            box-shadow: 0 2px 8px rgba(15,23,42,0.06);
            border-radius: 14px; padding: 12px 14px 4px 14px;
        }}
        .ptitle {{ font-size: 0.88rem; font-weight: 700; color: {TEXT}; margin: 0 0 2px 2px; }}
        .ptitle span {{ color: {MUTED}; font-weight: 500; font-size: 0.74rem; margin-left: 6px; }}
        </style>
        """
    ),
    unsafe_allow_html=True,
)


# =========================================================
# LOAD DATA FROM BIGQUERY
# =========================================================
@st.cache_data(ttl=3600, show_spinner="Loading data from BigQuery...")
def load_data() -> pd.DataFrame:
    client = bigquery.Client(project="weather-aq-pipeline")
    query = """
    SELECT *
    FROM `weather-aq-pipeline.weather_warehouse.daily_weather_air_quality`
    ORDER BY date_key
    """
    data = client.query(query).to_dataframe()
    data["date_key"] = pd.to_datetime(data["date_key"])
    return data


def aqi_cat(value) -> str:
    if pd.isna(value):
        return "n/a"
    for limit, name in [(20, "Good"), (40, "Fair"), (60, "Moderate"),
                        (80, "Poor"), (100, "Very Poor")]:
        if value < limit:
            return name
    return "Extremely Poor"


df_all = load_data()
df_all["aqi_cat"] = df_all["avg_european_aqi"].apply(aqi_cat)
min_d = df_all["date_key"].min().date()
max_d = df_all["date_key"].max().date()


# =========================================================
# CROSS-FILTER STATE
# =========================================================
st.session_state.setdefault("ver", 0)
st.session_state.setdefault("active", None)
st.session_state.setdefault("prev_sel", {})

TIME_CHARTS = ["ch_weather", "ch_aqi", "ch_pm", "ch_rain"]
ALL_CHARTS = TIME_CHARTS + ["ch_cat"]
ver = st.session_state["ver"]


def read_selection(chart: str):
    state = st.session_state.get(f"{chart}_{ver}")
    try:
        points = state["selection"]["points"]
    except Exception:
        return frozenset()

    selected = set()
    for p in points:
        if chart == "ch_cat":
            # Pie slices report a label / index instead of an x value
            label = p.get("label")
            if label is None:
                idx = p.get("point_index", p.get("point_number"))
                label = AQI_ORDER[idx] if idx is not None and idx < len(AQI_ORDER) else p.get("x")
            if label is not None:
                selected.add(str(label))
        else:
            x_value = p.get("x")
            if x_value is not None:
                selected.add(str(pd.to_datetime(x_value).date()))
    return frozenset(selected)


current = {chart: read_selection(chart) for chart in ALL_CHARTS}

for chart, selection in current.items():
    previous = st.session_state["prev_sel"].get(chart, frozenset())
    if selection != previous:
        if not selection:
            st.session_state["active"] = None
        elif chart == "ch_cat":
            st.session_state["active"] = ("cat", next(iter(selection)))
        else:
            st.session_state["active"] = ("dates", set(selection))

st.session_state["prev_sel"] = current
active = st.session_state["active"]


def reset_filters():
    st.session_state["ver"] += 1
    st.session_state["active"] = None
    st.session_state["prev_sel"] = {}


# =========================================================
# HEADER CONTROLS
# =========================================================
h1, h2, h3, h4 = st.columns([3.2, 1.3, 1.0, 0.7])
title_slot = h1.empty()

with h2:
    picked = st.date_input(
        "Date range",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d,
        label_visibility="collapsed",
    )

with h3:
    smooth = st.toggle("3-day smoothing", value=False)

with h4:
    st.button("↺ Reset", on_click=reset_filters, width="stretch", disabled=active is None)


# =========================================================
# DATE FILTER
# =========================================================
if isinstance(picked, (tuple, list)) and len(picked) == 2:
    start, end = picked
    df = df_all[
        (df_all["date_key"].dt.date >= start) & (df_all["date_key"].dt.date <= end)
    ].copy()
else:
    df = df_all.copy()

if df.empty:
    st.warning("No data in the selected range.")
    st.stop()


# =========================================================
# CROSS-FILTER
# =========================================================
df["day"] = df["date_key"].dt.strftime("%Y-%m-%d")

if active is None:
    mask = pd.Series(True, index=df.index)
elif active[0] == "dates":
    mask = df["day"].isin(active[1])
else:
    mask = df["aqi_cat"] == active[1]

if not mask.any():
    mask = pd.Series(True, index=df.index)
    active = None

dv = df[mask]
sel_idx = list(np.where(mask.values)[0]) if active is not None else None
x = df["date_key"]


# =========================================================
# DASHBOARD TITLE
# =========================================================
if active is None:
    filter_note = ""
elif active[0] == "dates":
    filter_note = f'<span class="badge badge-filter">FILTER · {len(dv)} day(s) selected</span>'
else:
    filter_note = f'<span class="badge badge-filter">FILTER · AQI {active[1]} · {len(dv)} day(s)</span>'

title_slot.markdown(
    html(
        f"""
        <div class="title-row">
        <div class="title-icon">🌦️</div>
        <div>
        <p class="app-title">Pune Weather &amp; Air Quality Dashboard</p>
        <p class="app-sub">
        <span class="badge">LIVE PIPELINE</span>
        {filter_note}
        Data from {min_d:%d %b} to {max_d:%d %b %Y} · click or drag on any chart to cross-filter
        </p>
        </div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================
def sm(series: pd.Series) -> pd.Series:
    return series.rolling(3, min_periods=1).mean() if smooth else series


def latest(column: str):
    series = dv[column].dropna()
    return series.iloc[-1] if len(series) else float("nan")


def kpi(col, icon, label, value, sub, color):
    col.markdown(
        html(
            f"""
            <div class="kpi" style="--accent:{color}">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


# =========================================================
# KPI CARDS
# =========================================================
avg_aqi = dv["avg_european_aqi"].mean()
k = st.columns(6)

kpi(k[0], "🌡️", "Avg Temperature", f"{dv['avg_temperature_c'].mean():.1f} °C",
    f"Latest {latest('avg_temperature_c'):.1f} °C", C_TEMP)
kpi(k[1], "💧", "Avg Humidity", f"{dv['avg_humidity_percent'].mean():.1f}%",
    f"Latest {latest('avg_humidity_percent'):.1f}%", C_HUM)
kpi(k[2], "🌫️", "Avg AQI (EU)", "–" if pd.isna(avg_aqi) else f"{avg_aqi:.0f}",
    f"{aqi_cat(avg_aqi)} · latest {latest('avg_european_aqi'):.0f}", C_AQI)
kpi(k[3], "🫁", "Avg PM2.5", f"{dv['avg_pm2_5'].mean():.1f}",
    f"Latest {latest('avg_pm2_5'):.1f} µg/m³", C_PM25)
kpi(k[4], "🍃", "Avg Wind", f"{dv['avg_wind_speed_kmh'].mean():.1f} km/h",
    f"Latest {latest('avg_wind_speed_kmh'):.1f} km/h", C_WIND)
kpi(k[5], "🌧️", "Total Rain", f"{dv['total_precipitation_mm'].sum():.1f} mm",
    f"{int((dv['total_precipitation_mm'] > 0).sum())} rainy days", C_RAIN)


# =========================================================
# CHART HELPERS
# =========================================================
PLOT_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "autoScale2d", "toImage"],
}

LINE = dict(shape="spline", smoothing=0.6)


def style(fig, height=CHART_H):
    fig.update_layout(
        height=height,
        margin=dict(l=4, r=4, t=22, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=11, color="#334155"),
        legend=dict(orientation="h", y=1.16, x=0, font=dict(size=10)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#CBD5E1", font_size=11, font_color=TEXT),
        dragmode="select",
        selectdirection="h",
    )
    fig.update_xaxes(showgrid=False, tickformat="%d %b", tickfont=dict(size=10), linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, tickfont=dict(size=10), zeroline=False)
    return fig


def highlight(fig):
    if sel_idx is not None:
        fig.update_traces(
            selectedpoints=sel_idx,
            selected=dict(marker=dict(opacity=1)),
            unselected=dict(marker=dict(opacity=0.22)),
        )
    return fig


def show(fig, chart, modes=("points", "box")):
    st.plotly_chart(
        fig,
        width="stretch",
        config=PLOT_CONFIG,
        key=f"{chart}_{ver}",
        on_select="rerun",
        selection_mode=modes,
    )


def panel(key):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container(border=True)


def title(text, hint=""):
    st.markdown(html(f'<div class="ptitle">{text}<span>{hint}</span></div>'),
                unsafe_allow_html=True)


# =========================================================
# ROW 1
# =========================================================
c1, c2, c3 = st.columns(3)

with c1:
    with panel("panel_weather"):
        title("🌡️ Temperature & Humidity", "drag to select days")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=x, y=sm(df["avg_temperature_c"]), name="Temp (°C)",
            line=dict(color=C_TEMP, width=2.6, **LINE), mode="lines+markers",
            marker=dict(size=6, color=C_TEMP)), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=x, y=sm(df["avg_humidity_percent"]), name="Humidity (%)",
            line=dict(color=C_HUM, width=2, **LINE), mode="lines+markers",
            marker=dict(size=5, color=C_HUM),
            fill="tozeroy", fillcolor="rgba(77,163,255,0.10)"), secondary_y=True)
        fig.update_yaxes(title_text="°C", title_font=dict(size=10), secondary_y=False)
        fig.update_yaxes(range=[0, 100], showgrid=False, title_text="%",
                         title_font=dict(size=10), secondary_y=True)
        show(style(highlight(fig)), "ch_weather")

with c2:
    with panel("panel_aqi"):
        title("💨 European AQI Trend", "shaded by category")
        fig = go.Figure()
        aqi_max = df["avg_european_aqi"].max(skipna=True)
        if pd.isna(aqi_max):
            aqi_max = 100
        top = max(100, float(aqi_max) * 1.1)
        for lo, hi, color in [(0, 20, AQI_COLORS[0]), (20, 40, AQI_COLORS[1]),
                              (40, 60, AQI_COLORS[2]), (60, 80, AQI_COLORS[3]),
                              (80, 100, AQI_COLORS[4]), (100, 300, AQI_COLORS[5])]:
            fig.add_hrect(y0=lo, y1=hi, fillcolor=color, opacity=0.13, line_width=0)
        fig.add_trace(go.Scatter(
            x=x, y=sm(df["avg_european_aqi"]), name="AQI",
            line=dict(color=C_AQI, width=2.8, **LINE), mode="lines+markers",
            marker=dict(size=7, color=C_AQI, line=dict(width=1, color="#FFFFFF"))))
        fig.update_yaxes(range=[0, top])
        fig.update_layout(showlegend=False)
        show(style(highlight(fig)), "ch_aqi")

with c3:
    with panel("panel_pm"):
        title("🫁 PM2.5 vs PM10", "µg/m³")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x, y=sm(df["avg_pm10"]), name="PM10",
            line=dict(color=C_PM10, width=2.2, **LINE), mode="lines+markers",
            marker=dict(size=5, color=C_PM10),
            fill="tozeroy", fillcolor="rgba(255,193,69,0.16)"))
        fig.add_trace(go.Scatter(
            x=x, y=sm(df["avg_pm2_5"]), name="PM2.5",
            line=dict(color=C_PM25, width=2.2, **LINE), mode="lines+markers",
            marker=dict(size=5, color=C_PM25),
            fill="tozeroy", fillcolor="rgba(255,77,109,0.20)"))
        show(style(highlight(fig)), "ch_pm")


# =========================================================
# ROW 2
# =========================================================
d1, d2, d3 = st.columns(3)

with d1:
    with panel("panel_cat"):
        title("🎯 AQI Category Distribution", "click a category to filter")
        base = dv if (active and active[0] == "dates") else df
        counts = base["aqi_cat"].value_counts().reindex(AQI_ORDER).fillna(0).astype(int)
        chosen = active[1] if (active and active[0] == "cat") else None
        pull_values = [0.08 if c == chosen else 0 for c in AQI_ORDER]

        fig = go.Figure(go.Pie(
            labels=AQI_ORDER, values=counts.values, hole=0.58, sort=False,
            pull=pull_values,
            marker=dict(colors=AQI_COLORS, line=dict(color="#FFFFFF", width=2)),
            textinfo="percent", textposition="inside",
            hovertemplate="<b>%{label}</b><br>%{value} day(s)<br>%{percent}<extra></extra>"))
        fig.update_layout(
            height=CHART_H,
            margin=dict(l=4, r=85, t=22, b=4),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=10, color=TEXT),
            showlegend=True,
            legend=dict(orientation="v", y=0.5, x=1.02, xanchor="left",
                        yanchor="middle", font=dict(size=9)),
            hovermode="closest",
        )
        show(fig, "ch_cat", modes=("points",))

with d2:
    with panel("panel_rain"):
        title("🌧️ Rainfall & Wind", "mm · km/h")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=x, y=df["total_precipitation_mm"], name="Rain (mm)",
            marker=dict(color=C_RAIN, cornerradius=4)), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=x, y=sm(df["avg_wind_speed_kmh"]), name="Wind (km/h)",
            line=dict(color=C_WIND, width=2.4, **LINE), mode="lines+markers",
            marker=dict(size=6, color=C_WIND)), secondary_y=True)
        fig.update_yaxes(showgrid=False, rangemode="tozero", secondary_y=True)
        fig.update_yaxes(rangemode="tozero", secondary_y=False)
        show(style(highlight(fig)), "ch_rain")

with d3:
    with panel("panel_table"):
        title("📊 Daily Summary", "follows the filter")
        table = dv[["date_key", "avg_temperature_c", "avg_humidity_percent",
                    "total_precipitation_mm", "avg_pm2_5", "avg_european_aqi"]].copy()
        table["date_key"] = table["date_key"].dt.strftime("%d %b")
        table.columns = ["Date", "Temp °C", "Hum %", "Rain mm", "PM2.5", "AQI"]
        st.dataframe(
            table.iloc[::-1],
            width="stretch",
            hide_index=True,
            height=CHART_H,
            column_config={
                "Temp °C": st.column_config.NumberColumn(format="%.1f"),
                "Hum %": st.column_config.NumberColumn(format="%.0f"),
                "Rain mm": st.column_config.NumberColumn(format="%.1f"),
                "PM2.5": st.column_config.NumberColumn(format="%.1f"),
                "AQI": st.column_config.ProgressColumn(format="%.0f", min_value=0, max_value=100),
            },
        )


# =========================================================
# FOOTER
# =========================================================
st.divider()
st.caption("Data pipeline: Open-Meteo → Python → PySpark → BigQuery → dbt → Airflow → Streamlit")