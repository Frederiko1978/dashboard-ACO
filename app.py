import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Dashboard ACO - Abastecimiento S&OP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos personalizados
from utils.data_loader import load_data, process_data, validate_columns, load_from_excel
from utils.calculations import calculate_cobertura, calculate_wape, categorize_cobertura
from pages import page_principal, page_estado_coberturas, page_evolucion_futura, page_wape

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .dataframe {
        font-size: 12px;
    }
    h1 {
        color: #6BBE45;
        font-weight: bold;
    }
    h2 {
        color: #2E7D32;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Logo y título
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("### 🌱 ANASAC")
    with col2:
        st.title("Dashboard de Abastecimiento S&OP - ACO")
    
    st.markdown("---")
    
    # --- Funcionalidad de carga de archivo ---
    st.sidebar.header("📂 Cargar Datos")
    uploaded_file = st.sidebar.file_uploader(
        "Sube tu archivo Excel aquí",
        type=['xlsx', 'xls'],
        help="Sube el archivo 'Master ACOL' para analizar los datos. El archivo subido tendrá prioridad sobre el que esté en la carpeta 'data'."
    )
    st.sidebar.markdown("---") # Separador

    df = None
    data_source_message = ""

    # 1. Prioridad: Archivo subido por el usuario
    if uploaded_file is not None:
        try:
            df = load_from_excel(uploaded_file)
            data_source_message = f"Archivo subido: **{uploaded_file.name}**"
        except Exception as e:
            st.error(f"❌ Error al leer el archivo subido: {e}")
            return
    
    # 2. Si no hay archivo subido, buscar en la carpeta 'data'
    else:
        df = load_data() # Usa la función cacheada de data_loader
        if df is not None and not df.empty:
            # Intentar obtener el nombre del archivo local para mostrarlo
            data_path = Path(__file__).parent / "data"
            excel_files = list(data_path.glob("*.xlsx")) + list(data_path.glob("*.xls"))
            if excel_files:
                data_source_message = f"Archivo local: **{excel_files[0].name}**"

    # Si después de ambos métodos no hay datos, mostrar mensaje y salir.
    if df is None or df.empty:
        st.warning("⚠️ No se han cargado datos.")
        st.info("""
        **Bienvenido al Dashboard de Abastecimiento S&OP.**

        Para comenzar, por favor carga el archivo de datos de una de estas dos formas:
        1.  **Usa el panel de la izquierda para subir tu archivo Excel.** Haz clic en "Browse files" para seleccionar tu archivo `Master ACOL...xlsx`.
        2.  O, guarda el archivo en la carpeta `data` del proyecto y recarga esta página.
        """)
        return

    # --- Validación de Columnas ---
    # Antes de procesar, verificar que el archivo tiene las columnas necesarias.
    is_valid, missing_cols = validate_columns(df)
    if not is_valid:
        st.error("❌ El archivo cargado no tiene el formato esperado.")
        st.warning("Faltan las siguientes columnas o grupos de columnas requeridas:")
        
        # Mostrar las columnas faltantes de forma clara
        for col_info in missing_cols:
            st.markdown(f"- {col_info}")
            
        st.info("Por favor, revisa el archivo Excel y asegúrate de que contenga todas las columnas necesarias antes de cargarlo.")
        
        with st.expander("🕵️ Ver columnas detectadas (para depuración)", expanded=True):
            st.write("El sistema detectó estas columnas en tu archivo:", list(df.columns))
            
        return # Detener la ejecución si el archivo no es válido

    # Procesar y mostrar el dashboard
    try:
        # Procesar datos
        df = process_data(df)
        
        # Sidebar con filtros
        st.sidebar.header("🔍 Filtros")
        
        # Filtro de fecha
        if 'Fecha' in df.columns:
            fechas_disponibles = sorted(df['Fecha'].dropna().unique())
            if fechas_disponibles:
                fecha_seleccionada = st.sidebar.multiselect(
                    "Fecha Año/Mes",
                    options=fechas_disponibles,
                    default=fechas_disponibles[-3:] if len(fechas_disponibles) >= 3 else fechas_disponibles
                )
            else:
                fecha_seleccionada = []
        else:
            fecha_seleccionada = []
        
        # Filtro de origen
        if 'Origen' in df.columns:
            origenes = sorted(df['Origen'].dropna().unique())
            origen_seleccionado = st.sidebar.multiselect(
                "Origen",
                options=["Todas"] + list(origenes),
                default=["Todas"]
            )
        else:
            origen_seleccionado = ["Todas"]
        
        # Filtro de material
        if 'Material' in df.columns:
            materiales = sorted(df['Material'].dropna().unique())
            material_seleccionado = st.sidebar.multiselect(
                "Material",
                options=["Todos"] + list(materiales[:50]),  # Limitar para performance
                default=["Todos"]
            )
        else:
            material_seleccionado = ["Todos"]
        
        # Filtro de estado de cobertura
        estado_cob = st.sidebar.selectbox(
            "Estado Cob(D)",
            options=["Todas", "Cob < 45", "Cob < 90", "Cob > 90"]
        )
        
        # Aplicar filtros
        df_filtered = df.copy()
        
        if fecha_seleccionada and 'Fecha' in df.columns:
            df_filtered = df_filtered[df_filtered['Fecha'].isin(fecha_seleccionada)]
        
        if "Todas" not in origen_seleccionado and 'Origen' in df.columns:
            df_filtered = df_filtered[df_filtered['Origen'].isin(origen_seleccionado)]
        
        if "Todos" not in material_seleccionado and 'Material' in df.columns:
            df_filtered = df_filtered[df_filtered['Material'].isin(material_seleccionado)]
        
        # Navegación de páginas
        st.sidebar.markdown("---")
        st.sidebar.header("📄 Navegación")
        
        page = st.sidebar.radio(
            "Selecciona una página:",
            ["📊 Principal", "🎯 Estado de Coberturas", "📈 Evolución Futura", "📉 WAPE (Kg-L)"]
        )
        
        # --- Botón de Exportar a PDF ---
        st.sidebar.markdown("---")
        st.sidebar.header("🖨️ Exportar")
        
        # CSS para impresión (oculta sidebar y ajusta layout)
        st.markdown("""
            <style>
            @media print {
                [data-testid="stSidebar"] { display: none !important; }
                [data-testid="stHeader"] { display: none !important; }
                .stDeployButton { display: none !important; }
                footer { display: none !important; }
                .stButton { display: none !important; }
                
                .block-container {
                    padding-top: 1rem !important;
                    padding-left: 1rem !important;
                    padding-right: 1rem !important;
                    max-width: 100% !important;
                }
                
                /* Evitar que los gráficos se corten entre páginas */
                .js-plotly-plot {
                    break-inside: avoid;
                    page-break-inside: avoid;
                }
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Botón HTML con JavaScript para imprimir
        st.sidebar.markdown("""
            <div style="text-align: center; margin-bottom: 10px;">
                <button onclick="window.print()" style="
                    background-color: #2E7D32; 
                    color: white; 
                    padding: 10px 20px; 
                    border: none; 
                    border-radius: 5px; 
                    cursor: pointer;
                    font-weight: bold;
                    width: 100%;
                    transition: background-color 0.3s;">
                    📄 Guardar como PDF
                </button>
            </div>
            <div style="font-size: 12px; color: gray; text-align: center;">
                Se abrirá el diálogo de impresión. Selecciona "Guardar como PDF".
            </div>
        """, unsafe_allow_html=True)
        
        # Mostrar página seleccionada
        if page == "📊 Principal":
            page_principal.show(df_filtered, estado_cob)
        elif page == "🎯 Estado de Coberturas":
            page_estado_coberturas.show(df_filtered, estado_cob)
        elif page == "📈 Evolución Futura":
            page_evolucion_futura.show(df_filtered, estado_cob)
        elif page == "📉 WAPE (Kg-L)":
            page_wape.show(df_filtered)
        
        # Información del dataset
        st.sidebar.markdown("---")
        st.sidebar.info(f"""
        **Fuente de Datos:**
        {data_source_message if data_source_message else "No se cargaron datos"}
        
        **Datos Filtrados:**
        - Registros: {len(df_filtered):,}
        - Materiales: {df_filtered['Material'].nunique() if 'Material' in df_filtered.columns else 'N/A'}
        - Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """)
        
    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar los datos: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
