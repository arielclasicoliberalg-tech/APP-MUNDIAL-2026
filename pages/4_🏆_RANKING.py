import streamlit as st
import pandas as pd
import altair as alt
from src.database import supabase
import base64

# --- FUNCIÓN PARA EL FONDO ---
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.7)), 
                              url("data:image/png;base64,{b64_encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

set_background("assets/fondo.png")

# --- SEGURIDAD ---
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

# --- DISEÑO VISUAL ---
st.title("🏆 RANKING GENERAL")
st.markdown("---")

# --- REGLAS DE PUNTUACIÓN (VISUALIZACIÓN) ---
with st.expander("ℹ️ Reglas de Puntuación"):
    st.markdown("""
    * **2 pts:** Acierto de marcador exacto (incluye empates).
    * **1 pt:** Acierto de ganador (sin marcador exacto).
    * **1 pt:** Acierto de empate (sin marcador exacto).
    """)

# --- OBTENCIÓN DE DATOS ---
# La vista vw_ranking ya filtra automáticamente 'WHERE activo = true'
try:
    res = supabase.table("vw_ranking").select("*").order("puntos_totales", desc=True).execute()
    data = res.data
except Exception as e:
    st.error(f"Error al cargar el ranking: {e}")
    st.stop()

if not data:
    st.info("Aún no hay puntos registrados. ¡Participa en los próximos partidos!")
else:
    df = pd.DataFrame(data)
    
    # --- SECCIÓN 1: TABLA DE POSICIONES ---
    st.subheader("📊 Tabla de Posiciones")
    
    def obtener_medalla(index):
        if index == 0: return "🥇 1er Lugar"
        if index == 1: return "🥈 2do Lugar"
        if index == 2: return "🥉 3er Lugar"
        return f"{index + 1}º Lugar"

    df_ranking = df.copy()
    # Asegurar que la columna Posición se genere correctamente
    df_ranking.insert(0, "Posición", [obtener_medalla(i) for i in range(len(df))])
    
    # Visualización mejorada con ProgressColumn para ver la brecha de puntos
    st.dataframe(
        df_ranking[['Posición', 'nombre', 'puntos_totales']], 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "nombre": st.column_config.TextColumn("Usuario", width="medium"),
            "puntos_totales": st.column_config.ProgressColumn(
                "Puntos Totales", 
                format="%d pts", 
                min_value=0, 
                max_value=int(df['puntos_totales'].max() + 5) if not df.empty else 10
            )
        }
    )

    # --- SECCIÓN 2: GRÁFICO DE RENDIMIENTO ---
    st.markdown("---")
    st.subheader("📈 Rendimiento de los Participantes")
    
    chart = alt.Chart(df).mark_bar(cornerRadiusTopRight=5, cornerRadiusTopLeft=5).encode(
        x=alt.X('nombre', sort='-y', title='Participante'),
        y=alt.Y('puntos_totales', title='Puntos Acumulados'),
        color=alt.Color('puntos_totales', scale=alt.Scale(scheme='goldgreen')),
        tooltip=['nombre', 'puntos_totales']
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)

# --- SEÑALÉTICA FINAL ---
st.markdown("---")
st.success("¡Mantente atento! Los puntos se calculan automáticamente tras cada resultado oficial.")