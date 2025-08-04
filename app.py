try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Streamlit no está instalado. Puedes instalarlo con: pip install streamlit"
    )

import pandas as pd

st.set_page_config(page_title="Eco-Pilot Bettermin", layout="wide")

st.title("🧠 ECO-PILOT - Simulador Beta de Relaves")

# Cargar datos
@st.cache_data
def load_data():
    try:
        return pd.read_csv("data/relaves.csv")
    except FileNotFoundError:
        st.error("No se encontró el archivo data/relaves.csv. Por favor, verifica la ruta o sube el archivo.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Menú desplegable
    relave = st.selectbox("Selecciona un relave:", df["Nombre del Relave"].unique())
    selected = df[df["Nombre del Relave"] == relave].iloc[0]

    # Mostrar datos base
    st.subheader("📋 Características del Relave")
    st.write(selected[["Región", "Tonelaje (t)", "Au (g/t)", "Cu (%)", "Ag (g/t)", "% Recuperación Global"]])

    # Cálculos
    au_recovered = selected["Tonelaje (t)"] * selected["Au (g/t)"] * selected["% Recuperación Global"]
    cu_recovered = selected["Tonelaje (t)"] * selected["Cu (%)"] * 10 * selected["% Recuperación Global"]
    ag_recovered = selected["Tonelaje (t)"] * selected["Ag (g/t)"] * selected["% Recuperación Global"]

    valor_au = au_recovered * selected["Precio Au (USD/g)"]
    valor_cu = cu_recovered * selected["Precio Cu (USD/kg)"]
    valor_ag = ag_recovered * selected["Precio Ag (USD/g)"]

    valor_total = valor_au + valor_cu + valor_ag

    # Mostrar resultados
    st.subheader("💰 Resultados Estimados")
    st.metric("Oro Recuperado (g)", f"{au_recovered:,.0f}")
    st.metric("Cobre Recuperado (kg)", f"{cu_recovered:,.0f}")
    st.metric("Plata Recuperada (g)", f"{ag_recovered:,.0f}")
    st.metric("Valor Total Estimado (USD)", f"${valor_total:,.0f}")

    # Footer
    st.caption("Desarrollado por Claudio Torrejón - Bettermin 2025")
else:
    st.warning("Carga o crea tu archivo relaves.csv para comenzar la simulación.")
