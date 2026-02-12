import pandas as pd
import os
from pathlib import Path
import streamlit as st

from .calculations import categorize_cobertura


# --- Definición de columnas requeridas ---
# Se define un mapa para permitir nombres alternativos en el archivo Excel.
# La clave es un nombre descriptivo, el valor es una lista de posibles nombres de columna.
REQUIRED_COLUMNS_MAP = {
    "Material": ["Material", "Materiales", "SKU", "Código", "Codigo", "Código Material", "Codigo Material", 
                 "CODIGO SAP", "Codigo SAP", "Producto", "PRODUCTO"],
    "Fecha/Mes": ["Fecha", "Mes", "Periodo", "Date", "Month"],
    "Forecast": ["FCST", "F (MKL)", "Forecast", "Presupuesto", "Ppto", "F"],
    "Inventario": ["Inv Kg-L", "Inventario", "Inv (MKL)", "Stock", "Inv", "Inv.", "Existencia"],
    "Despachos": ["Despachos KL", "Desp (MKL)", "Despachos", "Venta", "Venta Real", "Desp", "Salidas"]
}

def validate_columns(df):
    """
    Valida que el DataFrame contenga al menos una de las columnas para cada grupo requerido.
    Retorna (True, []) si es válido, o (False, lista_de_faltantes) si no lo es.
    NOTA: Si detecta formato pivoteado (fechas como columnas), retorna True ya que será transformado.
    """
    if df is None or df.empty:
        return False, ["El archivo está vacío o no se pudo leer."]

    # Limpiar los nombres de las columnas del DataFrame para una comparación robusta
    df_cols = set(str(c).strip().lower() for c in df.columns)
    
    # Detectar si es formato pivoteado (fechas como columnas)
    date_patterns = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                     'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
                     'january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november', 'december']
    
    has_date_columns = any(any(pattern in col for pattern in date_patterns) for col in df_cols)
    has_material_column = any(name.lower() in df_cols for name in REQUIRED_COLUMNS_MAP["Material"])
    
    # Si tiene columna de material y fechas como columnas, es formato pivoteado válido
    if has_material_column and has_date_columns:
        return True, []  # Será transformado después

    missing_descriptions = []
    for display_name, possible_names in REQUIRED_COLUMNS_MAP.items():
        # Verificar si al menos uno de los nombres posibles existe en las columnas del df
        if not any(name.lower() in df_cols for name in possible_names):
            missing_descriptions.append(f"**{display_name}**: no se encontró ninguna de las siguientes columnas -> `{', '.join(possible_names)}`")

    return (False, missing_descriptions) if missing_descriptions else (True, [])

def _find_header_row(df_preview, keywords=None):
    """
    Busca la fila que contiene ciertas palabras clave para usar como header.
    Retorna el índice de la fila.
    """
    if keywords is None:
        keywords = ['material', 'codigo', 'sku', 'producto']
    
    best_row = 0
    max_score = 0
    
    for i, row in df_preview.iterrows():
        row_str = " ".join([str(x).lower() for x in row.values if pd.notna(x)])
        score = sum(1 for k in keywords if k in row_str)
        if score > max_score:
            max_score = score
            best_row = i
            
    # Si encontramos una fila con buenas coincidencias, retornamos esa.
    # Si no, asumimos 0 si hay alguna coincidencia débil, o si no hay nada.
    return best_row if max_score > 0 else 0

