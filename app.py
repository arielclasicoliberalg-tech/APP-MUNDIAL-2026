import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Pronósticos Mundial",
    page_icon="⚽",
    layout="wide"
)

EXCEL_FILE = "MUNDIAL.xlsx"
DB_FILE = "mundial.db"
ADMIN_PASSWORD = "PIPOCHOCO"

# =====================================================
# CSS PREMIUM
# =====================================================

st.markdown("""
<style>

/* =====================================================
FONDO
===================================================== */

.stApp {
    background: linear-gradient(135deg, #020617, #071226);
    overflow: hidden;
}

/* =====================================================
PELOTAS ANIMADAS
===================================================== */

body::before {
    content: "⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽";
    position: fixed;
    top: 10%;
    left: -40%;
    font-size: 80px;
    opacity: 0.06;
    animation: mover1 40s linear infinite;
    z-index: 0;
    white-space: nowrap;
}

body::after {
    content: "⚽ ⚽ ⚽ ⚽ ⚽ ⚽";
    position: fixed;
    bottom: 15%;
    right: -40%;
    font-size: 100px;
    opacity: 0.05;
    animation: mover2 50s linear infinite;
    z-index: 0;
    white-space: nowrap;
}

@keyframes mover1 {
    0% {
        transform: translateX(-20%);
    }
    100% {
        transform: translateX(180%);
    }
}

@keyframes mover2 {
    0% {
        transform: translateX(20%);
    }
    100% {
        transform: translateX(-180%);
    }
}

/* =====================================================
CONTENIDO
===================================================== */

.block-container {
    position: relative;
    z-index: 2;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {
    background: rgba(2,6,23,0.95);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* =====================================================
TEXTOS
===================================================== */

h1, h2, h3, h4, h5, h6,
p, label, span {
    color: white !important;
}

/* =====================================================
CARDS
===================================================== */

.card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}

/* =====================================================
INPUTS
===================================================== */

.stSelectbox div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: white !important;
}

.stTextInput input {
    background-color: white !important;
    color: black !important;
    border-radius: 12px !important;
}

.stNumberInput input {
    background-color: white !important;
    color: black !important;
    font-size: 30px !important;
    font-weight: bold !important;
    text-align: center !important;
    border-radius: 14px !important;
}

/* =====================================================
BOTONES
===================================================== */

.stButton>button {
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    color: white;
    border-radius: 14px;
    border: none;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: bold;
    transition: 0.3s;
    box-shadow: 0 5px 15px rgba(37,99,235,0.4);
}

.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg,#7c3aed,#2563eb);
}

/* =====================================================
TABLAS
===================================================== */

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.04);
    border-radius: 15px;
}

/* =====================================================
FESTEJO
===================================================== */

.festejo {
    position: fixed;
    top: -50px;
    font-size: 35px;
    animation: caer 5s linear infinite;
    z-index: 9999;
}

.f1 { left: 5%; animation-delay: 0s; }
.f2 { left: 15%; animation-delay: 1s; }
.f3 { left: 25%; animation-delay: 2s; }
.f4 { left: 35%; animation-delay: 0.5s; }
.f5 { left: 45%; animation-delay: 1.5s; }
.f6 { left: 55%; animation-delay: 2.5s; }
.f7 { left: 65%; animation-delay: 0.7s; }
.f8 { left: 75%; animation-delay: 1.7s; }
.f9 { left: 85%; animation-delay: 2.7s; }

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
""", unsafe_allow_html=True)

