import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from streamlit_gsheets import GSheetsConnection # <--- Nova biblioteca aqui!

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E ESTILO VISUAL
# ==========================================
st.set_page_config(page_title="Dashboard Lives Semanais - Grupo Rugido", layout="wide")

# ... (Todo aquele código de CSS/Estilo do Tema Escuro continua igual aqui) ...

# ==========================================
# CARREGAMENTO E PREPARAÇÃO DOS DADOS
# ==========================================
# O ttl=600 faz o dashboard buscar dados novos na planilha a cada 10 minutos (600 segundos)
@st.cache_data(ttl=600)
def load_data():
    # 1. Cria a conexão com o Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. COLE O LINK DA SUA PLANILHA AQUI DENTRO DAS ASPAS
    url_planilha = "COLE_AQUI_O_LINK_COMPLETO_DA_SUA_PLANILHA"
    
    # 3. Faz a leitura das abas (os nomes têm que estar EXATAMENTE iguais aos da planilha)
    df_semanal = conn.read(spreadsheet=url_planilha, worksheet="Semanal")
    df_lives = conn.read(spreadsheet=url_planilha, worksheet="Lives e Grupos")

    # Limpa linhas vazias caso a planilha tenha linhas em branco no final
    df_semanal = df_semanal.dropna(subset=['Semana'])
    df_lives = df_lives.dropna(subset=['Semana', 'Tipo'])

    # Tratamento aba Semanal
    df_semanal['CPL (R$)'] = df_semanal['Investimento (R$)'] / df_semanal['Leads Ads']
    df_semanal['Taxa Entrada (%)'] = (df_semanal['Leads Entrada'] / df_semanal['Leads Ads']) * 100
    df_semanal['Taxa Saída (%)'] = (df_semanal['Leads Saída'] / df_semanal['Leads Entrada']) * 100

    return df_semanal, df_lives

df_semanal, df_lives = load_data()

# ... (O resto do código daqui pra baixo continua EXATAMENTE igual) ...

# ==========================================
# NAVEGAÇÃO E CONTROLE DE ESTADO
# ==========================================
if 'view' not in st.session_state:
    st.session_state.view = 'overview'
if 'selected_week' not in st.session_state:
    st.session_state.selected_week = None

def go_to_overview():
    st.session_state.view = 'overview'
    st.session_state.selected_week = None

def go_to_week(week_num):
    st.session_state.view = 'detail'
    st.session_state.selected_week = week_num

# Cabeçalho
st.markdown("<h2 class='header-title'>Grupo Rugido <span style='color: white; font-weight: 300;'>| Dashboard Lives Semanais</span></h2>", unsafe_allow_html=True)
st.markdown("---")

# Botões de Navegação Superiores
cols_nav = st.columns([2] + [1] * len(df_semanal['Semana'].unique()))
if cols_nav[0].button("🏠 Visão Geral", use_container_width=True):
    go_to_overview()

for idx, week in enumerate(sorted(df_semanal['Semana'].unique())):
    if cols_nav[idx+1].button(f"S{week}", use_container_width=True):
        go_to_week(week)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# CÁLCULOS GERAIS PARA AS LIVES
# ==========================================
def calculate_live_metrics(df_l):
    # Identificar colunas de grupos disponíveis
    gp_cols = [c for c in df_l.columns if c.startswith('Leads GP')]
    max_gps = len(gp_cols)
    
    resultados = []
    
    for _, row in df_l.iterrows():
        semana = row['Semana']
        ativo = row['Grupo Ativo']
        
        cliques_ativos = 0
        leads_ativos = 0
        cliques_passados = 0
        leads_passados = 0
        
        for i in range(1, max_gps + 1):
            gp_name = f'GP{i}'
            col_leads = f'Leads {gp_name}'
            col_cliques = f'Cliques {gp_name}'
            
            if col_leads in row and pd.notna(row[col_leads]) and row[col_leads] > 0:
                if gp_name == ativo:
                    cliques_ativos += row[col_cliques]
                    leads_ativos += row[col_leads]
                else:
                    cliques_passados += row.get(col_cliques, 0)
                    leads_passados += row[col_leads]
                    
        resultados.append({
            'Semana': semana,
            'Cliques Ativo': cliques_ativos,
            'Leads Ativo': leads_ativos,
            'Cliques Passados': cliques_passados,
            'Leads Passados': leads_passados
        })
        
    return pd.DataFrame(resultados)