def load_from_excel(file_source, sheet_name=None):
    """
    Versión mejorada que intenta cargar múltiples hojas y consolidar la información
    para generar un dataset completo con Forecast, Inventario y Despachos.
    """
    try:
        # Asegurar puntero al inicio si es buffer
        if hasattr(file_source, 'seek'):
            file_source.seek(0)
            
        xl = pd.ExcelFile(file_source)
        sheet_names = xl.sheet_names
        
        # --- Estrategia de Carga Multi-Hoja ---
        
        # 1. Cargar Forecast (Prioridad: 'Fcst Actual')
        df_fcst = pd.DataFrame()
        fcst_sheet = next((s for s in sheet_names if 'Fcst Actual' in s or 'Forecast' in s), None)
        
        if fcst_sheet:
            st.info(f"Cargando Forecast desde hoja: {fcst_sheet}...")
            # Leer header
            preview = pd.read_excel(xl, sheet_name=fcst_sheet, header=None, nrows=20)
            header_row = _find_header_row(preview, ['codigo', 'producto', 'enero', 'febrero'])
            df_raw = pd.read_excel(xl, sheet_name=fcst_sheet, header=header_row)
            
            # Unpivot
            df_fcst = unpivot_date_columns(df_raw, value_column_name='FCST')
        
        # 2. Cargar Inventario (Prioridad: 'StockACOL')
        df_inv = pd.DataFrame()
        stock_sheet = next((s for s in sheet_names if 'StockACOL' in s or 'Stock' in s), None)
        
        if stock_sheet:
            st.info(f"Cargando Inventario desde hoja: {stock_sheet}...")
            preview = pd.read_excel(xl, sheet_name=stock_sheet, header=None, nrows=20)
            header_row = _find_header_row(preview, ['material', 'libre', 'bloqueado'])
            df_raw_inv = pd.read_excel(xl, sheet_name=stock_sheet, header=header_row)
            
            # Normalizar columnas
            cols_map = {c.lower(): c for c in df_raw_inv.columns}
            mat_col = next((c for c in df_raw_inv.columns if 'material' in str(c).lower() and 'nombre' not in str(c).lower()), None)
            
            if mat_col:
                # Calcular total inventario (sumar columnas numéricas relevantes)
                inv_cols = [c for c in df_raw_inv.columns if any(k in str(c).lower() for k in ['libre', 'bloqueado', 'transito', 'calidad'])]
                if not inv_cols: # Si no hay detalle, buscar columna total
                    inv_cols = [c for c in df_raw_inv.columns if 'total' in str(c).lower() or 'cantidad' in str(c).lower()]
                
                if inv_cols:
                    df_raw_inv['Inv Total'] = df_raw_inv[inv_cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)
                    # Agrupar por Material para tener una sola fila por SKU (suma de todos los lotes/almacenes)
                    df_inv_grouped = df_raw_inv.groupby(mat_col)['Inv Total'].sum().reset_index()
                    df_inv = df_inv_grouped.rename(columns={mat_col: 'Material', 'Inv Total': 'Inv Kg-L'})
                    df_inv['Material'] = df_inv['Material'].astype(str).str.strip()

        # 3. Cargar Master/Despachos (Prioridad: 'Master Actual')
        # Si 'Master Actual' contiene ventas, lo usaremos.
        df_sales = pd.DataFrame()
        master_sheet = next((s for s in sheet_names if 'Master Actual' in s), None)
        # TODO: Implementar lógica de ventas si es necesario y clara
        
        # --- Consolidación ---
        
        if not df_fcst.empty:
            # Empezamos con el forecast como base principal (tiene fechas y materiales)
            df_final = df_fcst.copy()
            
            # Asegurar tipo de dato para merge
            df_final['Material'] = df_final['Material'].astype(str).str.strip()
            
            # Merge Inventario (Left Join en Material)
            if not df_inv.empty:
                # Como el inventario es un snapshot único, lo pegamos a todas las fechas del material
                df_final = pd.merge(df_final, df_inv, on='Material', how='left')
                df_final['Inv Kg-L'] = df_final['Inv Kg-L'].fillna(0)
            else:
                df_final['Inv Kg-L'] = 0
                
            # Merge Despachos (si tuviéramos)
            df_final['Despachos KL'] = 0 # Placeholder por ahora
            
            st.success("✅ Datos consolidados correctamente de múltiples hojas.")
            return df_final
            
        else:
            # Si no encontramos forecast, intentar cargar la primera hoja como fallback (método antiguo)
            st.warning("⚠️ No se detectó hoja de Forecast estándar. Intentando carga genérica de primera hoja...")
            preview = pd.read_excel(xl, sheet_name=0, header=None, nrows=20)
            header_row = _find_header_row(preview)
            df = pd.read_excel(xl, sheet_name=0, header=header_row)
            return df
        
    except Exception as e:
        st.error(f"Error al leer Excel: {e}")
        import traceback
        st.text(traceback.format_exc())
        return None

