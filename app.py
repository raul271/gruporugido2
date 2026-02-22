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

# ── CSS / ESTILO ULTRA-COMPACTO E ALINHADO ──────────────
st.markdown("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --primary-color: #e91e63;
    --secondary-color: #3b82f6;
    --success-color: #22c55e;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --purple-color: #8b5cf6;
    --indigo-color: #4f46e5;
    --text-primary: #111827;
    --text-secondary: #6b7280;
    --bg-light: #f8fafc; 
    --bg-white: #ffffff;
    --border-color: #e2e8f0;
}

.stApp { background-color: var(--bg-light); font-family: 'Inter', sans-serif; }
header, [data-testid="stHeader"] { background-color: transparent !important; }
[data-testid="stSidebar"] { background-color: var(--bg-white); border-right: 1px solid var(--border-color); }
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 1250px !important; }
[data-testid="collapsedControl"] { display: none !important; }

h1, h2, h3, h4 { color: var(--text-primary); font-weight: 700; line-height: 1.2; margin: 0; }
h4 { font-size: 1rem; margin-bottom: 0.8rem; margin-top: 1.5rem; }
.stCaption { color: var(--text-secondary); font-size: 0.85rem; }

/* --- NOVOS CARDS DE KPI HORIZONTAIS --- */
.kpi-card-new {
    background: var(--bg-white);
    border-radius: 8px;
    padding: 8px 12px;
    border: 1px solid var(--border-color);
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    display: flex;
    align-items: center; 
    gap: 10px;
    height: 60px; 
}
.kpi-icon {
    width: 32px; height: 32px;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    flex-shrink: 0; 
}
.kpi-content { flex: 1; display: flex; flex-direction: column; justify-content: center; overflow: hidden; }
.kpi-label { font-size: 0.55rem; color: var(--text-secondary); font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; }
.kpi-value { font-size: 1.1rem; font-weight: 800; color: var(--text-primary); line-height: 1; white-space: nowrap; }

