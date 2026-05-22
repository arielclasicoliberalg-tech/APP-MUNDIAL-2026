import streamlit as st
from src.database import supabase

st.title("📝 Registro")
email = st.text_input("Correo electrónico")
password = st.text_input("Contraseña", type="password")
nombre = st.text_input("Nombre de usuario")

if st.button("Crear Cuenta"):
    # VERIFICACIÓN DE SEGURIDAD ANTES DE ENVIAR
    if not email or not password or not nombre:
        st.warning("Por favor, completa todos los campos.")
    else:
        try:
            # Registro en Supabase Auth
            res = supabase.auth.sign_up({"email": email, "password": password})
            
            # Verificar si la respuesta contiene un usuario
            if hasattr(res, 'user') and res.user:
                # Upsert en perfiles
                supabase.table("profiles").upsert({
                    "id": res.user.id, 
                    "nombre": nombre, 
                    "rol": "user"
                }).execute()
                st.success("¡Registro exitoso! Confirma tu correo.")
            else:
                st.error("Error: El usuario no pudo ser creado.")
        except Exception as e:
            st.error(f"Error crítico: {e}")