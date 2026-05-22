import streamlit as st
from supabase import create_client

# Inicializar cliente usando los secretos de Streamlit
supabase = create_client(
    st.secrets["SUPABASE_URL"], 
    st.secrets["SUPABASE_KEY"]
)

def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        # Buscar el rol del usuario en la tabla profiles
        profile = supabase.table('profiles').select('rol, nombre').eq('id', res.user.id).execute()
        
        st.session_state["user_id"] = res.user.id
        st.session_state["user_name"] = profile.data[0]['nombre']
        st.session_state["role"] = profile.data[0]['rol']
        st.session_state["authenticated"] = True
        return True
    except Exception as e:
        return False

def reset_password(email):
    try:
        supabase.auth.reset_password_email(email)
        return True
    except:
        return False