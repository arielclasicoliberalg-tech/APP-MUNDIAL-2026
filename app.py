import streamlit as st
import base64
from src.database import supabase

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

        footer {{
            display: none !important;
        }}
        #MainMenu {{
            display: none !important;
        }}

        [data-testid="stSidebarNavLink"] span {{
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            word-break: break-word !important;
        }}
        [data-testid="stSidebarNavLink"] {{
            height: auto !important;
            padding: 8px 12px !important;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"No se encontró la imagen en {image_file}")

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="App del Mundial 2026", 
    layout="wide", 
    page_icon="⚽",
    initial_sidebar_state="auto"
)
set_background("assets/fondo.png")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LÓGICA DE AUTENTICACIÓN ---
if not st.session_state["authenticated"]:
    st.title("⚽ APP DEL MUNDIAL 2026")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 Iniciar sesión", "📝 Registro"])

    with tab1: #