@st.cache_data
def load_data():
    """
    Carga el archivo Excel desde la carpeta data
    """
    # Buscar archivo Excel en la carpeta data
    data_path = Path(__file__).parent.parent / "data"
    
    if not data_path.exists():
        st.warning("Creando carpeta 'data'...")
        data_path.mkdir(parents=True, exist_ok=True)
        return None
    
    # Buscar archivos Excel
    excel_files = list(data_path.glob("*.xlsx")) + list(data_path.glob("*.xls"))
    
    if not excel_files:
        return None
    
    # Usar el primer archivo encontrado
    file_path = excel_files[0]
    
    try:
        # Usar la carga inteligente
        df = load_from_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {str(e)}")
        return None

def unpivot_date_columns(df, value_column_name='FCST'):
    """
    Transforma un DataFrame con fechas como columnas a formato largo.
    Detecta columnas de fecha (ej: 'Enero 2026', 'Febrero 2026') y las convierte en filas.
    """
    # Identificar columna de material
    material_col = None
    descripcion_col = None
    
    df_cols_lower = [str(c).lower().strip() for c in df.columns]
    
    # Mapeo manual basado en inspección: 'CODIGO SAP'
    possible_material_cols = ['codigo sap', 'codigo', 'material', 'sku']
    possible_desc_cols = ['producto', 'descripcion', 'descripción']
    
    for col in df.columns:
        c_low = str(col).lower().strip()
        if material_col is None and c_low in possible_material_cols:
            material_col = col
        if descripcion_col is None and c_low in possible_desc_cols:
            descripcion_col = col
            
    if not material_col:
        # Fallback agresivo: buscar cualquier columna que contenga "cod"
        for col in df.columns:
            if 'cod' in str(col).lower():
                material_col = col
                break
    
    if not material_col:
        st.warning("No se encontró columna de material para transformar datos")
        return df

    # Identificar columnas de fecha
    date_patterns = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                     'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    
    date_columns = []
    id_vars = [material_col]
    if descripcion_col:
        id_vars.append(descripcion_col)

    # Agregar columnas Extra si existen (ej. Segmento)
    for col in df.columns:
        if str(col).lower() in ['segmento', 'um', 'origen']:
            id_vars.append(col)
        elif isinstance(col, str) and any(p in col.lower() for p in date_patterns):
            # Verificar si no es una columna de "Dif" o "Var"
            if 'dif' not in col.lower() and 'var' not in col.lower() and 'venta' not in col.lower() and '$' not in col:
                date_columns.append(col)
        # Soporte para columnas datetime directas
        elif isinstance(col, pd.Timestamp) or 'datetime' in str(type(col)):
             date_columns.append(col)

    if not date_columns:
        return df

    # Transformar
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=date_columns,
        var_name='Fecha',
        value_name=value_column_name
    )
    
    # Limpieza final
    rename_dict = {material_col: 'Material'}
    if descripcion_col:
        rename_dict[descripcion_col] = 'Descripción'
    df_long = df_long.rename(columns=rename_dict)
    
    # Convertir Fechas
    # Manejar fechas que ya son datetime y texto mezclado
    def parse_dates_custom(x):
        try:
            return pd.to_datetime(x)
        except:
            return pd.to_datetime(x, format='%B %Y', errors='coerce') # Intento con nombre de mes español (necesita locale set o map manual)
            
    # Mapeo manual de meses español a inglés para parseo fácil sin locale
    es_to_en = {
        'enero': 'January', 'febrero': 'February', 'marzo': 'March', 'abril': 'April',
        'mayo': 'May', 'junio': 'June', 'julio': 'July', 'agosto': 'August',
        'septiembre': 'September', 'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
    }
    
    def clean_date_str(x):
        if isinstance(x, pd.Timestamp):
            return x
        s = str(x).lower()
        for es, en in es_to_en.items():
            if es in s:
                # Eliminar sufijos numéricos si existen (ej. ".1")
                s = s.split('.')[0] 
                # Reemplazar mes
                s = s.replace(es, en)
                return s
        return x

    df_long['Fecha_Str'] = df_long['Fecha'].apply(clean_date_str)
    df_long['Fecha'] = pd.to_datetime(df_long['Fecha_Str'], errors='coerce')
    df_long.drop(columns=['Fecha_Str'], inplace=True)
    
    # Eliminar fechas inválidas
    df_long = df_long.dropna(subset=['Fecha'])

    return df_long