.icon-blue { background-color: #e0f2fe; color: var(--secondary-color); }
.icon-green { background-color: #dcfce7; color: var(--success-color); }
.icon-orange { background-color: #ffedd5; color: var(--warning-color); }
.icon-red { background-color: #fee2e2; color: var(--danger-color); }
.icon-pink { background-color: #fce7f3; color: var(--primary-color); }
.icon-purple { background-color: #ede9fe; color: var(--purple-color); }
.icon-indigo { background-color: #e0e7ff; color: var(--indigo-color); }

/* --- BARRA DE MÉTTRICAS DA SEMANA --- */
.metric-bar-new {
    background: var(--bg-white); border-radius: 8px; border: 1px solid var(--border-color);
    padding: 12px 16px; display: flex; justify-content: space-around; align-items: center;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02); margin-bottom: 12px; 
}
.mb-item { text-align: center; }
.mb-label { font-size: 0.65rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }
.mb-value { font-size: 1.1rem; font-weight: 800; color: var(--text-primary); line-height: 1; }

/* --- ACORDEÃO DAS LIVES --- */
.streamlit-expanderHeader {
    background-color: var(--bg-white); border: 1px solid var(--border-color);
    border-radius: 6px; padding: 8px 14px; font-weight: 600; font-size: 0.9rem;
    color: var(--text-primary); margin-bottom: 4px;
}
.streamlit-expanderHeader:hover { border-color: var(--primary-color); background-color: #fff1f7; }
.streamlit-expanderContent {
    background-color: var(--bg-white); border: 1px solid var(--border-color);
    border-top: none; border-bottom-left-radius: 6px; border-bottom-right-radius: 6px;
    padding: 12px 16px; margin-top: -4px; margin-bottom: 8px;
}
.live-summary-metrics {
    display: grid; grid-template-columns: repeat(6, 1fr); 
    gap: 12px; margin-bottom: 10px; text-align: center;
    padding-bottom: 10px; border-bottom: 1px dashed var(--border-color);
}

/* --- TABELA DE GRUPOS --- */
.styled-table {
    width: 100%; border-collapse: collapse; margin: 4px 0 0 0; 
    font-size: 0.8rem; border-radius: 6px; overflow: hidden;
    border: 1px solid var(--border-color);
}
.styled-table thead tr { background-color: #f8fafc; color: var(--text-secondary); text-align: left; font-weight: 600; }
.styled-table th, .styled-table td { padding: 6px 10px; }
.styled-table tbody tr { border-bottom: 1px solid var(--border-color); }
.styled-table tbody tr:last-of-type { border-bottom: none; }
.styled-table tbody tr:hover { background-color: #f1f5f9; }
.active-group-row { background-color: #f0fdf4 !important; }
.active-group-row td:first-child { font-weight: 700; color: var(--success-color); position: relative; }
.active-group-row td:first-child::before { content: '●'; color: var(--success-color); position: absolute; left: 2px; font-size: 0.6rem; top: 8px; }
.ctr-badge { padding: 2px 5px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }
.ctr-high { background-color: #dcfce7; color: var(--success-color); }
.ctr-med { background-color: #ffedd5; color: var(--warning-color); }
.ctr-low { background-color: #fee2e2; color: var(--danger-color); }

/* --- BOTÕES DE NAVEGAÇÃO --- */
button[kind="secondary"] {
    background: var(--bg-white) !important; color: var(--text-secondary) !important;
    border: 1px solid var(--border-color) !important; border-radius: 6px !important;
    font-weight: 600 !important; font-size: 13px !important; padding: 6px 16px !important;
}
button[kind="secondary"]:hover { border-color: var(--primary-color) !important; color: var(--primary-color) !important; background: #fff1f7 !important; }
button[kind="primary"] {
    background: var(--primary-color) !important; color: #ffffff !important;
    border: 1px solid var(--primary-color) !important; border-radius: 6px !important;
    font-weight: 700 !important; font-size: 13px !important; padding: 6px 16px !important;
    box-shadow: 0 2px 4px rgba(233, 30, 99, 0.2);
}
button[kind="primary"]:hover { background: #d81b60 !important; border-color: #d81b60 !important; color: #ffffff !important; }

.week-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 8px; border-bottom: 2px solid var(--primary-color);
    margin-top: 12px; margin-bottom: 16px;
}
.week-title-text { font-size: 1.3rem; font-weight: 800; color: var(--text-primary); margin: 0; display:flex; align-items:center; gap:8px;}
.week-subtitle { font-size: 0.85rem; color: var(--text-secondary); font-weight: 500; display:flex; align-items:center;}

.brand { display: flex; align-items: center; gap: 8px; margin-bottom: 0px; }
.brand-text { font-size: 20px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.5px; }
.brand-highlight { color: var(--primary-color); }
.sub-title { font-size: 11px; color: var(--text-secondary); display: flex; align-items: center; gap: 4px; margin-top: -2px;}

.stPlotlyChart { margin-top: -15px; }
</style>
""", unsafe_allow_html=True)

# ── FUNÇÕES AUXILIARES ──────────────────────────────────
MAX_GP = 8

def fmt(v): return f"{v:,.0f}".replace(",", ".")
def fmt_float(v): return f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
def fmtR(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def pct(v): return f"{v:.1f}%"

def kpi_new_html(label, value, icon_class, icon_name):
    return f'<div class="kpi-card-new"><div class="kpi-icon {icon_class}"><i class="{icon_name}"></i></div><div class="kpi-content"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div></div>'

def generate_groups_table(grupos):
    if not grupos: return "<small>Sem dados de grupos.</small>"
    html = '<table class="styled-table"><thead><tr><th>Grupo</th><th>Leads</th><th>Cliques</th><th>CTR</th></tr></thead><tbody>'
    for g in grupos:
        row_class = "active-group-row" if g["ativo"] else ""
        ctr_val = g["ctr"]
        ctr_class = "ctr-high" if ctr_val >= 40 else ("ctr-med" if ctr_val >= 20 else "ctr-low")
        html += f'<tr class="{row_class}"><td>{g["nome"]}</td><td>{fmt(g["leads"])}</td><td>{fmt(g["cliques"])}</td><td><span class="ctr-badge {ctr_class}">{pct(ctr_val)}</span></td></tr>'
    html += '</tbody></table>'
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
        s = int(safe_float(get_val(row, ["Microciclo", "Semana"])))
        if s <= 0: continue
        inv = safe_float(get_val(row, ["Investimento (R$)", "Investimento"]))
        la = safe_float(get_val(row, "Leads Ads"))
        le = safe_float(get_val(row, "Leads Entrada"))
        ls_ = safe_float(get_val(row, ["Leads Saida", "Leads Saída"]))
        vt = safe_float(get_val(row, "Vendas Total"))
        rec = safe_float(get_val(row, ["Receita (R$)", "Receita"]))
        
        captacao = str(get_val(row, ["Captação", "Captacao", "Capitação"])).strip()
        if str(captacao) in ["0", "0.0", "nan", "None"]: captacao = ""

        # --- NOVAS COLUNAS DO MICROCICLO COMPLETO ---
        ne_mc = safe_float(get_val(row, ["NE-MC", "NEMC", "NE MC", "Novos Espectadores"]))
        wt_mc = safe_float(get_val(row, ["WT-MC", "WTMC", "WT MC", "Watchtime"]))
        
        records.append(dict(
            semana=s, investimento=inv, leadsAds=la, leadsEntrada=le, leadsSaida=ls_, 
            vendas=vt, receita=rec, captacao=captacao, ne_mc=ne_mc, wt_mc=wt_mc
        ))
    return records

def process_lives(df):
    lives = []
    if df is None: return lives
    for _, row in df.iterrows():
        semana = int(safe_float(get_val(row, ["Microciclo", "Semana"])))
        tipo = str(get_val(row, "Tipo")).strip().upper()
        label = str(get_val(row, "Label")).strip()
        if not semana or not tipo or not label or tipo == "NAN": continue
        ga = str(get_val(row, "Grupo Ativo")).strip().upper()
        
        # Mantém a métrica individual do vídeo na aba de Lives
        novos_espectadores = safe_float(get_val(row, ["NE", "Novos Espectadores", "Espectadores Novos", "Novos"]))
        watchtime = safe_float(get_val(row, ["Watchtime", "Watch time", "Tempo"]))
        
        grupos = []
        for g in range(1, MAX_GP + 1):
            leads = safe_float(get_group_val(row, "leads", g))
            cliques = safe_float(get_group_val(row, "cliques", g))
            ctr = round((cliques / leads) * 100, 1) if leads > 0 else 0.0
            if leads > 0 or cliques > 0:
                grupos.append(dict(nome=f"GP{g}", leads=leads, cliques=cliques, ctr=ctr, ativo=f"GP{g}" == ga))
        
        ativo_leads = sum(g["leads"] for g in grupos if g["ativo"])
        ativo_cliques = sum(g["cliques"] for g in grupos if g["ativo"])

        lives.append(dict(
            semana=semana, tipo=tipo, label=label,
            data=str(get_val(row, "Data")).strip(),
            cliquesTotal=safe_float(get_val(row, ["Cliques Total", "Cliques"])), 
            pico=safe_float(get_val(row, "Pico")),
            novos=novos_espectadores, 
            watchtime=watchtime, 
            vendas=safe_float(get_val(row, ["Vendas", "Vendas Total"])),
            grupos=grupos,
            ativo_leads=ativo_leads,     
            ativo_cliques=ativo_cliques  
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
    font=dict(family="Inter", color="#6b7280", size=11), 
    margin=dict(l=30, r=10, t=20, b=20), 
    xaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#f1f5f9"),
    yaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#f1f5f9"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10), yanchor="bottom", y=1.0, xanchor="right", x=1),
    hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e2e8f0", font=dict(family="Inter", size=12, color="#111827")),
)

# ── GERENCIAMENTO DE ESTADO E CONEXÃO FIXA ──────────────
if "page" not in st.session_state: st.session_state.page = "overview"
if "sel_week" not in st.session_state: st.session_state.sel_week = None

ID_DA_PLANILHA = "17WFm9kfssn7I0YhMIaZ3_6bEBHVVdJlD"
if "sheet_id" not in st.session_state: 
    st.session_state.sheet_id = ID_DA_PLANILHA

# ── CARREGAMENTO DE DADOS ───────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def fetch_all(sid):
    sem_df, liv_df = load_data(sid)
    if sem_df is None: return None, None
    return process_semanal(sem_df), process_lives(liv_df)

sid = st.session_state.get("sheet_id", "")
with st.spinner("Sincronizando com Google Sheets..."):
    semanal, lives = fetch_all(sid)

if semanal is None:
    st.error("Erro ao conectar com a planilha. Verifique as permissões de acesso do link.")
    st.stop()

# ── CÁLCULOS GERAIS ─────────────────────────────────────
sem_map = {s["semana"]: s for s in semanal}
active_weeks = sorted([s for s, data in sem_map.items() if data.get("investimento", 0) > 0])

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
    
    # --- PUXANDO AS MÉTRICAS OFICIAIS DO MICROCICLO DA ABA SEMANAL ---
    tne = m.get("ne_mc", 0)
    twt = m.get("wt_mc", 0)
    
    cpl = inv / la if la > 0 else 0
    txE = (le / la) * 100 if la > 0 else 0
    txS = (ls_ / le) * 100 if le > 0 else 0 
    
    # O CPNE agora é calculado sobre o total oficial do MC (NE-MC)
    cpne = inv / tne if tne > 0 else 0 
    captacao = m.get("captacao", "")

    lvp_lives = [live for live in wl if live['tipo'] == 'LVP']
    lvg_lives = [live for live in wl if live['tipo'] == 'LVG']

    ativo_leads_lvp = sum(live['ativo_leads'] for live in lvp_lives)
    ativo_cliques_lvp = sum(live['ativo_cliques'] for live in lvp_lives)
    ctr_lvp = round((ativo_cliques_lvp / ativo_leads_lvp) * 100, 1) if ativo_leads_lvp > 0 else 0.0

    ativo_leads_lvg = sum(live['ativo_leads'] for live in lvg_lives)
    ativo_cliques_lvg = sum(live['ativo_cliques'] for live in lvg_lives)
    ctr_lvg = round((ativo_cliques_lvg / ativo_leads_lvg) * 100, 1) if ativo_leads_lvg > 0 else 0.0
    
    lives_label_str = " + ".join(l["label"] for l in wl)
    if not lives_label_str:
        lives_label_str = "Fase de Captação"
        
    weeks_data.append(dict(
        sn=s, **st_, tc=tc, pico=max((l["pico"] for l in wl), default=0),
        tne=tne, twt=twt, cpne=cpne, 
        ctr_lvp=ctr_lvp, ctr_lvg=ctr_lvg, captacao=captacao,
        inv=inv, la=la, le=le, ls=ls_, cpl=cpl, txE=round(txE, 1), txS=round(txS, 1),
        vt=tv + m.get("vendas", 0),
        lives_label=lives_label_str, evs=wl, m=m
    ))

ti = sum(w["inv"] for w in weeks_data)
tla = sum(w["la"] for w in weeks_data)
tle = sum(w["le"] for w in weeks_data)
tls = sum(w["ls"] for w in weeks_data)
total_cliques_all = sum(w["tc"] for w in weeks_data)
total_pico_all = sum(w["pico"] for w in weeks_data)
tv_all = sum(w["vt"] for w in weeks_data)
total_novos_all = sum(w["tne"] for w in weeks_data)

# O CPNE Global também reflete a soma oficial do NE-MC
cpne_global = ti / total_novos_all if total_novos_all > 0 else 0

# ── CABEÇALHO PRINCIPAL E BOTÃO DE ATUALIZAR ────────────
h_col1, h_col2 = st.columns([5, 1])
with h_col1:
    st.markdown("""
    <div class="brand">
        <span class="brand-text">Grupo <span class="brand-highlight">Rugido</span></span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sub-title">🟢 Sincronizado via Google Sheets</div>', unsafe_allow_html=True)

with h_col2:
    st.markdown("<div style='margin-bottom: 5px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("<div style='margin-bottom: 12px'></div>", unsafe_allow_html=True)

# ── NAVEGAÇÃO SUPERIOR ──────────────────────────────────
num_weeks = len(active_weeks)
spacer_width = max(1, 10 - (1.2 + num_weeks * 0.8)) 
nav_cols = st.columns([1.2] + [0.8] * num_weeks + [spacer_width])

with nav_cols[0]:
    btn_type = "primary" if st.session_state.sel_week is None else "secondary"
    if st.button("📊 Geral", use_container_width=True, type=btn_type):
        st.session_state.sel_week = None
        st.rerun()

for i, s in enumerate(active_weeks):
    with nav_cols[i + 1]:
        btn_type = "primary" if st.session_state.sel_week == s else "secondary"
        if st.button(f"MC {s}", use_container_width=True, type=btn_type):
            st.session_state.sel_week = s
            st.rerun()

st.markdown("<div style='margin-bottom: 12px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TELA: VISÃO GERAL
# ════════════════════════════════════════════════════════
if st.session_state.sel_week is None:
    st.markdown('<div class="week-header"><div class="week-title-text"><i class="fa-solid fa-chart-line" style="color:var(--primary-color); margin-right:8px"></i> Visão Geral do Lançamento</div><div class="week-subtitle">Acumulado de todos os microciclos</div></div>', unsafe_allow_html=True)

    cols = st.columns(6)
    kpis_overview = [
        ("Investimento", fmtR(ti), "icon-red", "fa-solid fa-money-bill-wave"),
        ("Leads Ads", fmt(tla), "icon-blue", "fa-solid fa-bullseye"),
        ("CPL", fmtR(ti / tla) if tla > 0 else "–", "icon-orange", "fa-solid fa-coins"),
        ("Novos Espect. (MC)", fmt(total_novos_all), "icon-purple", "fa-solid fa-user-plus"),
        ("CPNE", fmtR(cpne_global), "icon-orange", "fa-solid fa-tags"),
        ("Vendas", fmt(tv_all), "icon-pink", "fa-solid fa-ticket-alt"),
    ]
    for col, (label, value, icon_cls, icon_name) in zip(cols, kpis_overview):
        with col: st.markdown(kpi_new_html(label, value, icon_cls, icon_name), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 24px'></div>", unsafe_allow_html=True)

    # --- PRIMEIRA LINHA DE GRÁFICOS: COM HOVER FORMATADO EM R$ ---
    col_f, col_g = st.columns([1, 1])
    with col_f:
        st.markdown('<h4>Evolução de Custos (CPL vs CPNE)</h4>', unsafe_allow_html=True)
        fig1 = go.Figure()
        
        # Adicionando o CPL formatado no Hover (text)
        fig1.add_trace(go.Scatter(
            x=[f"MC {w['sn']}" for w in weeks_data], 
            y=[w["cpl"] for w in weeks_data], 
            mode='lines+markers', 
            name="CPL", 
            text=[fmtR(w["cpl"]) for w in weeks_data],
            hovertemplate="%{text}<extra></extra>", # Isso força o hover a mostrar o R$ bonitinho
            line=dict(color="#f59e0b", width=3), 
            marker=dict(size=8)
        ))
        
        # Adicionando o CPNE formatado no Hover (text)
        fig1.add_trace(go.Scatter(
            x=[f"MC {w['sn']}" for w in weeks_data], 
            y=[w["cpne"] for w in weeks_data], 
            mode='lines+markers', 
            name="CPNE", 
            text=[fmtR(w["cpne"]) for w in weeks_data],
            hovertemplate="%{text}<extra></extra>", # Isso força o hover a mostrar o R$ bonitinho
            line=dict(color="#8b5cf6", width=3), 
            marker=dict(size=8)
        ))
        
        fig1.update_layout(**PLOT_LAYOUT, height=280, hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True, config=dict(displayModeBar=False))
    
    with col_g:
        st.markdown('<h4>CTR do Grupo Principal: LVP vs LVG</h4>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=[f"MC {w['sn']}" for w in weeks_data], y=[w["ctr_lvp"] for w in weeks_data], name="LVP (Prospecção)", marker_color="#3b82f6", text=[pct(w["ctr_lvp"]) if w["ctr_lvp"] > 0 else "" for w in weeks_data], textposition="auto"))
        fig2.add_trace(go.Bar(x=[f"MC {w['sn']}" for w in weeks_data], y=[w["ctr_lvg"] for w in weeks_data], name="LVG (Conteúdo)", marker_color="#f59e0b", text=[pct(w["ctr_lvg"]) if w["ctr_lvg"] > 0 else "" for w in weeks_data], textposition="auto"))
        fig2.update_layout(**PLOT_LAYOUT, barmode="group", height=280) 
        fig2.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig2, use_container_width=True, config=dict(displayModeBar=False))

    st.markdown("<div style='margin-bottom: 24px'></div>", unsafe_allow_html=True)

    col_h, col_i = st.columns([1, 1])
    with col_h:
        st.markdown('<h4><i class="fa-solid fa-clock" style="color:var(--indigo-color); margin-right:6px"></i> Watchtime por Microciclo</h4>', unsafe_allow_html=True)
        fig3 = go.Figure(go.Bar(x=[f"MC {w['sn']}" for w in weeks_data], y=[w["twt"] for w in weeks_data], marker_color="#4f46e5", text=[fmt_float(w["twt"]) if w["twt"] > 0 else "" for w in weeks_data], textposition="auto"))
        fig3.update_layout(**PLOT_LAYOUT, height=250)
        st.plotly_chart(fig3, use_container_width=True, config=dict(displayModeBar=False))
        
    with col_i:
        st.markdown('<h4><i class="fa-solid fa-user-plus" style="color:var(--purple-color); margin-right:6px"></i> Novos Espectadores (NE) por Microciclo</h4>', unsafe_allow_html=True)
        fig4 = go.Figure(go.Bar(x=[f"MC {w['sn']}" for w in weeks_data], y=[w["tne"] for w in weeks_data], marker_color="#8b5cf6", text=[fmt(w["tne"]) if w["tne"] > 0 else "" for w in weeks_data], textposition="auto"))
        fig4.update_layout(**PLOT_LAYOUT, height=250)
        st.plotly_chart(fig4, use_container_width=True, config=dict(displayModeBar=False))


    st.markdown('<h4>Resumo</h4>', unsafe_allow_html=True)
    for w in weeks_data:
        c1, c2 = st.columns([1, 15])
        with c1:
            st.markdown(f'<div style="background:#fff1f7;border-radius:6px;height:32px;display:flex;align-items:center;justify-content:center;border:1px solid #fce7f3"><span style="font-size:13px;font-weight:700;color:#e91e63">MC {w["sn"]}</span></div>', unsafe_allow_html=True)
        with c2:
            cap_resumo = f"Captação: {w['captacao']}  |  " if w['captacao'] else ""
            label = f"{w['lives_label']}  |  {cap_resumo}Watchtime (MC): {fmt_float(w['twt'])}  |  NE (MC): {fmt(w['tne'])}  |  CPNE: {fmtR(w['cpne'])}  |  Vendas: {fmt(w['vt'])}"
            if st.button(label, key=f"week_list_{w['sn']}", use_container_width=True, type="secondary"):
                st.session_state.sel_week = w["sn"]
                st.rerun()

# ════════════════════════════════════════════════════════
# TELA: DETALHE DO MICROCICLO
# ════════════════════════════════════════════════════════
else:
    sw = st.session_state.sel_week
    w = next((w for w in weeks_data if w["sn"] == sw), None)
    if w is None: st.error("Microciclo não encontrado"); st.stop()

    date_badge = f"<span style='font-size:0.9rem; font-weight:500; color:var(--text-secondary); margin-left: 12px; border-left: 2px solid var(--border-color); padding-left: 12px;'><i class='fa-regular fa-calendar'></i> {w['captacao']}</span>" if w['captacao'] else ""

    st.markdown(f'''
    <div class="week-header">
        <div class="week-title-text" style="display:flex; align-items:center;">
            <i class="fa-solid fa-bullseye" style="color:var(--primary-color); margin-right:8px"></i> Microciclo {sw} {date_badge}
        </div>
        <div class="week-subtitle">{len(w['evs'])} live(s) analisada(s)</div>
    </div>
    ''', unsafe_allow_html=True)

    m = w["m"] if isinstance(w["m"], dict) else {}
    
    cols1 = st.columns(6)
    kpis_s1 = [
        ("Investimento", fmtR(m.get("investimento", 0)), "icon-red", "fa-solid fa-money-bill-wave"),
        ("Leads Ads", fmt(m.get("leadsAds", 0)), "icon-blue", "fa-solid fa-bullseye"),
        ("CPL", fmtR(w["cpl"]) if w["la"] > 0 else "–", "icon-orange", "fa-solid fa-coins"),
        ("Novos Espect. (MC)", fmt(w["tne"]), "icon-purple", "fa-solid fa-user-plus"),
        ("CPNE", fmtR(w["cpne"]), "icon-orange", "fa-solid fa-tags"),
        ("Watchtime (MC)", fmt_float(w["twt"]), "icon-indigo", "fa-solid fa-clock"),
    ]
    for col, (l, v, ic, iname) in zip(cols1, kpis_s1):
        with col: st.markdown(kpi_new_html(l, v, ic, iname), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 10px'></div>", unsafe_allow_html=True)

    cols2 = st.columns(6)
    kpis_s2 = [
        ("Leads Entrada", fmt(m.get("leadsEntrada", 0)), "icon-green", "fa-solid fa-users"),
        ("Taxa Entrada", pct(w["txE"]) if w["la"] > 0 else "–", "icon-green", "fa-solid fa-percentage"),
        ("Taxa de Saída", pct(w["txS"]) if w["le"] > 0 else "–", "icon-orange", "fa-solid fa-arrow-trend-down"),
        ("Leads Saíram", fmt(w["ls"]), "icon-red", "fa-solid fa-user-minus"),
        ("Total Cliques", fmt(w["tc"]), "icon-blue", "fa-solid fa-pointer"),
        ("Vendas do MC", fmt(w["vt"]), "icon-pink", "fa-solid fa-ticket-alt"),
    ]
    for col, (l, v, ic, iname) in zip(cols2, kpis_s2):
        with col: st.markdown(kpi_new_html(l, v, ic, iname), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px'></div>", unsafe_allow_html=True)

    st.markdown('<h4>Jornada de Conversão (1ª LVP - Grupo Principal)</h4>', unsafe_allow_html=True)
    
    primeira_lvp = next((ev for ev in w["evs"] if ev["tipo"] == "LVP"), None)
    
    if primeira_lvp:
        grupo_ativo = next((g for g in primeira_lvp["grupos"] if g["ativo"]), None)
        leads_ativos = grupo_ativo["leads"] if grupo_ativo else 0
        cliques_ativos = grupo_ativo["cliques"] if grupo_ativo else 0
        pico_lvp = primeira_lvp["pico"]
        vendas_lvp = primeira_lvp["vendas"]
        
        funnel_labels = ['Captação (Ads)', 'Entraram GP', 'Ficaram (Ativo)', 'Cliques (Ativo)', 'Pico (1ª LVP)', 'Vendas']
        funnel_values = [w['la'], w['le'], leads_ativos, cliques_ativos, pico_lvp, vendas_lvp]
    else:
        funnel_labels = ['Captação (Ads)', 'Entraram GP', 'Ficaram GP', 'Cliques', 'Pico Máx', 'Vendas']
        ficaram_grupo = w['le'] - w['ls']
        funnel_values = [w['la'], w['le'], ficaram_grupo, w['tc'], w['pico'], w['vt']]
    
    base_val = funnel_values[0] if funnel_values[0] > 0 else max(1, max(funnel_values))
    text_vals = [f"<b>{v:,.0f}</b><br>({(v/base_val)*100:.1f}%)" for v in funnel_values]

    fig_funnel_sem = go.Figure()
    fig_funnel_sem.add_trace(go.Scatter(
        x=funnel_labels, 
        y=funnel_values,
        mode='lines+markers+text',
        text=text_vals,
        textposition='top center',
        textfont=dict(size=11, color='#111827'),
        cliponaxis=False,
        marker=dict(size=12, color='#e91e63', line=dict(width=2, color='white')),
        line=dict(width=4, color='#e91e63', shape='spline'), 
        fill='tozeroy', 
        fillcolor='rgba(233, 30, 99, 0.08)'
    ))
    
    fig_funnel_sem.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#6b7280", size=11),
        margin=dict(l=50, r=50, t=50, b=20), 
        height=260,
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, max(funnel_values)*1.4]), 
        xaxis=dict(showgrid=False, zeroline=False, range=[-0.3, 5.3]) 
    )
    st.plotly_chart(fig_funnel_sem, use_container_width=True, config=dict(displayModeBar=False))
    
    st.markdown("<div style='margin-bottom: 12px'></div>", unsafe_allow_html=True)

    st.markdown(f'<div class="metric-bar-new"><div class="mb-item"><div class="mb-label">Cliques Total</div><div class="mb-value">{fmt(w["tc"])}</div></div><div class="mb-item"><div class="mb-label">Pico Máx</div><div class="mb-value" style="color:var(--primary-color)">{fmt(w["pico"])}</div></div><div class="mb-item"><div class="mb-label">CTR Ativo Médio</div><div class="mb-value" style="color:var(--success-color)">{pct(w["aCTR"])}</div></div><div class="mb-item"><div class="mb-label">CTR Passados Médio</div><div class="mb-value" style="color:var(--warning-color)">{pct(w["pCTR"]) if w["pCTR"] > 0 else "–"}</div></div><div class="mb-item"><div class="mb-label">Grupo Ativo</div><div class="mb-value" style="color:var(--primary-color)">{w["ga"]}</div></div></div>', unsafe_allow_html=True)

    st.markdown("<h4>Detalhamento das Lives</h4>", unsafe_allow_html=True)

    for i, ev in enumerate(w["evs"]):
        tipo_badge_color = "#3b82f6" if ev["tipo"] == "LVP" else "#f59e0b"
        expander_title = f"{ev['label']} ({ev['data']}) | NE (Live): {fmt(ev['novos'])} | WT (Live): {fmt_float(ev['watchtime'])} | Vendas: {fmt(ev['vendas'])}"
        
        with st.expander(expander_title, expanded=(i==0)):
            st.markdown(f'''
            <div class="live-summary-metrics">
                <div><div style="font-size:0.65rem;color:#6b7280;text-transform:uppercase;font-weight:700;margin-bottom:2px">Tipo</div><div style="font-weight:800;color:{tipo_badge_color}">{ev["tipo"]}</div></div>
                <div><div style="font-size:0.65rem;color:#6b7280;text-transform:uppercase;font-weight:700;margin-bottom:2px">Cliques</div><div style="font-weight:800">{fmt(ev["cliquesTotal"])}</div></div>
                <div><div style="font-size:0.65rem;color:#6b7280;text-transform:uppercase;font-weight:700;margin-bottom:2px">Pico</div><div style="font-weight:800;color:var(--primary-color)">{fmt(ev["pico"])}</div></div>
                <div><div style="font-size:0.65rem;color:#6b7280;text-transform:uppercase;font-weight:700;margin-bottom:2px">Watchtime</div><div style="font-weight:800;color:var(--indigo-color)">{fmt_float(ev["watchtime"])}</div></div>
                <div><div style="font-size:0.65rem;color:#6b7280;text-transform:uppercase;font-weight:700;margin-bottom:2px">NE (Novos)</div><div style="font-weight:800;color:var(--purple-color)">{fmt(ev["novos"])}</div></div>
                <div><div style="font-size:0.65rem;color:#6b7280;text-transform:uppercase;font-weight:700;margin-bottom:2px">Vendas</div><div style="font-weight:800;color:var(--primary-color)">{fmt(ev["vendas"])}</div></div>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown(generate_groups_table(ev["grupos"]), unsafe_allow_html=True)

# ── RODAPÉ ──────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center;font-size:11px;color:#9ca3af;border-top:1px solid #e2e8f0;padding-top:16px">Grupo Rugido · Gestão de Audiência</div>', unsafe_allow_html=True)
