"""
CYBERINTEL — Dashboard Streamlit v3.1
======================================

Fichiers requis  :
  - datasets/suspicion_scores.csv        (Unified_scoring.py)
  - datasets/dashboard_data.csv          (pipeline_FINAL.ipynb)
  - datasets/predictions_finales.csv     (pipeline_FINAL.ipynb)
  - datasets/comparaison_modeles.csv     (pipeline_FINAL.ipynb)
  - datasets/cross_validation_results.csv (pipeline_FINAL.ipynb)
  - datasets/graph_links.json            (Unified_scoring.py)

Usage :
  streamlit run dashboard.py
"""

import json
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import streamlit as st

# ─────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CyberIntel v3.1",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

*, html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0c1222 100%) !important; color: #e2e8f0; }
header[data-testid="stHeader"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

.block-container {
    padding-top: 0 !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0e1a 100%) !important;
    border-right: 1px solid rgba(0,212,255,0.15) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem !important; }

.sidebar-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px; font-weight: 700;
    background: linear-gradient(135deg, #00d4ff, #00e676);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.filter-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    color: #00d4ff; margin-bottom: 1rem; display: block;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, rgba(13,17,23,0.9), rgba(10,14,26,0.9));
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 12px; padding: 1.25rem;
    position: relative; overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.kpi-card:hover { transform: translateY(-2px); border-color: rgba(0,212,255,0.3); }
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, #00d4ff, #00e676);
}
.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 600;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: #64748b; margin-bottom: 8px; margin-top: 4px;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 32px; font-weight: 700;
    color: #00d4ff; line-height: 1; margin-bottom: 8px;
}
.kpi-trend { font-size: 11px; color: #00e676; }

/* Section titles */
.section-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; font-weight: 600;
    color: #00d4ff; letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 1rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(0,212,255,0.2);
}

/* Chart label */
.chart-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 600;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: #64748b; margin-bottom: 0.4rem;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(13,17,23,0.85) !important;
    border: 1px solid rgba(0,212,255,0.22) !important;
    border-radius: 12px !important; padding: 1rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border: none !important; background: transparent !important;
}

/* Buttons */
.stButton > button {
    background: rgba(0,212,255,0.08) !important;
    color: #64748b !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important; font-weight: 600 !important;
    letter-spacing: 1px !important; border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.25), rgba(0,230,118,0.15)) !important;
    color: #00d4ff !important; border: 1px solid #00d4ff !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(13,17,23,0.8); border-radius: 8px; padding: 1rem;
    border: 1px solid rgba(0,212,255,0.12);
}

/* Info/warning banners */
.data-missing-banner {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 8px; padding: 1rem 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: #f59e0b;
    margin-bottom: 1rem;
}

