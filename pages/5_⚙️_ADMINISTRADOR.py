import streamlit as st
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
if st.session_state.get("role") != "admin":
    st.error("⚠️ Acceso denegado: Solo administradores.")
    st.stop()

st.title("⚙️ PANEL DE ADMINISTRADOR")
st.markdown("---")

tab1, tab2 = st.tabs(["🗑️ Gestión de Pronósticos", "⚽ Cargar Resultados"])

# --- TAB 1: GESTIÓN DE PRONÓSTICOS (ELIMINACIÓN LÓGICA) ---
with tab1:
    st.subheader("Gestionar Pronósticos")
    try:
        partidos_res = supabase.table("partidos").select("id, fecha, equipo_1, equipo_2").execute().data
    except Exception as e:
        st.error("Error al cargar partidos.")
        partidos_res = []
    
    if partidos_res:
        fecha_sel = st.selectbox("1. Selecciona Fecha", sorted(list(set([p['fecha'] for p in partidos_res]))), key="adm_f1")
        partidos_dia = [p for p in partidos_res if p['fecha'] == fecha_sel]
        partido_sel = st.selectbox("2. Selecciona Partido", [f"{p['equipo_1']} vs {p['equipo_2']}" for p in partidos_dia], key="adm_p1")
        partido_id = next(p['id'] for p in partidos_dia if f"{p['equipo_1']} vs {p['equipo_2']}" == partido_sel)
        
        # Obtenemos solo los activos
        res = supabase.table("pronosticos").select("id, goles_1, goles_2, profiles(nombre)").eq("partido_id", partido_id).eq("activo", True).execute()
        
        if res.data:
            st.write("Selecciona los pronósticos para marcar como eliminados:")
            to_delete = []
            for p in res.data:
                nombre = p['profiles']['nombre'] if p['profiles'] else "Anon"
                if st.checkbox(f"{nombre} | Apuesta: {p['goles_1']}-{p['goles_2']}", key=f"check_{p['id']}"):
                    to_delete.append(p['id'])
            
            if st.button("🗑️ Marcar como eliminados", type="primary"):
                for p_id in to_delete:
                    supabase.table("pronosticos").update({"activo": False}).eq("id", p_id).execute()
                st.success(f"Se procesaron {len(to_delete)} eliminaciones.")
                st.rerun()
        else:
            st.info("No hay pronósticos activos para este partido.")

# --- TAB 2: CARGAR RESULTADOS ---
with tab2:
    st.subheader("Finalizar Partidos")
    partidos_pendientes = supabase.table("partidos").select("*").eq("estado", "pendiente").execute().data
    
    if partidos_pendientes:
        fecha_p = st.selectbox("1. Selecciona Fecha", sorted(list(set([p['fecha'] for p in partidos_pendientes]))), key="adm_f2")
        partidos_dia_p = [p for p in partidos_pendientes if p['fecha'] == fecha_p]
        partido_sel_p = st.selectbox("2. Selecciona Partido", [f"{p['equipo_1']} vs {p['equipo_2']}" for p in partidos_dia_p], key="adm_p2")
        partido_obj = next(p for p in partidos_dia_p if f"{p['equipo_1']} vs {p['equipo_2']}" == partido_sel_p)
        
        c1, c2 = st.columns(2)
        g1 = c1.number_input(f"Goles {partido_obj['equipo_1']}", min_value=0, step=1, key="g1_final")
        g2 = c2.number_input(f"Goles {partido_obj['equipo_2']}", min_value=0, step=1, key="g2_final")
        
        if st.button("Guardar Resultado y Finalizar", type="primary"):
            try:
                # Al actualizar a 'finalizado', el Trigger en Supabase calculará los puntos automáticamente
                supabase.table("partidos").update({
                    "goles_1": g1, 
                    "goles_2": g2, 
                    "estado": "finalizado"
                }).eq("id", partido_obj['id']).execute()
                
                st.success(f"Resultado guardado: {partido_obj['equipo_1']} {g1} - {g2} {partido_obj['equipo_2']}.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar el partido: {e}")
    else:
        st.success("¡Todos los partidos han sido procesados!")