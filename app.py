# eco-pilot/app.py
try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Streamlit no está instalado. Puedes instalarlo con: pip install streamlit"
    )

import pandas as pd
import os

st.set_page_config(page_title="Eco-Pilot Bettermin", layout="wide")

st.title("🧠 ECO-PILOT - Simulador Beta de Relaves")

# Cargar datos
@st.cache_data

def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "data", "relaves.csv")
    if not os.path.exists(file_path):
        st.error(f"No se encontró el archivo en: {file_path}")
        return pd.DataFrame()
    return pd.read_csv(file_path)

df = load_data()

if not df.empty:
    relave = st.selectbox("Selecciona un relave:", df["Nombre del Relave"].unique())
    selected = df[df["Nombre del Relave"] == relave].iloc[0]

    st.subheader("📋 Características del Relave")
    st.write(selected[["Región", "Tonelaje (t)", "Au (g/t)", "Cu (%)", "Ag (g/t)", "% Recuperación Global"]])

    # MÓDULO 2: Preconcentración
    st.subheader("🧲 Módulo 2: Preconcentración TOMRA")
    st.markdown("Ingresa manualmente los parámetros estimados de recuperación en la etapa seca:")

    rec_au = st.number_input("Recuperación Au TOMRA (%)", min_value=0.0, max_value=100.0, value=80.0) / 100
    rec_cu = st.number_input("Recuperación Cu TOMRA (%)", min_value=0.0, max_value=100.0, value=75.0) / 100
    rec_ag = st.number_input("Recuperación Ag TOMRA (%)", min_value=0.0, max_value=100.0, value=70.0) / 100

    rechazo_tonelaje = st.number_input("Reducción de Tonelaje (%)", min_value=0.0, max_value=100.0, value=65.0)

    # Contaminantes y sulfuros (simulados por ahora)
    st.markdown("**Parámetros críticos del preconcentrado para BIOX:**")
    sulfuros = st.number_input("% Sulfuros Refractarios", min_value=0.0, max_value=100.0, value=12.0)
    arsenico = st.number_input("Arsénico (ppm)", min_value=0.0, value=3500.0)
    mercurio = st.number_input("Mercurio (ppm)", min_value=0.0, value=100.0)

    # Cálculos preconcentrado
    tonelaje_feed = selected["Tonelaje (t)"]
    tonelaje_concentrado = tonelaje_feed * (1 - rechazo_tonelaje / 100)

    au_recuperado = tonelaje_feed * selected["Au (g/t)"] * rec_au
    cu_recuperado = tonelaje_feed * selected["Cu (%)"] * 10 * rec_cu
    ag_recuperado = tonelaje_feed * selected["Ag (g/t)"] * rec_ag

    st.subheader("📦 Resultados del Preconcentrado")
    st.metric("Tonelaje Preconcentrado (t)", f"{tonelaje_concentrado:,.0f}")
    st.metric("Au Recuperado (g)", f"{au_recuperado:,.0f}")
    st.metric("Cu Recuperado (kg)", f"{cu_recuperado:,.0f}")
    st.metric("Ag Recuperado (g)", f"{ag_recuperado:,.0f}")

    # Simulación Económica
    valor_au = au_recuperado * selected["Precio Au (USD/g)"]
    valor_cu = cu_recuperado * selected["Precio Cu (USD/kg)"]
    valor_ag = ag_recuperado * selected["Precio Ag (USD/g)"]
    valor_total = valor_au + valor_cu + valor_ag

    st.subheader("💰 Valor Económico Estimado")
    st.metric("Total Estimado (USD)", f"${valor_total:,.0f}")

    # MÓDULO 3: BIOX
    st.subheader("🧬 Módulo 3: Biooxidación (BIOX)")
    st.markdown("Ingrese los parámetros operacionales para simular el rendimiento del consorcio bacteriano:")

    ph = st.number_input("pH de operación", min_value=0.5, max_value=3.0, value=1.6, step=0.1)
    temp = st.number_input("Temperatura (°C)", min_value=30.0, max_value=50.0, value=42.0, step=0.5)
    tiempo = st.number_input("Tiempo de residencia (días)", min_value=1.0, max_value=10.0, value=5.0)
    redox = st.number_input("Eh Redox (mV)", min_value=300, max_value=700, value=450)
    do = st.number_input("Oxígeno disuelto (mg/L)", min_value=2.0, max_value=10.0, value=7.0)
    fe3 = st.number_input("Fe(III) disponible (g/L)", min_value=5.0, max_value=30.0, value=15.0)
    solidos = st.number_input("% sólidos en pulpa", min_value=5.0, max_value=25.0, value=18.0)

    st.markdown("**Resultado Simulado:**")
    eficiencia_biox = min(95, max(60, 70 + (temp - 40) + (redox - 400)/10 - (ph - 1.6)*10))
    st.metric("Eficiencia estimada BIOX (%)", f"{eficiencia_biox:.1f}%")
    oro_final = au_recuperado * (eficiencia_biox / 100)
    st.metric("Au Liberado en BIOX (g)", f"{oro_final:,.0f}")

    # MÓDULO 4: Lixiviación y Producción Final
    st.subheader("⚗️ Módulo 4: Lixiviación y Producción Final")
    st.markdown("Estimación de recuperación metalúrgica final y proyección de ventas:")

    lixiviacion_ef = st.slider("Eficiencia de Lixiviación (%)", min_value=50, max_value=100, value=92)
    electroobtencion_ef = st.slider("Eficiencia Electroobtención Cu (%)", min_value=80, max_value=100, value=95)

    oro_dore = oro_final * (lixiviacion_ef / 100)
    cobre_catodos = cu_recuperado * (eficiencia_biox / 100) * (electroobtencion_ef / 100)

    valor_dore = oro_dore * selected["Precio Au (USD/g)"]
    valor_catodos = cobre_catodos * selected["Precio Cu (USD/kg)"]
    valor_final_total = valor_dore + valor_catodos

    st.metric("Dore Producido (g Au)", f"{oro_dore:,.0f}")
    st.metric("Cátodos Producidos (kg Cu)", f"{cobre_catodos:,.0f}")
    st.metric("Valor Total Estimado (USD)", f"${valor_final_total:,.0f}")

    st.caption("Desarrollado por Claudio Torrejón - Bettermin 2025")
else:
    st.warning("Carga o crea tu archivo relaves.csv para comenzar la simulación.")