@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.5; transform:scale(1.2); }
}
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: linear-gradient(135deg,#00d4ff,#00e676); border-radius: 3px; }
[data-testid="stDataFrame"] { border-radius: 8px !important; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# NAVIGATION STATE
# ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Overview"

def navigate_to(page):
    st.session_state.page = page

# ─────────────────────────────────────────────
# CONSTANTES VISUELLES
# ─────────────────────────────────────────────
COLOR_MAP  = {"HIGH": "#ff3b5c", "MEDIUM": "#f59e0b", "LOW": "#00e676"}
BASE_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono", color="#94a3b8", size=11),
    margin=dict(t=10, b=10, l=10, r=10),
)
GRID = dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")

# ─────────────────────────────────────────────
# CHARGEMENT DES DONNÉES 
# ─────────────────────────────────────────────

@st.cache_data
def load_all_data():
    base = Path("datasets")
    missing = []

    # ── 1. suspicion_scores.csv ──────────────────────────────
    scores_path = base / "suspicion_scores.csv"
    if scores_path.exists():
        scores = pd.read_csv(scores_path)

        
        if "risk_level" not in scores.columns and "suspicion_score" in scores.columns:
            def classify(s):
                if s >= 0.62: return "HIGH"
                elif s >= 0.45: return "MEDIUM"
                return "LOW"
            scores["risk_level"] = scores["suspicion_score"].apply(classify)
    else:
        missing.append("suspicion_scores.csv")
        scores = pd.DataFrame()

    # ── 2. dashboard_data.csv ────────────────────────────────
    dash_path = base / "dashboard_data.csv"
    if dash_path.exists():
        dashboard = pd.read_csv(dash_path)
    else:
        missing.append("dashboard_data.csv")
        dashboard = pd.DataFrame()

    # ── 3. predictions_finales.csv ───────────────────────────
    preds_path = base / "predictions_finales.csv"
    if preds_path.exists():
        preds = pd.read_csv(preds_path)
    else:
        missing.append("predictions_finales.csv")
        preds = pd.DataFrame()

    # ── 4. comparaison_modeles.csv ───────────────────────────
    comp_path = base / "comparaison_modeles.csv"
    if comp_path.exists():
        comparaison = pd.read_csv(comp_path, index_col=0)
    else:
        missing.append("comparaison_modeles.csv")
        comparaison = pd.DataFrame()

    # ── 5. graph_links.json ──────────────────────────────────
    links_path = base / "graph_links.json"
    if links_path.exists():
        with open(links_path, "r", encoding="utf-8") as f:
            links = json.load(f)
    else:
        missing.append("graph_links.json")
        links = []

    return scores, dashboard, preds, comparaison, links, missing


scores, dashboard, preds, comparaison, links, missing_files = load_all_data()


def missing_banner(filename: str, script: str):
    """Affiche un bandeau d'avertissement si un fichier est absent."""
    st.markdown(
        f'<div class="data-missing-banner">⚠ <b>{filename}</b> introuvable — '
        f'exécutez <b>{script}</b> pour générer ce fichier.</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1.5rem 0; border-bottom:1px solid rgba(0,212,255,0.15); margin-bottom:1.5rem;">
        <div class="sidebar-logo">CYBERINTEL</div>
        <div style="font-size:10px; color:#475569; margin-top:8px;">Threat Intelligence Platform v3.1</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="filter-title">Filtres d\'analyse</span>', unsafe_allow_html=True)

    if not scores.empty and "risk_level" in scores.columns:
        available_risks = sorted(scores["risk_level"].dropna().unique().tolist())
        risk_filter = st.multiselect("Niveau de risque", options=["HIGH", "MEDIUM", "LOW"],
                                     default=available_risks, key="risk_filter")
        score_min = st.slider("Score minimum", 0.0, 1.0, 0.0, 0.01, key="score_min")
        top_n     = st.slider("Top N domaines", 5, 50, 20, key="top_n")
    else:
        risk_filter = ["HIGH", "MEDIUM", "LOW"]
        score_min   = 0.0
        top_n       = 20

    st.markdown("---")
    st.markdown('<span class="filter-title">Distribution réelle</span>', unsafe_allow_html=True)
    if not scores.empty and "risk_level" in scores.columns:
        for risk in ["HIGH", "MEDIUM", "LOW"]:
            cnt   = len(scores[scores["risk_level"] == risk])
            color = COLOR_MAP[risk]
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                <span style="color:{color};font-size:11px;">● {risk}</span>
                <span style="color:#e2e8f0;font-family:monospace;">{cnt}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.caption("Aucune donnée chargée.")

    st.markdown("---")

    # Statut des fichiers
    all_files = {
        "suspicion_scores.csv":       ("Unified_scoring.py",       Path("datasets/suspicion_scores.csv").exists()),
        "dashboard_data.csv":         ("pipeline_FINAL.ipynb",  Path("datasets/dashboard_data.csv").exists()),
        "predictions_finales.csv":    ("pipeline_FINAL.ipynb",  Path("datasets/predictions_finales.csv").exists()),
        "comparaison_modeles.csv":    ("pipeline_FINAL.ipynb",  Path("datasets/comparaison_modeles.csv").exists()),
        "graph_links.json":           ("Unified_scoring.py",       Path("datasets/graph_links.json").exists()),
    }
    st.markdown('<span class="filter-title">Fichiers chargés</span>', unsafe_allow_html=True)
    for fname, (_, ok) in all_files.items():
        icon  = "✅" if ok else "❌"
        color = "#00e676" if ok else "#ff3b5c"
        st.markdown(f'<div style="font-size:10px;color:{color};margin-bottom:4px;">{icon} {fname}</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.caption(f"Dernière actualisation : {datetime.now().strftime('%H:%M:%S')}")

# ─────────────────────────────────────────────
# DONNÉES FILTRÉES
# ─────────────────────────────────────────────
if not scores.empty and "risk_level" in scores.columns and "suspicion_score" in scores.columns:
    filtered_df = scores[
        (scores["risk_level"].isin(risk_filter)) &
        (scores["suspicion_score"] >= score_min)
    ].sort_values("suspicion_score", ascending=False)
else:
    filtered_df = pd.DataFrame()

# ─────────────────────────────────────────────
# HELPERS VISUELS
# ─────────────────────────────────────────────
def framed_chart(title, fig, key=None):
    st.markdown(f'<div class="chart-label">{title}</div>', unsafe_allow_html=True)
    with st.container(border=True):
        kw = dict(use_container_width=True)
        if key: kw["key"] = key
        st.plotly_chart(fig, **kw)


def framed_dataframe(title, data, height=400):
    st.markdown(f'<div class="chart-label">{title}</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.dataframe(data, use_container_width=True, height=height)


def make_gauge(score: float):
    if score >= 0.62:
        bar_color, zone = "#ff3b5c", "CRITIQUE"
    elif score >= 0.45:
        bar_color, zone = "#f59e0b", "MODERE"
    else:
        bar_color, zone = "#00e676", "FAIBLE"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 24, "color": bar_color, "family": "JetBrains Mono"},
                "valueformat": ".3f"},
        domain={"x": [0, 1], "y": [0, 0.85]},
        gauge={
            "axis": {"range": [0, 1], "tickwidth": 1, "tickcolor": "#475569",
                     "tickfont": {"size": 9, "color": "#64748b", "family": "JetBrains Mono"},
                     "tickvals": [0, 0.45, 0.62, 1], "ticktext": ["0", "0.45", "0.62", "1"]},
            "bar":     {"color": bar_color, "thickness": 0.18},
            "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
            "steps": [
                {"range": [0, 0.45],    "color": "rgba(0,230,118,0.12)"},
                {"range": [0.45, 0.62], "color": "rgba(245,158,11,0.12)"},
                {"range": [0.62, 1],    "color": "rgba(255,59,92,0.12)"},
            ],
            "threshold": {"line": {"color": "#ff3b5c", "width": 2}, "thickness": 0.75, "value": 0.62}
        }
    ))
    fig.update_layout(height=110, paper_bgcolor="rgba(0,0,0,0)",
                      font={"family": "JetBrains Mono"},
                      margin=dict(t=5, b=0, l=18, r=18))
    return fig, bar_color, zone

