import streamlit as st
from src.database import supabase

st.title("🔑 Recuperar Contraseña")

# --- DETECTAR SI VIENE DEL LINK DEL CORREO ---
params = st.query_params

if "type" in params and params["type"] == "recovery":
    st.subheader("🔐 Escribe tu nueva contraseña")
    st.info("Ingresa la nueva contraseña para tu cuenta.")
    
    nueva_pass = st.text_input("Nueva contraseña", type="password", key="np1")
    confirmar_pass = st.text_input("Confirmar contraseña", type="password", key="np2")
    
    if st.button("Guardar nueva contraseña", type="primary"):
        if not nueva_pass or not confirmar_pass:
            st.warning("Completa ambos campos.")
        elif nueva_pass != confirmar_pass:
            st.error("Las contraseñas no coinciden.")
        elif len(nueva_pass) < 6:
            st.error("Mínimo 6 caracteres.")
        else:
            try:
                supabase.auth.update_user({"password": nueva_pass})
                st.success("✅ ¡Contraseña actualizada! Ya puedes iniciar sesión.")
                st.query_params.clear()
            except Exception as e:
                st.error(f"Error al actualizar: {e}")

else:
    # --- FORMULARIO NORMAL PARA PEDIR CORREO ---
    st.subheader("Ingresa tu correo para recuperar tu cuenta")
    email = st.text_input("Correo electrónico registrado")
    
    if st.button("Enviar correo de recuperación", type="primary"):
        if not email:
            st.warning("Ingresa tu correo.")
        else:
            try:
                supabase.auth.reset_password_email(email)
                st.success("✅ Revisa tu correo y haz clic en el link que te enviamos.")
            except Exception as e:
                st.error(f"Error: {e}")