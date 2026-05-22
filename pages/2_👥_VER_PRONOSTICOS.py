import streamlit as st
import pandas as pd
from src.database import supabase
import base64
from datetime import datetime, timedelta

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

# --- DISEÑO ---
st.title("👥 PRONÓSTICOS DE LA COMUNIDAD")
st.markdown("---")

# --- OBTENCIÓN DE DATOS ---
partidos_data = supabase.table("partidos").select("*").execute().data

if not partidos_data:
    st.info("No hay partidos registrados aún.")
else:
    fechas = sorted(list(set([p['fecha'] for p in partidos_data])))
    st.markdown("""
    <h1 style='font-size:30px; margin-bottom:-15px;'>
    📅 1. Selecciona la fecha
    </h1>
    """, unsafe_allow_html=True)

    fecha_sel = st.selectbox(
    "",
    fechas,
    label_visibility="collapsed"
    )
    
    partidos_dia = [p for p in partidos_data if p['fecha'] == fecha_sel]
    partido_sel = st.selectbox("🏟️ 2. Selecciona el partido", [f"{p['equipo_1']} vs {p['equipo_2']}" for p in partidos_dia])
    partido = next(p for p in partidos_dia if f"{p['equipo_1']} vs {p['equipo_2']}" == partido_sel)

    st.markdown("---")
    st.subheader(f"📊 Pronósticos: {partido['equipo_1']} vs {partido['equipo_2']}")
    
    # Consulta a la base de datos (incluyendo created_at)
    res = supabase.table("pronosticos").select("goles_1, goles_2, created_at, profiles(nombre)").eq("partido_id", partido['id']).execute()
    
    if res.data:
        data = []
        for r in res.data:
            nombre = r['profiles']['nombre'] if r['profiles'] else "Usuario Anónimo"
            
            # --- LÓGICA DE HORA LOCAL (BOLIVIA -4h) ---
            # Parseamos la fecha ISO de la base de datos
            ts = datetime.fromisoformat(r['created_at'].replace('Z', '+00:00'))
            # Ajustamos a la hora de Bolivia
            hora_local = ts - timedelta(hours=4)
            hora_envio = hora_local.strftime("%d/%m %H:%M")
            
            data.append({
                "👤 USUARIO": nombre,
                "⚽ PARTIDO": f"{partido['equipo_1']} vs {partido['equipo_2']}",
                "🥅 APUESTA": f"{r['goles_1']} - {r['goles_2']}",
                "⏰ ENVÍO": hora_envio
            })
        
        df = pd.DataFrame(data)
        # Mostramos la tabla
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Aún no hay apuestas registradas para este partido.")