# ─────────────────────────────────────────────
# NAVBAR
# ─────────────────────────────────────────────
def render_navbar():
    c0, c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1, 1, 1, 1, 1, 1])
    with c0:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;height:56px;">
            <div style="width:36px;height:36px;background:linear-gradient(135deg,#00d4ff,#0066ff);
                        border-radius:8px;display:flex;align-items:center;justify-content:center;
                        font-size:13px;font-family:'JetBrains Mono',monospace;color:#fff;font-weight:700;">🛡️</div>
            <div>
                <span style="font-size:17px;font-weight:700;font-family:'JetBrains Mono',monospace;
                             background:linear-gradient(135deg,#00d4ff,#00e676);
                             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">CYBERINTEL</span>
                <span style="font-size:11px;color:#475569;margin-left:6px;">v3.1</span>
            </div>
        </div>""", unsafe_allow_html=True)

    pages = [("OVERVIEW", "Overview"), ("DOMAINES", "Domains"),
             ("ML ENGINE", "ML Engine"), ("RÉSEAU", "Network"),
             ("PIPELINE", "Pipeline")]
    cols  = [c1, c2, c3, c4, c5]
    for col, (label, page) in zip(cols, pages):
        with col:
            is_active = st.session_state.page == page
            st.button(label, key=f"nav_{page}", on_click=navigate_to, args=(page,),
                      use_container_width=True,
                      type="primary" if is_active else "secondary")

    with c6:
        if not scores.empty and "risk_level" in scores.columns:
            n_high = len(scores[scores["risk_level"] == "HIGH"])
        else:
            n_high = 0
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;height:56px;justify-content:flex-end;">
            <div style="width:8px;height:8px;background:#ff3b5c;border-radius:50%;animation:pulse 1.5s infinite;"></div>
            <span style="font-size:10px;font-weight:600;letter-spacing:2px;color:#ff3b5c;">{n_high} HIGH</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.2rem;'></div>", unsafe_allow_html=True)


render_navbar()

# ══════════════════════════════════════════════════════════════
# PAGE — OVERVIEW
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "Overview":

    if scores.empty or "suspicion_score" not in scores.columns:
        missing_banner("suspicion_scores.csv", "Unified_scoring.py")
        st.stop()

    # ── KPIs ──────────────────────────────────────────────────
    n_high   = len(scores[scores["risk_level"] == "HIGH"])
    n_medium = len(scores[scores["risk_level"] == "MEDIUM"])
    n_low    = len(scores[scores["risk_level"] == "LOW"])
    mean_score = scores["suspicion_score"].mean()

    n_preds_display = str(len(preds)) if not preds.empty else "—"

    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("Domaines HIGH risk",  str(n_high),           f"{n_high/len(scores)*100:.1f}% du total"),
        ("Score moyen",         f"{mean_score:.3f}",   "Seuil critique : 0.62"),
        ("Domaines analysés",   str(len(scores)),      f"Medium={n_medium} · Low={n_low}"),
        ("Pages prédites",      n_preds_display,       "Résultats des prédictions ML"),
    ]

    for col, (label, val, trend) in zip([c1, c2, c3, c4], kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-trend">{trend}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Layout principal (sans pie chart) ─────────────────────
    col_l = st.container()

    # Histogramme des scores
    fig_hist = px.histogram(
        scores, x="suspicion_score", color="risk_level",
        color_discrete_map=COLOR_MAP, nbins=40,
        labels={"suspicion_score": "Score de suspicion"},
    )

    fig_hist.add_vline(
        x=0.45, line_dash="dash", line_color="#f59e0b",
        annotation_text="Seuil MEDIUM", annotation_font_color="#f59e0b"
    )

    fig_hist.add_vline(
        x=0.62, line_dash="dash", line_color="#ff3b5c",
        annotation_text="Seuil HIGH", annotation_font_color="#ff3b5c"
    )

    fig_hist.update_layout(
        **BASE_LAYOUT,
        height=320,
        xaxis=dict(**GRID),
        yaxis=dict(**GRID),
        barmode="overlay",
        showlegend=True,
        legend=dict(font=dict(color="#64748b", size=10))
    )

    framed_chart(
        "Fréquence des scores de suspicion par niveau de risque — seuils LOW / MEDIUM / HIGH",
        fig_hist
    )

    # ── Top N domaines suspects ──────────────────────────────
    if not filtered_df.empty:
        top_d = filtered_df.head(top_n)

        fig_bar = px.bar(
            top_d,
            x="suspicion_score",
            y="domain",
            orientation="h",
            color="risk_level",
            color_discrete_map=COLOR_MAP,
            text="suspicion_score",
            labels={"suspicion_score": "Score", "domain": ""},
        )

        fig_bar.update_traces(
            texttemplate="%{text:.3f}",
            textposition="outside",
            marker_line_width=0
        )

        fig_bar.update_layout(
            **BASE_LAYOUT,
            height=max(400, top_n * 28),
            xaxis=dict(**GRID),
            hovermode="y unified"
        )

        framed_chart(
            f"Classement des {top_n} domaines les plus suspects selon le score de suspicion",
            fig_bar
        )

    else:
        st.info("Aucun domaine ne correspond aux filtres sélectionnés.")

# ══════════════════════════════════════════════════════════════
# PAGE — DOMAINS
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "Domains":

    st.markdown('<div class="section-title">Analyse détaillée des domaines</div>', unsafe_allow_html=True)

    if filtered_df.empty:
        missing_banner("suspicion_scores.csv", "Unified_scoring.py")
        st.stop()

    max_score  = float(filtered_df["suspicion_score"].max())
    mean_score = float(filtered_df["suspicion_score"].mean())
    med_score  = float(filtered_df["suspicion_score"].median())
    high_pct   = (len(filtered_df[filtered_df["risk_level"] == "HIGH"]) / len(filtered_df) * 100
                  if len(filtered_df) > 0 else 0)

    col_gauge, col_kpi1, col_kpi2 = st.columns(3)

    with col_gauge:
        gauge_fig, g_color, g_zone = make_gauge(max_score)
        with st.container(border=True):
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;
                        letter-spacing:1.5px;text-transform:uppercase;color:#64748b;
                        display:flex;align-items:center;gap:10px;padding:0.1rem 0 0 0;">
                SCORE MAX FILTRÉ
                <span style="background:rgba(255,255,255,0.05);border:1px solid {g_color}55;
                             color:{g_color};padding:2px 10px;border-radius:20px;font-size:10px;letter-spacing:2px;">
                    {g_zone}
                </span>
            </div>""", unsafe_allow_html=True)
            st.plotly_chart(gauge_fig, use_container_width=True)
            st.markdown("""
            <div style="display:flex;justify-content:center;gap:1rem;padding-bottom:0.35rem;
                        font-family:'JetBrains Mono',monospace;font-size:10px;">
                <div><span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                                  background:#00e676;margin-right:4px;"></span><span style="color:#64748b;">LOW &lt;0.45</span></div>
                <div><span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                                  background:#f59e0b;margin-right:4px;"></span><span style="color:#64748b;">MED 0.45-0.62</span></div>
                <div><span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                                  background:#ff3b5c;margin-right:4px;"></span><span style="color:#64748b;">HIGH &gt;0.62</span></div>
            </div>""", unsafe_allow_html=True)

   
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Décomposition des contributions au score ──────────────
    contrib_cols = [c for c in ["ml_contrib", "stance_contrib",
                                "contradiction_contrib", "community_contrib"]
                    if c in filtered_df.columns]
    if contrib_cols:
        st.markdown('<div class="section-title">Décomposition des contributions au score de suspicion</div>',
                    unsafe_allow_html=True)
        top20 = filtered_df.head(20).copy()
        fig_stack = go.Figure()
        contrib_colors = {
            "ml_contrib": "#00d4ff",
            "stance_contrib": "#f59e0b",
            "contradiction_contrib": "#ff3b5c",
            "community_contrib": "#00e676",
        }
        contrib_labels = {
            "ml_contrib": "ML fake proba (×0.55)",
            "stance_contrib": "Stance (×0.15)",
            "contradiction_contrib": "Contradiction (×0.15)",
            "community_contrib": "Isolement communauté (×0.15)",
        }
        for col in contrib_cols:
            fig_stack.add_trace(go.Bar(
                x=top20["domain"], y=top20[col],
                name=contrib_labels.get(col, col),
                marker_color=contrib_colors.get(col, "#888"),
                marker_line_width=0,
            ))
        fig_stack.update_layout(**BASE_LAYOUT, barmode="stack", height=380,
                                xaxis=dict(**GRID, tickangle=-35),
                                yaxis=dict(**GRID, title="Contribution"),
                                legend=dict(font=dict(color="#64748b", size=10)),
                                hovermode="x unified")
        framed_chart("Poids de chaque signal (ML, stance, contradiction, isolement) dans le score final — Top 20", fig_stack)

    # ── Tableau complet ───────────────────────────────────────
    st.markdown('<div class="section-title">Tableau des domaines filtrés</div>', unsafe_allow_html=True)

    display_cols = [c for c in ["domain", "suspicion_score", "risk_level",
                                "ml_fake_proba", "contradiction_rate",
                                "stance_score", "community_iso"]
                    if c in filtered_df.columns]

    def color_risk(val):
        return ("color:#ff3b5c;font-weight:600" if val == "HIGH"
                else "color:#f59e0b" if val == "MEDIUM" else "color:#00e676")

    numeric_cols = [c for c in display_cols if c not in ["domain", "risk_level"]]
    styled = (filtered_df[display_cols].head(200)
              .style
              .map(color_risk, subset=["risk_level"])
              .format({c: "{:.4f}" for c in numeric_cols}))

    framed_dataframe(f"Détail des scores et indicateurs par domaine — {len(filtered_df)} domaines filtrés", styled, height=450)

    col_b1, col_b2, _ = st.columns([1, 1, 4])
    with col_b1:
        st.download_button("⬇ Exporter CSV",
            data=filtered_df.to_csv(index=False).encode(),
            file_name=f"cyberintel_suspicion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv")
    with col_b2:
        st.download_button("⬇ Exporter JSON",
            data=filtered_df.to_json(orient="records", indent=2).encode(),
            file_name=f"cyberintel_suspicion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json")

