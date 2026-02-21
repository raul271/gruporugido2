import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import StringIO

# ── CONFIGURAÇÃO DA PÁGINA ──────────────────────────────
st.set_page_config(
    page_title="Dashboard Lives Semanais — Grupo Rugido",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS / ESTILO DO NOVO DESIGN ─────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --primary-color: #e91e63;
    --secondary-color: #3b82f6;
    --success-color: #22c55e;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --text-primary: #111827;
    --text-secondary: #6b7280;
    --bg-light: #f3f4f6;
    --bg-white: #ffffff;
    --border-color: #e5e7eb;
}

/* Reset geral */
.stApp { background-color: var(--bg-light); font-family: 'Inter', sans-serif; }
header, [data-testid="stHeader"] { background-color: transparent !important; }
[data-testid="stSidebar"] { background-color: var(--bg-white); border-right: 1px solid var(--border-color); }
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }
.block-container { padding-top: 3rem !important; max-width: 1100px !important; }

/* Tipografia */
h1, h2, h3, h4 { color: var(--text-primary); font-weight: 700; }
h2 { font-size: 1.75rem; margin-bottom: 0.5rem; }
h4 { font-size: 1.1rem; margin-bottom: 1rem; margin-top: 2rem; }
.stCaption { color: var(--text-secondary); font-size: 0.9rem; }

/* --- NOVOS CARDS DE KPI --- */
.kpi-card-new {
    background: var(--bg-white);
    border-radius: 12px;
    padding: 20px;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    display: flex;
    align-items: center;
    gap: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card-new:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.06);
    border-color: var(--primary-color);
}
.kpi-icon {
    width: 48px; height: 48px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}
.kpi-content { flex: 1; }
.kpi-label { font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 1.5rem; font-weight: 800; color: var(--text-primary); margin: 4px 0; }
.kpi-sub { font-size: 0.8rem; color: var(--text-secondary); }

