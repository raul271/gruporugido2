import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO
import time

# ── DADOS HISTÓRICOS "CHUMBADOS" PARA VELOCIDADE ────────
PAST_DATA = {
    "Nov 23": [
        {"mc": 1, "investimento": 635.0, "leads": 0.0, "ne": 253.0, "wt": 353.03, "cpl": 0, "cpne": 2.509, "cpwt": 1.798},
        {"mc": 2, "investimento": 711.0, "leads": 0.0, "ne": 218.0, "wt": 203.16, "cpl": 0, "cpne": 3.261, "cpwt": 3.499},
        {"mc": 3, "investimento": 3135.12, "leads": 0.0, "ne": 194.0, "wt": 206.2, "cpl": 0, "cpne": 16.160, "cpwt": 15.204},
        {"mc": 4, "investimento": 3204.48, "leads": 0.0, "ne": 267.0, "wt": 218.14, "cpl": 0, "cpne": 12.001, "cpwt": 14.690},
        {"mc": 5, "investimento": 1450.63, "leads": 0.0, "ne": 225.0, "wt": 187.16, "cpl": 0, "cpne": 6.447, "cpwt": 7.750},
        {"mc": 6, "investimento": 6851.4, "leads": 0.0, "ne": 539.0, "wt": 881.97, "cpl": 0, "cpne": 12.711, "cpwt": 7.768},
        {"mc": 7, "investimento": 926.3, "leads": 0.0, "ne": 161.0, "wt": 180.67, "cpl": 0, "cpne": 5.753, "cpwt": 5.127}
    ],
    "Jan 24": [
        {"mc": 1, "investimento": 219.02, "leads": 0.0, "ne": 129.0, "wt": 138.51, "cpl": 0, "cpne": 1.697, "cpwt": 1.581},
        {"mc": 5, "investimento": 558.32, "leads": 0.0, "ne": 223.0, "wt": 270.49, "cpl": 0, "cpne": 2.503, "cpwt": 2.064},
        {"mc": 6, "investimento": 839.28, "leads": 0.0, "ne": 267.0, "wt": 333.09, "cpl": 0, "cpne": 3.143, "cpwt": 2.519},
        {"mc": 7, "investimento": 3401.75, "leads": 0.0, "ne": 472.0, "wt": 536.48, "cpl": 0, "cpne": 7.207, "cpwt": 6.340},
        {"mc": 8, "investimento": 9807.48, "leads": 0.0, "ne": 1457.0, "wt": 1555.1, "cpl": 0, "cpne": 6.731, "cpwt": 6.306},
        {"mc": 9, "investimento": 9950.81, "leads": 0.0, "ne": 2111.0, "wt": 3264.38, "cpl": 0, "cpne": 4.713, "cpwt": 3.048},
        {"mc": 10, "investimento": 3222.67, "leads": 0.0, "ne": 972.0, "wt": 1505.68, "cpl": 0, "cpne": 3.315, "cpwt": 2.140}
    ],
    "Mar 24": [
        {"mc": 1, "investimento": 954.1, "leads": 71.0, "ne": 1059.0, "wt": 1477.05, "cpl": 13.438, "cpne": 0.900, "cpwt": 0.645},
        {"mc": 2, "investimento": 5493.16, "leads": 1453.0, "ne": 1443.0, "wt": 2245.55, "cpl": 3.780, "cpne": 3.806, "cpwt": 2.446},
        {"mc": 3, "investimento": 3155.1, "leads": 864.0, "ne": 1790.0, "wt": 2172.39, "cpl": 3.651, "cpne": 1.762, "cpwt": 1.452},
        {"mc": 4, "investimento": 8139.58, "leads": 293.0, "ne": 1619.0, "wt": 2482.62, "cpl": 27.780, "cpne": 5.027, "cpwt": 3.278},
        {"mc": 5, "investimento": 9456.53, "leads": 851.0, "ne": 1641.0, "wt": 2398.42, "cpl": 11.112, "cpne": 5.762, "cpwt": 3.942},
        {"mc": 6, "investimento": 9724.64, "leads": 402.0, "ne": 2394.0, "wt": 6067.86, "cpl": 24.190, "cpne": 4.062, "cpwt": 1.602},
        {"mc": 7, "investimento": 9137.49, "leads": 296.0, "ne": 983.0, "wt": 2050.5, "cpl": 30.869, "cpne": 9.295, "cpwt": 4.456}
    ],
    "Mai 24": [
        {"mc": 1, "investimento": 1909.28, "leads": 8.0, "ne": 914.0, "wt": 1357.23, "cpl": 238.66, "cpne": 2.088, "cpwt": 1.406},
        {"mc": 2, "investimento": 8444.77, "leads": 996.0, "ne": 1496.0, "wt": 1999.78, "cpl": 8.478, "cpne": 5.644, "cpwt": 4.222},
        {"mc": 3, "investimento": 11305.18, "leads": 950.0, "ne": 2022.0, "wt": 2677.21, "cpl": 11.900, "cpne": 5.591, "cpwt": 4.222},
        {"mc": 4, "investimento": 11697.5, "leads": 1120.0, "ne": 2120.0, "wt": 3186.69, "cpl": 10.444, "cpne": 5.517, "cpwt": 3.670},
        {"mc": 5, "investimento": 15198.82, "leads": 1090.0, "ne": 2475.0, "wt": 5032.36, "cpl": 13.943, "cpne": 6.140, "cpwt": 3.020},
        {"mc": 6, "investimento": 15510.91, "leads": 732.0, "ne": 2030.0, "wt": 4870.07, "cpl": 21.189, "cpne": 7.640, "cpwt": 3.184},
        {"mc": 7, "investimento": 10610.9, "leads": 265.0, "ne": 2142.0, "wt": 7585.04, "cpl": 40.041, "cpne": 4.953, "cpwt": 1.398},
        {"mc": 8, "investimento": 7182.24, "leads": 107.0, "ne": 957.0, "wt": 2483.27, "cpl": 67.123, "cpne": 7.504, "cpwt": 2.892},
        {"mc": 9, "investimento": 4787.55, "leads": 103.0, "ne": 993.0, "wt": 2341.84, "cpl": 46.481, "cpne": 4.821, "cpwt": 2.044}
    ],
    "Jul 24": [
        {"mc": 1, "investimento": 2570.77, "leads": 305.0, "ne": 1114.0, "wt": 2215.87, "cpl": 8.428, "cpne": 2.307, "cpwt": 1.160},
        {"mc": 2, "investimento": 9585.96, "leads": 868.0, "ne": 1715.0, "wt": 3068.18, "cpl": 11.043, "cpne": 5.589, "cpwt": 3.124},
        {"mc": 3, "investimento": 14245.39, "leads": 1289.0, "ne": 2128.0, "wt": 3581.88, "cpl": 11.051, "cpne": 6.694, "cpwt": 3.977},
        {"mc": 4, "investimento": 12164.61, "leads": 1211.0, "ne": 1599.0, "wt": 2917.43, "cpl": 10.045, "cpne": 7.607, "cpwt": 4.169},
        {"mc": 5, "investimento": 15011.85, "leads": 946.0, "ne": 2492.0, "wt": 4313.42, "cpl": 15.868, "cpne": 6.024, "cpwt": 3.480},
        {"mc": 6, "investimento": 32636.93, "leads": 1581.0, "ne": 1929.0, "wt": 4436.89, "cpl": 20.643, "cpne": 16.919, "cpwt": 7.355},
        {"mc": 7, "investimento": 28509.77, "leads": 1330.0, "ne": 2188.0, "wt": 6073.05, "cpl": 21.435, "cpne": 13.030, "cpwt": 4.694},
        {"mc": 8, "investimento": 14433.84, "leads": 13.0, "ne": 2736.0, "wt": 9121.2, "cpl": 1110.295, "cpne": 5.275, "cpwt": 1.582},
        {"mc": 9, "investimento": 22708.52, "leads": 84.0, "ne": 1037.0, "wt": 3560.24, "cpl": 270.339, "cpne": 21.898, "cpwt": 6.378}
    ],
    "Set 24": [
        {"mc": 1, "investimento": 21500.23, "leads": 833.0, "ne": 1666.0, "wt": 3569.5, "cpl": 25.810, "cpne": 12.905, "cpwt": 6.023},
        {"mc": 2, "investimento": 20994.01, "leads": 1566.0, "ne": 2531.0, "wt": 4172.94, "cpl": 13.406, "cpne": 8.294, "cpwt": 5.030},
        {"mc": 3, "investimento": 26701.1, "leads": 1822.0, "ne": 2522.0, "wt": 4922.71, "cpl": 14.654, "cpne": 10.587, "cpwt": 5.424},
        {"mc": 4, "investimento": 30171.4, "leads": 1634.0, "ne": 2674.0, "wt": 5276.06, "cpl": 18.464, "cpne": 11.283, "cpwt": 5.718},
        {"mc": 5, "investimento": 31207.94, "leads": 957.0, "ne": 2640.0, "wt": 6003.86, "cpl": 32.610, "cpne": 11.821, "cpwt": 5.197},
        {"mc": 6, "investimento": 29276.17, "leads": 1054.0, "ne": 1480.0, "wt": 4787.85, "cpl": 27.776, "cpne": 19.781, "cpwt": 6.114},
        {"mc": 7, "investimento": 20027.49, "leads": 3.0, "ne": 2777.0, "wt": 11465.53, "cpl": 6675.83, "cpne": 7.211, "cpwt": 1.746},
        {"mc": 8, "investimento": 26550.79, "leads": 680.0, "ne": 119.0, "wt": 326.72, "cpl": 39.045, "cpne": 223.115, "cpwt": 81.264}
    ],
    "Nov 24": [
        {"mc": 1, "investimento": 9022.61, "leads": 802.0, "ne": 1876.0, "wt": 3416.66, "cpl": 11.250, "cpne": 4.809, "cpwt": 2.640},
        {"mc": 2, "investimento": 21052.6, "leads": 1642.0, "ne": 2197.0, "wt": 3978.69, "cpl": 12.821, "cpne": 9.582, "cpwt": 5.291},
        {"mc": 3, "investimento": 30320.12, "leads": 2189.0, "ne": 2159.0, "wt": 3810.66, "cpl": 13.851, "cpne": 14.043, "cpwt": 7.956},
        {"mc": 4, "investimento": 50143.55, "leads": 1016.0, "ne": 2442.0, "wt": 5007.97, "cpl": 49.353, "cpne": 20.533, "cpwt": 10.012},
        {"mc": 5, "investimento": 26328.66, "leads": 1416.0, "ne": 2206.0, "wt": 5009.59, "cpl": 18.593, "cpne": 11.935, "cpwt": 5.255},
        {"mc": 6, "investimento": 58009.82, "leads": 1594.0, "ne": 3070.0, "wt": 6125.38, "cpl": 36.392, "cpne": 18.895, "cpwt": 9.470},
        {"mc": 7, "investimento": 61959.96, "leads": 1661.0, "ne": 2755.0, "wt": 5100.99, "cpl": 37.302, "cpne": 22.490, "cpwt": 12.146},
        {"mc": 8, "investimento": 33425.5, "leads": 288.0, "ne": 4052.0, "wt": 9968.24, "cpl": 116.060, "cpne": 8.249, "cpwt": 3.353},
        {"mc": 9, "investimento": 29630.95, "leads": 581.0, "ne": 993.0, "wt": 2776.49, "cpl": 50.999, "cpne": 29.839, "cpwt": 10.672}
    ],
    "Jan 25": [
        {"mc": 1, "investimento": 22920.31, "leads": 1391.0, "ne": 1628.0, "wt": 3828.87, "cpl": 16.477, "cpne": 14.078, "cpwt": 5.986},
        {"mc": 2, "investimento": 26777.01, "leads": 1290.0, "ne": 1512.0, "wt": 4245.74, "cpl": 20.757, "cpne": 17.709, "cpwt": 6.306},
        {"mc": 3, "investimento": 32760.53, "leads": 980.0, "ne": 1586.0, "wt": 3375.47, "cpl": 33.429, "cpne": 20.656, "cpwt": 9.705},
        {"mc": 4, "investimento": 50349.23, "leads": 1963.0, "ne": 1931.0, "wt": 3918.67, "cpl": 25.649, "cpne": 26.074, "cpwt": 12.848},
        {"mc": 5, "investimento": 60074.4, "leads": 1313.0, "ne": 2275.0, "wt": 4391.48, "cpl": 45.753, "cpne": 26.406, "cpwt": 13.679},
        {"mc": 6, "investimento": 71521.02, "leads": 2923.0, "ne": 1338.0, "wt": 2802.24, "cpl": 24.468, "cpne": 53.453, "cpwt": 25.522},
        {"mc": 7, "investimento": 55883.31, "leads": 1936.0, "ne": 1520.0, "wt": 3233.14, "cpl": 28.865, "cpne": 36.765, "cpwt": 17.284},
        {"mc": 8, "investimento": 46760.42, "leads": 208.0, "ne": 3470.0, "wt": 9240.34, "cpl": 224.809, "cpne": 13.475, "cpwt": 5.060},
        {"mc": 9, "investimento": 30398.61, "leads": 523.0, "ne": 907.0, "wt": 2957.62, "cpl": 58.123, "cpne": 33.515, "cpwt": 10.278}
    ],
    "Mar 25": [
        {"mc": 1, "investimento": 8697.59, "leads": 658.0, "ne": 1120.0, "wt": 3248.42, "cpl": 13.218, "cpne": 7.765, "cpwt": 2.677},
        {"mc": 2, "investimento": 19270.68, "leads": 1245.0, "ne": 1661.0, "wt": 3400.01, "cpl": 15.478, "cpne": 11.601, "cpwt": 5.667},
        {"mc": 3, "investimento": 39398.62, "leads": 1855.0, "ne": 1910.0, "wt": 4046.97, "cpl": 21.239, "cpne": 20.627, "cpwt": 9.735},
        {"mc": 4, "investimento": 41838.92, "leads": 1711.0, "ne": 2542.0, "wt": 6113.06, "cpl": 24.452, "cpne": 16.459, "cpwt": 6.844},
        {"mc": 5, "investimento": 49764.07, "leads": 1277.0, "ne": 1882.0, "wt": 4316.95, "cpl": 38.969, "cpne": 26.442, "cpwt": 11.527},
        {"mc": 6, "investimento": 64629.9, "leads": 1060.0, "ne": 1488.0, "wt": 3216.23, "cpl": 60.971, "cpne": 43.434, "cpwt": 20.094},
        {"mc": 7, "investimento": 43295.57, "leads": 405.0, "ne": 1149.0, "wt": 2139.83, "cpl": 106.902, "cpne": 37.681, "cpwt": 20.233},
        {"mc": 8, "investimento": 24816.59, "leads": 7.0, "ne": 2010.0, "wt": 4094.19, "cpl": 3545.227, "cpne": 12.346, "cpwt": 6.061},
        {"mc": 9, "investimento": 14250.54, "leads": 0.0, "ne": 555.0, "wt": 1341.57, "cpl": 0, "cpne": 25.676, "cpwt": 10.622}
    ],
    "Mai 25": [
        {"mc": 1, "investimento": 14349.96, "leads": 0.0, "ne": 1007.0, "wt": 2844.3, "cpl": 0, "cpne": 14.250, "cpwt": 5.045},
        {"mc": 2, "investimento": 20924.92, "leads": 0.0, "ne": 1218.0, "wt": 3569.93, "cpl": 0, "cpne": 17.179, "cpwt": 5.861},
        {"mc": 3, "investimento": 31594.25, "leads": 0.0, "ne": 875.0, "wt": 2314.24, "cpl": 0, "cpne": 36.107, "cpwt": 13.652},
        {"mc": 4, "investimento": 32615.32, "leads": 0.0, "ne": 909.0, "wt": 1998.18, "cpl": 0, "cpne": 35.880, "cpwt": 16.322},
        {"mc": 5, "investimento": 30832.49, "leads": 0.0, "ne": 1449.0, "wt": 2863.54, "cpl": 0, "cpne": 21.278, "cpwt": 10.767},
        {"mc": 6, "investimento": 30480.82, "leads": 0.0, "ne": 884.0, "wt": 1957.15, "cpl": 0, "cpne": 34.480, "cpwt": 15.574},
        {"mc": 7, "investimento": 21409.62, "leads": 0.0, "ne": 893.0, "wt": 1588.74, "cpl": 0, "cpne": 23.974, "cpwt": 13.475},
        {"mc": 8, "investimento": 15968.28, "leads": 0.0, "ne": 1502.0, "wt": 2953.3, "cpl": 0, "cpne": 10.631, "cpwt": 5.406},
        {"mc": 9, "investimento": 14694.15, "leads": 0.0, "ne": 296.0, "wt": 988.15, "cpl": 0, "cpne": 49.642, "cpwt": 14.870}
    ],
    "Jul 25": [
        {"mc": 1, "investimento": 16350.81, "leads": 0.0, "ne": 442.0, "wt": 947.3, "cpl": 0, "cpne": 36.992, "cpwt": 17.260},
        {"mc": 2, "investimento": 23651.06, "leads": 0.0, "ne": 467.0, "wt": 1008.45, "cpl": 0, "cpne": 50.644, "cpwt": 23.452},
        {"mc": 3, "investimento": 35248.43, "leads": 0.0, "ne": 1172.0, "wt": 3383.03, "cpl": 0, "cpne": 30.075, "cpwt": 10.419},
        {"mc": 4, "investimento": 41005.21, "leads": 0.0, "ne": 1073.0, "wt": 2462.04, "cpl": 0, "cpne": 38.215, "cpwt": 16.654},
        {"mc": 5, "investimento": 45815.38, "leads": 0.0, "ne": 1462.0, "wt": 3990.57, "cpl": 0, "cpne": 31.337, "cpwt": 11.480},
        {"mc": 6, "investimento": 61306.83, "leads": 0.0, "ne": 1147.0, "wt": 2696.85, "cpl": 0, "cpne": 53.449, "cpwt": 22.732},
        {"mc": 7, "investimento": 59513.5, "leads": 0.0, "ne": 861.0, "wt": 1497.58, "cpl": 0, "cpne": 69.121, "cpwt": 39.739},
        {"mc": 8, "investimento": 30394.11, "leads": 0.0, "ne": 1422.0, "wt": 3148.42, "cpl": 0, "cpne": 21.374, "cpwt": 9.653},
        {"mc": 9, "investimento": 21648.89, "leads": 0.0, "ne": 585.0, "wt": 1233.04, "cpl": 0, "cpne": 37.006, "cpwt": 17.557}
    ],
    "Set 25": [
        {"mc": 1, "investimento": 18750.67, "leads": 0.0, "ne": 2062.0, "wt": 2185.19, "cpl": 0, "cpne": 9.093, "cpwt": 8.580},
        {"mc": 2, "investimento": 35343.03, "leads": 0.0, "ne": 1031.0, "wt": 1857.65, "cpl": 0, "cpne": 34.280, "cpwt": 19.025},
        {"mc": 3, "investimento": 56837.23, "leads": 0.0, "ne": 1197.0, "wt": 1903.01, "cpl": 0, "cpne": 47.483, "cpwt": 29.867},
        {"mc": 4, "investimento": 90865.67, "leads": 0.0, "ne": 1169.0, "wt": 2317.65, "cpl": 0, "cpne": 77.729, "cpwt": 39.205}
    ]
}


