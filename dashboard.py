import os
import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Estação Climática IoT", page_icon="🌡️", layout="wide")

DB_PATH = os.environ.get("DB_PATH", "estacao_climatica.db")


@st.cache_data(ttl=5)
def carregar_dados():
    conn = sqlite3.connect(DB_PATH)
    # Filtro de sanidade direto na query: qualquer leitura fora da faixa
    # fisicamente plausivel do DHT11 (0-100% e -40 a 80C) e lixo de boot/
    # reset do ESP8266/Mega, nunca uma leitura real do sensor.
    df = pd.read_sql_query(
        """SELECT * FROM leitura
           WHERE humidade BETWEEN 0 AND 100
             AND temperatura BETWEEN -40 AND 80
           ORDER BY id""",
        conn,
    )
    conn.close()
    df["data"] = pd.to_datetime(df["data"])
    return df


st.title("🌡️ Estação Meteorológica IoT — Dashboard")
st.caption("DHT11 → Arduino Mega → ESP8266 (Wi-Fi/HTTP) → SQLite")

if st.button("🔄 Atualizar agora"):
    st.cache_data.clear()

df = carregar_dados()

# --- Aviso de leituras descartadas (transparencia) ---
conn_check = sqlite3.connect(DB_PATH)
total_bruto = conn_check.execute("SELECT COUNT(*) FROM leitura").fetchone()[0]
conn_check.close()
descartadas = total_bruto - len(df)
if descartadas > 0:
    st.sidebar.warning(f"⚠️ {descartadas} leituras fora da faixa plausível (0-100% / -40 a 80°C) foram descartadas automaticamente do gráfico.")

if df.empty:
    st.warning("Nenhuma leitura encontrada no banco de dados. Confirme se o coletor (salvar_dados.py) já rodou.")
    st.stop()

# --- Filtro: exclui leituras de teste, se a coluna existir ---
if "teste" in df.columns:
    somente_reais = st.sidebar.checkbox("Excluir leituras de teste", value=True)
    if somente_reais:
        df = df[df["teste"] == 0]

if df.empty:
    st.warning("Nenhuma leitura real encontrada (todas foram marcadas como teste).")
    st.stop()

# --- Filtro de período ---
st.sidebar.header("Filtros")
data_min = df["data"].min().to_pydatetime()
data_max = df["data"].max().to_pydatetime()

if data_min == data_max:
    intervalo = (data_min, data_max)
    st.sidebar.info("Apenas uma leitura disponível até o momento.")
else:
    intervalo = st.sidebar.slider(
        "Período",
        min_value=data_min,
        max_value=data_max,
        value=(data_min, data_max),
        format="DD/MM/YY HH:mm",
    )

df_filtrado = df[(df["data"] >= intervalo[0]) & (df["data"] <= intervalo[1])]

# --- Metricas do topo ---
ultima = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌡️ Temperatura atual", f"{ultima['temperatura']:.1f} °C")
col2.metric("💧 Umidade atual", f"{ultima['humidade']:.1f} %")
col3.metric("🕒 Última leitura", ultima["data"].strftime("%d/%m %H:%M:%S"))
col4.metric("📊 Leituras no período", f"{len(df_filtrado)}")

st.divider()

# --- Grafico de serie temporal (eixo duplo) ---
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_filtrado["data"], y=df_filtrado["temperatura"],
    name="Temperatura (°C)", line=dict(color="#e74c3c"), yaxis="y1"
))
fig.add_trace(go.Scatter(
    x=df_filtrado["data"], y=df_filtrado["humidade"],
    name="Umidade (%)", line=dict(color="#3498db"), yaxis="y2"
))

fig.update_layout(
    title="Temperatura e Umidade ao Longo do Tempo",
    xaxis=dict(title="Data/Hora"),
    yaxis=dict(title="Temperatura (°C)", side="left", color="#e74c3c"),
    yaxis2=dict(title="Umidade (%)", side="right", overlaying="y", color="#3498db"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified",
    height=450,
)
st.plotly_chart(fig, use_container_width=True)

# --- Estatisticas do periodo ---
st.subheader("Estatísticas do período selecionado")
col1, col2 = st.columns(2)
with col1:
    st.write("**Temperatura (°C)**")
    st.dataframe(df_filtrado["temperatura"].describe().to_frame(name="valor"), use_container_width=True)
with col2:
    st.write("**Umidade (%)**")
    st.dataframe(df_filtrado["humidade"].describe().to_frame(name="valor"), use_container_width=True)

# --- Media por dia ---
st.subheader("Médias diárias")
df_diario = (
    df_filtrado.assign(dia=df_filtrado["data"].dt.date)
    .groupby("dia")[["temperatura", "humidade"]]
    .mean()
    .round(1)
    .reset_index()
)
st.bar_chart(df_diario.set_index("dia"))

# --- Tabela de dados brutos ---
with st.expander("Ver dados brutos"):
    st.dataframe(
        df_filtrado.sort_values("data", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

st.caption(f"Fonte: `{DB_PATH}` — {len(df)} leituras totais no banco. Cache atualiza a cada 5s.")