df_metricas_lives = calculate_live_metrics(df_lives)
df_lives = pd.concat([df_lives.reset_index(drop=True), df_metricas_lives.drop('Semana', axis=1)], axis=1)

# Agrupando por semana para gráficos
df_lives_agg = df_lives.groupby('Semana').agg({
    'Cliques Ativo': 'sum',
    'Leads Ativo': 'sum',
    'Cliques Passados': 'sum',
    'Leads Passados': 'sum',
    'Cliques Total': 'sum'
}).reset_index()

df_lives_agg['CTR Ativo (%)'] = np.where(df_lives_agg['Leads Ativo'] > 0, (df_lives_agg['Cliques Ativo'] / df_lives_agg['Leads Ativo']) * 100, 0)
df_lives_agg['CTR Passados (%)'] = np.where(df_lives_agg['Leads Passados'] > 0, (df_lives_agg['Cliques Passados'] / df_lives_agg['Leads Passados']) * 100, 0)


# ==========================================
# TELA 1: VISÃO GERAL
# ==========================================
if st.session_state.view == 'overview':
    
    # 1. KPIs ACUMULADOS
    total_inv = df_semanal['Investimento (R$)'].sum()
    total_leads = df_semanal['Leads Ads'].sum()
    cpl_medio = total_inv / total_leads if total_leads > 0 else 0
    total_entrada = df_semanal['Leads Entrada'].sum()
    taxa_entrada = (total_entrada / total_leads * 100) if total_leads > 0 else 0
    total_saida = df_semanal['Leads Saída'].sum()
    taxa_saida = (total_saida / total_entrada * 100) if total_entrada > 0 else 0
    total_vendas = df_semanal['Vendas Total'].sum()

    kpi_cols = st.columns(6)
    kpis = [
        ("Investimento Total", f"R$ {total_inv:,.2f}", "top-bar-red"),
        ("Leads Ads Total", f"{total_leads:,.0f}", "top-bar-blue"),
        ("CPL Médio", f"R$ {cpl_medio:,.2f}", "top-bar-orange"),
        ("Taxa Entrada Média", f"{taxa_entrada:.1f}%", "top-bar-green"),
        ("Taxa Saída Média", f"{taxa_saida:.1f}%", "top-bar-yellow"),
        ("Vendas Total", f"{total_vendas:,.0f}", "top-bar-pink")
    ]
    
    for col, (title, value, css_class) in zip(kpi_cols, kpis):
        col.markdown(f"""
        <div class="kpi-card {css_class}">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. GRÁFICOS
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown("#### Cliques por Semana")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x="S" + df_lives_agg['Semana'].astype(str), y=df_lives_agg['Cliques Passados'], name='Grupos Passados', marker_color='#eab308'))
        fig1.add_trace(go.Bar(x="S" + df_lives_agg['Semana'].astype(str), y=df_lives_agg['Cliques Ativo'], name='Grupo Ativo', marker_color='#22c55e'))
        fig1.add_trace(go.Scatter(x="S" + df_lives_agg['Semana'].astype(str), y=df_lives_agg['Cliques Total'], name='Total', mode='lines+markers', line=dict(color='white', dash='dash')))
        fig1.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig1, use_container_width=True)

    with g_col2:
        st.markdown("#### CTR: Ativo vs Passados")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x="S" + df_lives_agg['Semana'].astype(str), y=df_lives_agg['CTR Ativo (%)'], name='CTR Ativo', marker_color='#22c55e'))
        fig2.add_trace(go.Bar(x="S" + df_lives_agg['Semana'].astype(str), y=df_lives_agg['CTR Passados (%)'], name='CTR Passados', marker_color='#eab308'))
        fig2.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)

    # 3. LISTA DE SEMANAS
    st.markdown("#### Detalhamento Semanal")
    for _, row in df_semanal.iterrows():
        sem = row['Semana']
        # Resumo das lives
        lives_sem = df_lives[df_lives['Semana'] == sem]
        labels_lives = " + ".join(lives_sem['Label'].dropna().tolist())
        grupo_ativo = lives_sem['Grupo Ativo'].iloc[0] if not lives_sem.empty else "N/A"
        
        with st.container():
            st.markdown(f"""
            <div class="live-card" style="padding:15px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h3 style="margin:0; color:#22c55e;">Semana {sem}</h3>
                    <p style="margin:0; color:#aaa;">{labels_lives} | Ativo: <b>{grupo_ativo}</b></p>
                </div>
                <div style="text-align: right; display:flex; gap: 20px;">
                    <div><span style="color:#aaa; font-size:12px;">Investimento</span><br><b>R$ {row['Investimento (R$)']:,.2f}</b></div>
                    <div><span style="color:#aaa; font-size:12px;">CPL</span><br><b>R$ {row['CPL (R$)']:,.2f}</b></div>
                    <div><span style="color:#aaa; font-size:12px;">Tx Entrada</span><br><b>{row['Taxa Entrada (%)']:.1f}%</b></div>
                    <div><span style="color:#aaa; font-size:12px;">Tx Saída</span><br><b>{row['Taxa Saída (%)']:.1f}%</b></div>
                    <div><span style="color:#aaa; font-size:12px;">Vendas</span><br><b>{row['Vendas Total']}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# TELA 2: DETALHE DA SEMANA
# ==========================================
elif st.session_state.view == 'detail':
    sem = st.session_state.selected_week
    st.markdown(f"<h3 style='color:#22c55e;'>Detalhamento: Semana {sem}</h3>", unsafe_allow_html=True)
    
    # Dados da semana
    dados_sem = df_semanal[df_semanal['Semana'] == sem].iloc[0] if not df_semanal[df_semanal['Semana'] == sem].empty else None
    
    if dados_sem is not None:
        # KPIs Linha 1
        c1, c2, c3, c4 = st.columns(4)
        kpis_l1 = [
            ("Investimento", f"R$ {dados_sem['Investimento (R$)']:,.2f}", "top-bar-red"),
            ("Leads Ads", f"{dados_sem['Leads Ads']:,.0f}", "top-bar-blue"),
            ("CPL", f"R$ {dados_sem['CPL (R$)']:,.2f}", "top-bar-orange"),
            ("Vendas Total", f"{dados_sem['Vendas Total']:,.0f}", "top-bar-pink")
        ]
        for col, (t, v, css) in zip([c1, c2, c3, c4], kpis_l1):
            col.markdown(f'<div class="kpi-card {css}"><div class="kpi-title">{t}</div><div class="kpi-value">{v}</div></div>', unsafe_allow_html=True)

        # KPIs Linha 2
        c5, c6, c7, c8 = st.columns(4)
        kpis_l2 = [
            ("Leads Entrada", f"{dados_sem['Leads Entrada']:,.0f}", "top-bar-green"),
            ("Leads Saída", f"{dados_sem['Leads Saída']:,.0f}", "top-bar-yellow"),
            ("Taxa Entrada", f"{dados_sem['Taxa Entrada (%)']:.1f}%", "top-bar-green"),
            ("Taxa Saída", f"{dados_sem['Taxa Saída (%)']:.1f}%", "top-bar-yellow")
        ]
        for col, (t, v, css) in zip([c5, c6, c7, c8], kpis_l2):
            col.markdown(f'<div class="kpi-card {css}"><div class="kpi-title">{t}</div><div class="kpi-value">{v}</div></div>', unsafe_allow_html=True)

    # Resumo Geral Barra Horizontal
    lives_sem = df_lives[df_lives['Semana'] == sem]
    if not lives_sem.empty:
        total_cliques_sem = lives_sem['Cliques Total'].sum()
        pico_max = lives_sem['Pico'].max()
        ativo_sem = lives_sem['Grupo Ativo'].iloc[0]
        
        agg_sem = df_lives_agg[df_lives_agg['Semana'] == sem].iloc[0]
        ctr_ativo_sem = agg_sem['CTR Ativo (%)']
        ctr_pass_sem = agg_sem['CTR Passados (%)']

        st.markdown(f"""
        <div style="background-color:#1a1a33; padding:15px; border-radius:8px; border:1px solid #333; display:flex; justify-content:space-around; margin-bottom: 25px;">
            <div style="text-align:center"><span style="color:#aaa; font-size:12px">Total Cliques</span><br><b>{total_cliques_sem}</b></div>
            <div style="text-align:center"><span style="color:#aaa; font-size:12px">Pico Máximo</span><br><b>{pico_max}</b></div>
            <div style="text-align:center"><span style="color:#aaa; font-size:12px">CTR Grupo Ativo ({ativo_sem})</span><br><b style="color:#22c55e;">{ctr_ativo_sem:.1f}%</b></div>
            <div style="text-align:center"><span style="color:#aaa; font-size:12px">CTR Grupos Passados</span><br><b style="color:#eab308;">{ctr_pass_sem:.1f}%</b></div>
        </div>
        """, unsafe_allow_html=True)

        # Cards das Lives Individuais
        for _, live in lives_sem.iterrows():
            tipo_nome = "Prospecção" if live['Tipo'] == 'LVP' else "Conteúdo"
            cor_tipo = "#3b82f6" if live['Tipo'] == 'LVP' else "#f97316"
            ativo = live['Grupo Ativo']
            
            # Cálculo CTR do grupo ativo nesta live
            col_leads_ativo = f"Leads {ativo}"
            col_cliques_ativo = f"Cliques {ativo}"
            ctr_ativo_live = 0
            if col_leads_ativo in live and live[col_leads_ativo] > 0:
                ctr_ativo_live = (live[col_cliques_ativo] / live[col_leads_ativo]) * 100

            st.markdown(f"""
            <div class="live-card">
                <div style="display:flex; justify-content:space-between; border-bottom:1px solid #333; padding-bottom:10px; margin-bottom:15px;">
                    <div>
                        <h4 style="margin:0;">{live['Label']} <span style="font-size:12px; background-color:{cor_tipo}; padding:2px 6px; border-radius:4px; margin-left:10px;">{tipo_nome}</span></h4>
                        <span style="color:#aaa; font-size:14px;">Data: {live['Data']}</span>
                    </div>
                    <div style="display:flex; gap:20px; text-align:right;">
                        <div><span style="color:#aaa; font-size:12px;">Cliques</span><br><b>{live['Cliques Total']}</b></div>
                        <div><span style="color:#aaa; font-size:12px;">Pico</span><br><b>{live['Pico']}</b></div>
                        <div><span style="color:#aaa; font-size:12px;">CTR Ativo</span><br><b style="color:#22c55e;">{ctr_ativo_live:.1f}%</b></div>
                        <div><span style="color:#aaa; font-size:12px;">Vendas</span><br><b>{live['Vendas']}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Renderizando os mini-cards de grupos
            st.markdown("<div style='display:flex; gap:10px; flex-wrap:wrap;'>", unsafe_allow_html=True)
            
            gp_cols = [c for c in live.index if str(c).startswith('Leads GP')]
            for c in gp_cols:
                gp_nome = c.replace('Leads ', '')
                leads_gp = live[c]
                cliques_gp = live.get(f'Cliques {gp_nome}', 0)
                
                if pd.notna(leads_gp) and leads_gp > 0:
                    ctr_gp = (cliques_gp / leads_gp) * 100 if leads_gp > 0 else 0
                    
                    is_ativo = (gp_nome == ativo)
                    tag_html = "<span class='badge-ativo'>ATIVO</span><br>" if is_ativo else ""
                    
                    # Definição de cor do CTR
                    cor_ctr = "white"
                    if is_ativo:
                        cor_ctr = "#22c55e"
                    else:
                        cor_ctr = "#eab308" if ctr_gp > 20 else "#ef4444"

                    st.markdown(f"""
                    <div class="group-card" style="width: 120px;">
                        {tag_html}
                        <b style="color:#aaa;">{gp_nome}</b><br>
                        <span style="font-size:12px;">L: {int(leads_gp)} | C: {int(cliques_gp)}</span><br>
                        <b style="color:{cor_ctr}; font-size:14px;">{ctr_gp:.1f}%</b>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True) # Fecha live-card