/* Variantes de cor para os ícones */
.icon-blue { background-color: #dbeafe; color: var(--secondary-color); }
.icon-green { background-color: #d1fae5; color: var(--success-color); }
.icon-orange { background-color: #ffedd5; color: var(--warning-color); }
.icon-red { background-color: #fee2e2; color: var(--danger-color); }
.icon-pink { background-color: #fce7f3; color: var(--primary-color); }

/* --- BARRA DE MÉTTRICAS DA SEMANA --- */
.metric-bar-new {
    background: var(--bg-white);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    padding: 16px 24px;
    display: flex;
    justify-content: space-around;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    margin-bottom: 24px;
}
.mb-item { text-align: center; }
.mb-label { font-size: 0.75rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
.mb-value { font-size: 1.25rem; font-weight: 800; color: var(--text-primary); }

/* --- ESTILO PARA O ACORDEÃO DAS LIVES --- */
.streamlit-expanderHeader {
    background-color: var(--bg-white);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 12px 16px;
    font-weight: 600;
    color: var(--text-primary);
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    transition: all 0.2s;
}
.streamlit-expanderHeader:hover {
    border-color: var(--primary-color);
    background-color: #fdf2f8; /* Rosa bem clarinho */
}
.streamlit-expanderContent {
    background-color: var(--bg-white);
    border: 1px solid var(--border-color);
    border-top: none;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
.live-summary-metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
    text-align: center;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
}

/* --- NOVA TABELA DE GRUPOS --- */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 0.9rem;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border-color);
}
.styled-table thead tr {
    background-color: #f9fafb;
    color: var(--text-secondary);
    text-align: left;
    font-weight: 600;
}
.styled-table th, .styled-table td {
    padding: 12px 16px;
}
.styled-table tbody tr {
    border-bottom: 1px solid var(--border-color);
    transition: background-color 0.1s;
}
.styled-table tbody tr:last-of-type {
    border-bottom: none;
}
.styled-table tbody tr:hover {
    background-color: #f3f4f6;
}
/* Destaque para o grupo ativo na tabela */
.active-group-row {
    background-color: #ecfdf5 !important; /* Verde clarinho */
}
.active-group-row td:first-child {
    font-weight: 700;
    color: var(--success-color);
    position: relative;
}
.active-group-row td:first-child::before {
    content: '●';
    color: var(--success-color);
    position: absolute;
    left: 4px;
    font-size: 0.8rem;
}
.ctr-badge {
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.85rem;
}
.ctr-high { background-color: #d1fae5; color: var(--success-color); }
.ctr-med { background-color: #ffedd5; color: var(--warning-color); }
.ctr-low { background-color: #fee2e2; color: var(--danger-color); }

/* --- BOTÕES DE NAVEGAÇÃO --- */
button[kind="secondary"] {
    background: var(--bg-white) !important; color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 13px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    transition: all 0.2s;
}
button[kind="secondary"]:hover {
    border-color: var(--primary-color) !important; color: var(--primary-color) !important; background: #fdf2f8 !important;
}
button[kind="primary"] {
    background: #fdf2f8 !important;
    color: var(--primary-color) !important;
    border: 1px solid var(--primary-color) !important;
    border-radius: 8px !important;
    font-weight: 700 !important; font-size: 13px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

/* --- HEADER DA PÁGINA --- */
.brand { display: flex; align-items: center; gap: 10px; margin-bottom: 0px; }
.brand-text { font-size: 24px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.5px; }
.brand-highlight { color: var(--primary-color); }
.main-title { font-size: 14px; font-weight: 500; color: var(--text-secondary); margin: 0 0 24px 0; }
.sub-title { font-size: 12px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px;}

/* Plotly fixes */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── FUNÇÕES AUXILIARES (HELPERS) ────────────────────────
MAX_GP = 8

def fmt(v): return f"{v:,.0f}".replace(",", ".")
def fmtR(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def pct(v): return f"{v:.1f}%"

# --- NOVA FUNÇÃO PARA OS CARDS DE KPI COM ÍCONES ---
def kpi_new_html(label, value, icon_class, icon_name, sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ''
    return f'''
    <div class="kpi-card-new">
        <div class="kpi-icon {icon_class}">
            <i class="{icon_name}"></i>
        </div>
        <div class="kpi-content">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {sub_html}
        </div>
    </div>'''

# --- NOVA FUNÇÃO PARA GERAR A TABELA DE GRUPOS ---
def generate_groups_table(grupos):
    if not grupos: return "Sem dados de grupos."
    
    html = """
    <table class="styled-table">
        <thead>
            <tr>
                <th>Grupo</th>
                <th>Leads</th>
                <th>Cliques</th>
                <th>CTR</th>
            </tr>
        </thead>
        <tbody>
    """
    for g in grupos:
        row_class = "active-group-row" if g["ativo"] else ""
        ctr_val = g["ctr"]
        ctr_class = "ctr-high" if ctr_val >= 40 else ("ctr-med" if ctr_val >= 20 else "ctr-low")
        
        html += f"""
            <tr class="{row_class}">
                <td>{g['nome']}</td>
                <td>{fmt(g['leads'])}</td>
                <td>{fmt(g['cliques'])}</td>
                <td><span class="ctr-badge {ctr_class}">{pct(ctr_val)}</span></td>
            </tr>
        """
    html += "</tbody></table>"
    return html

def safe_float(v):
    if v is None or v == "" or (isinstance(v, float) and pd.isna(v)): return 0.0
    s = str(v).strip()
    for ch in ["R$", "r$", "%", " ", "\xa0"]: s = s.replace(ch, "")
    s = s.strip()
    if not s: return 0.0
    if "," in s: s = s.replace(".", "").replace(",", ".")
    try: return float(s)
    except: return 0.0

def parse_csv_from_url(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return pd.read_csv(StringIO(r.text))
    except: return None

def load_data(sheet_id):
    base = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    sem_df = parse_csv_from_url(f"{base}&sheet=Semanal")
    if sem_df is None: return None, None
    liv_df = parse_csv_from_url(f"{base}&sheet=Lives+e+Grupos")
    return sem_df, liv_df

def col_match(df_cols, target):
    target_lower = target.lower().strip()
    for c in df_cols:
        if c.lower().strip() == target_lower: return c
    for c in df_cols:
        cl = c.lower().strip()
        simple_t = target_lower.replace("í","i").replace("ã","a").replace("ç","c").replace("é","e").replace("ú","u")
        simple_c = cl.replace("í","i").replace("ã","a").replace("ç","c").replace("é","e").replace("ú","u")
        if simple_t == simple_c: return c
    return None

def get_val(row, names):
    if isinstance(names, str): names = [names]
    for name in names:
        if name in row.index: return row[name]
        matched = col_match(row.index.tolist(), name)
        if matched and matched in row.index: return row[matched]
    return 0

def get_group_val(row, metric_type, g):
    keys = ["lead", "lid"] if metric_type == "leads" else ["clique", "clic", "click"]
    for col in row.index:
        c_lower = str(col).lower().replace(" ", "").replace("í", "i").replace("é", "e")
        if any(k in c_lower for k in keys) and str(g) in c_lower:
            if "gp" in c_lower or "grup" in c_lower: return row[col]
    return 0

def process_semanal(df):
    records = []
    for _, row in df.iterrows():
        s = int(safe_float(get_val(row, "Semana")))
        if s <= 0: continue
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
    if df is None: return lives
    for _, row in df.iterrows():
        semana = int(safe_float(get_val(row, "Semana")))
        tipo = str(get_val(row, "Tipo")).strip().upper()
        label = str(get_val(row, "Label")).strip()
        if not semana or not tipo or not label or tipo == "NAN": continue
        ga = str(get_val(row, "Grupo Ativo")).strip().upper()
        grupos = []
        for g in range(1, MAX_GP + 1):
            leads = safe_float(get_group_val(row, "leads", g))
            cliques = safe_float(get_group_val(row, "cliques", g))
            ctr = round((cliques / leads) * 100, 1) if leads > 0 else 0.0
            if leads > 0 or cliques > 0:
                grupos.append(dict(nome=f"GP{g}", leads=leads, cliques=cliques, ctr=ctr, ativo=f"GP{g}" == ga))
        lives.append(dict(
            semana=semana, tipo=tipo, label=label,
            data=str(get_val(row, "Data")).strip(),
            cliquesTotal=safe_float(get_val(row, ["Cliques Total", "Cliques"])),
            pico=safe_float(get_val(row, "Pico")),
            vendas=safe_float(get_val(row, ["Vendas", "Vendas Total"])),
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

# ── PLOTLY LAYOUT ───────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#6b7280", size=12),
    margin=dict(l=50, r=20, t=30, b=40),
    xaxis=dict(gridcolor="#f3f4f6", zerolinecolor="#f3f4f6"),
    yaxis=dict(gridcolor="#f3f4f6", zerolinecolor="#f3f4f6"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e5e7eb", font=dict(family="Inter", size=13, color="#111827")),
)

# ── GERENCIAMENTO DE ESTADO (SESSION STATE) ─────────────
if "page" not in st.session_state: st.session_state.page = "overview"
if "sel_week" not in st.session_state: st.session_state.sel_week = None

# ── BARRA LATERAL (SIDEBAR) ─────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    st.markdown("Conecte sua planilha do Google Sheets para atualizar os dados.")
    sheet_id = st.text_input("ID da Planilha", value=st.session_state.get("sheet_id", ""), placeholder="Ex: 1AbCdEf...")
    col1, col2 = st.columns(2)
    with col1: connect = st.button("🔗 Conectar", use_container_width=True)
    with col2: refresh = st.button("🔄 Atualizar Dados", use_container_width=True)

    if connect and sheet_id: st.session_state.sheet_id = sheet_id
    if refresh: st.cache_data.clear()

    st.markdown("---")
    st.caption("Dashboard v2.0 - Design Clean")

# ── CARREGAMENTO DE DADOS ───────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def fetch_all(sid):
    sem_df, liv_df = load_data(sid)
    if sem_df is None: return None, None
    return process_semanal(sem_df), process_lives(liv_df)

sid = st.session_state.get("sheet_id", "")
if sid:
    with st.spinner("Carregando dados..."):
        semanal, lives = fetch_all(sid)
    if semanal is None:
        st.error("Não foi possível ler a planilha. Verifique o ID e as permissões.")
        st.stop()
    connected = True
else:
    # Dados de exemplo para preview
    semanal = [dict(semana=1, investimento=0, leadsAds=0, leadsEntrada=0, leadsSaida=0, vendas=0, receita=0)]
    lives = [dict(semana=1, tipo="LVP", label="Exemplo LVP", data="01/01", cliquesTotal=100, pico=50, vendas=0, grupos=[dict(nome="GP1", leads=150, cliques=100, ctr=66.7, ativo=True)])]
    connected = False

# ── CÁLCULOS GERAIS ─────────────────────────────────────
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

ti = sum(w["inv"] for w in weeks_data)
tla = sum(w["la"] for w in weeks_data)
tle = sum(w["le"] for w in weeks_data)
tls = sum(w["ls"] for w in weeks_data)
tv_all = sum(w["vt"] for w in weeks_data)

# ── CABEÇALHO PRINCIPAL ─────────────────────────────────
st.markdown("""
<div class="brand">
    <span class="brand-text">Grupo <span class="brand-highlight">Rugido</span></span>
</div>
<div class="main-title">Dashboard de Performance de Lives</div>
""", unsafe_allow_html=True)

status_icon = "🟢" if connected else "🟠"
status_text = "Planilha Conectada" if connected else "Modo Preview (Conecte a planilha na barra lateral)"
st.markdown(f'<div class="sub-title">{status_icon} {status_text}</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── NAVEGAÇÃO (Abas) ────────────────────────────────────
nav_cols = st.columns(len(active_weeks) + 1)

with nav_cols[0]:
    btn_type = "primary" if st.session_state.sel_week is None else "secondary"
    if st.button("📊 Visão Geral", use_container_width=True, type=btn_type):
        st.session_state.sel_week = None
        st.rerun()

for i, s in enumerate(active_weeks):
    with nav_cols[i + 1]:
        btn_type = "primary" if st.session_state.sel_week == s else "secondary"
        if st.button(f"S{s}", use_container_width=True, type=btn_type):
            st.session_state.sel_week = s
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TELA: VISÃO GERAL
# ════════════════════════════════════════════════════════
if st.session_state.sel_week is None:
    # --- KPIs GERAIS (Novo Design com Ícones) ---
    cols = st.columns(4)
    kpis_overview = [
        ("Investimento Total", fmtR(ti), "icon-red", "fa-solid fa-money-bill-wave"),
        ("Total Leads Ads", fmt(tla), "icon-blue", "fa-solid fa-bullseye"),
        ("CPL Médio", fmtR(ti / tla) if tla > 0 else "–", "icon-orange", "fa-solid fa-coins"),
        ("Total Vendas", fmt(tv_all), "icon-pink", "fa-solid fa-ticket-alt"),
    ]
    for col, (label, value, icon_cls, icon_name) in zip(cols, kpis_overview):
        with col: st.markdown(kpi_new_html(label, value, icon_cls, icon_name), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS ---
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown('<h4>Cliques por Semana</h4>', unsafe_allow_html=True)
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=[f"S{w['sn']}" for w in weeks_data], y=[w["ac"] for w in weeks_data], name="Ativo", marker_color="#22c55e"))
        fig1.add_trace(go.Bar(x=[f"S{w['sn']}" for w in weeks_data], y=[w["pc"] for w in weeks_data], name="Passados", marker_color="#f59e0b"))
        fig1.update_layout(**PLOT_LAYOUT, barmode="stack", height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig1, use_container_width=True, config=dict(displayModeBar=False))
    
    with col_g2:
        st.markdown('<h4>CTR Médio: Ativo vs Passados</h4>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=[f"S{w['sn']}" for w in weeks_data], y=[w["aCTR"] for w in weeks_data], name="CTR Ativo", marker_color="#22c55e", text=[pct(w["aCTR"]) for w in weeks_data], textposition="auto"))
        fig2.add_trace(go.Bar(x=[f"S{w['sn']}" for w in weeks_data], y=[w["pCTR"] for w in weeks_data], name="CTR Passados", marker_color="#f59e0b", text=[pct(w["pCTR"]) if w["pCTR"] > 0 else "" for w in weeks_data], textposition="auto"))
        fig2.update_layout(**PLOT_LAYOUT, barmode="group", height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig2.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig2, use_container_width=True, config=dict(displayModeBar=False))

    # --- LISTA DE SEMANAS (Design Mais Limpo) ---
    st.markdown('<h4>Resumo das Semanas</h4>', unsafe_allow_html=True)
    for w in weeks_data:
        c1, c2 = st.columns([1, 10])
        with c1:
            st.markdown(f'<div style="background:#fdf2f8;border-radius:10px;height:50px;display:flex;align-items:center;justify-content:center;border:1px solid #fce7f3"><span style="font-size:18px;font-weight:700;color:#e91e63">S{w["sn"]}</span></div>', unsafe_allow_html=True)
        with c2:
            # Usando um botão com estilo secundário para parecer um item de lista clicável
            label = f"Lives: {w['lives_label']} | Invest: {fmtR(w['inv'])} | Vendas: {fmt(w['vt'])}"
            if st.button(label, key=f"week_list_{w['sn']}", use_container_width=True, type="secondary"):
                st.session_state.sel_week = w["sn"]
                st.rerun()

# ════════════════════════════════════════════════════════
# TELA: DETALHE DA SEMANA
# ════════════════════════════════════════════════════════
else:
    sw = st.session_state.sel_week
    w = next((w for w in weeks_data if w["sn"] == sw), None)
    if w is None: st.error("Semana não encontrada"); st.stop()

    if st.button("← Voltar", type="secondary"):
        st.session_state.sel_week = None
        st.rerun()

    st.markdown(f"<h2>Semana {sw} <span style='font-weight:400; font-size:1.2rem; color:#6b7280'>({len(w['evs'])} lives)</span></h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- KPIs DA SEMANA (Novo Design) ---
    m = w["m"] if isinstance(w["m"], dict) else {}
    cols1 = st.columns(4)
    kpis_s1 = [
        ("Investimento", fmtR(m.get("investimento", 0)), "icon-red", "fa-solid fa-money-bill-wave"),
        ("Leads Ads", fmt(m.get("leadsAds", 0)), "icon-blue", "fa-solid fa-bullseye", "Captados"),
        ("CPL", fmtR(w["cpl"]) if w["la"] > 0 else "–", "icon-orange", "fa-solid fa-coins"),
        ("Vendas", fmt(w["vt"]), "icon-pink", "fa-solid fa-ticket-alt"),
    ]
    for col, (l, v, ic, iname, sub) in zip(cols1, kpis_s1):
        with col: st.markdown(kpi_new_html(l, v, ic, iname, sub), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    cols2 = st.columns(4)
    kpis_s2 = [
        ("Leads Entrada", fmt(m.get("leadsEntrada", 0)), "icon-green", "fa-solid fa-user-plus"),
        ("Leads Saída", fmt(m.get("leadsSaida", 0)), "icon-orange", "fa-solid fa-user-minus"),
        ("Taxa Entrada", pct(w["txE"]) if w["la"] > 0 else "–", "icon-green", "fa-solid fa-percentage"),
        ("Taxa Saída", pct(w["txS"]) if w["le"] > 0 else "–", "icon-orange", "fa-solid fa-arrow-right-from-bracket"),
    ]
    for col, (l, v, ic, iname) in zip(cols2, kpis_s2):
        with col: st.markdown(kpi_new_html(l, v, ic, iname), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BARRA DE MÉTTRICAS AGREGADAS (Novo Design) ---
    st.markdown(f"""
    <div class="metric-bar-new">
        <div class="mb-item"><div class="mb-label">Total Cliques</div><div class="mb-value">{fmt(w["tc"])}</div></div>
        <div class="mb-item"><div class="mb-label">Pico Máximo</div><div class="mb-value" style="color:var(--primary-color)">{fmt(w["pico"])}</div></div>
        <div class="mb-item"><div class="mb-label">CTR Ativo Médio</div><div class="mb-value" style="color:var(--success-color)">{pct(w["aCTR"])}</div></div>
        <div class="mb-item"><div class="mb-label">CTR Passados Médio</div><div class="mb-value" style="color:var(--warning-color)">{pct(w["pCTR"]) if w["pCTR"] > 0 else "–"}</div></div>
        <div class="mb-item"><div class="mb-label">Grupo Ativo</div><div class="mb-value" style="color:var(--primary-color)">{w["ga"]}</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4>Detalhamento das Lives</h4>", unsafe_allow_html=True)

    # --- LIVES INDIVIDUAIS (DESIGN DE ACORDEÃO + TABELA) ---
    for i, ev in enumerate(w["evs"]):
        # Cabeçalho do Acordeão
        tipo_badge_color = "#3b82f6" if ev["tipo"] == "LVP" else "#f59e0b"
        expander_title = f"{ev['label']}  |  {ev['data']}  |  Vendas: {fmt(ev['vendas'])}"
        
        with st.expander(expander_title, expanded=(i==0)): # A primeira live já vem aberta
            # Resumo da Live dentro do acordeão
            st.markdown(f"""
            <div class="live-summary-metrics">
                <div><div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;font-weight:600">Tipo</div><div style="font-weight:700;color:{tipo_badge_color}">{ev["tipo"]}</div></div>
                <div><div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;font-weight:600">Total Cliques</div><div style="font-weight:700">{fmt(ev["cliquesTotal"])}</div></div>
                <div><div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;font-weight:600">Pico</div><div style="font-weight:700;color:var(--primary-color)">{fmt(ev["pico"])}</div></div>
                <div><div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;font-weight:600">Vendas</div><div style="font-weight:700;color:var(--primary-color)">{fmt(ev["vendas"])}</div></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Tabela de Grupos
            st.markdown('**Performance por Grupo:**')
            st.markdown(generate_groups_table(ev["grupos"]), unsafe_allow_html=True)

# ── RODAPÉ ──────────────────────────────────────────────
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center;font-size:12px;color:#9ca3af;border-top:1px solid #e5e7eb;padding-top:24px">© 2024 Grupo Rugido · Dashboard de Performance</div>', unsafe_allow_html=True)