# =====================================================
# BASE DE DATOS
# =====================================================

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pronosticos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        id_partido INTEGER,
        goles_1 INTEGER,
        goles_2 INTEGER,
        timestamp_registro TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Resultados_Oficiales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_partido INTEGER,
        goles_1 INTEGER,
        goles_2 INTEGER,
        timestamp_registro TEXT
    )
    """)

    conn.commit()
    conn.close()


if not os.path.exists(DB_FILE):
    init_database()

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
# LOGIN SIMPLE
# =====================================================

st.sidebar.title("👤 IDENTIFICACIÓN")

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

# SOLO ARIEL VE ADMINISTRACIÓN
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

    st.subheader(f"Usuario: {usuario_actual}")

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

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM Pronosticos
        WHERE nombre = ?
        AND id_partido = ?
        """, (
            usuario_actual,
            int(info["NUMERO_PARTIDO"])
        ))

        existe = cursor.fetchone()

        if existe:

            st.error(
                "⚠️ Ya registraste un pronóstico para este partido."
            )

        else:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            cursor.execute("""
            INSERT INTO Pronosticos
            (
                nombre,
                id_partido,
                goles_1,
                goles_2,
                timestamp_registro
            )
            VALUES (?, ?, ?, ?, ?)
            """, (
                usuario_actual,
                int(info["NUMERO_PARTIDO"]),
                goles1,
                goles2,
                timestamp
            ))

            conn.commit()

            st.success(
                "✅ Pronóstico guardado correctamente."
            )

            st.balloons()

            st.markdown("""
            <div class="festejo f1">⚽</div>
            <div class="festejo f2">⚽</div>
            <div class="festejo f3">⚽</div>
            <div class="festejo f4">⚽</div>
            <div class="festejo f5">⚽</div>
            <div class="festejo f6">⚽</div>
            <div class="festejo f7">⚽</div>
            <div class="festejo f8">⚽</div>
            <div class="festejo f9">⚽</div>
            """, unsafe_allow_html=True)

        conn.close()

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

    conn = get_connection()

    query = f"""
    SELECT
        nombre,
        goles_1 || ' - ' || goles_2 as pronostico,
        timestamp_registro
    FROM Pronosticos
    WHERE id_partido = {int(info["NUMERO_PARTIDO"])}
    ORDER BY timestamp_registro
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    df["PARTIDO"] = partido

    df = df[
        [
            "nombre",
            "PARTIDO",
            "pronostico",
            "timestamp_registro"
        ]
    ]

    df.columns = [
        "NOMBRE",
        "PARTIDO",
        "PRONÓSTICO",
        "FECHA REGISTRO"
    ]

    st.dataframe(
        df,
        use_container_width=True
    )

# =====================================================
# VISTA 3
# =====================================================

elif vista == "🏆 RESULTADOS OFICIALES":

    st.title("🏆 RESULTADOS OFICIALES")

    conn = get_connection()

    # SOLO ARIEL VE PANEL ADMIN
    if usuario_actual.upper() == "ARIEL":

        st.subheader("🔐 Panel Administrador")

        password = st.text_input(
            "Ingrese contraseña",
            type="password"
        )

        autorizado = password == ADMIN_PASSWORD

        if autorizado:

            st.success("✅ Acceso autorizado.")

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

                cursor = conn.cursor()

                cursor.execute("""
                DELETE FROM Resultados_Oficiales
                WHERE id_partido = ?
                """, (int(info["NUMERO_PARTIDO"]),))

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                cursor.execute("""
                INSERT INTO Resultados_Oficiales
                (
                    id_partido,
                    goles_1,
                    goles_2,
                    timestamp_registro
                )
                VALUES (?, ?, ?, ?)
                """, (
                    int(info["NUMERO_PARTIDO"]),
                    g1,
                    g2,
                    timestamp
                ))

                conn.commit()

                st.success("✅ Resultado guardado.")

    # TABLA PARA TODOS

    st.subheader("📋 Resultados Registrados")

    resultados = pd.read_sql_query("""
    SELECT *
    FROM Resultados_Oficiales
    ORDER BY id_partido
    """, conn)

    conn.close()

    if not resultados.empty:

        resultados = resultados.merge(
            partidos_df[
                [
                    "NUMERO_PARTIDO",
                    "EQUIPO_1",
                    "EQUIPO_2"
                ]
            ],
            left_on="id_partido",
            right_on="NUMERO_PARTIDO",
            how="left"
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

        st.info("Aún no existen resultados oficiales.")

# =====================================================
# VISTA 4
# =====================================================

elif vista == "📊 TABLA DE PUNTOS":

    st.title("📊 TABLA DE PUNTOS")

    conn = get_connection()

    pron = pd.read_sql_query(
        "SELECT * FROM Pronosticos",
        conn
    )

    real = pd.read_sql_query(
        "SELECT * FROM Resultados_Oficiales",
        conn
    )

    conn.close()

    if pron.empty or real.empty:

        st.warning("No existen datos suficientes.")
        st.stop()

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

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    tabla.columns = [
        "USUARIO",
        "PUNTOS"
    ]

    st.dataframe(
        tabla,
        use_container_width=True
    )

# =====================================================
# VISTA 5 SOLO ARIEL
# =====================================================

elif vista == "🗑️ ADMINISTRAR PRONÓSTICOS":

    st.title("🗑️ ADMINISTRAR PRONÓSTICOS")

    password = st.text_input(
        "Ingrese contraseña administrador",
        type="password"
    )

    if password == ADMIN_PASSWORD:

        conn = get_connection()

        pronosticos = pd.read_sql_query("""
        SELECT *
        FROM Pronosticos
        ORDER BY timestamp_registro DESC
        """, conn)

        if pronosticos.empty:

            st.warning("No existen pronósticos.")

        else:

            pronosticos = pronosticos.merge(
                partidos_df[
                    [
                        "NUMERO_PARTIDO",
                        "EQUIPO_1",
                        "EQUIPO_2"
                    ]
                ],
                left_on="id_partido",
                right_on="NUMERO_PARTIDO",
                how="left"
            )

            pronosticos["PARTIDO"] = (
                pronosticos["EQUIPO_1"]
                + " vs "
                + pronosticos["EQUIPO_2"]
            )

            pronosticos["PRONOSTICO"] = (
                pronosticos["goles_1"].astype(str)
                + " - "
                + pronosticos["goles_2"].astype(str)
            )

            mostrar = pronosticos[
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

            id_eliminar = st.number_input(
                "Ingrese ID a eliminar",
                min_value=1,
                step=1
            )

            if st.button("🗑️ ELIMINAR PRONÓSTICO"):

                cursor = conn.cursor()

                cursor.execute("""
                DELETE FROM Pronosticos
                WHERE id = ?
                """, (id_eliminar,))

                conn.commit()

                st.success(
                    "✅ Pronóstico eliminado correctamente."
                )

        conn.close()

    else:
        st.info("Ingrese contraseña administrador.")