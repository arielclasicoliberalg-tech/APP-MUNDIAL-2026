import streamlit as st
import pandas as pd
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
st.title("📊 RESULTADOS OFICIALES")
st.markdown("---")

# --- OBTENCIÓN DE DATOS ---
partidos_data = supabase.table("partidos").select("*").eq("estado", "finalizado").execute().data

if not partidos_data:
    st.markdown("""
    <div style='text-align:center; padding:40px;'>
        <p style='font-size:60px;'>⚽</p>
        <p style='font-size:24px; color:gray;'>Aún no hay resultados disponibles.</p>
        <p style='font-size:16px; color:gray;'>Los resultados aparecerán aquí cuando finalicen los partidos.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # --- SELECCIÓN DE FECHA ---
    fechas = sorted(list(set([p['fecha'] for p in partidos_data])))
    with st.container(border=True):
        st.write("#### 📅 1. Selecciona la fecha")
        fecha_sel = st.selectbox("Fecha", fechas, label_visibility="collapsed")

    # --- SELECCIÓN DE PARTIDO ---
    partidos_dia = [p for p in partidos_data if p['fecha'] == fecha_sel]
    with st.container(border=True):
        st.write("#### 🏟️ 2. Selecciona el partido")
        partido_sel = st.selectbox("Partido",
                                   [f"{p['equipo_1']} vs {p['equipo_2']}" for p in partidos_dia],
                                   label_visibility="collapsed")
        partido = next(p for p in partidos_dia if f"{p['equipo_1']} vs {p['equipo_2']}" == partido_sel)

    # --- RESULTADO FINAL ---
    st.markdown("---")
    st.write("#### ✅ Resultado Final")

    col1, col2, col3 = st.columns([1, 0.3, 1])

    with col1:
        st.markdown(f"""
        <div style='text-align:center;'>
            <p style='font-size:30px; font-weight:bold;'>{partido['equipo_1']}</p>
            <p style='font-size:90px; margin-top:-20px;'>{partido['goles_1']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='display:flex; justify-content:center; align-items:center; height:150px;'>
            <p style='font-size:80px; font-weight:bold; margin:0;'>-</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style='text-align:center;'>
            <p style='font-size:30px; font-weight:bold;'>{partido['equipo_2']}</p>
            <p style='font-size:90px; margin-top:-20px;'>{partido['goles_2']}</p>
        </div>
        """, unsafe_allow_html=True)

st.caption("Los resultados son validados y actualizados por la administración.")
