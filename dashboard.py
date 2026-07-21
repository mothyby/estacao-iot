import os
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# --- Configuração da Página ---
st.set_page_config(
    page_title="Yby Tech — Gestão & Confiabilidade IoT V2",
    page_icon="🌱",
    layout="wide"
)

DB_PATH = os.environ.get("DB_PATH", "estacao_climatica.db")

# Procura o arquivo de logo em assets/ ou na raiz
LOGO_PATH = None
for caminho in [os.path.join("assets", "logo.jpg"), os.path.join("assets", "logo.png"), "logo.jpg", "logo.png"]:
    if os.path.exists(caminho):
        LOGO_PATH = caminho
        break


@st.cache_data(ttl=3)
def carregar_dados_coleta():
    """Carrega e normaliza os dados da tabela 'coleta_evento' ou 'leitura'."""
    conn = sqlite3.connect(DB_PATH)
    try:
        # Tenta a tabela V2 primeiro
        df = pd.read_sql_query("SELECT * FROM coleta_evento ORDER BY id ASC", conn)
    except Exception:
        df = pd.DataFrame()

    # Fallback para tabela antiga caso a V2 esteja vazia
    if df.empty:
        try:
            df = pd.read_sql_query("SELECT * FROM leitura ORDER BY id ASC", conn)
        except Exception:
            df = pd.DataFrame()

    conn.close()

    if not df.empty:
        # 1. Normalização rigorosa da coluna de Data/Hora
        coluna_tempo_encontrada = None
        for col in ["timestamp_iso", "timestamp", "data", "created_at"]:
            if col in df.columns:
                coluna_tempo_encontrada = col
                break
        
        if coluna_tempo_encontrada:
            df.rename(columns={coluna_tempo_encontrada: "timestamp"}, inplace=True)
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        else:
            # Fallback de emergência se nenhuma coluna temporal for achada
            df["timestamp"] = pd.Series(pd.date_range(start="2026-01-01", periods=len(df), freq="min"))

        # 2. Normalização da coluna de Umidade
        if "umidade" not in df.columns:
            for col in df.columns:
                if col.startswith("umi") or col.startswith("hum"):
                    df.rename(columns={col: "umidade"}, inplace=True)
                    break

        # 3. Garantia de colunas V2 caso venha da tabela legada
        if "duracao_execucao_ms" not in df.columns:
            df["duracao_execucao_ms"] = 0.0
        if "status" not in df.columns:
            df["status"] = "OK"
        if "http_code" not in df.columns:
            df["http_code"] = 200
        if "erro" not in df.columns:
            df["erro"] = None

    return df


# --- Cabeçalho Executivo Yby Tech ---
col_logo, col_titulo = st.columns([1, 5], vertical_alignment="center")

with col_logo:
    if LOGO_PATH:
        st.image(LOGO_PATH, width=130)
    else:
        st.markdown("## 🌱 **Yby Tech**")

with col_titulo:
    st.title("Yby Tech — Soluções de Automação & Confiabilidade IoT")
    st.caption("Estação Meteorológica V2 | Monitoramento em Tempo Real & Análise de SLAs de Processo")

st.divider()

# --- Botão de Atualização Manual ---
col_btn, _ = st.columns([1, 5])
with col_btn:
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()

df = carregar_dados_coleta()

if df.empty or "timestamp" not in df.columns:
    st.warning("⚠️ Nenhuma leitura encontrada no banco de dados (`estacao_climatica.db`). Verifique se a coleta está ativa.")
    st.stop()

