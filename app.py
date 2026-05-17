from supabase import create_client
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Pronósticos Mundial",
    page_icon="⚽",
    layout="wide"
)

EXCEL_FILE = "MUNDIAL.xlsx"

IMAGE_BACKGROUND = "Gemini_Generated_Image_yb9b8yyb9b8yyb9b.png"

SUPABASE_URL = "https://wadioikactpavpspwitz.supabase.co"

SUPABASE_KEY = "TU_SUPABASE_KEY"

ADMIN_PASSWORD = "PIPOCHOCO"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =====================================================
# FUNCION IMAGEN BASE64
# =====================================================

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image(IMAGE_BACKGROUND)

# =====================================================
# ESTILOS
# =====================================================

st.markdown(f"""
<style>

/* =========================
FONDO PRINCIPAL
========================= */

.stApp {{
    background:
        linear-gradient(
            rgba(0,0,0,0.80),
            rgba(0,0,0,0.85)
        ),
        url("data:image/png;base64,{img_base64}");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* =========================
TEXTOS
========================= */

h1,h2,h3,h4,h5,h6,p,span,label,div {{
    color:white !important;
}}

/* =========================
SIDEBAR
========================= */

section[data-testid="stSidebar"] {{
    background: rgba(2,6,23,0.92);
    border-right: 1px solid rgba(255,255,255,0.1);
}}

/* =========================
CARDS
========================= */

.card {{
    background: rgba(255,255,255,0.08);
    border-radius: 25px;
    padding: 25px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 0 25px rgba(0,0,0,0.5);
}}

/* =========================
BOTONES
========================= */

.stButton>button {{
    background: linear-gradient(90deg,#2563eb,#9333ea);
    color: white;
    border: none;
    border-radius: 15px;
    font-size: 18px;
    font-weight: bold;
    padding: 12px 25px;
    transition: 0.3s;
    width: 100%;
}}

.stButton>button:hover {{
    transform: scale(1.03);
    box-shadow: 0 0 20px rgba(147,51,234,0.6);
}}

/* =========================
INPUTS
========================= */

.stNumberInput input {{
    background: rgba(255,255,255,0.95) !important;
    color: black !important;
    font-size: 35px !important;
    font-weight: bold !important;
    text-align: center !important;
    border-radius: 15px !important;
}}

/* =========================
TABLAS
========================= */

[data-testid="stDataFrame"] {{
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 10px;
}}

/* =========================
SELECTBOX
========================= */

.stSelectbox div[data-baseweb="select"] {{
    background-color: rgba(255,255,255,0.08);
    border-radius: 12px;
}}

/* =========================
PLOTLY
========================= */

.js-plotly-plot {{
    border-radius: 20px;
    overflow: hidden;
}}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SONIDO ENTRADA
# =====================================================

st.markdown("""
<audio autoplay>
<source src="https://www.soundjay.com/buttons/sounds/button-09.mp3" type="audio/mpeg">
</audio>
""", unsafe_allow_html=True)

# =====================================================
# CARGAR EXCEL
# =====================================================

@st.cache_data
def cargar_datos():

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

partidos_df, nombres_df = cargar_datos()

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

menu = [
    "📝 LLENAR MIS PRONÓSTICOS",
    "📋 MIS PRONÓSTICOS",
    "🏆 RESULTADOS OFICIALES",
    "📊 TABLA DE PUNTOS"
]

if usuario_actual.upper() == "ARIEL":
    menu.append("🗑️ ADMINISTRAR PRONÓSTICOS")

vista = st.sidebar.radio(
    "Seleccione vista",
    menu
)

# =====================================================
# VISTA 1
# =====================================================

if vista == "📝 LLENAR MIS PRONÓSTICOS":

    st.title("⚽ PRONÓSTICOS MUNDIAL")

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

        validar = supabase.table(
            "Pronosticos"
        ).select("*").eq(
            "nombre",
            usuario_actual
        ).eq(
            "id_partido",
            int(info["NUMERO_PARTIDO"])
        ).execute()

        if len(validar.data) > 0:

            st.error(
                "⚠️ Ya registraste un pronóstico para este partido."
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

            st.success("✅ Pronóstico guardado.")

    st.markdown("</div>", unsafe_allow_html=True)

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

    data = supabase.table(
        "Resultados_Oficiales"
    ).select("*").execute()

    resultados = pd.DataFrame(data.data)

    if not resultados.empty:

        resultados = resultados.merge(
            partidos_df,
            left_on="id_partido",
            right_on="NUMERO_PARTIDO"
        )

        resultados["PARTIDO"] = (
            resultados["EQUIPO_1"]
            + " vs "
            + resultados["EQUIPO_2"]
        )

        resultados["RESULTADO"] = (
            resultados["goles_1"].astype(str)
            + " - "
            + resultados["goles_2"].astype(str)
        )

        mostrar = resultados[
            [
                "PARTIDO",
                "RESULTADO",
                "timestamp_registro"
            ]
        ]

        mostrar.columns = [
            "PARTIDO",
            "RESULTADO OFICIAL",
            "FECHA REGISTRO"
        ]

        st.dataframe(
            mostrar,
            use_container_width=True
        )

    else:

        st.info(
            "Aún no existen resultados oficiales registrados."
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
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
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

# =====================================================
# ADMINISTRAR PRONÓSTICOS
# =====================================================

elif vista == "🗑️ ADMINISTRAR PRONÓSTICOS":

    st.title("🗑️ ADMINISTRAR PRONÓSTICOS")

    password_admin = st.text_input(
        "Ingrese contraseña de administrador",
        type="password"
    )

    if password_admin == ADMIN_PASSWORD:

        data = supabase.table(
            "Pronosticos"
        ).select("*").execute()

        df = pd.DataFrame(data.data)

        if not df.empty:

            df = df.merge(
                partidos_df,
                left_on="id_partido",
                right_on="NUMERO_PARTIDO"
            )

            df["PARTIDO"] = (
                df["EQUIPO_1"]
                + " vs "
                + df["EQUIPO_2"]
            )

            df["PRONOSTICO"] = (
                df["goles_1"].astype(str)
                + " - "
                + df["goles_2"].astype(str)
            )

            mostrar = df[
                [
                    "id",
                    "nombre",
                    "PARTIDO",
                    "PRONOSTICO",
                    "timestamp_registro"
                ]
            ]

            mostrar.columns = [
                "ID",
                "USUARIO",
                "PARTIDO",
                "PRONÓSTICO",
                "FECHA REGISTRO"
            ]

            st.dataframe(
                mostrar,
                use_container_width=True
            )

            ids = mostrar["ID"].tolist()

            eliminar_id = st.selectbox(
                "Seleccione ID a eliminar",
                ids
            )

            if st.button("❌ ELIMINAR PRONÓSTICO"):

                supabase.table(
                    "Pronosticos"
                ).delete().eq(
                    "id",
                    int(eliminar_id)
                ).execute()

                st.success(
                    "✅ Pronóstico eliminado correctamente."
                )

                st.rerun()

        else:

            st.info(
                "No existen pronósticos registrados."
            )

    elif password_admin != "":

        st.error(
            "❌ Contraseña incorrecta."
        )