# ── CONFIGURAÇÃO DA PÁGINA ──────────────────────────────
st.set_page_config(
    page_title="Dashboard Lançamento Março 26",
    page_icon="🚀",
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
    cb = int(time.time())
    base = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&_cb={cb}"
    sem_df = parse_csv_from_url(f"{base}&sheet=Semanal")
    liv_df = parse_csv_from_url(f"{base}&sheet=Lives+e+Grupos")
    return sem_df, liv_df

def col_match(df_cols, target):
    target_lower = str(target).lower().strip()
    for c in df_cols:
        if str(c).lower().strip() == target_lower: return c
    for c in df_cols:
        cl = str(c).lower().strip()
        simple_t = target_lower.replace("í","i").replace("ã","a").replace("ç","c").replace("é","e").replace("ú","u").replace("-", "").replace(" ", "")
        simple_c = cl.replace("í","i").replace("ã","a").replace("ç","c").replace("é","e").replace("ú","u").replace("-", "").replace(" ", "")
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

def aggregate_launch(mc_list):
    if not mc_list: return {'investimento':0, 'leads':0, 'ne':0, 'wt':0, 'cpl':0, 'cpne':0, 'cpwt':0}
    t_inv = sum(x['investimento'] for x in mc_list)
    t_leads = sum(x['leads'] for x in mc_list)
    t_ne = sum(x['ne'] for x in mc_list)
    t_wt = sum(x['wt'] for x in mc_list)
    return {
        'mc': 'Geral',
        'investimento': t_inv,
        'leads': t_leads,
        'ne': t_ne,
        'wt': t_wt,
        'cpl': t_inv / t_leads if t_leads > 0 else 0,
        'cpne': t_inv / t_ne if t_ne > 0 else 0,
        'cpwt': t_inv / t_wt if t_wt > 0 else 0
    }

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

# ── CARREGAMENTO DE DADOS (PLANILHA ATUAL) ──────────────
@st.cache_data(ttl=120, show_spinner=False)
def fetch_all(sid):
    sem_df, liv_df = load_data(sid)
    if sem_df is None: return None, None
    return process_semanal(sem_df), process_lives(liv_df)

sid = st.session_state.get("sheet_id", "")
with st.spinner("Sincronizando Lançamento Atual..."):
    semanal, lives = fetch_all(sid)

if semanal is None:
    st.error("Erro ao conectar com a planilha do Lançamento Março 26.")
    st.stop()

# ── CÁLCULOS GERAIS (MARÇO 26) ──────────────────────────
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
    
    tne = m.get("ne_mc", 0)
    twt = m.get("wt_mc", 0)
    
    cpl = inv / la if la > 0 else 0
    txE = (le / la) * 100 if la > 0 else 0
    txS = (ls_ / le) * 100 if le > 0 else 0 
    
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

cpne_global = ti / total_novos_all if total_novos_all > 0 else 0

# ── CABEÇALHO PRINCIPAL E BOTÃO DE ATUALIZAR ────────────
h_col1, h_col2 = st.columns([5, 1])
with h_col1:
    st.markdown("""
    <div class="brand">
        <span class="brand-text">Lançamento <span class="brand-highlight">Março 26</span></span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sub-title">🟢 Grupo Rugido · Gestão de Audiência</div>', unsafe_allow_html=True)

with h_col2:
    st.markdown("<div style='margin-bottom: 5px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("<div style='margin-bottom: 12px'></div>", unsafe_allow_html=True)

# ── NAVEGAÇÃO ESTRUTURAL DAS ABAS MAIORES ───────────────
tab_atual, tab_anteriores, tab_comp = st.tabs(["🚀 Março 26 (Atual)", "⏪ Lançamentos Anteriores", "⚖️ Comparativo de Microciclos"])


# ════════════════════════════════════════════════════════
# ABA 1: LANÇAMENTO ATUAL (MARÇO 26)
# ════════════════════════════════════════════════════════
with tab_atual:
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

        col_f, col_g = st.columns([1, 1])
        with col_f:
            st.markdown('<h4>Evolução de Custos (CPL vs CPNE)</h4>', unsafe_allow_html=True)
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=[f"MC {w['sn']}" for w in weeks_data], y=[w["cpl"] for w in weeks_data], mode='lines+markers', name="CPL", text=[fmtR(w["cpl"]) for w in weeks_data], hovertemplate="%{text}<extra></extra>", line=dict(color="#f59e0b", width=3), marker=dict(size=8)))
            fig1.add_trace(go.Scatter(x=[f"MC {w['sn']}" for w in weeks_data], y=[w["cpne"] for w in weeks_data], mode='lines+markers', name="CPNE", text=[fmtR(w["cpne"]) for w in weeks_data], hovertemplate="%{text}<extra></extra>", line=dict(color="#8b5cf6", width=3), marker=dict(size=8)))
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


# ════════════════════════════════════════════════════════
# ABA 2: LANÇAMENTOS ANTERIORES (HISTÓRICO)
# ════════════════════════════════════════════════════════
with tab_anteriores:
    st.markdown("### ⏪ Dados Históricos de Lançamentos")
    
    # Remove as opções vazias para não sujar a interface
    valid_launches = {k: v for k, v in PAST_DATA.items() if len(v) > 0}
    
    if valid_launches:
        sel_l = st.selectbox("Escolha o Lançamento:", list(valid_launches.keys()))
        
        mcs_l = valid_launches[sel_l]
        mc_options = ["Geral"] + [f"MC {m['mc']}" for m in mcs_l]
        
        st.markdown("<div style='margin-bottom: 12px'></div>", unsafe_allow_html=True)
        sel_mc_ant = st.radio("Filtro de Microciclo:", mc_options, horizontal=True)
        st.markdown("<div style='margin-bottom: 24px'></div>", unsafe_allow_html=True)
        
        if sel_mc_ant == "Geral":
            d_show = aggregate_launch(mcs_l)
            st.markdown(f"#### Resultados Globais: {sel_l}")
        else:
            idx = int(sel_mc_ant.replace("MC ", "")) - 1
            d_show = mcs_l[idx]
            st.markdown(f"#### Resultados: {sel_l} - {sel_mc_ant}")
            
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(kpi_new_html("Investimento", fmtR(d_show['investimento']), "icon-red", "fa-solid fa-money-bill-wave"), unsafe_allow_html=True)
        with c2: st.markdown(kpi_new_html("Leads LVP", fmt(d_show['leads']), "icon-blue", "fa-solid fa-users"), unsafe_allow_html=True)
        with c3: st.markdown(kpi_new_html("CPL", fmtR(d_show['cpl']), "icon-orange", "fa-solid fa-coins"), unsafe_allow_html=True)
        with c4: st.markdown(kpi_new_html("Novos Espectadores", fmt(d_show['ne']), "icon-purple", "fa-solid fa-eye"), unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 12px'></div>", unsafe_allow_html=True)
        c5, c6, c7, c8 = st.columns(4)
        with c5: st.markdown(kpi_new_html("CPNE", fmtR(d_show['cpne']), "icon-orange", "fa-solid fa-tags"), unsafe_allow_html=True)
        with c6: st.markdown(kpi_new_html("Watchtime", fmt_float(d_show['wt']), "icon-indigo", "fa-solid fa-clock"), unsafe_allow_html=True)
        with c7: st.markdown(kpi_new_html("Custo por WT", fmtR(d_show['cpwt']), "icon-red", "fa-solid fa-chart-line"), unsafe_allow_html=True)
        with c8: st.markdown(kpi_new_html("Status", "Fechado", "icon-green", "fa-solid fa-check"), unsafe_allow_html=True)
    else:
        st.info("Nenhum dado de lançamento passado encontrado.")


# ════════════════════════════════════════════════════════
# ABA 3: COMPARATIVO DE MICROCICLOS
# ════════════════════════════════════════════════════════
with tab_comp:
    st.markdown("### ⚖️ Comparativo Lado a Lado")
    st.caption("Filtre até 3 cenários diferentes (seja o lançamento completo ou um microciclo específico) para comparar a eficiência da operação.")
    
    all_l = {k: v for k, v in PAST_DATA.items() if len(v) > 0}
    if weeks_data:
        mar26 = []
        for w in weeks_data:
            mar26.append({
                'mc': w['sn'],
                'investimento': w['inv'],
                'leads': w['la'], 
                'ne': w['tne'],
                'wt': w['twt'],
                'cpl': w['cpl'],
                'cpne': w['cpne'],
                'cpwt': w['inv'] / w['twt'] if w['twt'] > 0 else 0
            })
        all_l["Março 26 (Atual)"] = mar26
        
    if all_l:
        col_c1, col_c2, col_c3 = st.columns(3)
        cols_ui = [col_c1, col_c2, col_c3]
        
        l_keys = list(all_l.keys())
        def_1 = l_keys.index("Março 26 (Atual)") if "Março 26 (Atual)" in l_keys else 0
        def_2 = l_keys.index("Jul 25") if "Jul 25" in l_keys else 0 # Setup inteligente
        def_idx = [def_1, def_2, 0]
        
        for i in range(3):
            with cols_ui[i]:
                st.markdown(f"<h4 style='text-align:center; color:var(--primary-color)'>Cenário {i+1}</h4>", unsafe_allow_html=True)
                
                opts_l = ["Nenhum"] + l_keys
                try: 
                    d_idx = def_idx[i] + 1 if i < 2 else 0
                except: 
                    d_idx = 0
                    
                sel_l_comp = st.selectbox("Lançamento", opts_l, index=d_idx, key=f"comp_l_{i}")
                
                if sel_l_comp != "Nenhum":
                    mcs_comp = all_l[sel_l_comp]
                    opts_m = ["Geral"] + [f"MC {m['mc']}" for m in mcs_comp]
                    sel_m_comp = st.selectbox("Microciclo", opts_m, key=f"comp_m_{i}")
                    
                    if sel_m_comp == "Geral":
                        data_c = aggregate_launch(mcs_comp)
                    else:
                        m_idx = int(sel_m_comp.replace("MC ", "")) - 1
                        data_c = mcs_comp[m_idx]
                        
                    st.markdown("<hr style='margin:12px 0; border-color:var(--border-color)'>", unsafe_allow_html=True)
                    
                    st.markdown(kpi_new_html("Investimento", fmtR(data_c['investimento']), "icon-red", "fa-solid fa-money-bill-wave"), unsafe_allow_html=True)
                    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
                    st.markdown(kpi_new_html("Leads LVP", fmt(data_c['leads']), "icon-blue", "fa-solid fa-users"), unsafe_allow_html=True)
                    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
                    st.markdown(kpi_new_html("CPL", fmtR(data_c['cpl']), "icon-orange", "fa-solid fa-coins"), unsafe_allow_html=True)
                    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
                    st.markdown(kpi_new_html("Novos Espectadores", fmt(data_c['ne']), "icon-purple", "fa-solid fa-eye"), unsafe_allow_html=True)
                    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
                    st.markdown(kpi_new_html("CPNE", fmtR(data_c['cpne']), "icon-orange", "fa-solid fa-tags"), unsafe_allow_html=True)
                    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
                    st.markdown(kpi_new_html("Watchtime", fmt_float(data_c['wt']), "icon-indigo", "fa-solid fa-clock"), unsafe_allow_html=True)
                    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
                    st.markdown(kpi_new_html("Custo por WT", fmtR(data_c['cpwt']), "icon-red", "fa-solid fa-chart-line"), unsafe_allow_html=True)
                else:
                    st.markdown("<br><div style='text-align:center; color:var(--text-secondary); font-size:0.85rem;'>Selecione um lançamento para visualizar os dados.</div>", unsafe_allow_html=True)

# ── RODAPÉ ──────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center;font-size:11px;color:#9ca3af;border-top:1px solid #e2e8f0;padding-top:16px">Grupo Rugido · Gestão de Audiência</div>', unsafe_allow_html=True)
