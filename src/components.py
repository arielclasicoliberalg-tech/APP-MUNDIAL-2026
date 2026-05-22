import streamlit as st

def mostrar_header():
    st.markdown("### 📊 Agencia de Datos - Gestión Deportiva")
    st.divider()

def estilo_boton_apuesta():
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #007BFF;
            color: white;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)