def process_data(df):
    """
    Procesa y limpia los datos del Excel
    """
    if df is None or df.empty:
        return df
    
    # Copiar dataframe para no modificar el original
    df = df.copy()
    
    # Limpiar nombres de columnas
    df.columns = [str(col).strip() for col in df.columns]

    # --- Estandarización de nombres de columnas ---
    # Mapa para renombrar columnas alternativas a los nombres estándar usados en la app
    canonical_map = {
        # Material
        'material': 'Material', 'materiales': 'Material', 'sku': 'Material', 
        'código': 'Material', 'codigo': 'Material', 'producto': 'Material',
        'código material': 'Material', 'codigo material': 'Material',        'codigo sap': 'Material', 'c\u00f3digo sap': 'Material',        'descripción material': 'Descripción',
        'descripcion material': 'Descripción',
        # Fecha
        'fecha': 'Fecha', 'mes': 'Mes', 'periodo': 'Fecha', 'date': 'Fecha', 'month': 'Mes',
        # Forecast
        'fcst': 'FCST', 'f (mkl)': 'FCST', 'forecast': 'FCST', 'presupuesto': 'FCST', 'ppto': 'FCST', 'f': 'FCST',
        # Inventario
        'inv kg-l': 'Inv Kg-L', 'inventario': 'Inv Kg-L', 'inv (mkl)': 'Inv Kg-L', 'stock': 'Inv Kg-L', 'inv': 'Inv Kg-L', 'inv.': 'Inv Kg-L', 'existencia': 'Inv Kg-L',
        # Despachos
        'despachos kl': 'Despachos KL', 'desp (mkl)': 'Despachos KL', 'despachos': 'Despachos KL', 'venta': 'Despachos KL', 'venta real': 'Despachos KL', 'desp': 'Despachos KL', 'salidas': 'Despachos KL',
        # Otros
        'origen': 'Origen',
        'cob(d)': 'Cob(D)',
        'cob (d)': 'Cob(D)',
        'cobertura': 'Cob(D)',
        'q': 'Q',
        'q (mkl)': 'Q'
    }

    new_columns = []
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in canonical_map:
            new_columns.append(canonical_map[col_lower])
        else:
            new_columns.append(col)
    df.columns = new_columns
    
    # --- Lógica mejorada para la creación de la columna 'Fecha' ---
    # Prioridad: 1. Columna 'Fecha' existente, 2. Columna 'Mes' existente.
    if not ('Fecha' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Fecha'])):
        date_col_source = None
        if 'Fecha' in df.columns:
            date_col_source = 'Fecha'
        elif 'Mes' in df.columns:
            date_col_source = 'Mes'

        if date_col_source:
            try:
                df['Fecha'] = pd.to_datetime(df[date_col_source], errors='coerce')
                
                if df['Fecha'].isna().all():
                    st.warning(f"La columna '{date_col_source}' no pudo ser convertida a fechas válidas. Verifique el formato en el archivo Excel.")
                elif df['Fecha'].isna().any():
                     st.info(f"Algunos valores en la columna '{date_col_source}' no pudieron ser convertidos a fecha y fueron ignorados.")

            except Exception as e:
                st.error(f"Ocurrió un error inesperado al procesar la columna de fecha '{date_col_source}': {e}")
    
    if 'Fecha' not in df.columns:
        st.warning("No se encontró una columna de fecha ('Fecha' o 'Mes'). Los filtros y gráficos basados en tiempo no estarán disponibles.")
    
    # Convertir columnas numéricas
    numeric_columns = ['FCST', 'Prod Kg-L', 'Inv Kg-L', 'Q', 'Cob(D)', 'Cobertura', 
                       'Inventario', 'Despachos KL', 'FCST Act']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calcular cobertura si no existe
    if 'Cob(D)' not in df.columns and 'Inv Kg-L' in df.columns and 'FCST' in df.columns:
        # Cobertura = (Inventario / FCST) * 30 días (aproximado)
        df['Cob(D)'] = (df['Inv Kg-L'] / df['FCST'].replace(0, 1)) * 30
    
    # Categorizar estados de cobertura
    if 'Cob(D)' in df.columns:
        df['Estado_Cobertura'] = df['Cob(D)'].apply(categorize_cobertura)
    
    return df
