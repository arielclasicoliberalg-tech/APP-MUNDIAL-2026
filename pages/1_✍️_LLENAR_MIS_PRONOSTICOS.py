import streamlit as st
from src.database import supabase
from src.utils import es_fecha_valida
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pronósticos", layout="centered")

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

if "user_id" not in st.session_state:
    st.error("⚠️ Sesión no encontrada.")
    st.stop()

# --- DISEÑO ---
st.title("⚽ MUNDIAL 2026")
st.markdown("### ✍️ LLENAR MIS PRONÓSTICOS")

# --- OBTENCIÓN DE DATOS ---
try:
    # Solo traemos partidos 'pendiente'
    partidos_data = supabase.table("partidos").select("*").eq("estado", "pendiente").execute().data
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    st.stop()

if not partidos_data:
    st.warning("No hay partidos pendientes disponibles.")
else:
    # 1. Selección de Fecha
    fechas = sorted(list(set([p['fecha'] for p in partidos_data])))
    st.markdown("""
<style>
label[data-testid="stWidgetLabel"] p {
    font-size: 28px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)
    fecha_sel = st.selectbox("📅 1. Selecciona la fecha", fechas)
    
    # 2. Filtrado y Selección de Partido
    partidos_dia = [p for p in partidos_data if p['fecha'] == fecha_sel]
    partido_sel = st.selectbox("🏟️ 2. Selecciona el partido", [f"{p['equipo_1']} vs {p['equipo_2']}" for p in partidos_dia])
    partido = next(p for p in partidos_dia if f"{p['equipo_1']} vs {p['equipo_2']}" == partido_sel)

    col1, col2 = st.columns(2)
    col1.metric("⏰ Hora", partido['hora'])
    col2.metric("👥 Grupo", partido['grupo'])
    
    st.markdown("---")

    # --- LÓGICA DE PRONÓSTICO ---
    if not es_fecha_valida(partido['fecha'], partido['hora']):
        st.error("🚫 Este partido ya comenzó o finalizó.")
    else:
        # Verificamos si existe un pronóstico ACTIVO
        existe = supabase.table("pronosticos")\
            .select("id")\
            .eq("user_id", st.session_state["user_id"])\
            .eq("partido_id", partido['id'])\
            .eq("activo", True)\
            .execute().data
        
        if existe:
            st.warning("✅ Ya tienes un pronóstico activo para este partido.")
            if st.button("🔄 Refrescar"):
                st.rerun()
        else:
            st.markdown("""
<style>
div[data-testid="stNumberInput"] label p {
    font-size: 40px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)
            with st.form(key=f"form_{partido['id']}"):
                c1, c2, c3 = st.columns([1, 0.5, 1])
                g1 = c1.number_input(f"Goles {partido['equipo_1']}", min_value=0, max_value=20, step=1)
                c2.markdown("<br><h2 style='text-align: center;'>vs</h2>", unsafe_allow_html=True)
                g2 = c3.number_input(f"Goles {partido['equipo_2']}", min_value=0, max_value=20, step=1)
                
                submit = st.form_submit_button("💾 Guardar mi Pronóstico", use_container_width=True)
                
                if submit:
                    try:
                        data_upsert = {
                            "user_id": st.session_state["user_id"], 
                            "partido_id": partido['id'], 
                            "goles_1": int(g1), 
                            "goles_2": int(g2),
                            "activo": True 
                        }
                        # Upsert para permitir re-llenar automáticamente
                        supabase.table("pronosticos").upsert(
                            data_upsert, 
                            on_conflict="user_id, partido_id"
                        ).execute()
                        
                        st.success(f"⚽ ¡Pronóstico registrado para {partido['equipo_1']} vs {partido['equipo_2']}!")
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Error al guardar en la base de datos: {e}")

st.sidebar.markdown("---")
st.sidebar.info("Puedes editar tus pronósticos hasta antes del inicio del partido.")