# --- Sidebar (Menu Lateral) ---
with st.sidebar:
    if LOGO_PATH:
        st.image(LOGO_PATH)
    st.markdown("<h2 style='text-align: center;'>Yby Tech</h2>", unsafe_allow_html=True)
    st.caption("<p style='text-align: center;'>Engenharia de Automação & Dados</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.header("⚙️ Filtros Operacionais")
    
    # Remoção de NaT caso exista algum timestamp corrompido
    df_valido_tempo = df.dropna(subset=["timestamp"])
    
    if df_valido_tempo.empty:
        st.error("Não foi possível processar os registros de data/hora do banco.")
        st.stop()

    data_min = df_valido_tempo["timestamp"].min().to_pydatetime()
    data_max = df_valido_tempo["timestamp"].max().to_pydatetime()

    if data_min == data_max:
        intervalo = (data_min, data_max)
        st.info("Apenas 1 ciclo de amostragem registrado.")
    else:
        intervalo = st.slider(
            "Período de Análise",
            min_value=data_min,
            max_value=data_max,
            value=(data_min, data_max),
            format="DD/MM/YY HH:mm",
        )

# Filtragem por período selecionado
df_filtrado = df[(df["timestamp"] >= intervalo[0]) & (df["timestamp"] <= intervalo[1])].copy()

# Leituras físicas válidas para análise do processo
df_validos = df_filtrado[
    (df_filtrado["status"] == "OK") & 
    (df_filtrado["umidade"].between(0, 100)) & 
    (df_filtrado["temperatura"].between(-40, 80))
]

# --- Abas do Dashboard ---
aba_processo, aba_confiabilidade = st.tabs(["📊 Monitoramento do Processo", "⚙️ Confiabilidade do Gateway (SLA)"])

# ==========================================
# ABA 1: MONITORAMENTO DO PROCESSO
# ==========================================
with aba_processo:
    if not df_validos.empty:
        ultima = df_validos.iloc[-1]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ Temperatura Atual", f"{ultima['temperatura']:.1f} °C")
        col2.metric("💧 Umidade Atual", f"{ultima['umidade']:.1f} %")
        col3.metric("🕒 Último Ciclo Válido", ultima["timestamp"].strftime("%H:%M:%S"))
        col4.metric("📊 Total de Amostras Válidas", f"{len(df_validos)}")

        st.divider()

        # Gráfico Temporal de Variáveis Ambientais
        fig_processo = go.Figure()
        fig_processo.add_trace(go.Scatter(
            x=df_validos["timestamp"], y=df_validos["temperatura"],
            name="Temperatura (°C)", line=dict(color="#2ecc71", width=2), yaxis="y1"
        ))
        fig_processo.add_trace(go.Scatter(
            x=df_validos["timestamp"], y=df_validos["umidade"],
            name="Umidade (%)", line=dict(color="#3498db", width=2), yaxis="y2"
        ))

        fig_processo.update_layout(
            title="Série Temporal de Variáveis Ambientais",
            xaxis=dict(title="Data/Hora"),
            yaxis=dict(title="Temperatura (°C)", side="left", color="#2ecc71"),
            yaxis2=dict(title="Umidade (%)", side="right", overlaying="y", color="#3498db"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            height=400,
        )
        st.plotly_chart(fig_processo)

        col_est1, col_est2 = st.columns(2)
        with col_est1:
            st.subheader("Estatísticas de Temperatura (°C)")
            st.dataframe(df_validos["temperatura"].describe().to_frame(name="Métrica"))
        with col_est2:
            st.subheader("Estatísticas de Umidade (%)")
            st.dataframe(df_validos["umidade"].describe().to_frame(name="Métrica"))

    else:
        st.warning("Nenhum dado ambiental válido encontrado no período selecionado.")

# ==========================================
# ABA 2: CONFIABILIDADE & INFRAESTRUTURA
# ==========================================
with aba_confiabilidade:
    total_ciclos = len(df_filtrado)
    ciclos_sucesso = len(df_filtrado[df_filtrado["status"] == "OK"])
    taxa_disponibilidade = (ciclos_sucesso / total_ciclos * 100) if total_ciclos > 0 else 0.0
    latencia_media = df_filtrado["duracao_execucao_ms"].mean() if total_ciclos > 0 else 0.0

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    col_kpi1.metric("🎯 Disponibilidade do Gateway", f"{taxa_disponibilidade:.2f} %")
    col_kpi2.metric("⚡ Latência Média de Coleta", f"{latencia_media:.1f} ms")
    col_kpi3.metric("🔄 Total de Requisições", f"{total_ciclos}")
    col_kpi4.metric("❌ Falhas Gravadas", f"{total_ciclos - ciclos_sucesso}")

    st.divider()

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("⚡ Desempenho de Latência da Rede (ms)")
        fig_latencia = px.line(
            df_filtrado, 
            x="timestamp", 
            y="duracao_execucao_ms",
            title="Tempo de Resposta HTTP/JSON (ESP8266 → Gateway)",
            labels={"duracao_execucao_ms": "Latência (ms)", "timestamp": "Data/Hora"},
            color_discrete_sequence=["#f39c12"]
        )
        fig_latencia.update_layout(height=350)
        st.plotly_chart(fig_latencia)

    with col_graf2:
        st.subheader("🎯 Ocorrência de Status Operacionais")
        status_counts = df_filtrado["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Quantidade"]
        fig_status = px.pie(
            status_counts, 
            names="Status", 
            values="Quantidade",
            title="Distribuição das Respostas do Gateway",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_status.update_layout(height=350)
        st.plotly_chart(fig_status)

    with st.expander("🔍 Inspecionar Eventos e Erros Registrados"):
        cols_exibir = [c for c in ["id", "timestamp", "status", "http_code", "duracao_execucao_ms", "erro", "temperatura", "umidade"] if c in df_filtrado.columns]
        st.dataframe(
            df_filtrado.sort_values("timestamp", ascending=False)[cols_exibir],
            hide_index=True,
        )

st.caption(f"© Yby Tech — Soluções Industriais | Banco de Dados: `{DB_PATH}`")
