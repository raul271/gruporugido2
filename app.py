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
