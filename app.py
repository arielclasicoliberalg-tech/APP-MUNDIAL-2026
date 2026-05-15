from supabase import create_client
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Pronósticos Mundial",
    page_icon="⚽",
    layout="wide"
)

EXCEL_FILE = "MUNDIAL.xlsx"

# =====================================================
# SUPABASE
# =====================================================

SUPABASE_URL = "https://wadioikactpavpspwitz.supabase.co"

SUPABASE_KEY = "TU_ANON_PUBLIC_KEY"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

ADMIN_PASSWORD = "PIPOCHOCO"

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #020617, #071226);
    overflow: hidden;
}

body::before {
    content: "⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽";
    position: fixed;
    top: 8%;
    left: -60%;
    font-size: 90px;
    opacity: 0.07;
    animation: mover1 30s linear infinite;
    z-index: 0;
    white-space: nowrap;
}

body::after {
    content: "⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽";
    position: fixed;
    bottom: 10%;
    right: -60%;
    font-size: 110px;
    opacity: 0.05;
    animation: mover2 35s linear infinite;
    z-index: 0;
    white-space: nowrap;
}

@keyframes mover1 {
    0% {
        transform: translateX(-10%);
    }
    100% {
        transform: translateX(220%);
    }
}

@keyframes mover2 {
    0% {
        transform: translateX(10%);
    }
    100% {
        transform: translateX(-220%);
    }
}

.block-container {
    position: relative;
    z-index: 2;
}

section[data-testid="stSidebar"] {
    background: rgba(2,6,23,0.95);
}

h1, h2, h3, h4, h5, h6,
p, label, span {
    color: white !important;
}

.card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}

.stTextInput input {
    background-color: white !important;
    color: black !important;
}

.stNumberInput input {
    background-color: white !important;
    color: black !important;
    font-size: 35px !important;
    font-weight: bold !important;
    text-align: center !important;
}