# ══════════════════════════════════════════════════════════════
# PAGE — ML ENGINE
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "ML Engine":

    st.markdown('<div class="section-title">Moteur de détection Machine Learning</div>', unsafe_allow_html=True)

    # ── Guard : comparaison_modeles.csv obligatoire ───────────
    if comparaison.empty:
        missing_banner("comparaison_modeles.csv", "pipeline_FINAL_v5.ipynb")
        st.stop()

    # ── KPIs — uniquement depuis le CSV ──────────────────────
    # Meilleur modèle = celui avec le F1-macro le plus élevé
    if "F1-macro" in comparaison.columns:
        best_model = comparaison["F1-macro"].astype(float).idxmax()
        best = comparaison.loc[best_model]
        acc_best = float(best["Accuracy"]) if "Accuracy" in best.index else None
        f1_macro = float(best["F1-macro"])
        auc_best = float(best["ROC-AUC"]) if "ROC-AUC" in best.index else None
        f1_fake  = float(best["F1-fake"])  if "F1-fake"  in best.index else None
    else:
        st.error("comparaison_modeles.csv ne contient pas la colonne F1-macro.")
        st.stop()

    # Prédictions fake/real depuis le CSV
    n_fake  = len(preds[preds["predicted_label"] == "fake"]) if not preds.empty and "predicted_label" in preds.columns else None
    n_total = len(preds) if not preds.empty else None

    c1, c2, c3, c4 = st.columns(4)
    kpi_vals = [
        (f"{best_model} Accuracy",  f"{acc_best:.4f}" if acc_best is not None else "—",  "Meilleur modèle (F1-macro)"),
        ("F1-macro",                f"{f1_macro:.4f}",                                    f"F1-fake = {f1_fake:.4f}" if f1_fake is not None else ""),
        ("ROC-AUC",                 f"{auc_best:.4f}" if auc_best is not None else "—",   "Test set"),
        ("Pages FAKE prédites",     str(n_fake) if n_fake is not None else "—",
                                    f"{n_fake/n_total*100:.1f}% du total" if n_fake is not None and n_total else "Données de prédictions absentes"),
    ]
    for col, (label, val, trend) in zip([c1, c2, c3, c4], kpi_vals):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-trend">{trend}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Comparaison des modèles ───────────────────────────────
    cl, cr = st.columns(2)

    with cl:
        fig_cmp = go.Figure()
        available_metrics = [m for m in ["Accuracy", "F1-fake", "F1-real", "F1-macro", "ROC-AUC"]
                             if m in comparaison.columns]
        colors = ["#00d4ff", "#f59e0b", "#00e676", "#ff3b5c", "#a78bfa"]
        for i, metric in enumerate(available_metrics):
            fig_cmp.add_trace(go.Bar(
                name=metric,
                x=comparaison.index.tolist(),
                y=comparaison[metric].astype(float).tolist(),
                marker_color=colors[i % len(colors)],
                marker_line_width=0,
            ))
        fig_cmp.update_layout(**BASE_LAYOUT, barmode="group", height=320,
                              xaxis=dict(**GRID), yaxis=dict(**GRID, range=[0.7, 1.02]),
                              legend=dict(font=dict(color="#64748b", size=10)),
                              hovermode="x unified")
        framed_chart("Performances comparées des modèles — Accuracy, F1 et ROC-AUC", fig_cmp)

    with cr:
        if not preds.empty and "prediction_confidence" in preds.columns and "predicted_label" in preds.columns:
            fig_conf = px.histogram(
                preds, x="prediction_confidence",
                color="predicted_label",
                color_discrete_map={"fake": "#ff3b5c", "real": "#00e676"},
                nbins=30, labels={"prediction_confidence": "Confiance ML"},
            )
            fig_conf.add_vline(x=0.70, line_dash="dash", line_color="#00d4ff",
                               annotation_text="Seuil semi-supervisé 0.70")
            fig_conf.update_layout(**BASE_LAYOUT, barmode="overlay", height=320,
                                   xaxis=dict(**GRID), yaxis=dict(**GRID))
            framed_chart("Répartition des niveaux de confiance du modèle par classe prédite", fig_conf)
        else:
            if preds.empty:
                missing_banner("predictions_finales.csv", "pipeline_FINAL_v5.ipynb")
            else:
                st.info("Colonne `prediction_confidence` ou `predicted_label` absente de predictions_finales.csv.")

    # ── Matrice de confusion — uniquement si labels réels disponibles ──
    if (not preds.empty
            and "label" in preds.columns
            and "predicted_label" in preds.columns):
        from sklearn.metrics import confusion_matrix
        valid_preds = preds.dropna(subset=["label", "predicted_label"])
        y_true = valid_preds["label"]
        y_pred = valid_preds["predicted_label"]
        valid  = y_true.isin(["fake", "real"]) & y_pred.isin(["fake", "real"])
        if valid.sum() >= 10:
            cm = confusion_matrix(y_true[valid], y_pred[valid], labels=["fake", "real"])
            fig_hm = go.Figure(go.Heatmap(
                z=cm, x=["Prédit: Real", "Prédit: Fake"],
                y=["Réel: Real", "Réel: Fake"],
                text=cm, texttemplate="%{text}",
                textfont={"size": 18, "color": "white"},
                colorscale=[[0, "#0d1117"], [0.5, "#1a2332"], [1, "#00d4ff"]],
                showscale=False,
            ))
            fig_hm.update_layout(**BASE_LAYOUT, height=280,
                                  xaxis_title="Prédiction", yaxis_title="Vérité terrain")
            framed_chart(f"Matrice de confusion — vrais positifs, faux positifs et erreurs de classification ({valid.sum()} pages labellisées)", fig_hm)
        else:
            st.info(f"Pas assez de labels communs pour la matrice de confusion ({valid.sum()} lignes valides).")
    else:
        st.info("Matrice de confusion indisponible : colonnes `label` et/ou `predicted_label` absentes de predictions_finales.csv.")

    # ── Tableau comparaison ───────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    def highlight_best_model(s):
        return ["background-color:rgba(0,230,118,0.15); color:#00e676; font-weight:600"
                if s.name == best_model else "" for _ in s]

    numeric_cmp_cols = comparaison.select_dtypes(include="number").columns.tolist()
    styled_cmp = (comparaison.style
                  .apply(highlight_best_model, axis=1)
                  .format({c: "{:.4f}" for c in numeric_cmp_cols}))
    framed_dataframe("Tableau récapitulatif des métriques pour chaque modèle testé", styled_cmp, height=220)



