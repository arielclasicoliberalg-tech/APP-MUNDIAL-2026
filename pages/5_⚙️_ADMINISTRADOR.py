import streamlit as st
from src.database import supabase, supabase_admin
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

tab1, tab2, tab3, tab4 = st.tabs(["🗑️ Gestión de Pronósticos", "⚽ Cargar Resultados", "🔑 Resetear Contraseña", "🔄 Resetear Todo"])

# --- TAB 1: GESTIÓN DE PRONÓSTICOS ---
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

# --- TAB 3: RESETEAR CONTRASEÑA ---
with tab3:
    st.subheader("🔑 Cambiar contraseña de un usuario")
    st.info("Busca al usuario por su apodo y asígnale una contraseña temporal.")

    try:
        usuarios = supabase.table("profiles").select("id, nombre, email_asociado").execute().data
    except Exception as e:
        st.error("Error al cargar usuarios.")
        usuarios = []

    if usuarios:
        nombres = [u['nombre'] for u in usuarios]
        apodo_sel = st.selectbox("Selecciona el usuario", nombres, key="reset_user")
        nueva_clave = st.text_input("Nueva contraseña temporal", type="password", key="reset_pass")

        if st.button("🔑 Cambiar contraseña", type="primary"):
            if not nueva_clave:
                st.warning("Escribe una contraseña.")
            elif len(nueva_clave) < 6:
                st.error("Mínimo 6 caracteres.")
            else:
                try:
                    user_id = next(u['id'] for u in usuarios if u['nombre'] == apodo_sel)
                    supabase_admin.auth.admin.update_user_by_id(user_id, {"password": nueva_clave})
                    st.success(f"✅ Contraseña de **{apodo_sel}** actualizada.")
                except Exception as e:
                    st.error(f"Error al cambiar contraseña: {e}")
    else:
        st.info("No hay usuarios registrados.")

# --- TAB 4: RESETEAR TODO ---
with tab4:
    st.subheader("🔄 Panel de reseteo")
    st.markdown("---")

    # --- RESETEAR PUNTOS ---
    st.subheader("1️⃣ Resetear puntos")
    st.warning("⚠️ Pondrá en 0 los puntos de todos los pronósticos.")
    conf1 = st.checkbox("Confirmo resetear todos los puntos a 0", key="conf_puntos")
    if st.button("🔄 Resetear puntos", type="primary", key="btn_puntos"):
        if not conf1:
            st.error("Marca la casilla de confirmación.")
        else:
            try:
                supabase.table("pronosticos").update({"puntos": 0}).neq("id", "00000000-0000-0000-0000-000000000000").execute()
                st.success("✅ Todos los puntos reseteados a 0.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")

    # --- BORRAR PRONÓSTICOS ---
    st.subheader("2️⃣ Borrar todos los pronósticos")
    st.warning("⚠️ Borrará TODOS los pronósticos de todos los usuarios.")
    conf2 = st.checkbox("Confirmo borrar todos los pronósticos", key="conf_pronosticos")
    if st.button("🗑️ Borrar pronósticos", type="primary", key="btn_pronosticos"):
        if not conf2:
            st.error("Marca la casilla de confirmación.")
        else:
            try:
                supabase.table("pronosticos").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                st.success("✅ Todos los pronósticos borrados.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")

    # --- BORRAR RESULTADOS ---
    st.subheader("3️⃣ Borrar resultados de partidos")
    st.warning("⚠️ Pondrá todos los partidos en estado 'pendiente' y borrará los goles.")
    conf3 = st.checkbox("Confirmo borrar todos los resultados", key="conf_resultados")
    if st.button("🗑️ Borrar resultados", type="primary", key="btn_resultados"):
        if not conf3:
            st.error("Marca la casilla de confirmación.")
        else:
            try:
                supabase.table("partidos").update({
                    "goles_1": None,
                    "goles_2": None,
                    "estado": "pendiente"
                }).neq("id", "00000000-0000-0000-0000-000000000000").execute()
                st.success("✅ Todos los resultados borrados. Partidos vueltos a pendiente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