.stButton>button {
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    color: white;
    border-radius: 14px;
    border: none;
    padding: 12px 24px;
    font-size: 18px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SONIDO ENTRADA
# =====================================================

st.markdown(
    """
    <audio autoplay>
        <source src="https://www.soundjay.com/buttons/sounds/button-09.mp3" type="audio/mpeg">
    </audio>
    """,
    unsafe_allow_html=True
)

# =====================================================
# CARGAR EXCEL
# =====================================================

@st.cache_data
def load_data():

    partidos = pd.read_excel(
        EXCEL_FILE,
        sheet_name="PARTIDOS"
    )

    nombres = pd.read_excel(
        EXCEL_FILE,
        sheet_name="NOMBRES"
    )

    partidos["FECHA"] = pd.to_datetime(
        partidos["FECHA"]
    ).dt.date

    return partidos, nombres


partidos_df, nombres_df = load_data()

# =====================================================
# LOGIN
# =====================================================

st.sidebar.title("👤 USUARIO")

usuario_actual = st.sidebar.selectbox(
    "Seleccione usuario",
    nombres_df["NOMBRE"].tolist()
)

# =====================================================
# FUNCIONES
# =====================================================

def obtener_partidos(fecha):

    df = partidos_df[
        partidos_df["FECHA"] == fecha
    ].copy()

    df["PARTIDO"] = (
        df["EQUIPO_1"]
        + " vs "
        + df["EQUIPO_2"]
    )

    return df


def calcular_puntos(pg1, pg2, rg1, rg2):

    if pg1 == rg1 and pg2 == rg2:
        return 2

    pron = pg1 - pg2
    real = rg1 - rg2

    if pron == 0 and real == 0:
        return 1

    if (pron > 0 and real > 0) or \
       (pron < 0 and real < 0):
        return 1

    return 0

# =====================================================
# MENÚ
# =====================================================

opciones_menu = [
    "📝 LLENAR MIS PRONÓSTICOS",
    "📋 MIS PRONÓSTICOS",
    "🏆 RESULTADOS OFICIALES",
    "📊 TABLA DE PUNTOS"
]

if usuario_actual.upper() == "ARIEL":

    opciones_menu.append(
        "🗑️ ADMINISTRAR PRONÓSTICOS"
    )

vista = st.sidebar.radio(
    "Seleccione vista",
    opciones_menu
)

# =====================================================
# VISTA 1
# =====================================================

if vista == "📝 LLENAR MIS PRONÓSTICOS":

    st.title("📝 LLENAR MIS PRONÓSTICOS")

    fechas = sorted(
        partidos_df["FECHA"].unique()
    )

    fecha = st.selectbox(
        "FECHA",
        fechas
    )

    partidos_fecha = obtener_partidos(fecha)

    partido = st.selectbox(
        "PARTIDO",
        partidos_fecha["PARTIDO"].tolist()
    )

    info = partidos_fecha[
        partidos_fecha["PARTIDO"] == partido
    ].iloc[0]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.write(f"⏰ Hora: {info['HORA']}")
    st.write(f"🏆 Grupo: {info['GRUPO']}")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"<h1 style='text-align:center'>{info['EQUIPO_1']}</h1>",
            unsafe_allow_html=True
        )

        goles1 = st.number_input(
            "",
            min_value=0,
            step=1,
            key="g1"
        )

    with col2:

        st.markdown(
            f"<h1 style='text-align:center'>{info['EQUIPO_2']}</h1>",
            unsafe_allow_html=True
        )

        goles2 = st.number_input(
            "",
            min_value=0,
            step=1,
            key="g2"
        )

    if st.button("💾 GUARDAR PRONÓSTICO"):

        validacion = supabase.table(
            "Pronosticos"
        ).select("*").eq(
            "nombre",
            usuario_actual
        ).eq(
            "id_partido",
            int(info["NUMERO_PARTIDO"])
        ).execute()

        if len(validacion.data) > 0:

            st.error(
                "⚠️ Ya registraste un pronóstico."
            )

        else:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            supabase.table(
                "Pronosticos"
            ).insert({
                "nombre": usuario_actual,
                "id_partido": int(info["NUMERO_PARTIDO"]),
                "goles_1": goles1,
                "goles_2": goles2,
                "timestamp_registro": timestamp
            }).execute()

            st.success(
                "✅ Pronóstico guardado."
            )

            st.markdown(
                """
                <audio autoplay>
                    <source src="https://www.soundjay.com/human/sounds/applause-8.mp3" type="audio/mpeg">
                </audio>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <style>

                .pelotas {
                    position: fixed;
                    top: -100px;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: 9999;
                }

                .pelota {
                    position: absolute;
                    font-size: 50px;
                    animation: caer 4s linear forwards;
                }

                @keyframes caer {
                    0% {
                        transform: translateY(-100px) rotate(0deg);
                        opacity: 1;
                    }

                    100% {
                        transform: translateY(120vh) rotate(720deg);
                        opacity: 0;
                    }
                }

                </style>

                <div class="pelotas">
                    <div class="pelota" style="left:5%; animation-delay:0s;">⚽</div>
                    <div class="pelota" style="left:15%; animation-delay:0.2s;">⚽</div>
                    <div class="pelota" style="left:25%; animation-delay:0.4s;">⚽</div>
                    <div class="pelota" style="left:35%; animation-delay:0.6s;">⚽</div>
                    <div class="pelota" style="left:45%; animation-delay:0.8s;">⚽</div>
                    <div class="pelota" style="left:55%; animation-delay:1s;">⚽</div>
                    <div class="pelota" style="left:65%; animation-delay:1.2s;">⚽</div>
                    <div class="pelota" style="left:75%; animation-delay:1.4s;">⚽</div>
                    <div class="pelota" style="left:85%; animation-delay:1.6s;">⚽</div>
                    <div class="pelota" style="left:95%; animation-delay:1.8s;">⚽</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# VISTA 2
# =====================================================

elif vista == "📋 MIS PRONÓSTICOS":

    st.title("📋 MIS PRONÓSTICOS")

    fechas = sorted(
        partidos_df["FECHA"].unique()
    )

    fecha = st.selectbox(
        "FECHA",
        fechas
    )

    partidos_fecha = obtener_partidos(fecha)

    partido = st.selectbox(
        "PARTIDO",
        partidos_fecha["PARTIDO"].tolist()
    )

    info = partidos_fecha[
        partidos_fecha["PARTIDO"] == partido
    ].iloc[0]

    data = supabase.table(
        "Pronosticos"
    ).select("*").eq(
        "id_partido",
        int(info["NUMERO_PARTIDO"])
    ).execute()

    df = pd.DataFrame(data.data)

    if not df.empty:

        df["PARTIDO"] = partido

        df["PRONÓSTICO"] = (
            df["goles_1"].astype(str)
            + " - "
            + df["goles_2"].astype(str)
        )

        mostrar = df[
            [
                "nombre",
                "PARTIDO",
                "PRONÓSTICO",
                "timestamp_registro"
            ]
        ]

        mostrar.columns = [
            "NOMBRE",
            "PARTIDO",
            "PRONÓSTICO",
            "FECHA REGISTRO"
        ]

        st.dataframe(
            mostrar,
            use_container_width=True
        )

# =====================================================
# VISTA 3
# =====================================================

elif vista == "🏆 RESULTADOS OFICIALES":

    st.title("🏆 RESULTADOS OFICIALES")

    if usuario_actual.upper() == "ARIEL":

        password = st.text_input(
            "Ingrese contraseña",
            type="password"
        )

        if password == ADMIN_PASSWORD:

            fechas = sorted(
                partidos_df["FECHA"].unique()
            )

            fecha = st.selectbox(
                "FECHA",
                fechas
            )

            partidos_fecha = obtener_partidos(fecha)

            partido = st.selectbox(
                "PARTIDO",
                partidos_fecha["PARTIDO"].tolist()
            )

            info = partidos_fecha[
                partidos_fecha["PARTIDO"] == partido
            ].iloc[0]

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    f"<h1 style='text-align:center'>{info['EQUIPO_1']}</h1>",
                    unsafe_allow_html=True
                )

                g1 = st.number_input(
                    "",
                    min_value=0,
                    step=1,
                    key="of1"
                )

            with col2:

                st.markdown(
                    f"<h1 style='text-align:center'>{info['EQUIPO_2']}</h1>",
                    unsafe_allow_html=True
                )

                g2 = st.number_input(
                    "",
                    min_value=0,
                    step=1,
                    key="of2"
                )

            if st.button("💾 GUARDAR RESULTADO"):

                supabase.table(
                    "Resultados_Oficiales"
                ).delete().eq(
                    "id_partido",
                    int(info["NUMERO_PARTIDO"])
                ).execute()

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                supabase.table(
                    "Resultados_Oficiales"
                ).insert({
                    "id_partido": int(info["NUMERO_PARTIDO"]),
                    "goles_1": g1,
                    "goles_2": g2,
                    "timestamp_registro": timestamp
                }).execute()

                st.success(
                    "✅ Resultado guardado."
                )

# =====================================================
# VISTA 4
# =====================================================

elif vista == "📊 TABLA DE PUNTOS":

    st.title("📊 TABLA DE PUNTOS")

    pron = pd.DataFrame(
        supabase.table(
            "Pronosticos"
        ).select("*").execute().data
    )

    real = pd.DataFrame(
        supabase.table(
            "Resultados_Oficiales"
        ).select("*").execute().data
    )

    if not pron.empty and not real.empty:

        merged = pron.merge(
            real,
            on="id_partido",
            suffixes=("_pron", "_real")
        )

        merged = merged.merge(
            partidos_df,
            left_on="id_partido",
            right_on="NUMERO_PARTIDO"
        )

        puntos = []

        for _, row in merged.iterrows():

            fecha_partido = datetime.combine(
                row["FECHA"],
                pd.to_datetime(
                    str(row["HORA"])
                ).time()
            )

            fecha_registro = datetime.strptime(
                row["timestamp_registro_pron"],
                "%Y-%m-%d %H:%M:%S"
            )

            if fecha_registro > fecha_partido:
                pts = 0
            else:
                pts = calcular_puntos(
                    row["goles_1_pron"],
                    row["goles_2_pron"],
                    row["goles_1_real"],
                    row["goles_2_real"]
                )

            puntos.append(pts)

        merged["PUNTOS"] = puntos

        tabla = merged.groupby(
            "nombre"
        )["PUNTOS"].sum().reset_index()

        tabla = tabla.sort_values(
            by="PUNTOS",
            ascending=False
        )

        fig = px.bar(
            tabla,
            x="PUNTOS",
            y="nombre",
            orientation="h",
            text="PUNTOS",
            color="nombre"
        )

        fig.update_layout(
            paper_bgcolor="#071226",
            plot_bgcolor="#071226",
            font_color="white",
            height=600,
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            tabla,
            use_container_width=True
        )