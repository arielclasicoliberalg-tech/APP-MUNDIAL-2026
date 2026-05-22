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
st.set_page_config(page_title="App del Mundial 2026", layout="wide", page_icon="⚽")
set_background("assets/fondo.png")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LÓGICA DE AUTENTICACIÓN ---
if not st.session_state["authenticated"]:
    st.title("⚽ APP DEL MUNDIAL 2026")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🔑 Iniciar sesión", "📝 Registro", "🔄 Recuperar Contraseña"])

    with tab1: # LOGIN
        st.subheader("Acceder con tu Apodo")
        input_name = st.text_input("Nombre de usuario (Apodo)", key="l_name")
        password = st.text_input("Contraseña", type="password", key="l_pass")
        
        if st.button("Entrar", type="primary"):
            profile = supabase.table("profiles").select("nombre, email_asociado, rol").eq("nombre", input_name).execute()
            if profile.data:
                try:
                    email = profile.data[0]['email_asociado']
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.update({
                        "authenticated": True,
                        "user_id": res.user.id,
                        "nombre_usuario": input_name,
                        "role": profile.data[0].get('rol', 'user')
                    })
                    st.rerun()
                except Exception:
                    st.error("Credenciales incorrectas.")
            else:
                st.error("El apodo no existe.")

    with tab2: # REGISTRO
        st.subheader("Crear nueva cuenta")
        new_name = st.text_input("Nombre de usuario (Apodo)", key="r_name")
        new_email = st.text_input("Correo electrónico", key="r_email")
        new_pass = st.text_input("Contraseña", type="password", key="r_pass")
        
        if st.button("Registrarse"):
            if not new_name or not new_email or not new_pass:
                st.warning("Completa todos los campos.")
            else:
                try:
                    auth = supabase.auth.sign_up({"email": new_email, "password": new_pass})
                    if hasattr(auth, 'user') and auth.user:
                        supabase.table("profiles").upsert({
                            "id": auth.user.id, 
                            "nombre": new_name, 
                            "email_asociado": new_email,
                            "rol": "user"
                        }).execute()
                        st.success("¡Cuenta creada! Revisa tu correo.")
                    else:
                        st.error("No se pudo crear la cuenta.")
                except Exception as e:
                    st.error(f"Error al registrar: {e}")

    with tab3: # RECUPERAR
        st.subheader("Recuperar Contraseña")
        rec_email = st.text_input("Ingresa tu correo registrado", key="rec_email")
        if st.button("Enviar instrucciones"):
            try:
                supabase.auth.reset_password_email(rec_email)
                st.success("Revisa tu correo.")
            except Exception as e:
                st.error(f"Error: {e}")
    st.stop()

# --- ZONA AUTENTICADA ---
with st.sidebar:
    st.write(f"👤 Hola, **{st.session_state.get('nombre_usuario')}**")
    if st.button("🚪 Cerrar sesión"):
        supabase.auth.sign_out()
        st.session_state["authenticated"] = False
        st.rerun()

st.title("⚽ ¡Bienvenido al Mundial 2026!")
st.write("Usa el menú lateral para navegar.")