# ══════════════════════════════════════════════════════════════
# PAGE — RÉSEAU
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "Network":

    st.markdown('<div class="section-title">Graphe des relations entre domaines</div>', unsafe_allow_html=True)

    @st.cache_data
    def build_network(links_data, scores_df, max_nodes):
        G = nx.Graph()
        for lk in links_data:
            G.add_edge(lk["source"], lk["target"])
        if not scores_df.empty and "suspicion_score" in scores_df.columns:
            top_set = set(scores_df.sort_values("suspicion_score", ascending=False)
                          .head(max_nodes)["domain"].tolist())
            G = G.subgraph([n for n in G.nodes() if n in top_set]).copy()
        try:
            from networkx.algorithms.community import greedy_modularity_communities
            comms = list(greedy_modularity_communities(G)) if G.nodes() else []
        except Exception:
            comms = []
        cmap = {node: i for i, c in enumerate(comms) for node in c}
        return G, cmap, comms

    if not links:
        missing_banner("graph_links.json", "Unified_scoring.py")
    else:
        m1, m2, m3 = st.columns(3)
        G_prev, _, comms_prev = build_network(links, scores, 80)
        for col, (label, val, sub) in zip([m1, m2, m3], [
            ("Nœuds",       str(len(G_prev.nodes())), "Domaines suspects"),
            ("Liens",       str(len(G_prev.edges())), "Connexions détectées"),
            ("Communautés", str(len(comms_prev)),     "Clusters identifiés"),
        ]):
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{val}</div>
                    <div class="kpi-trend">{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        fc1, fc2, _ = st.columns([2, 2, 4])
        with fc1:
            max_nodes   = st.slider("Nombre de nœuds", 20, min(200, len(links)*2 or 200), 80, 10)
        with fc2:
            show_labels = st.checkbox("Afficher les labels", value=False)

        G, community_map, communities = build_network(links, scores, max_nodes)

        if G.nodes():
            pos = nx.spring_layout(G, seed=42, k=0.8)
            ex, ey = [], []
            for u, v in G.edges():
                x0, y0 = pos[u]; x1, y1 = pos[v]
                ex += [x0, x1, None]; ey += [y0, y1, None]

            edge_tr = go.Scatter(
                x=ex, y=ey, mode="lines",
                line=dict(width=0.8, color="rgba(0,212,255,0.2)"), hoverinfo="none",
            )

            nx_list, ny_list, nt_list, nc_list, ns_list = [], [], [], [], []
            for node in G.nodes():
                x, y = pos[node]; nx_list.append(x); ny_list.append(y)
                row  = scores[scores["domain"] == node] if not scores.empty else pd.DataFrame()
                sv   = float(row["suspicion_score"].values[0]) if len(row) else 0.3
                risk = row["risk_level"].values[0] if len(row) and "risk_level" in row.columns else "LOW"
                nt_list.append(f"<b>{node}</b><br>Score:{sv:.3f}<br>Risque:{risk}<br>Cluster:#{community_map.get(node, 0)+1}")
                nc_list.append(sv); ns_list.append(8 + sv * 20)

            node_tr = go.Scatter(
                x=nx_list, y=ny_list,
                mode="markers" + ("+text" if show_labels else ""),
                text=[n[:25] for n in G.nodes()] if show_labels else None,
                textposition="top center",
                hoverinfo="text", hovertext=nt_list,
                marker=dict(
                    size=ns_list, color=nc_list,
                    colorscale=[[0, "#00e676"], [0.5, "#f59e0b"], [1, "#ff3b5c"]],
                    showscale=True,
                    colorbar=dict(title="Score", tickfont=dict(size=10, color="#64748b"), thickness=12),
                    line=dict(width=1.5, color="#0a0e1a"),
                ),
            )
            fig_g = go.Figure(data=[edge_tr, node_tr])
            fig_g.update_layout(
                showlegend=False, hovermode="closest", height=580,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                **BASE_LAYOUT,
            )
            framed_chart("Carte des connexions entre domaines suspects — taille proportionnelle au score, couleur = niveau de risque", fig_g)

            if communities:
                comm_rows = []
                for i, comm in enumerate(communities[:15]):
                    mb  = list(comm)
                    if not scores.empty and "suspicion_score" in scores.columns:
                        avg  = scores[scores["domain"].isin(mb)]["suspicion_score"].mean()
                        high = len(scores[(scores["domain"].isin(mb)) & (scores["risk_level"] == "HIGH")])
                        avg_str = f"{avg:.3f}" if not np.isnan(avg) else "N/A"
                    else:
                        avg_str = "N/A"; high = "N/A"
                    comm_rows.append({
                        "Cluster":       f"#{i+1}",
                        "Membres":       len(mb),
                        "Score moyen":   avg_str,
                        "Menaces HIGH":  high,
                        "Domaines clés": ", ".join(sorted(mb)[:5]) + ("…" if len(mb) > 5 else ""),
                    })
                framed_dataframe("Groupes de domaines interconnectés — score moyen et concentration de menaces par cluster",
                                 pd.DataFrame(comm_rows), height=320)
        else:
            st.warning("Graphe vide après filtrage. Augmentez le nombre de nœuds.")

# ══════════════════════════════════════════════════════════════
# PAGE — PIPELINE
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "Pipeline":

    st.markdown('<div class="section-title">Vue d\'ensemble du pipeline complet</div>', unsafe_allow_html=True)

    # ── KPIs dataset ──────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    n_dash   = len(dashboard)    if not dashboard.empty    else 0
    n_preds  = len(preds)        if not preds.empty        else 0
    n_scores = len(scores)       if not scores.empty       else 0
    n_models = len(comparaison)  if not comparaison.empty  else 0

    for col, (label, val, trend) in zip([c1, c2, c3, c4], [
        ("Pages dashboard_data", str(n_dash)   if n_dash   > 0 else "—", "Données brutes du pipeline"),

        ("Domaines scorés",      str(n_scores) if n_scores > 0 else "—", "Scores de suspicion calculés"),
        ("Modèles comparés",     str(n_models) if n_models > 0 else "—", "Algorithmes évalués"),
    ]):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-trend">{trend}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Stylométrie depuis dashboard_data ────────────────────
    stylo_cols = ["avg_word_len", "vocab_richness", "text_length", "label"]
    if not dashboard.empty and all(c in dashboard.columns for c in stylo_cols):
        st.markdown('<div class="section-title">Stylométrie — fake vs real </div>',
                    unsafe_allow_html=True)
        stylo = (dashboard[dashboard["label"].isin(["fake", "real"])]
                 .groupby("label")[["avg_word_len", "vocab_richness", "text_length"]]
                 .mean().reset_index())
        if not stylo.empty:
            cl, cr = st.columns(2)
            with cl:
                fig_s = px.bar(
                    stylo.melt(id_vars="label", value_vars=["avg_word_len", "vocab_richness"]),
                    x="variable", y="value", color="label",
                    color_discrete_map={"fake": "#ff3b5c", "real": "#00e676"},
                    barmode="group",
                    labels={"variable": "Métrique", "value": "Valeur moyenne"})
                fig_s.update_layout(**BASE_LAYOUT, height=280, xaxis=dict(**GRID), yaxis=dict(**GRID))
                framed_chart("Longueur moyenne des mots et richesse du vocabulaire — fake vs real", fig_s)
            with cr:
                fig_tl = px.bar(
                    stylo, x="label", y="text_length",
                    color="label", color_discrete_map={"fake": "#ff3b5c", "real": "#00e676"},
                    labels={"text_length": "Longueur texte (mots)"},
                    text="text_length")
                fig_tl.update_traces(texttemplate="%{text:.0f}", textposition="outside")
                fig_tl.update_layout(**BASE_LAYOUT, height=280, xaxis=dict(**GRID), yaxis=dict(**GRID))
                framed_chart("Volume textuel moyen des articles — fake vs real", fig_tl)
    elif not dashboard.empty:
        st.info("Colonnes stylométriques non trouvées dans dashboard_data.csv : "
                + ", ".join([c for c in stylo_cols if c not in dashboard.columns]))
    else:
        missing_banner("dashboard_data.csv", "pipeline_FINAL_v5.ipynb")

 
# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#475569;font-size:11px;'>"
    "CYBERINTEL Threat Intelligence Platform v3.1"
    "</p>", unsafe_allow_html=True
)