import pandas as pd
import numpy as np

def calculate_cobertura(inventario, demanda_mensual):
    """
    Calcula días de cobertura
    Cobertura (días) = (Inventario / Demanda mensual) * 30
    """
    if demanda_mensual == 0 or pd.isna(demanda_mensual):
        return 0
    return (inventario / demanda_mensual) * 30

def calculate_wape(forecast, actual):
    """
    Calcula WAPE (Weighted Absolute Percentage Error)
    WAPE = (Σ|Actual - Forecast| / Σ|Actual|) * 100
    """
    if isinstance(forecast, pd.Series) and isinstance(actual, pd.Series):
        total_actual = actual.sum()
        if total_actual == 0:
            return 0
        return (abs(actual - forecast).sum() / total_actual) * 100
    else:
        if actual == 0:
            return 0
        return (abs(actual - forecast) / actual) * 100

def categorize_cobertura(dias):
    """
    Categoriza el estado de cobertura
    """
    if pd.isna(dias):
        return "Sin Dato"
    elif dias < 45:
        return "Cob < 45"
    elif dias < 90:
        return "Cob < 90"
    else:
        return "Cob > 90"

def calculate_estado_stats(df, estado_col='Estado_Cobertura'):
    """
    Calcula estadísticas por estado de cobertura
    """
    if estado_col not in df.columns:
        return pd.DataFrame()
    
    stats = df.groupby(estado_col).agg({
        'Material': 'count',
        'Inv Kg-L': 'sum',
        'FCST': 'sum'
    }).reset_index()
    
    stats.columns = ['Estado', 'Cantidad_SKU', 'Inventario_Total', 'FCST_Total']
    
    # Calcular porcentajes
    total_sku = stats['Cantidad_SKU'].sum()
    stats['Porcentaje_SKU'] = (stats['Cantidad_SKU'] / total_sku * 100).round(1)
    
    return stats

def calculate_top_materials(df, value_col='Inv Kg-L', top_n=15, ascending=False):
    """
    Obtiene los top N materiales por valor
    """
    if value_col not in df.columns or 'Material' not in df.columns:
        return pd.DataFrame()
    
    top = df.nlargest(top_n, value_col) if not ascending else df.nsmallest(top_n, value_col)
    
    # Seleccionar columnas dinámicamente
    cols_to_return = ['Material', value_col]
    if 'Origen' in df.columns:
        cols_to_return.append('Origen')
    if 'Descripción' in df.columns:
        cols_to_return.append('Descripción')
        
    return top[cols_to_return].copy()

def calculate_evolucion_inventario(df, fecha_col='Fecha', inv_col='Inv Kg-L'):
    """
    Calcula la evolución del inventario por mes
    """
    if fecha_col not in df.columns or inv_col not in df.columns:
        return pd.DataFrame()
    
    evolucion = df.groupby(fecha_col).agg({
        inv_col: 'sum',
        'FCST': 'sum',
        'Despachos KL': 'sum'
    }).reset_index()
    
    return evolucion

def calculate_wape_evolution(df, fecha_col='Fecha'):
    """
    Calcula la evolución del WAPE por mes
    """
    if fecha_col not in df.columns:
        return pd.DataFrame()
    
    wape_data = []
    
    for fecha in df[fecha_col].unique():
        df_mes = df[df[fecha_col] == fecha]
        
        if 'FCST' in df_mes.columns and 'Despachos KL' in df_mes.columns:
            fcst_total = df_mes['FCST'].sum()
            desp_total = df_mes['Despachos KL'].sum()
            
            wape = calculate_wape(fcst_total, desp_total)
            dif = abs(desp_total - fcst_total)
            
            wape_data.append({
                'Fecha': fecha,
                'FCST': fcst_total,
                'Despachos': desp_total,
                'Dif_Wape_Abs': dif,
                'Wape_%': wape
            })
    
    return pd.DataFrame(wape_data)

def calculate_distribucion_origen(df):
    """
    Calcula la distribución de SKUs por origen
    """
    if 'Origen' not in df.columns:
        return pd.DataFrame()
    
    dist = df.groupby('Origen').agg({
        'Material': 'nunique'
    }).reset_index()
    
    dist.columns = ['Origen', 'N_SKU']
    dist = dist.sort_values('N_SKU', ascending=True)
    
    return dist
