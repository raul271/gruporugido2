import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import StringIO

# ── CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Lives Semanais — Grupo Rugido",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── TEMA CLEAN/BRANCO CUSTOMIZADO ──────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

/* Reset geral */
.stApp { background-color: #f4f6f8; font-family: 'DM Sans', sans-serif; }
header, [data-testid="stHeader"] { background-color: transparent !important; }
[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e5e7eb; }

/* Cards de KPI */
.kpi-card {
    background: #ffffff; border-radius: 12px; padding: 16px 14px;
    border: 1px solid #e5e7eb; position: relative; overflow: hidden; text-align: left;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.kpi-card .bar { position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.kpi-card .label { font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 600; }
.kpi-card .value { font-size: 24px; font-weight: 800; margin-bottom: 2px; color: #111827; }
.kpi-card .sub { font-size: 11px; color: #9ca3af; }

/* Marca (Estilo Referência) */
.brand { display: flex; align-items: center; gap: 8px; margin-bottom: -4px; }
.brand-text { font-size: 28px; font-weight: 800; color: #1e293b; letter-spacing: -0.5px; }
.brand-highlight { color: #e91e63; }
.main-title { font-size: 16px; font-weight: 600; color: #6b7280; margin: 0 0 16px 0; }
.sub-title { font-size: 13px; color: #4b5563; }

/* Live card */
.live-card { background: #ffffff; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden; margin-bottom: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.live-header { padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.live-body { padding: 16px; }

/* Grupo card */
.grupo-card { border-radius: 8px; padding: 10px 12px; }
.grupo-card.ativo { background: #ecfdf5; border: 1px solid #a7f3d0; }
.grupo-card.passivo { background: #f9fafb; border: 1px solid #e5e7eb; }

/* Week card */
.week-card {
    background: #ffffff; border-radius: 12px; border: 1px solid #e5e7eb;
    padding: 14px 18px; margin-bottom: 8px; cursor: pointer; transition: border-color 0.2s;
}
.week-card:hover { border-color: #e91e63 !important; }

/* Metric bar */
.metric-bar { background: #ffffff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 14px 20px; display: flex; gap: 28px; flex-wrap: wrap; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.metric-item .m-label { font-size: 10px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
.metric-item .m-value { font-size: 18px; font-weight: 800; color: #111827; }

/* Botões do tab */
div[data-testid="stHorizontalBlock"] button {
    background: #ffffff !important; color: #374151 !important;
    border: 1px solid #d1d5db !important; border-radius: 8px !important;
    font-weight: 700 !important; font-size: 13px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
div[data-testid="stHorizontalBlock"] button:hover {
    border-color: #e91e63 !important; color: #e91e63 !important; background: #fdf2f8 !important;
}

/* Esconder elementos padrão do Streamlit e Ajustar Padding do Topo */
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }
.block-container { padding-top: 4rem !important; max-width: 1000px !important; } /* AQUI CORRIGE O TÍTULO TAMPADO */

/* Plotly background fix */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────
MAX_GP = 8

def fmt(v):
    return f"{v:,.0f}".replace(",", ".")

def fmtR(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(v):
    return f"{v:.1f}%"

def kpi_html(label, value, color, sub=""):
    sub_html = f'<div class="sub">{sub}</div>' if sub else ''
    return f'''
    <div class="kpi-card">
        <div class="bar" style="background:{color}"></div>
        <div class="label">{label}</div>
        <div class="value" style="color:{color}">{value}</div>
        {sub_html}
    </div>'''

def safe_float(v):
    if v is None or v == "" or (isinstance(v, float) and pd.isna(v)):
        return 0.0
    s = str(v).strip()
    for ch in ["R$", "r$", "%", " ", "\xa0"]:
        s = s.replace(ch, "")
    s = s.strip()
    if not s:
        return 0.0
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

def parse_csv_from_url(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return pd.read_csv(StringIO(r.text))
    except:
        return None

def load_data(sheet_id):
    base = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

    # Semanal
    sem_df = parse_csv_from_url(f"{base}&sheet=Semanal")
    if sem_df is None:
        return None, None

    # Lives e Grupos (Correção da Semana 1)
    lives_url = f"{base}&sheet=Lives+e+Grupos"
    liv_df = parse_csv_from_url(lives_url)

    return sem_df, liv_df

def col_match(df_cols, target):
    target_lower = target.lower().strip()
    for c in df_cols:
        if c.lower().strip() == target_lower:
            return c
    for c in df_cols:
        cl = c.lower().strip()
        simple_t = target_lower.replace("í","i").replace("ã","a").replace("ç","c").replace("é","e").replace("ú","u")
        simple_c = cl.replace("í","i").replace("ã","a").replace("ç","c").replace("é","e").replace("ú","u")
        if simple_t == simple_c:
            return c
    return None

def get_val(row, names):
    if isinstance(names, str):
        names = [names]
    for name in names:
        if name in row.index:
            return row[name]
        matched = col_match(row.index.tolist(), name)
        if matched and matched in row.index:
            return row[matched]
    return 0

def process_semanal(df):
    records = []
    for _, row in df.iterrows():
        s = int(safe_float(get_val(row, "Semana")))
        if s <= 0:
            continue
        inv = safe_float(get_val(row, ["Investimento (R$)", "Investimento"]))
        la = safe_float(get_val(row, "Leads Ads"))
        le = safe_float(get_val(row, "Leads Entrada"))
        ls_ = safe_float(get_val(row, ["Leads Saida", "Leads Saída"]))
        vt = safe_float(get_val(row, "Vendas Total"))
        rec = safe_float(get_val(row, ["Receita (R$)", "Receita"]))
        records.append(dict(semana=s, investimento=inv, leadsAds=la, leadsEntrada=le, leadsSaida=ls_, vendas=vt, receita=rec))
    return records

def process_lives(df):
    lives = []
    if df is None:
        return lives
    for _, row in df.iterrows():
        semana = int(safe_float(row.get("Semana", 0)))
        tipo = str(row.get("Tipo", "")).strip().upper()
        label = str(row.get("Label", "")).strip()
        if not semana or not tipo or not label or tipo == "NAN":
            continue
        ga = str(row.get("Grupo Ativo", "")).strip().upper()
        grupos = []
        for g in range(1, MAX_GP + 1):
            leads = safe_float(row.get(f"Leads GP{g}", 0))
            cliques = safe_float(row.get(f"Cliques GP{g}", 0))
            ctr = safe_float(row.get(f"CTR GP{g}", 0))
            if leads > 0 or cliques > 0:
                grupos.append(dict(nome=f"GP{g}", leads=leads, cliques=cliques, ctr=ctr, ativo=f"GP{g}" == ga))
        lives.append(dict(
            semana=semana, tipo=tipo, label=label,
            data=str(row.get("Data", "")).strip(),
            cliquesTotal=safe_float(row.get("Cliques Total", 0)),
            pico=safe_float(row.get("Pico", 0)),
            vendas=safe_float(row.get("Vendas", 0)),
            grupos=grupos,
        ))
    return lives

def calc_stats(grupos):
    at = [g for g in grupos if g["ativo"]]
    pa = [g for g in grupos if not g["ativo"]]
    ac = sum(g["cliques"] for g in at)
    pc = sum(g["cliques"] for g in pa)
    al = sum(g["leads"] for g in at)
    pl = sum(g["leads"] for g in pa)
    return dict(
        ac=ac, pc=pc,
        aCTR=round((ac / al) * 100, 1) if al > 0 else 0,
        pCTR=round((pc / pl) * 100, 1) if pl > 0 else 0,
        ga=at[0]["nome"] if at else "-"
    )

# ── PLOTLY LAYOUT (Adaptado pro Tema Claro) ────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#6b7280", size=12),
    margin=dict(l=50, r=20, t=30, b=40),
    xaxis=dict(gridcolor="#f3f4f6", zerolinecolor="#f3f4f6"),
    yaxis=dict(gridcolor="#f3f4f6", zerolinecolor="#f3f4f6"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e5e7eb", font=dict(family="DM Sans", size=13, color="#111827")),
)

# ── SESSION STATE ──────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "overview"
if "sel_week" not in st.session_state:
    st.session_state.sel_week = None

# ── SIDEBAR: CONEXÃO ───────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Conectar Planilha")
    st.markdown("""
    1. Copie a planilha pro Google Sheets
    2. Compartilhe como "Qualquer pessoa com o link"
    3. Copie o ID da URL (entre `/d/` e `/edit`)
    4. Cole abaixo
    """)
    sheet_id = st.text_input("ID da Planilha", value=st.session_state.get("sheet_id", ""), placeholder="1AbCdEf...")
    col1, col2 = st.columns(2)
    with col1:
        connect = st.button("🔗 Conectar", use_container_width=True)
    with col2:
        refresh = st.button("🔄 Atualizar", use_container_width=True)

    if connect and sheet_id:
        st.session_state.sheet_id = sheet_id
    if refresh:
        st.cache_data.clear()

# ── LOAD DATA ──────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def fetch_all(sid):
    sem_df, liv_df = load_data(sid)
    if sem_df is None:
        return None, None
    return process_semanal(sem_df), process_lives(liv_df)

sid = st.session_state.get("sheet_id", "")
if sid:
    with st.spinner("Buscando dados da planilha..."):
        semanal, lives = fetch_all(sid)
    if semanal is None:
        st.error("Erro ao buscar. Verifique se a planilha está compartilhada como 'Qualquer pessoa com o link'.")
        st.stop()
    connected = True
else:
    # Default data
    semanal = [
        dict(semana=1, investimento=0, leadsAds=0, leadsEntrada=0, leadsSaida=0, vendas=0, receita=0),
        dict(semana=2, investimento=0, leadsAds=0, leadsEntrada=0, leadsSaida=0, vendas=0, receita=0),
        dict(semana=3, investimento=0, leadsAds=0, leadsEntrada=0, leadsSaida=0, vendas=0, receita=0),
        dict(semana=4, investimento=0, leadsAds=0, leadsEntrada=0, leadsSaida=0, vendas=0, receita=0),
    ]
    lives = [
        dict(semana=1, tipo="LVP", label="LVP", data="27/01", cliquesTotal=203, pico=261, vendas=0,
             grupos=[dict(nome="GP1", leads=274, cliques=203, ctr=74.09, ativo=True)]),
        dict(semana=2, tipo="LVP", label="LVP", data="03/02", cliquesTotal=648, pico=249, vendas=0,
             grupos=[dict(nome="GP1", leads=226, cliques=98, ctr=43.36, ativo=False),
                     dict(nome="GP2", leads=460, cliques=357, ctr=77.61, ativo=True)]),
        dict(semana=2, tipo="LVG", label="LVG", data="04/02", cliquesTotal=287, pico=187, vendas=0,
             grupos=[dict(nome="GP1", leads=218, cliques=37, ctr=16.97, ativo=False),
                     dict(nome="GP2", leads=617, cliques=154, ctr=24.96, ativo=True)]),
    ]
    connected = False

# ── COMPUTE ────────────────────────────────────────────
sem_map = {s["semana"]: s for s in semanal}
active_weeks = sorted(set(l["semana"] for l in lives))

weeks_data = []
for s in active_weeks:
    wl = [l for l in lives if l["semana"] == s]
    all_g = [g for l in wl for g in l["grupos"]]
    st_ = calc_stats(all_g)
    tc = sum(l["cliquesTotal"] for l in wl)
    tv = sum(l["vendas"] for l in wl)
    m = sem_map.get(s, {})
    inv = m.get("investimento", 0)
    la = m.get("leadsAds", 0)
    le = m.get("leadsEntrada", 0)
    ls_ = m.get("leadsSaida", 0)
    cpl = inv / la if la > 0 else 0
    txE = (le / la) * 100 if la > 0 else 0
    txS = (ls_ / le) * 100 if le > 0 else 0
    weeks_data.append(dict(
        sn=s, **st_, tc=tc, pico=max((l["pico"] for l in wl), default=0),
        inv=inv, la=la, le=le, ls=ls_, cpl=cpl, txE=round(txE, 1), txS=round(txS, 1),
        vt=tv + m.get("vendas", 0),
        lives_label=" + ".join(l["label"] for l in wl), evs=wl, m=m
    ))

# Overall KPIs
ti = sum(w["inv"] for w in weeks_data)
tla = sum(w["la"] for w in weeks_data)
tle = sum(w["le"] for w in weeks_data)
tls = sum(w["ls"] for w in weeks_data)
tv_all = sum(w["vt"] for w in weeks_data)

# ── HEADER ─────────────────────────────────────────────
st.markdown("""
<div class="brand">
    <span class="brand-text">Grupo <span class="brand-highlight">Rugido</span></span>
</div>
<div class="main-title">Dashboard Lives Semanais</div>
""", unsafe_allow_html=True)

status = "🟢 Conectado ao Google Sheets" if connected else "📋 Dados locais (preview) — conecte sua planilha na barra lateral"
st.markdown(f'<div class="sub-title">{status}</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── NAV ────────────────────────────────────────────────
nav_cols = st.columns(len(active_weeks) + 1)
with nav_cols[0]:
    if st.button("📊 Visão Geral", use_container_width=True):
        st.session_state.sel_week = None
        st.rerun()
for i, s in enumerate(active_weeks):
    with nav_cols[i + 1]:
        if st.button(f"S{s}", use_container_width=True):
            st.session_state.sel_week = s
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# VISÃO GERAL
# ══════════════════════════════════════════════════════
if st.session_state.sel_week is None:

    # KPIs
    cols = st.columns(6)
    kpis = [
        ("Investimento", fmtR(ti), "#ef4444", "Total tráfego"),
        ("Leads Ads", fmt(tla), "#3b82f6", "Captados"),
        ("CPL", fmtR(ti / tla) if tla > 0 else "–", "#f97316", ""),
        ("Taxa Entrada", pct((tle / tla) * 100) if tla > 0 else "–", "#22c55e", ""),
        ("Taxa Saída", pct((tls / tle) * 100) if tle > 0 else "–", "#f59e0b", ""),
        ("Vendas", fmt(tv_all), "#ec4899", "Ingressos"),
    ]
    for col, (l, v, c, s) in zip(cols, kpis):
        with col:
            st.markdown(kpi_html(l, v, c, s), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico 1: Cliques por Semana
    st.markdown('<h4 style="color:#111827;">Cliques por Semana</h4>', unsafe_allow_html=True)
    st.caption("Verde = ativo · Amarelo = passados")

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=[f"S{w['sn']}" for w in weeks_data],
        y=[w["ac"] for w in weeks_data],
        name="Cliques Ativo", marker_color="#22c55e",
    ))
    fig1.add_trace(go.Bar(
        x=[f"S{w['sn']}" for w in weeks_data],
        y=[w["pc"] for w in weeks_data],
        name="Cliques Passados", marker_color="#f59e0b",
    ))
    fig1.add_trace(go.Scatter(
        x=[f"S{w['sn']}" for w in weeks_data],
        y=[w["tc"] for w in weeks_data],
        name="Total", mode="lines+markers",
        line=dict(color="#111827", width=2, dash="dash"),
        marker=dict(color="#111827", size=6),
    ))
    fig1.update_layout(**PLOT_LAYOUT, barmode="stack", height=320)
    st.plotly_chart(fig1, use_container_width=True, config=dict(displayModeBar=False))

    # Gráfico 2: CTR Ativo vs Passados
    st.markdown('<h4 style="color:#111827;">CTR: Ativo vs Passados</h4>', unsafe_allow_html=True)
    st.caption("Comparativo semana a semana")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=[f"S{w['sn']}" for w in weeks_data],
        y=[w["aCTR"] for w in weeks_data],
        name="CTR Ativo", marker_color="#22c55e",
        text=[pct(w["aCTR"]) for w in weeks_data], textposition="outside",
        textfont=dict(color="#22c55e", size=11),
    ))
    fig2.add_trace(go.Bar(
        x=[f"S{w['sn']}" for w in weeks_data],
        y=[w["pCTR"] for w in weeks_data],
        name="CTR Passados", marker_color="#f59e0b",
        text=[pct(w["pCTR"]) if w["pCTR"] > 0 else "" for w in weeks_data], textposition="outside",
        textfont=dict(color="#f59e0b", size=11),
    ))
    fig2.update_layout(**PLOT_LAYOUT, barmode="group", height=300)
    fig2.update_yaxes(gridcolor="#f3f4f6", ticksuffix="%")
    st.plotly_chart(fig2, use_container_width=True, config=dict(displayModeBar=False))

    # Cards de semana
    st.markdown('<h4 style="color:#111827;">Semanas</h4>', unsafe_allow_html=True)
    for w in weeks_data:
        col1, col2 = st.columns([1, 12])
        with col1:
            st.markdown(f"""
            <div style="background:#fdf2f8;border-radius:8px;width:46px;height:46px;display:flex;align-items:center;justify-content:center;margin-top:4px">
                <span style="font-size:17px;font-weight:800;color:#e91e63">S{w['sn']}</span>
            </div>""", unsafe_allow_html=True)
        with col2:
            if st.button(
                f"**{w['lives_label']}** · {w['ga']} ativo · Invest: {fmtR(w['inv'])} · CPL: {fmtR(w['cpl']) if w['la'] > 0 else '–'} · Entrada: {pct(w['txE']) if w['la'] > 0 else '–'} · Saída: {pct(w['txS']) if w['le'] > 0 else '–'} · Vendas: {fmt(w['vt'])}",
                key=f"week_{w['sn']}", use_container_width=True
            ):
                st.session_state.sel_week = w["sn"]
                st.rerun()

# ══════════════════════════════════════════════════════
# DETALHE DA SEMANA
# ══════════════════════════════════════════════════════
else:
    sw = st.session_state.sel_week
    w = next((w for w in weeks_data if w["sn"] == sw), None)
    if w is None:
        st.error("Semana não encontrada")
        st.stop()

    if st.button("← Voltar pra Visão Geral"):
        st.session_state.sel_week = None
        st.rerun()

    st.markdown(f"<h2 style='color:#111827'>Semana {sw}</h2>", unsafe_allow_html=True)
    st.caption(f"{len(w['evs'])} live{'s' if len(w['evs']) > 1 else ''}")

    # KPIs linha 1
    cols = st.columns(4)
    m = w["m"] if isinstance(w["m"], dict) else {}
    kpis1 = [
        ("Investimento", fmtR(m.get("investimento", 0)), "#ef4444", ""),
        ("Leads Ads", fmt(m.get("leadsAds", 0)), "#3b82f6", "Captados"),
        ("CPL", fmtR(w["cpl"]) if w["la"] > 0 else "–", "#f97316", ""),
        ("Vendas Total", fmt(w["vt"]), "#ec4899", ""),
    ]
    for col, (l, v, c, s) in zip(cols, kpis1):
        with col:
            st.markdown(kpi_html(l, v, c, s), unsafe_allow_html=True)

    # KPIs linha 2
    cols = st.columns(4)
    kpis2 = [
        ("Leads Entrada", fmt(m.get("leadsEntrada", 0)), "#22c55e", "Entraram no grupo"),
        ("Leads Saída", fmt(m.get("leadsSaida", 0)), "#f59e0b", "Saíram do grupo"),
        ("Taxa Entrada", pct(w["txE"]) if w["la"] > 0 else "–", "#22c55e", ""),
        ("Taxa Saída", pct(w["txS"]) if w["le"] > 0 else "–", "#f59e0b", ""),
    ]
    for col, (l, v, c, s) in zip(cols, kpis2):
        with col:
            st.markdown(kpi_html(l, v, c, s), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Barra de resumo
    st.markdown(f"""
    <div class="metric-bar">
        <div class="metric-item"><div class="m-label">Total Cliques</div><div class="m-value">{fmt(w['tc'])}</div></div>
        <div class="metric-item"><div class="m-label">Pico</div><div class="m-value" style="color:#e91e63">{fmt(w['pico'])}</div></div>
        <div class="metric-item"><div class="m-label">CTR Ativo</div><div class="m-value" style="color:#22c55e">{pct(w['aCTR'])}</div></div>
        <div class="metric-item"><div class="m-label">CTR Passados</div><div class="m-value" style="color:#f59e0b">{pct(w['pCTR']) if w['pCTR'] > 0 else '–'}</div></div>
        <div class="metric-item"><div class="m-label">Grupo Ativo</div><div class="m-value" style="color:#e91e63">{w['ga']}</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h4 style="color:#111827;">Lives Individuais</h4>', unsafe_allow_html=True)

    # Live cards
    for ev in w["evs"]:
        tc = "#3b82f6" if ev["tipo"] == "LVP" else "#f59e0b"
        tl = "Prospecção" if ev["tipo"] == "LVP" else "Conteúdo"
        est = calc_stats(ev["grupos"])

        st.markdown(f"""
        <div class="live-card">
            <div class="live-header" style="background:{tc}10;border-bottom:1px solid {tc}20">
                <div style="display:flex;align-items:center;gap:8px">
                    <div style="width:8px;height:8px;border-radius:50%;background:{tc}"></div>
                    <span style="font-size:15px;font-weight:800;color:{tc}">{ev['label']}</span>
                    <span style="font-size:10px;color:{tc};background:{tc}18;padding:2px 8px;border-radius:6px;font-weight:600">{tl}</span>
                </div>
                <span style="font-size:12px;color:#6b7280">{ev['data']}</span>
            </div>
            <div class="live-body">
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px;text-align:center">
                    <div><div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600">Total Cliques</div><div style="font-size:18px;font-weight:800;color:#111827">{fmt(ev['cliquesTotal'])}</div></div>
                    <div><div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600">Pico</div><div style="font-size:18px;font-weight:800;color:#e91e63">{fmt(ev['pico'])}</div></div>
                    <div><div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600">CTR Ativo</div><div style="font-size:18px;font-weight:800;color:#22c55e">{pct(est['aCTR'])}</div></div>
                    <div><div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600">Vendas</div><div style="font-size:18px;font-weight:800;color:#ec4899">{fmt(ev['vendas'])}</div></div>
                </div>
        """, unsafe_allow_html=True)

        if ev["grupos"]:
            n_cols = min(len(ev["grupos"]), 5)
            grupos_html = f'<div style="font-size:11px;color:#4b5563;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-weight:700">Grupos</div>'
            grupos_html += f'<div style="display:grid;grid-template-columns:repeat({n_cols},1fr);gap:8px">'
            for g in ev["grupos"]:
                cls = "ativo" if g["ativo"] else "passivo"
                nc = "#22c55e" if g["ativo"] else "#4b5563"
                tag = '<span style="font-size:8px;color:#22c55e;background:#22c55e20;padding:1px 5px;border-radius:4px;font-weight:700;margin-left:6px">ATIVO</span>' if g["ativo"] else ""
                ctr_c = "#22c55e" if g["ativo"] else ("#f59e0b" if g["ctr"] > 20 else "#ef4444")
                grupos_html += f'''
                <div class="grupo-card {cls}">
                    <div style="display:flex;align-items:center;margin-bottom:6px">
                        <span style="font-size:12px;font-weight:700;color:{nc}">{g['nome']}</span>{tag}
                    </div>
                    <div style="font-size:11px;color:#6b7280;line-height:1.9">
                        <div>Leads: <strong style="color:#111827">{fmt(g['leads'])}</strong></div>
                        <div>Cliques: <strong style="color:#111827">{fmt(g['cliques'])}</strong></div>
                        <div>CTR: <strong style="color:{ctr_c}">{g['ctr']}%</strong></div>
                    </div>
                </div>'''
            grupos_html += "</div>"
            st.markdown(grupos_html, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center;font-size:11px;color:#9ca3af;border-top:1px solid #e5e7eb;padding-top:16px">Dashboard Lives Semanais · Grupo Rugido</div>', unsafe_allow_html=True)
