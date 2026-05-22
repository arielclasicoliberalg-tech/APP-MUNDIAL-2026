import streamlit as st
from src.database import supabase

st.title("🔑 Recuperar Contraseña")
email = st.text_input("Ingresa tu correo registrado")

if st.button("Enviar correo de recuperación"):
    try:
        supabase.auth.reset_password_email(email)
        st.success("Revisa tu correo para cambiar tu contraseña.")
    except Exception as e:
        st.error(f"Error: {e}")